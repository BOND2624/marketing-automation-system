"""YouTube Data API v3 integration."""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from api_integrations.base import BaseIntegration

logger = logging.getLogger(__name__)


class YouTubeIntegration(BaseIntegration):
    """Integration with YouTube Data API v3."""
    
    def __init__(self, credentials: Dict[str, Any]):
        """
        Initialize YouTube integration.
        
        Args:
            credentials: Should contain:
                - 'api_key' for YouTube Data API v3 (required)
                - 'oauth2_credentials' for video uploads (optional, Dict or file path)
        """
        super().__init__(credentials, rate_limit_calls=10000, rate_limit_period=86400)  # 10k/day
        self.api_key = credentials.get("api_key")
        self.oauth_credentials = credentials.get("oauth2_credentials")
        self.youtube_oauth = None  # For authenticated (upload) operations
        
        if not self.api_key:
            raise ValueError("YouTube API key is required")
        
        try:
            # API key client for read operations
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        except Exception as e:
            logger.error(f"Failed to initialize YouTube API client: {e}")
            self.youtube = None
        
        # Initialize OAuth2 client if credentials provided
        if self.oauth_credentials:
            self._init_oauth_client()

    def _get_client(self):
        """Get authenticated client if available, fallback to public client."""
        return self.youtube_oauth if self.youtube_oauth else self.youtube    
    def _init_oauth_client(self):
        """Initialize OAuth2 client for authenticated operations."""
        try:
            from google.oauth2.credentials import Credentials
            import json
            
            # Handle different credential formats
            if isinstance(self.oauth_credentials, str):
                # File path to token JSON
                if os.path.exists(self.oauth_credentials):
                    with open(self.oauth_credentials, 'r') as f:
                        token_data = json.load(f)
                    creds = Credentials.from_authorized_user_info(token_data)
                else:
                    logger.warning(f"OAuth token file not found: {self.oauth_credentials}")
                    return
            elif isinstance(self.oauth_credentials, dict):
                # Direct token dictionary
                creds = Credentials.from_authorized_user_info(self.oauth_credentials)
            else:
                logger.warning("Invalid OAuth2 credentials format")
                return
            
            # Build authenticated YouTube client
            self.youtube_oauth = build('youtube', 'v3', credentials=creds)
            logger.info("OAuth2 YouTube client initialized for uploads")
            
        except ImportError:
            logger.warning("OAuth2 libraries not available. Install: pip install google-auth-oauthlib google-auth-httplib2")
        except Exception as e:
            logger.error(f"Failed to initialize OAuth2 client: {e}")
    
    def test_connection(self) -> bool:
        """Test YouTube API connection (both Key and OAuth)."""
        key_works = False
        oauth_works = False

        # 1. Test Public API Key (Public access)
        if self.youtube:
            try:
                self._handle_rate_limit()
                request = self.youtube.videos().list(
                    part="id",
                    chart="mostPopular",
                    maxResults=1
                )
                request.execute()
                key_works = True
            except HttpError as e:
                if e.resp.status == 403 and "quotaExceeded" in str(e):
                    logger.warning("YouTube API Key is valid but quota exceeded.")
                    key_works = True # Consider valid but limited
                else:
                    logger.error(f"YouTube Public Key test failed: {e}")
            except Exception as e:
                logger.error(f"YouTube Public Key test failed: {e}")

        # 2. Test OAuth (Personal/Upload access)
        if self.youtube_oauth:
            try:
                self._handle_rate_limit()
                # Use channels().list(mine=True) - requires youtube.readonly or youtube scopes
                request = self.youtube_oauth.channels().list(
                    part="id",
                    mine=True
                )
                request.execute()
                oauth_works = True
            except HttpError as e:
                if e.resp.status == 403 and "insufficientPermissions" in str(e):
                    logger.warning("YouTube OAuth token has insufficient scopes for health check (likely only 'upload').")
                    # If it's just insufficient permissions for THIS call, the token might still be valid for uploads
                    oauth_works = True 
                else:
                    logger.error(f"YouTube OAuth test failed: {e}")
            except Exception as e:
                logger.error(f"YouTube OAuth test failed: {e}")
        
        # If we have OAuth, it MUST work (or be valid-ish). 
        # If we only have Key, it MUST work.
        if self.youtube_oauth:
            return oauth_works
        return key_works
    
    def sync_channel_stats(self, channel_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Sync channel statistics.
        
        Args:
            channel_id: YouTube channel ID (if None, uses 'mine' - requires OAuth)
        
        Returns:
            Dictionary with channel stats
        """
        if not self.youtube:
            return {"error": "YouTube API client not initialized"}
        
        try:
            self._handle_rate_limit()
            
            # For now, using search to demonstrate (requires channel_id for actual channel stats)
            # In production, you'd use channels().list() with OAuth or API key with channel ID
            stats = {
                "subscriber_count": 0,
                "video_count": 0,
                "view_count": 0,
                "channel_id": channel_id,
                "synced_at": datetime.utcnow().isoformat()
            }
            
            if self.youtube_oauth:
                # Always prioritize authenticated "mine" view to ensure full access
                request = self.youtube_oauth.channels().list(
                    part="statistics,snippet",
                    mine=True
                )
            elif channel_id and self.youtube:
                 request = self.youtube.channels().list(
                    part="statistics,snippet",
                    id=channel_id
                )
            else:
                return {"error": "Channel ID required or OAuth credentials missing"}

            response = request.execute()
            
            if response.get("items"):
                item = response["items"][0]
                stats_data = item.get("statistics", {})
                stats.update({
                    "subscriber_count": int(stats_data.get("subscriberCount", 0)),
                    "video_count": int(stats_data.get("videoCount", 0)),
                    "view_count": int(stats_data.get("viewCount", 0)),
                    "channel_name": item.get("snippet", {}).get("title", ""),
                    "channel_id": item.get("id")  # Update with actual ID
                })
            
            return stats
        except HttpError as e:
            return self._handle_error(e, "sync_channel_stats")
    
    def sync_video_analytics(self, channel_id: Optional[str] = None, max_videos: int = 50) -> Dict[str, Any]:
        """
        Sync video analytics.
        
        Args:
            channel_id: YouTube channel ID
            max_videos: Maximum number of videos to fetch
        
        Returns:
            Dictionary with video analytics
        """
        if not self.youtube:
            return {"error": "YouTube API client not initialized"}
        
        try:
            videos = []
            self._handle_rate_limit()
            
            # Get channel uploads playlist
            if self.youtube_oauth:
                # Always prioritize authenticated "mine" view which reveals private uploads
                # Use the OAuth client for THIS request specifically
                channel_request = self.youtube_oauth.channels().list(
                    part="contentDetails",
                    mine=True
                )
                # Ensure we use OAuth client for subsequent requests too
                client = self.youtube_oauth
            elif channel_id and self.youtube:
                # Public fallback
                channel_request = self.youtube.channels().list(
                    part="contentDetails",
                    id=channel_id
                )
                client = self.youtube
            else:
                 return {"error": "Channel ID required or OAuth credentials missing"}

            channel_response = channel_request.execute()
            
            if channel_response.get("items"):
                uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
                
                # Get videos from uploads playlist
                playlist_request = client.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=uploads_playlist_id,
                    maxResults=min(max_videos, 50)
                )
                playlist_response = playlist_request.execute()
                
                video_ids = [item["contentDetails"]["videoId"] for item in playlist_response.get("items", [])]
                
                
                if video_ids:
                    self._handle_rate_limit()
                    # Get video statistics
                    videos_request = client.videos().list(
                        part="statistics,snippet",
                        id=",".join(video_ids)
                    )
                    videos_response = videos_request.execute()
                    
                    for item in videos_response.get("items", []):
                        stats = item.get("statistics", {})
                        videos.append({
                            "video_id": item["id"],
                            "title": item["snippet"].get("title", ""),
                            "views": int(stats.get("viewCount", 0)),
                            "likes": int(stats.get("likeCount", 0)),
                            "comments": int(stats.get("commentCount", 0)),
                            "published_at": item["snippet"].get("publishedAt", "")
                        })
            
            
            return {
                "videos": videos,
                "total_videos": len(videos),
                "synced_at": datetime.utcnow().isoformat(),
                "debug_info": {
                    "mode": "oauth" if client == self.youtube_oauth else "public",
                    "channel_id_param": channel_id,
                    "playlist_id": uploads_playlist_id,
                    "items_found": len(video_ids)
                }
            }
        except HttpError as e:
            return self._handle_error(e, "sync_video_analytics")

    def get_single_video_stats(self, video_id: str) -> Dict[str, Any]:
        """Statistics + snippet for one video (dashboard detail pane)."""
        client = self._get_client()
        if not client:
            return {"error": "YouTube API client not initialized"}
        if not video_id:
            return {"error": "video_id is required"}
        try:
            self._handle_rate_limit()
            resp = client.videos().list(
                part="statistics,snippet,contentDetails",
                id=video_id,
            ).execute()
            items = resp.get("items") or []
            if not items:
                return {"error": "Video not found", "video_id": video_id}
            item = items[0]
            stats = item.get("statistics", {})
            snip = item.get("snippet", {})
            return {
                "video_id": item["id"],
                "title": snip.get("title", ""),
                "description": snip.get("description", ""),
                "published_at": snip.get("publishedAt", ""),
                "thumbnail": (snip.get("thumbnails") or {})
                .get("medium", {})
                .get("url"),
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "duration": item.get("contentDetails", {}).get("duration"),
            }
        except HttpError as e:
            return self._handle_error(e, "get_single_video_stats")
    
    def sync_data(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Sync all YouTube data.
        
        Args:
            since: Only sync data since this datetime
        
        Returns:
            Dictionary with all synced data
        """
        channel_id = self.credentials.get("channel_id")
        
        result = {
            "channel": "youtube",
            "channel_stats": {},
            "video_analytics": {},
            "success": True,
            "errors": [],
            "synced_at": datetime.utcnow().isoformat()
        }
        
        # Sync channel stats
        try:
            stats = self.sync_channel_stats(channel_id)
            if "error" in stats:
                result["success"] = False
                result["errors"].append(stats["error"])
            else:
                result["channel_stats"] = stats
        except Exception as e:
            result["success"] = False
            result["errors"].append(str(e))
        
        # Sync video analytics
        try:
            analytics = self.sync_video_analytics(channel_id)
            if "error" in analytics:
                result["success"] = False
                result["errors"].append(analytics["error"])
            else:
                result["video_analytics"] = analytics
        except Exception as e:
            result["success"] = False
            result["errors"].append(str(e))
        
        return result
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: list = None,
        privacy_status: str = "public",
        category_id: str = "22"  # People & Blogs default
    ) -> Dict[str, Any]:
        """
        Upload a video to YouTube.
        
        Requires OAuth2 authentication (not just API key).
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            privacy_status: 'private', 'unlisted', or 'public' (default: public)
            category_id: YouTube category ID (default: 22 for People & Blogs)
        
        Returns:
            Dictionary with upload result including video_id
        """
        if not self.youtube_oauth:
            return {
                "success": False,
                "error": "OAuth2 authentication required for video upload. Generate token with: python scripts/generate_youtube_token.py"
            }
        
        if not os.path.exists(video_path):
            return {
                "success": False,
                "error": f"Video file not found: {video_path}"
            }
        
        try:
            self._handle_rate_limit()
            
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Create media upload
            media = MediaFileUpload(
                video_path,
                chunksize=-1,
                resumable=True,
                mimetype='video/*'
            )
            
            # Execute upload
            request = self.youtube_oauth.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            # Perform resumable upload
            video_id = None
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.info(f"Upload progress: {progress}%")
                if response:
                    video_id = response.get('id')
            
            return {
                "success": True,
                "video_id": video_id,
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "title": title,
                "privacy_status": privacy_status
            }
            
        except HttpError as e:
            error_msg = f"YouTube upload error: {e.error_details if hasattr(e, 'error_details') else str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Upload failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": error_msg
            }

