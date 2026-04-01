from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import os
import json

from core.database import get_db, ChannelType
from core.config import get_settings
from api_integrations.youtube import YouTubeIntegration
from services.analytics_service import AnalyticsService

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

def get_channel_id_from_oauth(integration):
    """Get authenticated user's channel ID using OAuth."""
    try:
        if not integration.youtube_oauth:
            logger.warning("OAuth client not initialized")
            return None
            
        request = integration.youtube_oauth.channels().list(
            part="id",
            mine=True
        )
        response = request.execute()
        
        if response.get("items"):
            channel_id = response["items"][0]["id"]
            logger.info(f"Detected channel ID from OAuth: {channel_id}")
            return channel_id
    except Exception as e:
        logger.error(f"Failed to get channel ID from OAuth: {e}")
    return None

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
async def get_youtube_stats(db: Session = Depends(get_db)):
    """Fetch high-level channel stats with trends."""
    integration = get_youtube_integration()
    analytics_service = AnalyticsService(db)
    
    # 1. Fetch latest raw stats from API (if possible)
    channel_id = os.getenv("YOUTUBE_CHANNEL_ID")
    if not channel_id:
        channel_id = get_channel_id_from_oauth(integration)
        
    current_stats = {}
    if channel_id:
        try:
            current_stats = integration.sync_channel_stats(channel_id)
        except Exception as e:
            logger.error(f"Error syncing latest stats: {e}")
    
    # 2. Get trends and sparklines from historical snapshots in DB
    # This works regardless of whether the real-time API call for current_stats succeeded
    enriched_stats = analytics_service.get_channel_stats_with_trends(ChannelType.YOUTUBE)
    
    # 3. Merge API results with historical analysis
    # Prefer API current_stats (real-time) if available, otherwise fallback to latest snapshot
    return {
        "subscriber_count": current_stats.get("subscriber_count") or enriched_stats.get("subscriber_count", 0),
        "view_count": current_stats.get("view_count") or enriched_stats.get("view_count", 0),
        "video_count": current_stats.get("video_count") or enriched_stats.get("video_count", 0),
        "channel_name": current_stats.get("channel_name") or enriched_stats.get("channel_name", "Unknown"),
        "channel_id": channel_id or enriched_stats.get("channel_id"),
        "trends": enriched_stats.get("trends", {}),
        "sparklines": enriched_stats.get("sparklines", {}),
        "api_sync_success": bool(current_stats)
    }

    return analytics

@router.get("/analytics")
async def get_youtube_analytics():
    """Fetch video analytics for the chart."""
    integration = get_youtube_integration()
    
    # Try env variable first, then OAuth auto-detect
    channel_id = os.getenv("YOUTUBE_CHANNEL_ID")
    
    if not channel_id:
        logger.info("YOUTUBE_CHANNEL_ID not set, attempting OAuth detection...")
        channel_id = get_channel_id_from_oauth(integration)
        
    if not channel_id:
        logger.error("Could not determine channel ID from env or OAuth")
        return {
            "error": "Channel ID not found. Set YOUTUBE_CHANNEL_ID env variable.",
            "videos": [],
            "total_videos": 0
        }
    
    logger.info(f"Fetching analytics for channel: {channel_id}")
    analytics = integration.sync_video_analytics(channel_id, max_videos=50)
    
    # Ensure we always return valid structure   
    if "error" in analytics:
        return {
            "error": analytics["error"],
            "videos": [],
            "total_videos": 0
        }
    return analytics

@router.get("/videos")
async def get_youtube_videos_alias():
    """Alias for /analytics to support frontend polling."""
    return await get_youtube_analytics()

@router.get("/export")
async def export_youtube_stats(db: Session = Depends(get_db)):
    """Export YouTube analytics as CSV."""
    from fastapi.responses import StreamingResponse
    import io
    import csv
    
    analytics_service = AnalyticsService(db)
    # Get last 30 snapshots for the report
    system_campaign_name = f"Global {ChannelType.YOUTUBE.value.capitalize()} Stats"
    campaign = db.query(Campaign).filter(
        Campaign.name == system_campaign_name,
        Campaign.channel == ChannelType.YOUTUBE
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="No analytics data found to export")
        
    snapshots = db.query(AnalyticsSnapshot).filter(
        AnalyticsSnapshot.campaign_id == campaign.campaign_id
    ).order_by(desc(AnalyticsSnapshot.timestamp)).limit(100).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp", "Subscribers", "Views", "Videos"])
    
    for s in snapshots:
        writer.writerow([
            s.timestamp.isoformat(),
            s.metrics.get("subscriber_count", 0),
            s.metrics.get("view_count", 0),
            s.metrics.get("video_count", 0)
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=youtube_analytics.csv"}
    )

@router.post("/seo-check")
async def seo_check(data: Dict[str, str]):
    """Analyze metadata for SEO and return a score."""
    title = data.get("title", "")
    description = data.get("description", "")
    
    score = 0
    suggestions = []
    
    # Title analysis (Max 100)
    if 50 <= len(title) <= 70:
        score += 40
    elif len(title) > 0:
        score += 20
        suggestions.append("Title length should ideally be between 50-70 characters.")
    else:
        suggestions.append("Title is required.")
        
    # Keyword density in description
    keywords = title.lower().split()
    found_keywords = [kw for kw in keywords if kw in description.lower() and len(kw) > 3]
    
    if len(found_keywords) >= 3:
        score += 40
    elif len(found_keywords) > 0:
        score += 20
        suggestions.append("Include more primary keywords from your title in the description.")
    else:
        suggestions.append("Mention your main keywords in the first 200 characters of the description.")
        
    # Formatting
    if "\n" in description:
        score += 20
    else:
        suggestions.append("Use line breaks to make your description more readable.")
        
    return {
        "score": score,
        "suggestions": suggestions,
        "keyword_coverage": len(found_keywords)
    }