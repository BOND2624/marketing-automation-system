from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from core.database import get_db, Campaign, CampaignExecution
from core.models import CampaignCreate, Campaign as CampaignSchema
from agents.campaign_manager import CampaignManagerAgent
from sqlalchemy import desc

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[CampaignSchema])
async def list_campaigns(db: Session = Depends(get_db)):
    """List all campaigns."""
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    return campaigns

@router.post("/", response_model=CampaignSchema)
async def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    """Create a new campaign."""
    agent = CampaignManagerAgent(db)
    result = agent.create_campaign(
        name=campaign.name,
        channel=campaign.channel,
        config=campaign.config,
        schedule=campaign.schedule
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    # Fetch the created campaign
    db_campaign = db.query(Campaign).filter(Campaign.campaign_id == result["campaign_id"]).first()
    return db_campaign

@router.post("/{campaign_id}/execute")
async def execute_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Trigger campaign execution."""
    agent = CampaignManagerAgent(db)
    result = agent.execute_campaign(campaign_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result
@router.get("/executions")
async def list_executions(limit: int = 10, db: Session = Depends(get_db)):
    """List recent campaign executions."""
    executions = db.query(CampaignExecution).order_by(
        desc(CampaignExecution.created_at)
    ).limit(limit).all()
    
    # Enrich with campaign names
    results = []
    for ex in executions:
        results.append({
            "id": ex.execution_id,
            "campaign_name": ex.campaign.name,
            "status": ex.status.value,
            "started_at": ex.started_at,
            "completed_at": ex.completed_at,
            "created_at": ex.created_at,
            "error_message": ex.error_message,
            "results": ex.results
        })
    return results
