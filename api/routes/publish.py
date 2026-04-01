import logging
import os

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Any, Dict, List

from core.database import get_db, ChannelType
from core.config import get_settings
from agents.campaign_manager import CampaignManagerAgent
from services.ngrok_service import ngrok_service
import json

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


class PersonalizePublishBody(BaseModel):
    """Seed text from the publish form for AI suggestions."""

    user_input: str = Field(..., min_length=1, max_length=8000)
    platform: str
    tone: str = "casual"


class PersonalizePublishResponse(BaseModel):
    success: bool
    title: str
    description: str
    body: str
    tags: List[str]
    hashtags: List[str]

def get_youtube_credentials():
    """Load YouTube API key / OAuth paths for uploads."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    token_file = os.path.join(project_root, "youtube_token.json")
    creds = {
        "api_key": settings.youtube_api_key,
        "channel_id": settings.youtube_channel_id,
    }
    if os.path.exists(token_file):
        creds["oauth2_credentials"] = token_file
    return creds


def get_meta_credentials():
    """Load Meta credentials from file or fallback to environment."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    token_file = os.path.join(project_root, "meta_token.json")
    
    creds = {
        "access_token": settings.facebook_access_token,
        "page_id": settings.facebook_page_id,
        "instagram_business_account_id": settings.instagram_business_account_id
    }
    
    if os.path.exists(token_file):
        try:
            with open(token_file, 'r') as f:
                file_creds = json.load(f)
                if file_creds.get("facebook_access_token"):
                    creds["access_token"] = file_creds["facebook_access_token"]
                if file_creds.get("facebook_page_id"):
                    creds["page_id"] = file_creds["facebook_page_id"]
                if file_creds.get("instagram_business_account_id"):
                    creds["instagram_business_account_id"] = file_creds["instagram_business_account_id"]
        except Exception as e:
            print(f"Error loading meta_token.json: {e}")
            
    masked_token = f"{creds['access_token'][:10]}...{creds['access_token'][-10:]}" if creds.get('access_token') else "None"
    print(f"DEBUG: get_meta_credentials returning token starting with: {masked_token}")
    return creds


