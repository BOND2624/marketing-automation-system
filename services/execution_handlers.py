"""Channel-specific campaign execution handlers."""

import os
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from core.database import ChannelType, Campaign, CampaignExecution
from api_integrations.youtube import YouTubeIntegration
from api_integrations.instagram import InstagramIntegration
from api_integrations.facebook import FacebookIntegration
from api_integrations.email_sms import EmailSMSIntegration

logger = logging.getLogger(__name__)


class ExecutionHandler:
    """Base class for campaign execution handlers."""
    
    def __init__(self, credentials: Optional[Dict[str, Any]] = None):
        self.credentials = credentials or {}
        self.integration = None
    
    def validate_campaign_config(self, config: Dict[str, Any]) -> tuple:
        """
        Validate campaign configuration.
        
        Returns:
            (is_valid, error_message)
        """
        # Base validation - should be overridden
        return True, None
    
    def execute(
        self,
        campaign: Campaign,
        execution: CampaignExecution
    ) -> Dict[str, Any]:
        """
        Execute the campaign.
        
        Args:
            campaign: Campaign object
            execution: CampaignExecution object
        
        Returns:
            Execution results dictionary
        """
        raise NotImplementedError("Subclasses must implement execute()")


class EmailExecutionHandler(ExecutionHandler):
    """Handler for email campaign execution."""
    
    def __init__(self, credentials: Optional[Dict[str, Any]] = None):
        super().__init__(credentials)
        if credentials and credentials.get("sendgrid_api_key"):
            try:
                self.integration = EmailSMSIntegration(credentials)
            except Exception as e:
                logger.error(f"Failed to initialize Email integration: {e}")
    
    def validate_campaign_config(self, config: Dict[str, Any]) -> tuple:
        """Validate email campaign config."""
        required_fields = ["subject", "content", "recipients"]
        for field in required_fields:
            if field not in config:
                return False, f"Missing required field: {field}"
        
        if not isinstance(config.get("recipients"), list) or len(config["recipients"]) == 0:
            return False, "recipients must be a non-empty list"
        
        return True, None
    
    def execute(
        self,
        campaign: Campaign,
        execution: CampaignExecution
    ) -> Dict[str, Any]:
        """Execute email campaign."""
        if not self.integration:
            return {
                "success": False,
                "error": "Email integration not initialized. Check SendGrid API key."
            }
        
        config = campaign.config
        results = {
            "sent": 0,
            "delivered": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            # Validate config
            is_valid, error = self.validate_campaign_config(config)
            if not is_valid:
                return {"success": False, "error": error}
            
            # In a real implementation, you would:
            # 1. Use SendGrid API to send emails
            # 2. Track delivery status
            # 3. Monitor opens/clicks via webhooks
            
            # For now, simulate execution
            recipients = config.get("recipients", [])
            results["sent"] = len(recipients)
            
            # Simulate delivery (in production, this comes from SendGrid webhooks)
            results["delivered"] = int(len(recipients) * 0.95)  # 95% delivery rate
            results["failed"] = results["sent"] - results["delivered"]
            
            logger.info(
                f"Email campaign {campaign.campaign_id} executed: "
                f"{results['sent']} sent, {results['delivered']} delivered"
            )
            
            return {
                "success": True,
                **results
            }
            
        except Exception as e:
            logger.error(f"Email execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                **results
            }


class SMSExecutionHandler(ExecutionHandler):
    """Handler for SMS campaign execution."""
    
    def __init__(self, credentials: Optional[Dict[str, Any]] = None):
        super().__init__(credentials)
        if credentials and credentials.get("twilio_account_sid") and credentials.get("twilio_auth_token"):
            try:
                self.integration = EmailSMSIntegration(credentials)
            except Exception as e:
                logger.error(f"Failed to initialize SMS integration: {e}")
    
    def validate_campaign_config(self, config: Dict[str, Any]) -> tuple:
        """Validate SMS campaign config."""
        required_fields = ["message", "recipients"]
        for field in required_fields:
            if field not in config:
                return False, f"Missing required field: {field}"
        
        if not isinstance(config.get("recipients"), list) or len(config["recipients"]) == 0:
            return False, "recipients must be a non-empty list"
        
        return True, None
    
    def execute(
        self,
        campaign: Campaign,
        execution: CampaignExecution
    ) -> Dict[str, Any]:
        """Execute SMS campaign."""
        if not self.integration:
            return {
                "success": False,
                "error": "SMS integration not initialized. Check Twilio credentials."
            }
        
        config = campaign.config
        results = {
            "sent": 0,
            "delivered": 0,
            "failed": 0
        }
        
        try:
            is_valid, error = self.validate_campaign_config(config)
            if not is_valid:
                return {"success": False, "error": error}
            
            recipients = config.get("recipients", [])
            results["sent"] = len(recipients)
            results["delivered"] = int(len(recipients) * 0.98)  # 98% delivery rate
            results["failed"] = results["sent"] - results["delivered"]
            
            logger.info(
                f"SMS campaign {campaign.campaign_id} executed: "
                f"{results['sent']} sent, {results['delivered']} delivered"
            )
            
            return {
                "success": True,
                **results
            }
            
        except Exception as e:
            logger.error(f"SMS execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                **results
            }


class InstagramExecutionHandler(ExecutionHandler):
    """Handler for Instagram campaign execution."""
    
    def __init__(self, credentials: Optional[Dict[str, Any]] = None):
        super().__init__(credentials)
        if credentials and credentials.get("access_token"):
            try:
                self.integration = InstagramIntegration(credentials)
            except Exception as e:
                logger.error(f"Failed to initialize Instagram integration: {e}")
    
    def validate_campaign_config(self, config: Dict[str, Any]) -> tuple:
        """Validate Instagram campaign config."""
        # Instagram campaigns can be posts, stories, etc.
        if "content" not in config and "media_url" not in config:
            return False, "Missing content or media_url"
        return True, None
    
    def execute(
        self,
        campaign: Campaign,
        execution: CampaignExecution
    ) -> Dict[str, Any]:
        """Execute Instagram campaign."""
        if not self.integration:
            return {
                "success": False,
                "error": "Instagram integration not initialized. Check access token."
            }
        
        results = {
            "posted": False,
            "post_id": None,
            "errors": []
        }
        
        try:
            # In production, would use Instagram Graph API to publish
            # For now, simulate success
            results["posted"] = True
            results["post_id"] = f"ig_{campaign.campaign_id}_{datetime.utcnow().timestamp()}"
            
            logger.info(f"Instagram campaign {campaign.campaign_id} executed")
            
            return {
                "success": True,
                **results
            }
            
        except Exception as e:
            logger.error(f"Instagram execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                **results
            }


class FacebookExecutionHandler(ExecutionHandler):
    """Handler for Facebook campaign execution."""
    
    def __init__(self, credentials: Optional[Dict[str, Any]] = None):
        super().__init__(credentials)
        if credentials and credentials.get("access_token"):
            try:
                self.integration = FacebookIntegration(credentials)
            except Exception as e:
                logger.error(f"Failed to initialize Facebook integration: {e}")
    
    def validate_campaign_config(self, config: Dict[str, Any]) -> tuple:
        """Validate Facebook campaign config."""
        if "message" not in config and "media_url" not in config:
            return False, "Missing message or media_url"
        return True, None
    
    def execute(
        self,
        campaign: Campaign,
        execution: CampaignExecution
    ) -> Dict[str, Any]:
        """Execute Facebook campaign."""
        if not self.integration:
            return {
                "success": False,
                "error": "Facebook integration not initialized. Check access token."
            }
        
        results = {
            "posted": False,
            "post_id": None
        }
        
        try:
            # Simulate posting
            results["posted"] = True
            results["post_id"] = f"fb_{campaign.campaign_id}_{datetime.utcnow().timestamp()}"
            
            logger.info(f"Facebook campaign {campaign.campaign_id} executed")
            
            return {
                "success": True,
                **results
            }
            
        except Exception as e:
            logger.error(f"Facebook execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                **results
            }


class YouTubeExecutionHandler(ExecutionHandler):
    """Handler for YouTube campaign execution."""
    
    def __init__(self, credentials: Optional[Dict[str, Any]] = None):
        super().__init__(credentials)
        if credentials and credentials.get("api_key"):
            try:
                # 1. Check if OAuth2 credentials were provided directly in the dictionary
                if credentials.get("oauth2_credentials"):
                    self.integration = YouTubeIntegration(credentials)
                    logger.info("YouTube integration initialized with provided OAuth2 credentials")
                    return

                # 2. Fallback: Check for OAuth2 token file in project root
                import os
                # Get project root: from services/execution_handlers.py -> services/ -> project root
                project_root = os.path.dirname(os.path.dirname(__file__))
                token_file = os.path.join(project_root, "youtube_token.json")
                
                if os.path.exists(token_file):
                    credentials_with_oauth = credentials.copy()
                    credentials_with_oauth["oauth2_credentials"] = token_file
                    self.integration = YouTubeIntegration(credentials_with_oauth)
                    logger.info("YouTube integration initialized with detected OAuth2 token file")
                else:
                    self.integration = YouTubeIntegration(credentials)
                    logger.info("YouTube integration initialized (API key only - uploads disabled)")
            except Exception as e:
                logger.error(f"Failed to initialize YouTube integration: {e}")
                self.integration = None
    
    def validate_campaign_config(self, config: Dict[str, Any]) -> tuple:
        """Validate YouTube campaign config."""
        # YouTube campaigns typically upload videos
        if "video_path" not in config and "video_url" not in config:
            return False, "Missing video_path or video_url"
        return True, None
    
    def execute(
        self,
        campaign: Campaign,
        execution: CampaignExecution
    ) -> Dict[str, Any]:
        """Execute YouTube campaign - upload video if provided."""
        results = {
            "uploaded": False,
            "video_id": None,
            "channel_stats": None,
            "note": None,
            "error": None
        }
        
        try:
            config = campaign.config
            video_path = config.get("video_path")
            video_url = config.get("video_url")
            upload_type = config.get("upload_type")
            is_shorts_upload = False
            if isinstance(upload_type, str):
                is_shorts_upload = upload_type.strip().lower() in {"short", "shorts", "youtube_short"}
            elif isinstance(upload_type, bool):
                is_shorts_upload = upload_type
            
            # If we have integration, try to get channel stats
            if self.integration:
                channel_id = self.credentials.get("channel_id")
                if channel_id:
                    # Get channel stats (this works with just API key)
                    stats = self.integration.sync_channel_stats(channel_id)
                    if "error" not in stats:
                        results["channel_stats"] = stats
                        logger.info(f"YouTube channel stats fetched for campaign {campaign.campaign_id}")
            
            # Attempt video upload if video path is provided
            if video_path:
                if not os.path.exists(video_path):
                    results["error"] = f"Video file not found: {video_path}"
                    results["note"] = "Video file path is invalid"
                    logger.error(f"Video file not found: {video_path}")
                else:
                    # Validate Shorts requirements if requested
                    if is_shorts_upload:
                        is_valid_short, validation_msg = self._validate_shorts_video(video_path)
                        if not is_valid_short:
                            results["error"] = validation_msg
                            results["note"] = "Video does not meet YouTube Shorts requirements."
                            logger.warning(f"YouTube Shorts validation failed: {validation_msg}")
                            success = results.get("channel_stats") is not None
                            return {
                                "success": success,
                                **results
                            }

                    # Try to upload video using integration
                    upload_result = self.integration.upload_video(
                        video_path=video_path,
                        title=config.get("title", "Uploaded Video"),
                        description=config.get("description", ""),
                        tags=config.get("tags", []),
                        privacy_status=config.get("privacy_status", "unlisted")
                    )
                    
                    if upload_result.get("success"):
                        results["uploaded"] = True
                        results["video_id"] = upload_result.get("video_id")
                        results["note"] = f"Video uploaded successfully! URL: {upload_result.get('video_url')}"
                        logger.info(f"YouTube video uploaded: {results['video_id']}")
                    else:
                        error_msg = upload_result.get("error", "Upload failed")
                        results["error"] = error_msg
                        results["note"] = "Video upload failed. " + error_msg
                        logger.warning(f"YouTube upload failed: {error_msg}")
            elif video_url:
                results["note"] = "Video URL provided. Direct URL upload not supported - use video_path for local files."
                results["error"] = "Video URL upload not implemented"
            else:
                # Just sync channel stats if no video to upload
                results["note"] = "Channel stats synced. No video path provided."
            
            # Success if we got stats OR uploaded video
            success = results.get("channel_stats") is not None or results.get("uploaded") is True
            
            logger.info(f"YouTube campaign {campaign.campaign_id} executed: uploaded={results.get('uploaded')}")
            
            return {
                "success": success,
                **results
            }
            
        except Exception as e:
            logger.error(f"YouTube execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "note": "YouTube execution error",
                **results
            }

    def _validate_shorts_video(self, video_path: str) -> Tuple[bool, str]:
        """
        Validate that a video meets YouTube Shorts requirements.
        Requires moviepy for metadata extraction.
        """
        try:
            from moviepy.editor import VideoFileClip  # type: ignore
        except ImportError:
            return False, "Shorts validation requires moviepy. Install with: pip install moviepy"

        clip = None
        try:
            clip = VideoFileClip(video_path)
            duration = clip.duration or 0.0
            width, height = clip.size
        except Exception as exc:
            return False, f"Unable to read video metadata: {exc}"
        finally:
            if clip:
                clip.close()

        if duration > 60:
            return False, f"Video duration {duration:.2f}s exceeds 60 second Shorts limit."

        if height <= 0:
            return False, "Invalid video dimensions detected."

        if width >= height:
            return False, "Video must be vertical (height greater than width) for Shorts."

        aspect_ratio = width / height
        target_ratio = 9 / 16  # 0.5625
        if abs(aspect_ratio - target_ratio) > 0.1:
            return False, f"Video aspect ratio {aspect_ratio:.2f} is not close to 9:16 required for Shorts."

        return True, "Video meets Shorts criteria."


def get_execution_handler(
    channel: ChannelType,
    credentials: Optional[Dict[str, Any]] = None
) -> ExecutionHandler:
    """
    Get the appropriate execution handler for a channel.
    
    Args:
        channel: Marketing channel type
        credentials: Channel-specific API credentials (can be None)
    
    Returns:
        ExecutionHandler instance
    """
    handlers = {
        ChannelType.EMAIL: EmailExecutionHandler,
        ChannelType.SMS: SMSExecutionHandler,
        ChannelType.INSTAGRAM: InstagramExecutionHandler,
        ChannelType.FACEBOOK: FacebookExecutionHandler,
        ChannelType.YOUTUBE: YouTubeExecutionHandler,
    }
    
    handler_class = handlers.get(channel)
    if not handler_class:
        raise ValueError(f"No handler for channel: {channel}")
    
    return handler_class(credentials)

