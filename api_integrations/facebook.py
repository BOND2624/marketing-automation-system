"""Facebook Graph API integration."""

import logging
import os
import requests
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from api_integrations.base import BaseIntegration

logger = logging.getLogger(__name__)


def _facebook_graph_root() -> str:
    """Allow `FACEBOOK_GRAPH_API_VERSION=v19.0` in .env if v21 field errors persist."""
    v = (os.environ.get("FACEBOOK_GRAPH_API_VERSION") or "v21.0").strip()
    if not v.startswith("v"):
        v = f"v{v}"
    return f"https://graph.facebook.com/{v}"


class FacebookIntegration(BaseIntegration):
    """Integration with Facebook Graph API."""
    
    def __init__(self, credentials: Dict[str, Any]):
        """
        Initialize Facebook integration.
        
        Args:
            credentials: Should contain 'access_token' and optionally 'page_id'
        """
        super().__init__(credentials, rate_limit_calls=200, rate_limit_period=3600)  # 200/hour default
        self.access_token = credentials.get("access_token")
        self.page_id = credentials.get("page_id")
        
        if not self.access_token:
            raise ValueError("Facebook access token is required")
        self._page_tokens_cache: Optional[List[str]] = None

    def _page_tokens_to_try(self) -> List[str]:
        """
        Collect Page access tokens to try (deduped, best first).

        1) GET /{page-id}?fields=access_token — Meta's primary way to get a Page token
           from a User token when you admin the Page (often works when /me/accounts is empty).
        2) GET /me/accounts — classic listing (needs pages_show_list on the User token).
        3) The configured token last (may already be a Page token).
        """
        if self._page_tokens_cache is not None:
            return self._page_tokens_cache

        tokens: List[str] = []
        seen: set = set()

        def add(tok: Optional[str]) -> None:
            if not tok or not isinstance(tok, str):
                return
            s = tok.strip()
            if s and s not in seen:
                seen.add(s)
                tokens.append(s)

        base = self.access_token.strip() if self.access_token else ""

        if self.page_id:
            # (1) Page node — documented: User token + page role returns page access_token
            pn = self._graph_get(
                str(self.page_id),
                {"fields": "id,access_token"},
                silent=True,
                access_token=self.access_token,
            )
            if isinstance(pn, dict) and not pn.get("error"):
                add(pn.get("access_token"))
                if tokens:
                    logger.info(
                        "Resolved Page access token via GET /%s?fields=access_token",
                        self.page_id,
                    )
            elif isinstance(pn, dict) and pn.get("error"):
                logger.debug(
                    "GET /{page-id}?fields=access_token: %s",
                    self._graph_error_message(pn),
                )

            # (2) /me/accounts
            data = self._graph_get(
                "me/accounts",
                {"fields": "id,access_token"},
                silent=True,
                access_token=self.access_token,
            )
            if isinstance(data, dict) and not data.get("error") and isinstance(data.get("data"), list):
                for acct in data["data"]:
                    if str(acct.get("id")) == str(self.page_id):
                        add(acct.get("access_token"))
                        logger.info("Page token from /me/accounts for page %s", self.page_id)
                        break
            elif isinstance(data, dict) and data.get("error"):
                logger.debug(
                    "me/accounts: %s",
                    self._graph_error_message(data),
                )

        add(base)

        self._page_tokens_cache = tokens
        return tokens

    def _graph_get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        *,
        silent: bool = False,
        access_token: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """GET Graph API; if silent=True, no ERROR logs; still returns JSON body on 4xx so callers can read `error`."""
        if not params:
            params = {}
        tok = access_token if access_token is not None else self.access_token
        merged = {**params, "access_token": tok}
        try:
            self._handle_rate_limit()
            response = requests.get(f"{_facebook_graph_root()}/{endpoint}", params=merged, timeout=60)
            try:
                body = response.json()
            except Exception:
                body = {"error": {"message": (response.text or "")[:400]}}

            if response.status_code != 200:
                if silent:
                    logger.debug(
                        "Facebook Graph non-OK %s: %s %s",
                        endpoint,
                        response.status_code,
                        (response.text or "")[:400],
                    )
                    if not isinstance(body, dict):
                        body = {"error": {"message": f"HTTP {response.status_code}"}}
                    return body
                response.raise_for_status()
            return body if isinstance(body, dict) else {"error": {"message": str(body)}}
        except requests.exceptions.RequestException as e:
            if silent:
                logger.debug("Facebook Graph request error %s: %s", endpoint, e)
                return {"error": {"message": str(e)}}
            logger.error("Facebook API request failed: %s", e)
            raise

    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to Facebook Graph API."""
        data = self._graph_get(endpoint, params, silent=False)
        assert data is not None
        return data
    
    def test_connection(self) -> bool:
        """Test Facebook API connection."""
        try:
            self._make_request("me")
            return True
        except Exception as e:
            logger.error(f"Facebook connection test failed: {e}")
            return False

    def _page_insights_request(self, page_id: str, params: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """GET /{page_id}/insights; returns (http_status, body_dict)."""
        merged = {**params, "access_token": self.access_token}
        self._handle_rate_limit()
        response = requests.get(
            f"{_facebook_graph_root()}/{page_id}/insights",
            params=merged,
            timeout=60,
        )
        try:
            body = response.json()
        except Exception:
            body = {"error": {"message": (response.text or "")[:300]}}
        return response.status_code, body

    @staticmethod
    def _graph_error_message(body: Dict[str, Any]) -> Optional[str]:
        err = body.get("error")
        if not err:
            return None
        if isinstance(err, dict):
            msg = err.get("message") or err.get("error_user_msg") or ""
            code = err.get("code")
            sub = err.get("error_subcode")
            parts = [msg.strip()] if msg else []
            if code is not None:
                parts.append(f"code={code}")
            if sub is not None:
                parts.append(f"subcode={sub}")
            return " ".join(parts) if parts else str(err)
        return str(err)

    def sync_page_insights(self, page_id: Optional[str] = None, metrics: Optional[list] = None) -> Dict[str, Any]:
        """
        Sync Facebook page insights.
        
        Args:
            page_id: Facebook page ID (uses self.page_id if not provided)
            metrics: List of metrics to fetch (default: page_media_view, page_post_engagements; see Meta deprecated-metrics doc)
        """
        target_page_id = page_id or self.page_id
        if not target_page_id:
            return {"error": "Facebook Page ID is required"}
        
        if not metrics:
            # page_impressions / page_engaged_users return (#100) invalid metric since Meta deprecations (use replacements).
            metrics = ["page_media_view", "page_post_engagements"]

        try:
            until_ts = int(datetime.utcnow().timestamp())
            since_ts = int((datetime.utcnow().timestamp() - 30 * 86400))
            metric_str = ",".join(metrics)
            # Order: periods that avoid since/until issues first, then split metrics (combined calls often fail).
            attempts: List[Dict[str, Any]] = [
                {"metric": "page_media_view", "period": "days_28"},
                {"metric": "page_post_engagements", "period": "days_28"},
                {"metric": metric_str, "period": "days_28"},
                {"metric": "page_media_view", "period": "week"},
                {"metric": "page_post_engagements", "period": "week"},
                {"metric": metric_str, "period": "day", "since": since_ts, "until": until_ts},
                {"metric": "page_media_view", "period": "day", "since": since_ts, "until": until_ts},
                {"metric": "page_post_engagements", "period": "day", "since": since_ts, "until": until_ts},
                {"metric": metric_str, "period": "day"},
                {"metric": "page_media_view", "period": "day"},
                {"metric": "page_post_engagements", "period": "day"},
            ]

            seen = set()
            unique_attempts = []
            for p in attempts:
                key = tuple(sorted((k, str(v)) for k, v in p.items()))
                if key in seen:
                    continue
                seen.add(key)
                unique_attempts.append(p)

            insights_data: Dict[str, Any] = {}
            last_graph_error: Optional[str] = None

            for params in unique_attempts:
                status, body = self._page_insights_request(target_page_id, params)
                if status != 200:
                    last_graph_error = self._graph_error_message(body) or f"HTTP {status}"
                    logger.debug("FB insights attempt failed %s: %s", params, last_graph_error)
                    continue
                if body.get("error"):
                    last_graph_error = self._graph_error_message(body) or str(body.get("error"))
                    logger.debug("FB insights body error %s: %s", params, last_graph_error)
                    continue

                for insight in body.get("data") or []:
                    metric_name = insight.get("name")
                    values = insight.get("values") or []
                    if not metric_name or metric_name in insights_data:
                        continue
                    if values:
                        insights_data[metric_name] = {
                            "current": values[-1].get("value", 0),
                            "values": [v.get("value", 0) for v in values],
                            "end_time": values[-1].get("end_time"),
                        }

                if "page_media_view" in insights_data and "page_post_engagements" in insights_data:
                    break

            if not insights_data:
                hint = (
                    "Use the Page access_token from GET /me/accounts (long-lived user token). "
                    "App: read_insights + pages_read_engagement. Avoid User tokens for /{page-id}/insights."
                )
                detail = last_graph_error or "No metrics returned (permission or unsupported combination)."
                return {
                    "error": f"{detail} — {hint}",
                    "insights": {},
                    "facebook_graph_error": last_graph_error,
                }

            return {
                "insights": insights_data,
                "synced_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return self._handle_error(e, "sync_page_insights")
    
    def sync_page_posts(self, page_id: Optional[str] = None, limit: int = 25) -> Dict[str, Any]:
        """
        Sync Facebook page posts.
        
        Args:
            page_id: Facebook page ID
            limit: Maximum number of posts to fetch
        """
        target_page_id = page_id or self.page_id
        if not target_page_id:
            return {"error": "Facebook Page ID is required"}
        
        try:
            lim = min(limit, 25)
            # `reactions.limit(0).summary(true)` is the reliable pattern for totals without paging reactions.
            # Try Page token from /me/accounts first when the stored token is a User token.
            core = (
                "id,message,created_time,"
                "reactions.limit(0).summary(true),comments.limit(0).summary(true),shares"
            )
            core_alt = (
                "id,message,created_time,reactions.summary(true),comments.summary(true),shares"
            )
            core_no_shares = (
                "id,message,created_time,"
                "reactions.limit(0).summary(true),comments.limit(0).summary(true)"
            )
            core_no_shares_alt = (
                "id,message,created_time,reactions.summary(true),comments.summary(true)"
            )
            with_permalink = (
                "id,message,created_time,permalink_url,"
                "reactions.limit(0).summary(true),comments.limit(0).summary(true),shares"
            )
            with_story = (
                "id,message,story,created_time,"
                "reactions.limit(0).summary(true),comments.limit(0).summary(true),shares"
            )
            variants: List[Tuple[str, Dict[str, Any]]] = [
                ("posts", {"fields": core, "limit": lim}),
                ("posts", {"fields": core_no_shares, "limit": lim}),
                ("posts", {"fields": core_alt, "limit": lim}),
                ("posts", {"fields": core_no_shares_alt, "limit": lim}),
                ("published_posts", {"fields": core, "limit": lim}),
                ("published_posts", {"fields": core_no_shares, "limit": lim}),
                ("published_posts", {"fields": core_alt, "limit": lim}),
                ("feed", {"fields": core, "limit": lim}),
                ("feed", {"fields": core_no_shares, "limit": lim}),
                ("feed", {"fields": core_alt, "limit": lim}),
                ("posts", {"fields": with_permalink, "limit": lim}),
                ("posts", {"fields": with_story, "limit": lim}),
                (
                    "posts",
                    {
                        "fields": "id,message,created_time,likes.summary(true),comments.summary(true),shares",
                        "limit": lim,
                    },
                ),
            ]

            minimal_variants: List[Tuple[str, Dict[str, Any]]] = [
                ("posts", {"fields": "id,message,story,created_time,permalink_url", "limit": lim}),
                ("feed", {"fields": "id,message,story,created_time", "limit": lim}),
                ("posts", {"fields": "id,message,created_time", "limit": lim}),
                ("published_posts", {"fields": "id,message,created_time", "limit": lim}),
                ("feed", {"fields": "id,message,created_time", "limit": lim}),
                ("posts", {"fields": "id,created_time", "limit": lim}),
            ]

            response: Optional[Dict[str, Any]] = None
            last_fail_hint: Optional[str] = None
            metrics_degraded = False

            def try_variants(variant_list: List[Tuple[str, Dict[str, Any]]]) -> bool:
                nonlocal response, last_fail_hint
                for token in self._page_tokens_to_try():
                    for edge, params in variant_list:
                        r = self._graph_get(
                            f"{target_page_id}/{edge}",
                            params=params,
                            silent=True,
                            access_token=token,
                        )
                        if not r:
                            continue
                        if r.get("error"):
                            last_fail_hint = self._graph_error_message(r) or str(r.get("error"))
                            continue
                        if isinstance(r.get("data"), list):
                            response = r
                            return True
                return False

            if not try_variants(variants):
                metrics_degraded = try_variants(minimal_variants)

            if not response or not isinstance(response.get("data"), list):
                hints = (
                    "If you use a User token: include pages_show_list + pages_read_engagement, then re-authorize — "
                    "we fetch a Page token via /me/accounts. Or paste a Page access token from Graph API "
                    "Explorer (Page → Get Page Access Token). Graph error: "
                )
                detail = (last_fail_hint or "No post list returned.").strip()
                return {
                    "error": f"{hints}{detail}",
                    "posts": [],
                    "total_posts": 0,
                    "graph_error": last_fail_hint,
                }

            posts = []
            for item in response.get("data", []):
                reactions_summary = (item.get("reactions") or {}).get("summary") or {}
                likes_summary = (item.get("likes") or {}).get("summary") or {}
                reaction_total = 0
                if isinstance(reactions_summary, dict):
                    reaction_total = int(reactions_summary.get("total_count") or 0)
                if reaction_total == 0 and isinstance(likes_summary, dict):
                    reaction_total = int(likes_summary.get("total_count") or 0)

                comments_data = (item.get("comments") or {}).get("summary", {})
                comment_total = 0
                if isinstance(comments_data, dict):
                    comment_total = int(comments_data.get("total_count") or 0)

                shares_raw = item.get("shares")
                if isinstance(shares_raw, dict):
                    shares_count = int(shares_raw.get("count") or 0)
                else:
                    shares_count = 0

                text = (item.get("message") or item.get("story") or "").strip()

                posts.append(
                    {
                        "post_id": item.get("id"),
                        "message": text,
                        "permalink_url": item.get("permalink_url"),
                        "created_time": item.get("created_time"),
                        # UI label "likes" — value is total reactions (Meta standard for Page posts).
                        "likes": reaction_total,
                        "comments": comment_total,
                        "shares": shares_count,
                    }
                )

            out: Dict[str, Any] = {
                "posts": posts,
                "total_posts": len(posts),
                "synced_at": datetime.utcnow().isoformat(),
            }
            if metrics_degraded:
                out["metrics_note"] = (
                    "Posts loaded without reaction/comment/shares fields (metrics may show 0). "
                    "For full engagement, use a Page access token with pages_read_engagement, or try "
                    "FACEBOOK_GRAPH_API_VERSION=v19.0 in .env if the Graph API returns field errors."
                )
            return out
        except Exception as e:
            return self._handle_error(e, "sync_page_posts")

    def get_page_public_info(self, page_id: Optional[str] = None) -> Dict[str, Any]:
        """Basic page profile for dashboards (name, fan count, link)."""
        target_page_id = page_id or self.page_id
        if not target_page_id:
            return {"error": "Facebook Page ID is required"}
        try:
            return self._make_request(
                target_page_id,
                params={"fields": "name,fan_count,link,picture.type(large)"},
            )
        except Exception as e:
            return self._handle_error(e, "get_page_public_info")

    def get_post_insights(self, post_id: str) -> Dict[str, Any]:
        """Metrics for a single page post (Page access token; Meta deprecated post_impressions / post_engaged_users)."""
        if not post_id:
            return {"error": "post_id is required"}
        try:
            last_err: Optional[str] = None
            candidates: List[Tuple[str, Dict[str, Any]]] = [
                ("post_media_view", {"period": "lifetime"}),
                ("post_total_media_view_unique", {"period": "lifetime"}),
                ("post_clicks", {"period": "lifetime"}),
                ("post_reactions_by_type_total", {"period": "lifetime"}),
                ("post_media_view", {"period": "day"}),
                ("post_clicks", {"period": "day"}),
            ]
            for token in self._page_tokens_to_try():
                insights: Dict[str, Any] = {}
                for metric, extra in candidates:
                    if metric in insights:
                        continue
                    params = {"metric": metric, **extra}
                    data = self._graph_get(
                        f"{post_id}/insights", params, silent=True, access_token=token
                    )
                    if not data:
                        continue
                    if data.get("error"):
                        last_err = self._graph_error_message(data) or str(data.get("error"))
                        continue
                    for row in data.get("data") or []:
                        name = row.get("name") or metric
                        values = row.get("values") or []
                        if not values:
                            continue
                        raw = values[-1].get("value")
                        if raw is not None and name:
                            insights[name] = raw
                if insights:
                    return {"post_id": post_id, "insights": insights}

            return {
                "post_id": post_id,
                "insights": {},
                "error": last_err
                or "No post insights (Page token + read_insights; try re-auth with pages_show_list).",
            }
        except Exception as e:
            return self._handle_error(e, "get_post_insights")
    
    def sync_ad_performance(self, ad_account_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Sync Facebook ad performance data.
        
        Args:
            ad_account_id: Facebook ad account ID
        
        Returns:
            Dictionary with ad performance data
        """
        if not ad_account_id:
            return {"error": "Ad account ID is required", "note": "Ad performance sync requires ad account access"}
        
        try:
            params = {
                "fields": "id,name,status,insights{impressions,clicks,spend,reach,cpc,cpp,cpm}",
                "limit": 25
            }
            
            response = self._make_request(
                f"act_{ad_account_id}/ads",
                params=params
            )
            
            ads = []
            for item in response.get("data", []):
                insights = item.get("insights", {}).get("data", [])
                if insights:
                    insight = insights[0]
                    ads.append({
                        "ad_id": item.get("id"),
                        "name": item.get("name"),
                        "status": item.get("status"),
                        "impressions": insight.get("impressions", 0),
                        "clicks": insight.get("clicks", 0),
                        "spend": insight.get("spend", 0),
                        "reach": insight.get("reach", 0),
                        "cpc": insight.get("cpc", 0),
                        "cpp": insight.get("cpp", 0),
                        "cpm": insight.get("cpm", 0)
                    })
            
            return {
                "ads": ads,
                "total_ads": len(ads),
                "synced_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return self._handle_error(e, "sync_ad_performance")
    
    def publish_post(self, message: str) -> str:
        """Publish a simple text post to the Facebook page."""
        if not self.page_id:
            raise ValueError("Facebook Page ID is required for publishing")
            
        endpoint = f"{self.page_id}/feed"
        params = {
            "message": message,
            "access_token": self.access_token
        }
        
        try:
            response = requests.post(f"{_facebook_graph_root()}/{endpoint}", params=params, timeout=90)
            if response.status_code != 200:
                print(f"Facebook API Error Body: {response.text}")
            response.raise_for_status()
            return response.json().get("id")
        except requests.exceptions.HTTPError as e:
            error_detail = response.text
            try:
                error_json = response.json()
                error_detail = error_json.get("error", {}).get("message", response.text)
            except:
                pass
            print(f"Failed to publish Facebook post: {error_detail}")
            raise Exception(f"Facebook API Error: {error_detail}")
        except Exception as e:
            print(f"Failed to publish Facebook post: {e}")
            raise

    def publish_photo(self, photo_source: str, message: str = "") -> str:
        """Publish a photo to the Facebook page. photo_source can be a URL or local path."""
        if not self.page_id:
            raise ValueError("Facebook Page ID is required for publishing")
            
        endpoint = f"{self.page_id}/photos"
        is_local = os.path.exists(photo_source)
        
        params = {
            "caption": message,
            "access_token": self.access_token
        }
        
        try:
            if is_local:
                with open(photo_source, 'rb') as f:
                    files = {'source': f}
                    response = requests.post(f"{_facebook_graph_root()}/{endpoint}", params=params, files=files, timeout=90)
            else:
                params["url"] = photo_source
                response = requests.post(f"{_facebook_graph_root()}/{endpoint}", params=params, timeout=90)
                
            if response.status_code != 200:
                print(f"Facebook API Error Body: {response.text}")
            response.raise_for_status()
            return response.json().get("post_id") or response.json().get("id")
        except requests.exceptions.HTTPError as e:
            error_detail = response.text
            try:
                error_json = response.json()
                error_detail = error_json.get("error", {}).get("message", response.text)
            except:
                pass
            print(f"Failed to publish Facebook photo: {error_detail}")
            raise Exception(f"Facebook API Error: {error_detail}")
        except Exception as e:
            print(f"Failed to publish Facebook photo: {e}")
            raise

    def publish_video(self, video_source: str, description: str = "") -> str:
        """Publish a video to the Facebook page. video_source can be a URL or local path."""
        if not self.page_id:
            raise ValueError("Facebook Page ID is required for publishing")
            
        endpoint = f"{self.page_id}/videos"
        is_local = os.path.exists(video_source)
        
        params = {
            "description": description,
            "access_token": self.access_token
        }
        
        try:
            if is_local:
                with open(video_source, 'rb') as f:
                    files = {'source': f}
                    response = requests.post(f"{_facebook_graph_root()}/{endpoint}", params=params, files=files, timeout=300) # Increased for direct upload
            else:
                params["file_url"] = video_source
                response = requests.post(f"{_facebook_graph_root()}/{endpoint}", params=params, timeout=120)
                
            if response.status_code != 200:
                print(f"Facebook API Error Body: {response.text}")
            response.raise_for_status()
            return response.json().get("id")
        except requests.exceptions.HTTPError as e:
            error_detail = response.text
            try:
                error_json = response.json()
                error_detail = error_json.get("error", {}).get("message", response.text)
            except:
                pass
            print(f"Failed to publish Facebook video: {error_detail}")
            raise Exception(f"Facebook API Error: {error_detail}")
        except Exception as e:
            print(f"Failed to publish Facebook video: {e}")
            raise

    def sync_data(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Sync all Facebook data.
        
        Args:
            since: Only sync data since this datetime
        
        Returns:
            Dictionary with all synced data
        """
        result = {
            "channel": "facebook",
            "page_insights": {},
            "page_posts": {},
            "ad_performance": {},
            "success": True,
            "errors": [],
            "synced_at": datetime.utcnow().isoformat()
        }
        
        # Sync page insights
        try:
            insights = self.sync_page_insights()
            if "error" in insights:
                result["success"] = False
                result["errors"].append(insights["error"])
            else:
                result["page_insights"] = insights
        except Exception as e:
            result["success"] = False
            result["errors"].append(str(e))
        
        # Sync page posts
        try:
            posts = self.sync_page_posts()
            if "error" in posts:
                result["success"] = False
                result["errors"].append(posts["error"])
            else:
                result["page_posts"] = posts
        except Exception as e:
            result["success"] = False
            result["errors"].append(str(e))
        
        # Sync ad performance (if ad account ID is available)
        ad_account_id = self.credentials.get("ad_account_id")
        if ad_account_id:
            try:
                ads = self.sync_ad_performance(ad_account_id)
                if "error" not in ads:
                    result["ad_performance"] = ads
            except Exception as e:
                result["errors"].append(f"Ad sync error: {str(e)}")
        
        return result

