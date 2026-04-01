"""CampaignManagerAgent - Manages marketing campaign automation."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from crewai import Agent, Task, LLM
try:
    from langchain_ollama import OllamaLLM as Ollama
except ImportError:
    try:
        from langchain_community.llms import Ollama
    except ImportError:
        from langchain.llms import Ollama

from core.database import ChannelType, CampaignStatus, ExecutionStatus
from core.config import get_settings
from services.campaign_service import CampaignService
from services.execution_handlers import get_execution_handler
from core.models import CampaignCreate, CampaignUpdate

logger = logging.getLogger(__name__)
settings = get_settings()


class CampaignManagerAgent:
    """
    CrewAI agent for managing marketing campaigns.
    
    Responsibilities:
    - Create and manage marketing campaigns
    - Schedule campaign execution
    - Execute campaigns across channels
    - Monitor campaign status
    - Handle failures and retries
    """
    
    def __init__(self, db: Session, llm=None):
        """
        Initialize CampaignManagerAgent.
        
        Args:
            db: Database session
            llm: Language model for CrewAI agent (optional)
        """
        self.db = db
        self.campaign_service = CampaignService(db)
        
        # Initialize LLM (free tier - Ollama by default)
        if llm is None:
            if settings.llm_provider == "ollama":
                self.llm = LLM(
                    model=f"ollama/{settings.ollama_model}",
                    base_url=settings.ollama_base_url
                )
            else:
                # Fallback to Ollama llama3 if provider unknown
                self.llm = LLM(model="ollama/llama3")
        else:
            self.llm = llm
        
        # Initialize the CrewAI agent
        self.agent = Agent(
            role="Campaign Manager",
            goal="Efficiently create, schedule, execute, and monitor marketing campaigns across all channels",
            backstory="""You are an expert marketing campaign manager with deep knowledge of
            multi-channel marketing automation. You understand campaign best practices, optimal
            timing, audience targeting, and how to maximize engagement across YouTube, Instagram,
            Facebook, Email, and SMS channels. You ensure campaigns are properly configured,
            executed on time, and monitored for performance.""",
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )
    
    def create_campaign(
        self,
        name: str,
        channel: ChannelType,
        config: Dict[str, Any],
        schedule: Optional[datetime] = None,
        created_by: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new marketing campaign.
        
        Args:
            name: Campaign name
            channel: Marketing channel
            config: Campaign configuration (content, targeting, etc.)
            schedule: Optional scheduled execution time
            created_by: User ID who created the campaign
        
        Returns:
            Dictionary with campaign details
        """
        try:
            campaign_data = CampaignCreate(
                name=name,
                channel=channel,
                config=config,
                schedule=schedule
            )
            
            campaign = self.campaign_service.create_campaign(
                campaign_data,
                created_by=created_by
            )
            
            logger.info(f"Campaign created: {campaign.campaign_id} - {campaign.name}")
            
            return {
                "success": True,
                "campaign_id": campaign.campaign_id,
                "name": campaign.name,
                "channel": campaign.channel.value,
                "status": campaign.status.value,
                "schedule": campaign.schedule.isoformat() if campaign.schedule else None
            }
            
        except Exception as e:
            logger.error(f"Failed to create campaign: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def execute_campaign(
        self,
        campaign_id: int,
        credentials: Optional[Dict[ChannelType, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Execute a marketing campaign.
        
        Args:
            campaign_id: Campaign ID to execute
            credentials: Channel-specific API credentials
        
        Returns:
            Execution results dictionary
        """
        campaign = self.campaign_service.get_campaign(campaign_id)
        if not campaign:
            return {
                "success": False,
                "error": f"Campaign {campaign_id} not found"
            }
        
        # Check campaign status
        if campaign.status not in [CampaignStatus.DRAFT, CampaignStatus.SCHEDULED]:
            return {
                "success": False,
                "error": f"Cannot execute campaign with status: {campaign.status}"
            }
        
        # Create execution record
        execution = self.campaign_service.create_execution(campaign_id)
        
        # Update campaign status
        campaign.status = CampaignStatus.RUNNING
        campaign.updated_at = datetime.utcnow()
        self.db.commit()
        
        # Update execution status
        self.campaign_service.update_execution_status(
            execution.execution_id,
            ExecutionStatus.RUNNING
        )
        
        try:
            # Get execution handler for the channel
            channel_creds = (credentials or {}).get(campaign.channel, {})
            handler = get_execution_handler(campaign.channel, channel_creds)
            
            # Execute the campaign
            results = handler.execute(campaign, execution)
            
            # Update execution with results
            if results.get("success"):
                self.campaign_service.update_execution_status(
                    execution.execution_id,
                    ExecutionStatus.SUCCESS,
                    results=results
                )
                campaign.status = CampaignStatus.COMPLETED
            else:
                self.campaign_service.update_execution_status(
                    execution.execution_id,
                    ExecutionStatus.FAILED,
                    results=results,
                    error_message=results.get("error")
                )
                campaign.status = CampaignStatus.FAILED
            
            campaign.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(
                f"Campaign {campaign_id} execution completed: "
                f"success={results.get('success')}"
            )
            
            return {
                "success": results.get("success", False),
                "execution_id": execution.execution_id,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Campaign execution failed: {e}", exc_info=True)
            
            # Mark execution as failed
            self.campaign_service.update_execution_status(
                execution.execution_id,
                ExecutionStatus.FAILED,
                error_message=str(e)
            )
            campaign.status = CampaignStatus.FAILED
            campaign.updated_at = datetime.utcnow()
            self.db.commit()
            
            return {
                "success": False,
                "error": str(e),
                "execution_id": execution.execution_id
            }
    
    def schedule_campaign(
        self,
        campaign_id: int,
        schedule_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Schedule a campaign for execution.
        
        Args:
            campaign_id: Campaign ID
            schedule_time: When to execute (None for immediate)
        
        Returns:
            Scheduling result
        """
        campaign = self.campaign_service.schedule_campaign(
            campaign_id,
            schedule_time
        )
        
        if not campaign:
            return {
                "success": False,
                "error": f"Campaign {campaign_id} not found"
            }
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "status": campaign.status.value,
            "schedule": campaign.schedule.isoformat() if campaign.schedule else None
        }
    
    def pause_campaign(self, campaign_id: int) -> Dict[str, Any]:
        """Pause a running campaign."""
        campaign = self.campaign_service.pause_campaign(campaign_id)
        
        if not campaign:
            return {
                "success": False,
                "error": f"Campaign {campaign_id} not found or cannot be paused"
            }
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "status": campaign.status.value
        }
    
    def resume_campaign(self, campaign_id: int) -> Dict[str, Any]:
        """Resume a paused campaign."""
        campaign = self.campaign_service.resume_campaign(campaign_id)
        
        if not campaign:
            return {
                "success": False,
                "error": f"Campaign {campaign_id} not found or cannot be resumed"
            }
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "status": campaign.status.value
        }
    
    def get_campaign_status(self, campaign_id: int) -> Dict[str, Any]:
        """
        Get comprehensive campaign status.
        
        Args:
            campaign_id: Campaign ID
        
        Returns:
            Campaign status and statistics
        """
        stats = self.campaign_service.get_campaign_stats(campaign_id)
        
        if not stats:
            return {
                "success": False,
                "error": f"Campaign {campaign_id} not found"
            }
        
        return {
            "success": True,
            **stats
        }
    
    def list_campaigns(
        self,
        status: Optional[CampaignStatus] = None,
        channel: Optional[ChannelType] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        List campaigns with optional filters.
        
        Args:
            status: Filter by status
            channel: Filter by channel
            limit: Maximum number of campaigns
        
        Returns:
            List of campaigns
        """
        campaigns = self.campaign_service.list_campaigns(
            status=status,
            channel=channel,
            limit=limit
        )
        
        return {
            "success": True,
            "count": len(campaigns),
            "campaigns": [
                {
                    "campaign_id": c.campaign_id,
                    "name": c.name,
                    "channel": c.channel.value,
                    "status": c.status.value,
                    "schedule": c.schedule.isoformat() if c.schedule else None,
                    "created_at": c.created_at.isoformat()
                }
                for c in campaigns
            ]
        }

