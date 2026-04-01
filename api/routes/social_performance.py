"""Cross-platform social performance for dashboard (YouTube, Instagram, Facebook)."""

from __future__ import annotations

import asyncio
import copy
import json
import logging
import os
import time
from typing import Any, Dict, Optional, Tuple

from fastapi import APIRouter, HTTPException, Query, Response

from core.config import get_settings
from api_integrations.facebook import FacebookIntegration
from api_integrations.instagram import InstagramIntegration

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

_OVERVIEW_TTL = float(os.environ.get("SOCIAL_OVERVIEW_CACHE_TTL", "120"))
_POST_INSIGHTS_TTL = float(os.environ.get("SOCIAL_POST_INSIGHTS_CACHE_TTL", "180"))
_OVERVIEW_CACHE: Optional[Tuple[float, Dict[str, Any]]] = None
_POST_INSIGHTS_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}


def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _meta_token_path() -> str:
    return os.path.join(_project_root(), "meta_token.json")


def load_meta_credentials() -> Optional[Dict[str, Any]]:
    data: Dict[str, Any] = {}
    path = _meta_token_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.warning("Could not read meta_token.json: %s", e)
    token = data.get("facebook_access_token") or settings.facebook_access_token
    page_id = data.get("facebook_page_id") or settings.facebook_page_id
    ig_id = data.get("instagram_business_account_id") or settings.instagram_business_account_id
    if not token:
        return None
    return {
        "access_token": token,
        "page_id": page_id,
        "instagram_business_account_id": ig_id,
    }


def _youtube_integration():
    from api.routes.youtube import get_youtube_integration

    return get_youtube_integration()


def _youtube_channel_id(integration) -> Optional[str]:
    import os as _os

    cid = _os.getenv("YOUTUBE_CHANNEL_ID")
    if cid:
        return cid
    from api.routes.youtube import get_channel_id_from_oauth

    return get_channel_id_from_oauth(integration)


