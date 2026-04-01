import os
import sys
import json
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal, AnalyticsSnapshot, Campaign, ChannelType, CampaignStatus

def simulate_snapshots():
    db = SessionLocal()
    try:
        # 1. Ensure Global YouTube Stats campaign exists
        system_campaign_name = "Global Youtube Stats" # Note: Case sensitivity in previous implementation was capitalized
        # Actually my implementation used capitalized: "Global Youtube Stats" or "Global YouTube Stats"?
        # Let's check the code: system_campaign_name = "Global YouTube Stats"
        system_campaign_name = "Global YouTube Stats"
        
        campaign = db.query(Campaign).filter(
            Campaign.name == system_campaign_name,
            Campaign.channel == ChannelType.YOUTUBE
        ).first()

        if not campaign:
            campaign = Campaign(
                name=system_campaign_name,
                channel=ChannelType.YOUTUBE,
                status=CampaignStatus.COMPLETED,
                config={"is_system": True}
            )
            db.add(campaign)
            db.commit()
            db.refresh(campaign)

        # 2. Create snapshots for the last 7 days
        base_subs = 12500
        base_views = 450000
        
        for i in range(10, -1, -1):
            timestamp = datetime.utcnow() - timedelta(days=i)
            # Add some growth
            subs = base_subs + (10 - i) * 120
            views = base_views + (10 - i) * 5400
            
            metrics = {
                "subscriber_count": subs,
                "video_count": 42,
                "view_count": views,
                "channel_name": "Test Marketing Channel"
            }
            
            snapshot = AnalyticsSnapshot(
                campaign_id=campaign.campaign_id,
                metrics=metrics,
                timestamp=timestamp
            )
            db.add(snapshot)
        
        db.commit()
        print(f"Successfully created 11 snapshots for {system_campaign_name}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    simulate_snapshots()
