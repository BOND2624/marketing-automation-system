"""Instagram Graph API integration."""

import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional

import requests

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
        """Make a GET request to Instagram Graph API."""
        if not params:
            params = {}
        params["access_token"] = self.access_token
        
        try:
            self._handle_rate_limit()
            response = requests.get(f"{self.BASE_URL}/{endpoint}", params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Instagram API GET request failed: {e}")
            raise

    def _post_request(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request to Instagram Graph API."""
        if not data:
            data = {}
        data["access_token"] = self.access_token

        try:
            self._handle_rate_limit()
            response = requests.post(f"{self.BASE_URL}/{endpoint}", data=data, timeout=30)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as http_err:
                # Log full Graph API error payload to help debugging
                try:
                    error_payload: Any = response.json()
                except ValueError:
                    error_payload = response.text
                logger.error(
                    "Instagram API POST request failed: %s | endpoint=%s | payload=%s",
                    http_err,
                    endpoint,
                    error_payload,
                )
                raise
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Instagram API POST request failed: {e}")
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

    # ------------------------------------------------------------------
    # Publishing (single image / video / reel)
    # ------------------------------------------------------------------

    def publish_media(
        self,
        caption: str,
        media_url: str,
        media_type: str = "IMAGE",
        is_carousel_item: bool = False,
    ) -> Dict[str, Any]:
        """
        Publish a single media item to the Instagram Business account.
        
        Args:
            caption: Text caption for the post.
            media_url: Publicly accessible URL to image or video.
            media_type: One of 'IMAGE', 'VIDEO', 'REELS', 'STORIES'. Defaults to 'IMAGE'.
            is_carousel_item: Whether this media is part of a carousel (not used yet).
        
        Returns:
            Dict with success flag, media_id, container_id, and any error information.
        """
        if not self.instagram_account_id:
            return {
                "success": False,
                "error": "Instagram Business Account ID is required for publishing.",
            }

        if not media_url:
            return {
                "success": False,
                "error": "media_url is required for publishing to Instagram.",
            }

        # Step 1: Create media container
        container_data: Dict[str, Any] = {
            "caption": caption or "",
        }

        media_type_upper = (media_type or "IMAGE").upper()
        if media_type_upper == "IMAGE":
            container_data["image_url"] = media_url
        else:
            # For VIDEO / REELS / STORIES we use video_url; for large files a resumable
            # upload is recommended, but here we rely on Meta fetching the URL directly.
            container_data["video_url"] = media_url
            container_data["media_type"] = media_type_upper

        try:
            container_resp = self._post_request(
                f"{self.instagram_account_id}/media",
                data=container_data,
            )
        except requests.exceptions.HTTPError as e:
            msg = str(e)
            if getattr(e, "response", None) is not None:
                try:
                    body = e.response.json()
                    err = body.get("error")
                    if isinstance(err, dict) and err.get("message"):
                        msg = err["message"]
                except Exception:
                    pass
            return {
                "success": False,
                "error": msg,
                "details": self._handle_error(e, "publish_media_create_container"),
            }
        except Exception as e:
            return self._handle_error(e, "publish_media_create_container")

        container_id = container_resp.get("id")
        if not container_id:
            return {
                "success": False,
                "error": "Failed to create Instagram media container.",
                "details": container_resp,
            }

        # Step 2: Poll container status until it's ready
        status = "IN_PROGRESS"
        max_attempts = 10
        attempt = 0

        while status in {"IN_PROGRESS", "PENDING"} and attempt < max_attempts:
            attempt += 1
            try:
                status_resp = self._make_request(
                    container_id,
                    params={"fields": "status_code"},
                )
                status = status_resp.get("status_code", "UNKNOWN")
            except Exception as e:
                logger.warning(f"Failed to check Instagram container status: {e}")
                status = "ERROR"
                break

            if status in {"IN_PROGRESS", "PENDING"}:
                time.sleep(2)

        if status != "FINISHED":
            return {
                "success": False,
                "error": f"Instagram media container not ready. Status: {status}",
                "container_id": container_id,
            }

        # Step 3: Publish the container
        try:
            publish_resp = self._post_request(
                f"{self.instagram_account_id}/media_publish",
                data={"creation_id": container_id},
            )
        except Exception as e:
            return self._handle_error(e, "publish_media_publish")

        media_id = publish_resp.get("id")
        if not media_id:
            return {
                "success": False,
                "error": "Failed to publish Instagram media.",
                "container_id": container_id,
                "details": publish_resp,
            }

        return {
            "success": True,
            "media_id": media_id,
            "container_id": container_id,
            "status": status,
        }