def build_social_overview() -> Dict[str, Any]:
    """
    Channel-level metrics + recent posts/videos for YouTube, Instagram, and Facebook (sync; run via thread pool).
    Each block includes `connected` and optional `error` when credentials are missing or APIs fail.
    """
    out: Dict[str, Any] = {
        "youtube": {"connected": False, "channel": None, "posts": []},
        "instagram": {"connected": False, "channel": None, "posts": []},
        "facebook": {"connected": False, "channel": None, "posts": []},
    }

    # --- YouTube (OAuth can list uploads without YOUTUBE_CHANNEL_ID) ---
    try:
        yt = _youtube_integration()
        ch_id = _youtube_channel_id(yt)
        stats: Dict[str, Any] = {}
        if ch_id:
            stats = yt.sync_channel_stats(ch_id) or {}
            if "error" not in stats:
                out["youtube"]["channel"] = {
                    "id": ch_id,
                    "name": stats.get("channel_name", "YouTube"),
                    "subscribers": stats.get("subscriber_count", 0),
                    "total_views": stats.get("view_count", 0),
                    "video_count": stats.get("video_count", 0),
                }
            else:
                out["youtube"]["error"] = stats.get("error")

        vids = yt.sync_video_analytics(ch_id, max_videos=30)
        if isinstance(vids, dict):
            if "error" in vids:
                out["youtube"]["videos_error"] = vids.get("error")
            for v in vids.get("videos", []) or []:
                out["youtube"]["posts"].append(
                    {
                        "id": v.get("video_id"),
                        "title": v.get("title", ""),
                        "subtitle": v.get("published_at", ""),
                        "metrics": {
                            "views": v.get("views", 0),
                            "likes": v.get("likes", 0),
                            "comments": v.get("comments", 0),
                        },
                    }
                )

        if out["youtube"]["channel"] or out["youtube"]["posts"]:
            out["youtube"]["connected"] = True
    except Exception as e:
        logger.exception("YouTube overview failed")
        out["youtube"]["error"] = str(e)

    # --- Meta (Instagram + Facebook) ---
    meta = load_meta_credentials()
    if not meta:
        out["instagram"]["error"] = "Meta not connected (token / .env)"
        out["facebook"]["error"] = "Meta not connected (token / .env)"
        return out

    access_token = meta["access_token"]

    # Instagram
    if meta.get("instagram_business_account_id"):
        try:
            ig = InstagramIntegration(
                {
                    "access_token": access_token,
                    "instagram_business_account_id": meta["instagram_business_account_id"],
                }
            )
            acc = ig.sync_account_info()
            if "error" not in acc:
                out["instagram"]["connected"] = True
                out["instagram"]["channel"] = {
                    "username": acc.get("username"),
                    "followers": acc.get("followers_count", 0),
                    "media_count": acc.get("media_count", 0),
                    "profile_picture_url": acc.get("profile_picture_url"),
                }
            else:
                out["instagram"]["error"] = acc.get("error")
            posts = ig.sync_posts(limit=25, include_insights=False)
            if "error" not in posts:
                for p in posts.get("posts", []):
                    ins = p.get("insights") or {}
                    out["instagram"]["posts"].append(
                        {
                            "id": p.get("post_id"),
                            "title": (p.get("caption") or "")[:120] or p.get("media_type", "Media"),
                            "subtitle": p.get("timestamp", ""),
                            "permalink": p.get("permalink"),
                            "media_type": p.get("media_type"),
                            "metrics": {
                                "likes": p.get("likes", 0),
                                "comments": p.get("comments", 0),
                                "impressions": ins.get("impressions"),
                                "reach": ins.get("reach"),
                                "engagement": ins.get("engagement")
                                or ins.get("total_interactions"),
                            },
                        }
                    )
            else:
                out["instagram"]["error"] = posts.get("error")
        except Exception as e:
            logger.exception("Instagram overview failed")
            out["instagram"]["error"] = str(e)
    else:
        out["instagram"]["error"] = "Instagram Business Account ID not configured"

    # Facebook
    if meta.get("page_id"):
        try:
            fb = FacebookIntegration(
                {"access_token": access_token, "page_id": meta["page_id"]}
            )
            page = fb.get_page_public_info()
            insights = fb.sync_page_insights()
            if "error" not in page:
                out["facebook"]["connected"] = True
                ins_data = (insights.get("insights") or {}) if isinstance(insights, dict) else {}
                imp = ins_data.get("page_media_view") or ins_data.get("page_impressions")
                eng = ins_data.get("page_post_engagements") or ins_data.get("page_engaged_users")
                out["facebook"]["channel"] = {
                    "name": page.get("name", "Facebook Page"),
                    "fan_count": page.get("fan_count", 0),
                    "link": page.get("link"),
                    "picture": (page.get("picture") or {}).get("data", {}).get("url"),
                    "impressions_30d": (imp or {}).get("current"),
                    "engaged_users_30d": (eng or {}).get("current"),
                    "fans_series_end": (ins_data.get("page_fans") or {}).get("end_time"),
                }
            else:
                out["facebook"]["error"] = page.get("error")
            if "error" in insights and "error" not in out["facebook"]:
                out["facebook"]["insights_error"] = insights.get("error")
            raw_posts = fb.sync_page_posts(limit=25)
            if "error" not in raw_posts:
                for p in raw_posts.get("posts", []):
                    msg = p.get("message") or ""
                    out["facebook"]["posts"].append(
                        {
                            "id": p.get("post_id"),
                            "title": msg[:120] or "Post",
                            "subtitle": p.get("created_time", ""),
                            "metrics": {
                                "likes": p.get("likes", 0),
                                "comments": p.get("comments", 0),
                                "shares": p.get("shares", 0),
                            },
                        }
                    )
            else:
                if not out["facebook"].get("error"):
                    out["facebook"]["posts_error"] = raw_posts.get("error")
        except Exception as e:
            logger.exception("Facebook overview failed")
            out["facebook"]["error"] = str(e)
    else:
        out["facebook"]["error"] = "Facebook Page ID not configured"

    return out


