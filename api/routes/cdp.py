from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from core.database import get_db, CustomerEvent

router = APIRouter()

@router.get("/activity")
async def get_cdp_activity(db: Session = Depends(get_db)):
    """Fetch the most recent customer events from the CDP."""
    events = db.query(CustomerEvent).order_by(desc(CustomerEvent.timestamp)).limit(20).all()
    
    return [
        {
            "id": e.id,
            "customer_id": e.customer_id,
            "event_type": e.event_type,
            "channel": e.channel.value if e.channel else "unknown",
            "timestamp": e.timestamp.isoformat(),
            "details": e.details
        }
        for e in events
    ]
