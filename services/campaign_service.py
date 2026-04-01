"""Campaign service for managing marketing campaigns."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from core.database import (
    Campaign, CampaignExecution, CampaignStatus, 
    ExecutionStatus, ChannelType
)
from core.models import CampaignCreate, CampaignUpdate

logger = logging.getLogger(__name__)


class CampaignService:
    """Service for managing marketing campaigns."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_campaign(
        self,
        campaign_data: CampaignCreate,
        created_by: Optional[int] = None
    ) -> Campaign:
        """
        Create a new marketing campaign.
        
        Args:
            campaign_data: Campaign creation data
            created_by: User ID who created the campaign
        
        Returns:
            Created Campaign object
        """
        campaign = Campaign(
            name=campaign_data.name,
            channel=campaign_data.channel,
            status=CampaignStatus.DRAFT,
            schedule=campaign_data.schedule,
            config=campaign_data.config,
            created_by=created_by
        )
        
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        
        logger.info(f"Created campaign: {campaign.campaign_id} - {campaign.name}")
        return campaign
    
    def get_campaign(self, campaign_id: int) -> Optional[Campaign]:
        """Get campaign by ID."""
        return self.db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
    
    def list_campaigns(
        self,
        status: Optional[CampaignStatus] = None,
        channel: Optional[ChannelType] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Campaign]:
        """
        List campaigns with optional filters.
        
        Args:
            status: Filter by campaign status
            channel: Filter by channel type
            limit: Maximum number of campaigns to return
            offset: Number of campaigns to skip
        
        Returns:
            List of Campaign objects
        """
        query = self.db.query(Campaign)
        
        if status:
            query = query.filter(Campaign.status == status)
        if channel:
            query = query.filter(Campaign.channel == channel)
        
        return query.order_by(Campaign.created_at.desc()).offset(offset).limit(limit).all()
    
    def update_campaign(
        self,
        campaign_id: int,
        campaign_data: CampaignUpdate
    ) -> Optional[Campaign]:
        """
        Update an existing campaign.
        
        Args:
            campaign_id: Campaign ID to update
            campaign_data: Campaign update data
        
        Returns:
            Updated Campaign object or None if not found
        """
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            return None
        
        # Update fields if provided
        if campaign_data.name is not None:
            campaign.name = campaign_data.name
        if campaign_data.channel is not None:
            campaign.channel = campaign_data.channel
        if campaign_data.status is not None:
            campaign.status = campaign_data.status
        if campaign_data.schedule is not None:
            campaign.schedule = campaign_data.schedule
        if campaign_data.config is not None:
            campaign.config = {**campaign.config, **campaign_data.config}
        
        campaign.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(campaign)
        
        logger.info(f"Updated campaign: {campaign_id}")
        return campaign
    
    def delete_campaign(self, campaign_id: int) -> bool:
        """
        Delete a campaign.
        
        Args:
            campaign_id: Campaign ID to delete
        
        Returns:
            True if deleted, False if not found
        """
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            return False
        
        # Only allow deletion of draft or completed campaigns
        if campaign.status not in [CampaignStatus.DRAFT, CampaignStatus.COMPLETED]:
            logger.warning(
                f"Cannot delete campaign {campaign_id} with status {campaign.status}"
            )
            return False
        
        self.db.delete(campaign)
        self.db.commit()
        
        logger.info(f"Deleted campaign: {campaign_id}")
        return True
    
    def schedule_campaign(
        self,
        campaign_id: int,
        schedule_time: Optional[datetime] = None
    ) -> Optional[Campaign]:
        """
        Schedule a campaign for execution.
        
        Args:
            campaign_id: Campaign ID to schedule
            schedule_time: When to execute (None for immediate)
        
        Returns:
            Updated Campaign object or None if not found
        """
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            return None
        
        if schedule_time:
            campaign.schedule = schedule_time
            campaign.status = CampaignStatus.SCHEDULED
        else:
            campaign.status = CampaignStatus.SCHEDULED
            campaign.schedule = datetime.utcnow()
        
        campaign.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(campaign)
        
        logger.info(f"Scheduled campaign {campaign_id} for {campaign.schedule}")
        return campaign
    
    def pause_campaign(self, campaign_id: int) -> Optional[Campaign]:
        """Pause a running campaign."""
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            return None
        
        if campaign.status == CampaignStatus.RUNNING:
            campaign.status = CampaignStatus.PAUSED
            campaign.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(campaign)
            logger.info(f"Paused campaign: {campaign_id}")
        
        return campaign
    
    def resume_campaign(self, campaign_id: int) -> Optional[Campaign]:
        """Resume a paused campaign."""
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            return None
        
        if campaign.status == CampaignStatus.PAUSED:
            campaign.status = CampaignStatus.SCHEDULED
            campaign.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(campaign)
            logger.info(f"Resumed campaign: {campaign_id}")
        
        return campaign
    
    def create_execution(
        self,
        campaign_id: int
    ) -> CampaignExecution:
        """
        Create a new campaign execution record.
        
        Args:
            campaign_id: Campaign ID
        
        Returns:
            CampaignExecution object
        """
        execution = CampaignExecution(
            campaign_id=campaign_id,
            status=ExecutionStatus.PENDING
        )
        
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        
        logger.info(f"Created execution {execution.execution_id} for campaign {campaign_id}")
        return execution
    
    def update_execution_status(
        self,
        execution_id: int,
        status: ExecutionStatus,
        results: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> Optional[CampaignExecution]:
        """
        Update campaign execution status.
        
        Args:
            execution_id: Execution ID
            status: New status
            results: Execution results
            error_message: Error message if failed
        
        Returns:
            Updated CampaignExecution object
        """
        execution = self.db.query(CampaignExecution).filter(
            CampaignExecution.execution_id == execution_id
        ).first()
        
        if not execution:
            return None
        
        execution.status = status
        
        if status == ExecutionStatus.RUNNING and not execution.started_at:
            execution.started_at = datetime.utcnow()
        elif status in [ExecutionStatus.SUCCESS, ExecutionStatus.FAILED]:
            execution.completed_at = datetime.utcnow()
        
        if results is not None:
            execution.results = results
        if error_message:
            execution.error_message = error_message
        
        self.db.commit()
        self.db.refresh(execution)
        
        logger.info(f"Updated execution {execution_id} to status {status}")
        return execution
    
    def get_campaign_executions(
        self,
        campaign_id: int,
        limit: int = 10
    ) -> List[CampaignExecution]:
        """Get executions for a campaign."""
        return self.db.query(CampaignExecution).filter(
            CampaignExecution.campaign_id == campaign_id
        ).order_by(CampaignExecution.created_at.desc()).limit(limit).all()
    
    def get_campaign_stats(self, campaign_id: int) -> Dict[str, Any]:
        """
        Get campaign statistics.
        
        Args:
            campaign_id: Campaign ID
        
        Returns:
            Dictionary with campaign statistics
        """
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            return {}
        
        executions = self.get_campaign_executions(campaign_id, limit=100)
        
        total_executions = len(executions)
        successful = sum(1 for e in executions if e.status == ExecutionStatus.SUCCESS)
        failed = sum(1 for e in executions if e.status == ExecutionStatus.FAILED)
        pending = sum(1 for e in executions if e.status == ExecutionStatus.PENDING)
        
        # Aggregate results
        total_sent = 0
        total_delivered = 0
        total_opens = 0
        total_clicks = 0
        
        for execution in executions:
            if execution.results:
                total_sent += execution.results.get("sent", 0)
                total_delivered += execution.results.get("delivered", 0)
                total_opens += execution.results.get("opens", 0)
                total_clicks += execution.results.get("clicks", 0)
        
        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.name,
            "status": campaign.status.value,
            "channel": campaign.channel.value,
            "executions": {
                "total": total_executions,
                "successful": successful,
                "failed": failed,
                "pending": pending
            },
            "metrics": {
                "sent": total_sent,
                "delivered": total_delivered,
                "opens": total_opens,
                "clicks": total_clicks,
                "delivery_rate": (total_delivered / total_sent * 100) if total_sent > 0 else 0,
                "open_rate": (total_opens / total_delivered * 100) if total_delivered > 0 else 0,
                "click_rate": (total_clicks / total_delivered * 100) if total_delivered > 0 else 0
            },
            "created_at": campaign.created_at.isoformat(),
            "updated_at": campaign.updated_at.isoformat()
        }

