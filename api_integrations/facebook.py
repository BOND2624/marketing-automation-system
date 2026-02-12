"""Facebook Graph API integration."""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

import requests

from api_integrations.base import BaseIntegration

logger = logging.getLogger(__name__)


class FacebookIntegration(BaseIntegration):
    """Integration with Facebook Graph API."""
    
    BASE_URL = "https://graph.facebook.com/v18.0"
    
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
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request to Facebook Graph API."""
        if not params:
            params = {}
        params["access_token"] = self.access_token
        
        try:
            self._handle_rate_limit()
            response = requests.get(f"{self.BASE_URL}/{endpoint}", params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Facebook API GET request failed: {e}")
            raise

    def _post_request(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request to Facebook Graph API."""
        if not data:
            data = {}
        data["access_token"] = self.access_token

        try:
            self._handle_rate_limit()
            response = requests.post(f"{self.BASE_URL}/{endpoint}", data=data, timeout=30)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as http_err:
                # Try to log the full Graph API error payload for easier debugging
                error_payload: Any
                try:
                    error_payload = response.json()
                except ValueError:
                    error_payload = response.text
                logger.error(
                    "Facebook API POST request failed: %s | endpoint=%s | payload=%s",
                    http_err,
                    endpoint,
                    error_payload,
                )
                # Re-raise so higher-level handlers can convert to a structured error
                raise
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Facebook API POST request failed: {e}")
            raise

    def _graph_error_message(self, response: requests.Response) -> str:
        """Extract human-readable error message from Graph API error response."""
        try:
            body = response.json()
            err = body.get("error") if isinstance(body, dict) else None
            if isinstance(err, dict) and err.get("message"):
                return err["message"].strip()
        except (ValueError, AttributeError):
            pass
        return response.text or response.reason or "Unknown error"

    def test_connection(self) -> bool:
        """Test Facebook API connection."""
        try:
            self._make_request("me")
            return True
        except Exception as e:
            logger.error(f"Facebook connection test failed: {e}")
            return False
    
    def sync_page_insights(self, page_id: Optional[str] = None, metrics: Optional[list] = None) -> Dict[str, Any]:
        """
        Sync Facebook page insights.
        
        Args:
            page_id: Facebook page ID (uses self.page_id if not provided)
            metrics: List of metrics to fetch (default: page_fans, page_impressions, page_engaged_users)
        """
        target_page_id = page_id or self.page_id
        if not target_page_id:
            return {"error": "Facebook Page ID is required"}
        
        if not metrics:
            metrics = ["page_fans", "page_impressions", "page_engaged_users"]
        
        try:
            # Get insights for last 30 days
            params = {
                "metric": ",".join(metrics),
                "period": "day",
                "since": int((datetime.utcnow().timestamp() - 30 * 86400)),
                "until": int(datetime.utcnow().timestamp())
            }
            
            response = self._make_request(
                f"{target_page_id}/insights",
                params=params
            )
            
            insights_data = {}
            for insight in response.get("data", []):
                metric_name = insight.get("name")
                values = insight.get("values", [])
                if values:
                    # Get the most recent value
                    insights_data[metric_name] = {
                        "current": values[-1].get("value", 0),
                        "values": [v.get("value", 0) for v in values],
                        "end_time": values[-1].get("end_time")
                    }
            
            return {
                "insights": insights_data,
                "synced_at": datetime.utcnow().isoformat()
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
            params = {
                "fields": "id,message,created_time,likes.summary(true),comments.summary(true),shares",
                "limit": min(limit, 25)
            }
            
            response = self._make_request(
                f"{target_page_id}/posts",
                params=params
            )
            
            posts = []
            for item in response.get("data", []):
                likes_data = item.get("likes", {}).get("summary", {})
                comments_data = item.get("comments", {}).get("summary", {})
                shares_data = item.get("shares", {})
                
                posts.append({
                    "post_id": item.get("id"),
                    "message": item.get("message", ""),
                    "created_time": item.get("created_time"),
                    "likes": likes_data.get("total_count", 0),
                    "comments": comments_data.get("total_count", 0),
                    "shares": shares_data.get("count", 0)
                })
            
            return {
                "posts": posts,
                "total_posts": len(posts),
                "synced_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return self._handle_error(e, "sync_page_posts")
    
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

    # ------------------------------------------------------------------
    # Publishing helpers
    # ------------------------------------------------------------------

    def publish_feed_post(
        self,
        message: str,
        link: Optional[str] = None,
        page_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Publish a text/link post to a Facebook Page feed.
        
        Args:
            message: Post message text.
            link: Optional URL to attach.
            page_id: Optional override for Page ID (uses self.page_id by default).
        """
        target_page_id = page_id or self.page_id
        if not target_page_id:
            return {"success": False, "error": "Facebook Page ID is required for publishing."}

        if not message and not link:
            return {"success": False, "error": "At least one of message or link is required."}

        data: Dict[str, Any] = {}
        if message:
            data["message"] = message
        if link:
            data["link"] = link

        try:
            resp = self._post_request(f"{target_page_id}/feed", data=data)
        except requests.exceptions.HTTPError as e:
            msg = self._graph_error_message(e.response) if e.response is not None else str(e)
            return {"success": False, "error": msg, "details": self._handle_error(e, "publish_feed_post")}
        except Exception as e:
            return self._handle_error(e, "publish_feed_post")

        post_id = resp.get("id")
        if not post_id:
            return {"success": False, "error": "Failed to publish Facebook feed post.", "details": resp}

        return {"success": True, "post_id": post_id}

    def publish_photo(
        self,
        image_url: str,
        caption: str = "",
        page_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Publish a photo to a Facebook Page.
        
        Args:
            image_url: Publicly accessible URL to the image.
            caption: Optional caption text.
            page_id: Optional override for Page ID.
        """
        target_page_id = page_id or self.page_id
        if not target_page_id:
            return {"success": False, "error": "Facebook Page ID is required for publishing photos."}

        if not image_url:
            return {"success": False, "error": "image_url is required for publishing a photo."}

        data: Dict[str, Any] = {"url": image_url}
        if caption:
            data["caption"] = caption

        try:
            resp = self._post_request(f"{target_page_id}/photos", data=data)
        except requests.exceptions.HTTPError as e:
            msg = self._graph_error_message(e.response) if e.response is not None else str(e)
            return {"success": False, "error": msg, "details": self._handle_error(e, "publish_photo")}
        except Exception as e:
            return self._handle_error(e, "publish_photo")

        post_id = resp.get("post_id") or resp.get("id")
        if not post_id:
            return {"success": False, "error": "Failed to publish Facebook photo.", "details": resp}

        return {"success": True, "post_id": post_id}

