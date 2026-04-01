"""Celery task scheduler for periodic data sync."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from celery import Celery
from sqlalchemy.orm import Session

from core.config import get_settings
from core.database import (
    get_db, ChannelType, ChannelCredential, CampaignStatus, Campaign,
    CampaignExecution, ExecutionStatus
)
import os
# from api.routes.youtube import get_youtube_status (Removed to avoid circular import)
from agents.data_integration import DataIntegrationAgent
from agents.campaign_manager import CampaignManagerAgent
from services.campaign_service import CampaignService
from datetime import datetime

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize Celery
celery_app = Celery(
    "marketing_automation",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


def get_channel_credentials(db: Session) -> Dict[ChannelType, Dict[str, Any]]:
    """
    Get active channel credentials from database.
    
    Args:
        db: Database session
    
    Returns:
        Dictionary mapping ChannelType to credentials dictionary
    """
    credentials = {}
    
    # Query active credentials
    active_creds = db.query(ChannelCredential).filter(
        ChannelCredential.is_active == True
    ).all()
    
    # TODO: Decrypt credentials (requires encryption service)
    # For now, returning placeholder structure
    for cred in active_creds:
        # In production, decrypt encrypted_credentials here
        # For now, assume credentials are already in the format needed
        credentials[cred.channel_type] = {
            "encrypted": True,
            "credential_id": cred.credential_id
        }
    
    return credentials


@celery_app.task(name="sync_all_channels")
def sync_all_channels_task(force_full_sync: bool = False):
    """
    Celery task to sync data from all channels.
    
    Args:
        force_full_sync: If True, sync all data regardless of timestamp
    
    Returns:
        Sync results dictionary
    """
    db = next(get_db())
    
    try:
        # Get channel credentials
        channel_credentials = get_channel_credentials(db)
        
        if not channel_credentials:
            logger.warning("No active channel credentials found")
            return {
                "success": False,
                "error": "No active channel credentials configured"
            }
        
        # Initialize agent
        agent = DataIntegrationAgent(db)
        
        # Determine sync window
        since = None if force_full_sync else datetime.utcnow() - timedelta(hours=24)
        
        # Sync all channels
        results = agent.sync_all_channels(channel_credentials, since)
        
        logger.info(f"Sync completed: {results.get('overall_success', False)}")
        
        return results
    
    except Exception as e:
        logger.error(f"Sync task failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="sync_single_channel")
def sync_single_channel_task(channel: str, force_full_sync: bool = False):
    """
    Celery task to sync data from a single channel.
    
    Args:
        channel: Channel name (youtube, instagram, facebook, email)
        force_full_sync: If True, sync all data regardless of timestamp
    
    Returns:
        Sync result dictionary
    """
    db = next(get_db())
    
    try:
        # Get channel credentials for specific channel
        channel_credentials = get_channel_credentials(db)
        channel_type = ChannelType(channel.lower())
        
        if channel_type not in channel_credentials:
            return {
                "success": False,
                "error": f"Credentials not found for channel: {channel}"
            }
        
        # Initialize agent
        agent = DataIntegrationAgent(db)
        
        # Determine sync window
        since = None if force_full_sync else datetime.utcnow() - timedelta(hours=24)
        
        # Sync specific channel
        if channel_type == ChannelType.YOUTUBE:
            result = agent.sync_youtube_data(channel_credentials[channel_type], since)
        elif channel_type == ChannelType.INSTAGRAM:
            result = agent.sync_instagram_data(channel_credentials[channel_type], since)
        elif channel_type == ChannelType.FACEBOOK:
            result = agent.sync_facebook_data(channel_credentials[channel_type], since)
        elif channel_type == ChannelType.EMAIL:
            result = agent.sync_email_sms_data(channel_credentials[channel_type], since)
        else:
            result = {"success": False, "error": f"Unsupported channel: {channel}"}
        
        logger.info(f"Channel {channel} sync completed: {result.get('success', False)}")
        
        return result
    
    except Exception as e:
        logger.error(f"Channel {channel} sync task failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="execute_campaign")
def execute_campaign_task(campaign_id: int):
    """
    Celery task to execute a campaign.
    
    Args:
        campaign_id: Campaign ID to execute
    
    Returns:
        Execution result dictionary
    """
    db = next(get_db())
    
    try:
        # Initialize agent
        agent = CampaignManagerAgent(db)
        
        # Execute campaign (credentials will be fetched from database if available)
        result = agent.execute_campaign(campaign_id)
        
        logger.info(f"Campaign {campaign_id} execution task completed: {result.get('success', False)}")
        
        return result
    
    except Exception as e:
        logger.error(f"Campaign {campaign_id} execution task failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="execute_scheduled_campaigns")
def execute_scheduled_campaigns_task():
    """
    Celery task to execute all scheduled campaigns that are ready.
    Runs periodically to check for campaigns ready to execute.
    """
    db = next(get_db())
    
    try:
        campaign_service = CampaignService(db)
        
        # Find scheduled campaigns ready to execute
        now = datetime.utcnow()
        scheduled_campaigns = db.query(Campaign).filter(
            Campaign.status == CampaignStatus.SCHEDULED,
            Campaign.schedule <= now
        ).all()
        
        results = []
        agent = CampaignManagerAgent(db)
        
        for campaign in scheduled_campaigns:
            try:
                result = agent.execute_campaign(campaign.campaign_id)
                results.append({
                    "campaign_id": campaign.campaign_id,
                    "success": result.get("success", False)
                })
            except Exception as e:
                logger.error(f"Failed to execute scheduled campaign {campaign.campaign_id}: {e}")
                results.append({
                    "campaign_id": campaign.campaign_id,
                    "success": False,
                    "error": str(e)
                })
        
        logger.info(f"Executed {len(scheduled_campaigns)} scheduled campaigns")
        
        return {
            "success": True,
            "executed": len(scheduled_campaigns),
            "results": results
        }
    
    except Exception as e:
        logger.error(f"Scheduled campaigns task failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="retry_failed_campaigns")
def retry_failed_campaigns_task(max_retries: int = 3):
    """
    Celery task to retry failed campaign executions.
    
    Args:
        max_retries: Maximum number of retry attempts
    """
    db = next(get_db())
    
    try:
        
        # Find failed executions that haven't exceeded max retries
        failed_executions = db.query(CampaignExecution).filter(
            CampaignExecution.status == ExecutionStatus.FAILED
        ).all()
        
        agent = CampaignManagerAgent(db)
        retried = 0
        
        for execution in failed_executions:
            campaign = execution.campaign
            
            # Check if we should retry
            # Count previous executions for this campaign
            previous_failures = db.query(CampaignExecution).filter(
                CampaignExecution.campaign_id == campaign.campaign_id,
                CampaignExecution.status == ExecutionStatus.FAILED
            ).count()
            
            if previous_failures < max_retries:
                try:
                    # Retry execution
                    result = agent.execute_campaign(campaign.campaign_id)
                    if result.get("success"):
                        retried += 1
                except Exception as e:
                    logger.error(f"Retry failed for campaign {campaign.campaign_id}: {e}")
        
        logger.info(f"Retried {retried} failed campaigns")
        
        return {
            "success": True,
            "retried": retried,
            "total_failed": len(failed_executions)
        }
    
    except Exception as e:
        logger.error(f"Retry failed campaigns task failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


# Configure periodic tasks (beat schedule)
celery_app.conf.beat_schedule = {
    "sync-all-channels-hourly": {
        "task": "sync_all_channels",
        "schedule": 3600.0,  # Every hour
        "args": (False,)  # Incremental sync
    },
    "sync-all-channels-daily": {
        "task": "sync_all_channels",
        "schedule": 86400.0,  # Every day
        "args": (True,)  # Full sync
    },
    "execute-scheduled-campaigns": {
        "task": "execute_scheduled_campaigns",
        "schedule": 300.0,  # Every 5 minutes
    },
    "retry-failed-campaigns": {
        "task": "retry_failed_campaigns",
        "schedule": 3600.0,  # Every hour
        "args": (3,)  # Max 3 retries
    },
}

@celery_app.task(name="publish_video", bind=True)
def publish_video(self, video_path: str, metadata: Dict[str, Any]):
    """
    Celery task to upload a video to YouTube using CampaignManagerAgent.
    """
    from core.config import get_settings
    from core.database import SessionLocal, ChannelType
    from agents.campaign_manager import CampaignManagerAgent
    
    settings = get_settings()
    db = SessionLocal()
    filename = os.path.basename(video_path)
    
    try:
        # 1. Update status to UPLOADING (Custom status for UI)
        self.update_state(state='UPLOADING', meta={'filename': filename})
        
        # 2. Check for absolute path to youtube_token.json
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        token_file = os.path.join(project_root, "youtube_token.json")
        
        # 3. Prepare credentials exactly as in the test script
        credentials = {
            ChannelType.YOUTUBE: {
                "api_key": settings.youtube_api_key,
                "channel_id": settings.youtube_api_key  # Fallback
            }
        }
        
        if os.path.exists(token_file):
            credentials[ChannelType.YOUTUBE]["oauth2_credentials"] = token_file
            logger.info(f"Injecting OAuth2 token from: {token_file}")
        else:
            logger.warning(f"OAuth2 token not found at {token_file} - upload will likely fail")

        # 4. Initialize CampaignManagerAgent
        agent = CampaignManagerAgent(db)
        
        # 5. Create a temporary campaign for this manual upload to ensure database tracking
        campaign_config = {
            "title": metadata.get("title", filename),
            "description": metadata.get("description", ""),
            "tags": metadata.get("tags", []),
            "privacy_status": metadata.get("privacy_status", "public"),
            "video_path": video_path
        }
        
        create_result = agent.create_campaign(
            name=f"Manual Upload: {filename}",
            channel=ChannelType.YOUTUBE,
            config=campaign_config
        )
        
        if not create_result.get("success"):
            return {"success": False, "error": f"Failed to create tracking campaign: {create_result.get('error')}"}
            
        campaign_id = create_result["campaign_id"]
        logger.info(f"Created tracking campaign {campaign_id} for {filename}")
        
        # 6. Execute campaign using the agent (handles status updates automatically)
        logger.info(f"Executing campaign {campaign_id} with injection...")
        execution_result = agent.execute_campaign(campaign_id, credentials)
        
        if execution_result.get("success"):
            results = execution_result.get("results", {})
            logger.info(f"Successfully published {filename}. Video ID: {results.get('video_id')}")
            return {
                "success": True,
                "video_id": results.get("video_id"),
                "video_url": results.get("video_url"),
                "campaign_id": campaign_id
            }
        else:
            error_msg = execution_result.get("error", "Unknown execution error")
            logger.error(f"Execution failed for {filename}: {error_msg}")
            return {"success": False, "error": error_msg}
            
    except Exception as e:
        logger.error(f"Publish task failed for {video_path}: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
    finally:
        db.close()
