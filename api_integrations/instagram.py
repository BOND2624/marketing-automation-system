"""Instagram Graph API integration."""

import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime

from api_integrations.base import BaseIntegration

logger = logging.getLogger(__name__)


class InstagramIntegration(BaseIntegration):
    """Integration with Instagram Graph API."""
    
    BASE_URL = "https://graph.facebook.com/v18.0"
    
    def __init__(self, credentials: Dict[str, Any]):
        """
        Initialize Instagram integration.
        
        Args:
            credentials: Should contain 'access_token' and optionally 'instagram_business_account_id'
        """
        super().__init__(credentials, rate_limit_calls=200, rate_limit_period=3600)  # 200/hour default
        self.access_token = credentials.get("access_token")
        self.instagram_account_id = credentials.get("instagram_business_account_id")
        
        if not self.access_token:
            raise ValueError("Instagram access token is required")
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to Instagram Graph API."""
        if not params:
            params = {}
        params["access_token"] = self.access_token
        
        try:
            self._handle_rate_limit()
            response = requests.get(f"{self.BASE_URL}/{endpoint}", params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Instagram API request failed: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test Instagram API connection."""
        try:
            if self.instagram_account_id:
                self._make_request(self.instagram_account_id)
            else:
                # Test with basic API call
                self._make_request("me")
            return True
        except Exception as e:
            logger.error(f"Instagram connection test failed: {e}")
            return False
    
    def sync_account_info(self) -> Dict[str, Any]:
        """Sync Instagram account information."""
        if not self.instagram_account_id:
            return {"error": "Instagram Business Account ID is required"}
        
        try:
            response = self._make_request(
                self.instagram_account_id,
                params={"fields": "id,username,profile_picture_url,followers_count,media_count"}
            )
            
            return {
                "account_id": response.get("id"),
                "username": response.get("username"),
                "profile_picture_url": response.get("profile_picture_url"),
                "followers_count": response.get("followers_count", 0),
                "media_count": response.get("media_count", 0),
                "synced_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return self._handle_error(e, "sync_account_info")
    
    def sync_posts(self, since: Optional[datetime] = None, limit: int = 25) -> Dict[str, Any]:
        """
        Sync Instagram posts.
        
        Args:
            since: Only sync posts since this datetime
            limit: Maximum number of posts to fetch
        """
        if not self.instagram_account_id:
            return {"error": "Instagram Business Account ID is required"}
        
        try:
            params = {
                "fields": "id,media_type,media_url,permalink,timestamp,caption,like_count,comments_count,insights",
                "limit": min(limit, 25)
            }
            
            if since:
                params["since"] = since.timestamp()
            
            # For insights, need to make separate requests
            response = self._make_request(
                f"{self.instagram_account_id}/media",
                params=params
            )
            
            posts = []
            for item in response.get("data", []):
                post_data = {
                    "post_id": item.get("id"),
                    "media_type": item.get("media_type"),
                    "media_url": item.get("media_url"),
                    "permalink": item.get("permalink"),
                    "timestamp": item.get("timestamp"),
                    "caption": item.get("caption", ""),
                    "likes": item.get("like_count", 0),
                    "comments": item.get("comments_count", 0),
                }
                
                # Try to get insights (impressions, reach, etc.)
                try:
                    insights_response = self._make_request(
                        f"{item.get('id')}/insights",
                        params={"metric": "impressions,reach,engagement"}
                    )
                    insights = {insight["name"]: insight["values"][0]["value"] 
                              for insight in insights_response.get("data", [])}
                    post_data["insights"] = insights
                except Exception as e:
                    logger.warning(f"Failed to fetch insights for post {item.get('id')}: {e}")
                
                posts.append(post_data)
            
            return {
                "posts": posts,
                "total_posts": len(posts),
                "synced_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return self._handle_error(e, "sync_posts")
    
    def sync_stories(self, limit: int = 25) -> Dict[str, Any]:
        """
        Sync Instagram stories.
        
        Args:
            limit: Maximum number of stories to fetch
        """
        if not self.instagram_account_id:
            return {"error": "Instagram Business Account ID is required"}
        
        try:
            params = {
                "fields": "id,media_type,media_url,timestamp",
                "limit": min(limit, 25)
            }
            
            response = self._make_request(
                f"{self.instagram_account_id}/stories",
                params=params
            )
            
            stories = [
                {
                    "story_id": item.get("id"),
                    "media_type": item.get("media_type"),
                    "media_url": item.get("media_url"),
                    "timestamp": item.get("timestamp")
                }
                for item in response.get("data", [])
            ]
            
            return {
                "stories": stories,
                "total_stories": len(stories),
                "synced_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return self._handle_error(e, "sync_stories")
    
    def sync_data(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Sync all Instagram data.
        
        Args:
            since: Only sync data since this datetime
        
        Returns:
            Dictionary with all synced data
        """
        result = {
            "channel": "instagram",
            "account_info": {},
            "posts": {},
            "stories": {},
            "success": True,
            "errors": [],
            "synced_at": datetime.utcnow().isoformat()
        }
        
        # Sync account info
        try:
            account_info = self.sync_account_info()
            if "error" in account_info:
                result["success"] = False
                result["errors"].append(account_info["error"])
            else:
                result["account_info"] = account_info
        except Exception as e:
            result["success"] = False
            result["errors"].append(str(e))
        
        # Sync posts
        try:
            posts = self.sync_posts(since)
            if "error" in posts:
                result["success"] = False
                result["errors"].append(posts["error"])
            else:
                result["posts"] = posts
        except Exception as e:
            result["success"] = False
            result["errors"].append(str(e))
        
        # Sync stories
        try:
            stories = self.sync_stories()
            if "error" in stories:
                result["success"] = False
                result["errors"].append(stories["error"])
            else:
                result["stories"] = stories
        except Exception as e:
            result["success"] = False
            result["errors"].append(str(e))
        
        return result