@router.get("/overview")
async def social_overview(
    response: Response,
    force_refresh: bool = Query(False, description="Bypass server-side cache"),
) -> Dict[str, Any]:
    """Cached overview; use force_refresh=true after publishing or changing tokens."""
    global _OVERVIEW_CACHE
    now = time.monotonic()
    if not force_refresh and _OVERVIEW_CACHE is not None:
        ts, cached = _OVERVIEW_CACHE
        if now - ts < _OVERVIEW_TTL:
            response.headers["X-Social-Cache"] = "HIT"
            remaining = max(0, int(_OVERVIEW_TTL - (now - ts)))
            response.headers["Cache-Control"] = f"private, max-age={remaining}"
            return copy.deepcopy(cached)

    payload = await asyncio.to_thread(build_social_overview)
    _OVERVIEW_CACHE = (time.monotonic(), copy.deepcopy(payload))
    response.headers["X-Social-Cache"] = "MISS"
    response.headers["Cache-Control"] = f"private, max-age={int(_OVERVIEW_TTL)}"
    return payload


def _compute_post_insights_sync(platform: str, item_id: str) -> Dict[str, Any]:
    """Sync body for post-insights (runs in thread pool)."""
    if platform == "youtube":
        yt = _youtube_integration()
        detail = yt.get_single_video_stats(item_id)
        if isinstance(detail, dict) and "error" in detail:
            raise RuntimeError(str(detail.get("error")))
        return {"platform": "youtube", "detail": detail}

    meta = load_meta_credentials()
    if not meta:
        raise ValueError("Meta credentials not configured")

    if platform == "instagram":
        if not meta.get("instagram_business_account_id"):
            raise ValueError("Instagram Business Account ID missing")
        ig = InstagramIntegration(
            {
                "access_token": meta["access_token"],
                "instagram_business_account_id": meta["instagram_business_account_id"],
            }
        )
        detail = ig.get_media_insights_detail(item_id)
        if isinstance(detail, dict) and "error" in detail:
            raise RuntimeError(str(detail.get("error")))
        return {"platform": "instagram", "detail": detail}

    if not meta.get("page_id"):
        raise ValueError("Facebook Page ID missing")
    fb = FacebookIntegration(
        {"access_token": meta["access_token"], "page_id": meta["page_id"]}
    )
    detail = fb.get_post_insights(item_id)
    if isinstance(detail, dict) and "error" in detail:
        raise RuntimeError(str(detail.get("error")))
    return {"platform": "facebook", "detail": detail}


@router.get("/post-insights")
async def post_insights(
    response: Response,
    platform: str = Query(..., description="youtube | instagram | facebook"),
    item_id: str = Query(..., description="Video ID, IG media ID, or FB post ID"),
    force_refresh: bool = Query(False, description="Bypass server-side cache for this item"),
) -> Dict[str, Any]:
    platform = platform.lower().strip()
    if platform not in ("youtube", "instagram", "facebook"):
        raise HTTPException(status_code=400, detail="platform must be youtube, instagram, or facebook")

    cache_key = f"{platform}:{item_id}"
    now = time.monotonic()
    if not force_refresh and cache_key in _POST_INSIGHTS_CACHE:
        ts, cached = _POST_INSIGHTS_CACHE[cache_key]
        if now - ts < _POST_INSIGHTS_TTL:
            response.headers["X-Social-Cache"] = "HIT"
            remaining = max(0, int(_POST_INSIGHTS_TTL - (now - ts)))
            response.headers["Cache-Control"] = f"private, max-age={remaining}"
            return copy.deepcopy(cached)

    try:
        body = await asyncio.to_thread(_compute_post_insights_sync, platform, item_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    except Exception as e:
        logger.exception("post-insights failed")
        raise HTTPException(status_code=502, detail=str(e)) from e

    _POST_INSIGHTS_CACHE[cache_key] = (time.monotonic(), copy.deepcopy(body))
    response.headers["X-Social-Cache"] = "MISS"
    response.headers["Cache-Control"] = f"private, max-age={int(_POST_INSIGHTS_TTL)}"
    return body
