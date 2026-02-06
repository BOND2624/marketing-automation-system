from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import json

from core.database import get_db
from core.config import get_settings
from api_integrations.youtube import YouTubeIntegration

router = APIRouter()
settings = get_settings()

def get_youtube_integration():
    """Dependency for YouTube integration."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    token_file = os.path.join(project_root, "youtube_token.json")
    
    creds = {"api_key": settings.youtube_api_key}
    if os.path.exists(token_file):
        creds["oauth2_credentials"] = token_file
        
    return YouTubeIntegration(creds)

import logging

logger = logging.getLogger(__name__)

@router.get("/status")
async def get_youtube_status():
    """Check YouTube OAuth token validity."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    token_file = os.path.join(project_root, "youtube_token.json")
    
    exists = os.path.exists(token_file)
    valid = False
    
    if exists:
        try:
            integration = get_youtube_integration()
            valid = integration.test_connection()
            if not valid:
                logger.warning("YouTube integration test returned False")
        except Exception as e:
            logger.error(f"YouTube status check error: {e}")
            valid = False
            
    return {
        "token_exists": exists,
        "is_valid": valid,
        "status": "active" if valid else "error"
    }

@router.get("/stats")
async def get_youtube_stats():
    """Fetch high-level channel stats."""
    # Assuming channel_id is in settings or some global config
    channel_id = os.getenv("YOUTUBE_CHANNEL_ID")
    if not channel_id:
        # Fallback to a default for testing or return error
        return {"error": "Channel ID not configured"}
        
    integration = get_youtube_integration()
    stats = integration.sync_channel_stats(channel_id)
    return stats

@router.get("/analytics")
async def get_youtube_analytics():
    """Fetch video analytics for the chart."""
    channel_id = os.getenv("YOUTUBE_CHANNEL_ID")
    if not channel_id:
        return {"error": "Channel ID not configured"}
        
    integration = get_youtube_integration()
    analytics = integration.sync_video_analytics(channel_id)
    return analytics
