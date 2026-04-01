"""Analytics service for calculating trends and aggregating metrics."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from core.database import AnalyticsSnapshot, Campaign, ChannelType

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for managing and calculating marketing analytics."""
    
    def __init__(self, db: Session):
        self.db = db
        
    def get_latest_snapshot(self, campaign_id: int) -> Optional[AnalyticsSnapshot]:
        """Get the most recent snapshot for a campaign."""
        return self.db.query(AnalyticsSnapshot).filter(
            AnalyticsSnapshot.campaign_id == campaign_id
        ).order_by(desc(AnalyticsSnapshot.timestamp)).first()
        
    def get_snapshot_at(self, campaign_id: int, target_time: datetime) -> Optional[AnalyticsSnapshot]:
        """Get the snapshot closest to a specific time (but not after it)."""
        return self.db.query(AnalyticsSnapshot).filter(
            AnalyticsSnapshot.campaign_id == campaign_id,
            AnalyticsSnapshot.timestamp <= target_time
        ).order_by(desc(AnalyticsSnapshot.timestamp)).first()
        
    def get_trend(self, campaign_id: int, metric_key: str, days: int = 1) -> Dict[str, Any]:
        """
        Calculate trend percentage for a specific metric.
        
        Returns:
            {
                "current": value,
                "previous": value,
                "percentage_change": float,
                "trend": "up" | "down" | "neutral"
            }
        """
        latest = self.get_latest_snapshot(campaign_id)
        if not latest:
            return {"current": 0, "previous": 0, "percentage_change": 0, "trend": "neutral"}
            
        target_time = latest.timestamp - timedelta(days=days)
        previous = self.get_snapshot_at(campaign_id, target_time)
        
        current_val = latest.metrics.get(metric_key, 0)
        previous_val = previous.metrics.get(metric_key, 0) if previous else 0
        
        if previous_val == 0:
            change = 100.0 if current_val > 0 else 0.0
        else:
            change = ((current_val - previous_val) / previous_val) * 100.0
            
        return {
            "current": current_val,
            "previous": previous_val,
            "percentage_change": round(change, 2),
            "trend": "up" if change > 0 else ("down" if change < 0 else "neutral")
        }
        
    def get_sparkline_data(self, campaign_id: int, metric_key: str, points: int = 7) -> List[int]:
        """Get a list of values for a sparkline graph."""
        snapshots = self.db.query(AnalyticsSnapshot).filter(
            AnalyticsSnapshot.campaign_id == campaign_id
        ).order_by(desc(AnalyticsSnapshot.timestamp)).limit(points).all()
        
        # Reverse to get chronological order
        values = [s.metrics.get(metric_key, 0) for s in reversed(snapshots)]
        
        # Pad with zeros if not enough data
        if len(values) < points:
            values = [0] * (points - len(values)) + values
            
        return values

    def get_global_stats(self, time_range: str = "7d") -> Dict[str, Any]:
        """Aggregate stats across all social channels."""
        channels = [ChannelType.YOUTUBE, ChannelType.INSTAGRAM, ChannelType.FACEBOOK]
        
        total_subscribers = 0
        total_views = 0
        total_videos = 0
        
        global_trends = {
            "subscribers": {"current": 0, "previous": 0, "percentage_change": 0, "trend": "neutral"},
            "views": {"current": 0, "previous": 0, "percentage_change": 0, "trend": "neutral"}
        }
        
        global_sparklines = {
            "subscribers": [],
            "views": []
        }
        
        for channel in channels:
            stats = self.get_channel_stats_with_trends(channel, time_range)
            
            total_subscribers += stats.get("subscriber_count", 0)
            total_views += stats.get("view_count", 0)
            total_videos += stats.get("video_count", 0)
            
            # Aggregate trends (sum current and previous)
            ch_trends = stats.get("trends", {})
            for key in ["subscribers", "views"]:
                if key in ch_trends:
                    global_trends[key]["current"] += ch_trends[key]["current"]
                    global_trends[key]["previous"] += ch_trends[key]["previous"]
            
            # Aggregate sparklines (sum point-by-point)
            ch_spark = stats.get("sparklines", {})
            for key in ["subscribers", "views"]:
                if key in ch_spark and ch_spark[key]:
                    if not global_sparklines[key]:
                        global_sparklines[key] = [0] * len(ch_spark[key])
                    for i, val in enumerate(ch_spark[key]):
                        if i < len(global_sparklines[key]):
                            global_sparklines[key][i] += val

        # Recalculate global percentage changes
        for key in ["subscribers", "views"]:
            curr = global_trends[key]["current"]
            prev = global_trends[key]["previous"]
            if prev > 0:
                change = round(((curr - prev) / prev) * 100, 2)
                global_trends[key]["percentage_change"] = change
                global_trends[key]["trend"] = "up" if change > 0 else ("down" if change < 0 else "neutral")

        return {
            "subscriber_count": total_subscribers,
            "view_count": total_views,
            "video_count": total_videos,
            "trends": global_trends,
            "sparklines": global_sparklines
        }

    def get_channel_stats_with_trends(self, channel: ChannelType, time_range: str = "7d") -> Dict[str, Any]:
        """Get overall stats for a channel with trends and sparklines."""
        # Map time_range string to days
        days_map = {"1d": 1, "7d": 7, "30d": 30, "all": 90}
        days = days_map.get(time_range, 7)
        
        # Fix: Ensure naming matches DataIntegrationAgent
        channel_name = "YouTube" if channel == ChannelType.YOUTUBE else channel.value.capitalize()
        system_campaign_name = f"Global {channel_name} Stats"
        campaign = self.db.query(Campaign).filter(
            Campaign.name == system_campaign_name,
            Campaign.channel == channel
        ).first()
        
        if not campaign:
            return {
                "subscriber_count": 0,
                "view_count": 0,
                "trends": {},
                "sparklines": {}
            }
            
        latest = self.get_latest_snapshot(campaign.campaign_id)
        if not latest:
            return {
                "subscriber_count": 0,
                "view_count": 0,
                "video_count": 0,
                "trends": {},
                "sparklines": {}
            }
            
        # Standard metrics for YouTube
        sub_trend = self.get_trend(campaign.campaign_id, "subscriber_count", days=days)
        view_trend = self.get_trend(campaign.campaign_id, "view_count", days=days)
        
        return {
            "subscriber_count": latest.metrics.get("subscriber_count", 0),
            "view_count": latest.metrics.get("view_count", 0),
            "video_count": latest.metrics.get("video_count", 0),
            "channel_name": latest.metrics.get("channel_name", "Unknown"),
            "trends": {
                "subscribers": sub_trend,
                "views": view_trend
            },
            "sparklines": {
                "subscribers": self.get_sparkline_data(campaign.campaign_id, "subscriber_count", points=days),
                "views": self.get_sparkline_data(campaign.campaign_id, "view_count", points=days)
            }
        }