@router.post("/personalize", response_model=PersonalizePublishResponse)
async def personalize_publish(body: PersonalizePublishBody) -> PersonalizePublishResponse:
    """
    Generate title, description/body, tags, and hashtags from user-provided text (Ollama).
    The client should show this for review; the user applies or keeps their own copy.
    """
    plat = body.platform.strip().lower()
    if plat not in ("youtube", "instagram", "facebook"):
        raise HTTPException(
            status_code=400,
            detail="Invalid platform. Use 'youtube', 'instagram', or 'facebook'.",
        )
    tone = (body.tone or "casual").strip().lower()
    if tone not in ("casual", "professional", "fun"):
        tone = "casual"

    try:
        from services.personalization_service import PersonalizationService

        svc = PersonalizationService()
        data = svc.suggest_for_publish(body.user_input.strip(), plat, tone=tone)
        return PersonalizePublishResponse(success=True, **data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("personalize_publish failed")
        raise HTTPException(
            status_code=503,
            detail="AI personalization unavailable. Ensure Ollama is running and llm_provider is configured.",
        ) from e


@router.post("/social")
async def publish_social(payload: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Publish content to Facebook, Instagram, or YouTube.
    Payload: {
        "platform": "facebook" | "instagram" | "youtube",
        "content": str,
        "media_url": str (optional),
        "media_type": "IMAGE" | "VIDEO" | "REELS" (optional, Meta),
        "title": str (optional, YouTube),
        "youtube_format": "short" | "video" (optional, YouTube — default "video")
    }
    """
    platform = payload.get("platform")
    content = payload.get("content") or ""
    media_url = payload.get("media_url")
    media_type = payload.get("media_type", "IMAGE")
    youtube_format = (payload.get("youtube_format") or "video").strip().lower()
    if youtube_format not in ("short", "video"):
        youtube_format = "video"

    if platform not in ["facebook", "instagram", "youtube"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid platform. Use 'facebook', 'instagram', or 'youtube'.",
        )

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    upload_dir = os.environ.get("UPLOAD_DIR") or os.path.join(project_root, "uploads")

    # --- YouTube: local video file only, uses CampaignManager + YouTubeExecutionHandler ---
    if platform == "youtube":
        if not media_url or str(media_url).startswith(("http://", "https://")):
            raise HTTPException(
                status_code=400,
                detail="YouTube publish requires a video file uploaded through the app (remote URL is not supported).",
            )
        filename = os.path.basename(str(media_url))
        local_video_path = os.path.join(upload_dir, filename)
        if not os.path.isfile(local_video_path):
            raise HTTPException(
                status_code=400,
                detail=f"Uploaded video not found on server: {filename}",
            )

        yt_creds = get_youtube_credentials()
        if not yt_creds.get("api_key"):
            raise HTTPException(
                status_code=400,
                detail="YouTube API key missing. Set YOUTUBE_API_KEY in your environment.",
            )

        title = (payload.get("title") or "").strip()
        if not title:
            first_line = content.strip().split("\n", 1)[0].strip()
            title = first_line[:100] if first_line else "Untitled upload"
        description = content.strip()

        agent = CampaignManagerAgent(db)
        channel = ChannelType.YOUTUBE
        config = {
            "video_path": local_video_path,
            "title": title,
            "description": description,
            "tags": payload.get("tags") or [],
            "privacy_status": payload.get("privacy_status") or "public",
            "upload_type": "short" if youtube_format == "short" else "video",
        }

        create_result = agent.create_campaign(
            name=f"Social Publish - YouTube ({youtube_format})",
            channel=channel,
            config=config,
        )
        if not create_result.get("success"):
            raise HTTPException(status_code=500, detail=create_result.get("error"))

        campaign_id = create_result["campaign_id"]
        credentials = {
            ChannelType.YOUTUBE: {
                "api_key": yt_creds["api_key"],
                "channel_id": yt_creds.get("channel_id"),
                **(
                    {"oauth2_credentials": yt_creds["oauth2_credentials"]}
                    if yt_creds.get("oauth2_credentials")
                    else {}
                ),
            }
        }
        exec_result = agent.execute_campaign(campaign_id, credentials)
        results = exec_result.get("results") or {}
        video_id = results.get("video_id")
        post_id = results.get("post_id") or video_id

        if exec_result.get("success"):
            return {
                "success": True,
                "campaign_id": campaign_id,
                "post_id": post_id,
                "video_id": video_id,
                "public_media_url": None,
            }
        error_msg = exec_result.get("error")
        if results.get("error"):
            error_msg = results["error"]
        return {
            "success": False,
            "error": error_msg or "YouTube upload failed. Check OAuth token and video requirements.",
            "campaign_id": campaign_id,
        }

    # Process media URL if it refers to a local file (Meta)
    processed_media_url = media_url
    if media_url and not media_url.startswith(("http://", "https://")):
        # Assume it's a filename in the uploads directory
        public_base = ngrok_service.public_url
        if not public_base:
            # Fallback for local testing - though external APIs won't reach this
            host = settings.api_host if settings.api_host != "0.0.0.0" else "localhost"
            public_base = f"http://{host}:{settings.api_port}"

        processed_media_url = f"{public_base}/uploads/{media_url}"
        print(f"DEBUG: Generated processed_media_url: {processed_media_url}")

    # Initialize Agent
    agent = CampaignManagerAgent(db)

    # Map platform to ChannelType
    channel = ChannelType.FACEBOOK if platform == "facebook" else ChannelType.INSTAGRAM

    # Build campaign config
    config = {
        "media_url": processed_media_url,
        "media_type": media_type,
    }
    if platform == "facebook":
        config["message"] = content
    else:
        config["content"] = content

    # Create Campaign
    create_result = agent.create_campaign(
        name=f"Social Publish - {platform.capitalize()}",
        channel=channel,
        config=config,
    )

    if not create_result.get("success"):
        raise HTTPException(status_code=500, detail=create_result.get("error"))

    campaign_id = create_result["campaign_id"]

    # Prepare Credentials (from file or fallback to settings)
    meta_creds = get_meta_credentials()

    credentials = {}
    if platform == "facebook":
        credentials[ChannelType.FACEBOOK] = {
            "access_token": meta_creds["access_token"],
            "page_id": meta_creds["page_id"],
        }
    else:
        credentials[ChannelType.INSTAGRAM] = {
            "access_token": meta_creds["access_token"],
            "instagram_business_account_id": meta_creds["instagram_business_account_id"],
        }

    # Execute Campaign
    exec_result = agent.execute_campaign(campaign_id, credentials)

    if exec_result.get("success"):
        return {
            "success": True,
            "campaign_id": campaign_id,
            "post_id": exec_result.get("results", {}).get("post_id"),
            "public_media_url": processed_media_url,
        }
    else:
        error_msg = exec_result.get("error")
        # Extract deeper error message if available from results
        if exec_result.get("results", {}).get("error"):
            error_msg = exec_result["results"]["error"]
            
        return {
            "success": False,
            "error": error_msg or "Failed to publish. Please check your integration settings.",
            "campaign_id": campaign_id
        }
