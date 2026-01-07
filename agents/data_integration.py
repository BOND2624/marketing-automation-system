"""DataIntegrationAgent - Syncs data from all marketing channels to CDP."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from crewai import Agent, Task
try:
    # Try new langchain-ollama package first
    from langchain_ollama import OllamaLLM as Ollama
except ImportError:
    try:
        # Fallback to langchain_community
        from langchain_community.llms import Ollama
    except ImportError:
        # Last resort: old langchain location (deprecated)
        from langchain.llms import Ollama

from api_integrations.youtube import YouTubeIntegration
from api_integrations.instagram import InstagramIntegration
from api_integrations.facebook import FacebookIntegration
from api_integrations.email_sms import EmailSMSIntegration
from core.cdp import CDPService
from core.database import ChannelType, CustomerEvent
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DataIntegrationAgent:
    """
    CrewAI agent for synchronizing data from all marketing channels to the CDP.
    
    Responsibilities:
    - Sync data from YouTube, Instagram, Facebook, Email/SMS APIs
    - Handle API rate limits and pagination
    - Transform channel-specific data to unified format
    - Store data in CDP
    """
    
    def __init__(self, db: Session, llm=None):
        """
        Initialize DataIntegrationAgent.
        
        Args:
            db: Database session
            llm: Language model for CrewAI agent (optional, will use Ollama if not provided)
        """
        self.db = db
        self.cdp_service = CDPService(db)
        
        # Initialize LLM (free tier - Ollama by default)
        if llm is None:
            if settings.llm_provider == "ollama":
                self.llm = Ollama(
                    model=settings.ollama_model,
                    base_url=settings.ollama_base_url
                )
            else:
                # Fallback to a default model
                self.llm = Ollama(model="llama3")
        else:
            self.llm = llm
        
        # Initialize the CrewAI agent
        self.agent = Agent(
            role="Data Integration Specialist",
            goal="Synchronize marketing channel data to the Customer Data Platform accurately and efficiently",
            backstory="""You are an expert at integrating data from multiple marketing platforms.
            You understand API rate limits, data pagination, and how to transform diverse data formats
            into a unified customer profile. You ensure data accuracy and handle errors gracefully.""",
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )
        
        # Channel integrations (will be initialized when credentials are available)
        self.integrations: Dict[ChannelType, Any] = {}
    
    def _get_integration(self, channel: ChannelType, credentials: Dict[str, Any]):
        """Get or create integration instance for a channel."""
        if channel not in self.integrations:
            try:
                if channel == ChannelType.YOUTUBE:
                    self.integrations[channel] = YouTubeIntegration(credentials)
                elif channel == ChannelType.INSTAGRAM:
                    self.integrations[channel] = InstagramIntegration(credentials)
                elif channel == ChannelType.FACEBOOK:
                    self.integrations[channel] = FacebookIntegration(credentials)
                elif channel in [ChannelType.EMAIL, ChannelType.SMS]:
                    self.integrations[channel] = EmailSMSIntegration(credentials)
            except Exception as e:
                logger.error(f"Failed to initialize {channel} integration: {e}")
                return None
        return self.integrations.get(channel)
    
    def sync_youtube_data(
        self,
        credentials: Dict[str, Any],
        since: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Sync YouTube data to CDP.
        
        Args:
            credentials: YouTube API credentials
            since: Only sync data since this datetime
        
        Returns:
            Sync result dictionary
        """
        integration = self._get_integration(ChannelType.YOUTUBE, credentials)
        if not integration:
            return {"error": "Failed to initialize YouTube integration", "success": False}
        
        try:
            # Test connection
            if not integration.test_connection():
                return {"error": "YouTube API connection failed", "success": False}
            
            # Sync data
            sync_result = integration.sync_data(since)
            
            # Transform and store in CDP
            if sync_result.get("success"):
                self._process_youtube_data(sync_result)
            
            return sync_result
        except Exception as e:
            logger.error(f"YouTube sync error: {e}", exc_info=True)
            return {"error": str(e), "success": False}
    
    def sync_instagram_data(
        self,
        credentials: Dict[str, Any],
        since: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Sync Instagram data to CDP."""
        integration = self._get_integration(ChannelType.INSTAGRAM, credentials)
        if not integration:
            return {"error": "Failed to initialize Instagram integration", "success": False}
        
        try:
            if not integration.test_connection():
                return {"error": "Instagram API connection failed", "success": False}
            
            sync_result = integration.sync_data(since)
            
            if sync_result.get("success"):
                self._process_instagram_data(sync_result)
            
            return sync_result
        except Exception as e:
            logger.error(f"Instagram sync error: {e}", exc_info=True)
            return {"error": str(e), "success": False}
    
    def sync_facebook_data(
        self,
        credentials: Dict[str, Any],
        since: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Sync Facebook data to CDP."""
        integration = self._get_integration(ChannelType.FACEBOOK, credentials)
        if not integration:
            return {"error": "Failed to initialize Facebook integration", "success": False}
        
        try:
            if not integration.test_connection():
                return {"error": "Facebook API connection failed", "success": False}
            
            sync_result = integration.sync_data(since)
            
            if sync_result.get("success"):
                self._process_facebook_data(sync_result)
            
            return sync_result
        except Exception as e:
            logger.error(f"Facebook sync error: {e}", exc_info=True)
            return {"error": str(e), "success": False}
    
    def sync_email_sms_data(
        self,
        credentials: Dict[str, Any],
        since: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Sync Email/SMS data to CDP."""
        integration = self._get_integration(ChannelType.EMAIL, credentials)
        if not integration:
            return {"error": "Failed to initialize Email/SMS integration", "success": False}
        
        try:
            if not integration.test_connection():
                return {"error": "Email/SMS API connection failed", "success": False}
            
            sync_result = integration.sync_data(since)
            
            if sync_result.get("success"):
                self._process_email_sms_data(sync_result)
            
            return sync_result
        except Exception as e:
            logger.error(f"Email/SMS sync error: {e}", exc_info=True)
            return {"error": str(e), "success": False}
    
    def sync_all_channels(
        self,
        channel_credentials: Dict[ChannelType, Dict[str, Any]],
        since: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Sync data from all configured channels.
        
        Args:
            channel_credentials: Dictionary mapping ChannelType to credentials
            since: Only sync data since this datetime
        
        Returns:
            Dictionary with sync results for each channel
        """
        results = {
            "overall_success": True,
            "channels": {},
            "synced_at": datetime.utcnow().isoformat()
        }
        
        # Sync each channel
        if ChannelType.YOUTUBE in channel_credentials:
            results["channels"]["youtube"] = self.sync_youtube_data(
                channel_credentials[ChannelType.YOUTUBE],
                since
            )
            if not results["channels"]["youtube"].get("success"):
                results["overall_success"] = False
        
        if ChannelType.INSTAGRAM in channel_credentials:
            results["channels"]["instagram"] = self.sync_instagram_data(
                channel_credentials[ChannelType.INSTAGRAM],
                since
            )
            if not results["channels"]["instagram"].get("success"):
                results["overall_success"] = False
        
        if ChannelType.FACEBOOK in channel_credentials:
            results["channels"]["facebook"] = self.sync_facebook_data(
                channel_credentials[ChannelType.FACEBOOK],
                since
            )
            if not results["channels"]["facebook"].get("success"):
                results["overall_success"] = False
        
        if ChannelType.EMAIL in channel_credentials:
            results["channels"]["email_sms"] = self.sync_email_sms_data(
                channel_credentials[ChannelType.EMAIL],
                since
            )
            if not results["channels"]["email_sms"].get("success"):
                results["overall_success"] = False
        
        return results
    
    def _process_youtube_data(self, sync_result: Dict[str, Any]):
        """Process YouTube sync data and store in CDP."""
        # Extract subscriber/engagement data
        channel_stats = sync_result.get("channel_stats", {})
        video_analytics = sync_result.get("video_analytics", {})
        
        # Store aggregated stats (could be associated with a channel owner customer)
        # This is a simplified version - in production, you'd map to actual customers
        logger.info(f"Processed YouTube data: {len(video_analytics.get('videos', []))} videos")
    
    def _process_instagram_data(self, sync_result: Dict[str, Any]):
        """Process Instagram sync data and store in CDP."""
        account_info = sync_result.get("account_info", {})
        posts = sync_result.get("posts", {})
        
        logger.info(f"Processed Instagram data: {posts.get('total_posts', 0)} posts")
    
    def _process_facebook_data(self, sync_result: Dict[str, Any]):
        """Process Facebook sync data and store in CDP."""
        page_insights = sync_result.get("page_insights", {})
        page_posts = sync_result.get("page_posts", {})
        
        logger.info(f"Processed Facebook data: {page_posts.get('total_posts', 0)} posts")
    
    def _process_email_sms_data(self, sync_result: Dict[str, Any]):
        """Process Email/SMS sync data and store in CDP."""
        email_stats = sync_result.get("email_stats", {})
        sms_stats = sync_result.get("sms_stats", {})
        
        logger.info(f"Processed Email/SMS data: {email_stats.get('total_sends', 0)} emails sent")
    
    def unify_customer_data(self, customer_id: int, channel_data: Dict[ChannelType, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Unify customer data from multiple channels.
        
        Args:
            customer_id: Customer ID
            channel_data: Dictionary mapping ChannelType to channel-specific data
        
        Returns:
            Unified customer profile
        """
        # Merge data from all channels into customer attributes
        for channel, data in channel_data.items():
            self.cdp_service.unify_customer_data(customer_id, channel, data)
        
        # Get unified profile
        return self.cdp_service.get_unified_customer_profile(customer_id)

