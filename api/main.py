from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import os

from core.database import get_db
from api.routes import campaigns, youtube, uploads
from api.routes.youtube import get_youtube_status

app = FastAPI(title="Unified Marketing Automation System API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(youtube.router, prefix="/api/youtube", tags=["youtube"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["uploads"])

@app.get("/api/status")
async def get_status(db: Session = Depends(get_db)):
    """Check system health status."""
    health = {
        "database": "error",
        "celery": "active",
        "youtube": False,
        "system": "online"
    }
    
    try:
        # Check DB
        db.execute(text("SELECT 1"))
        health["database"] = "active"
    except Exception as e:
        print(f"HEALTH_CHECK_DB_ERROR: {e}")
        
    try:
        # Check YouTube
        yt_status = await get_youtube_status()
        health["youtube"] = yt_status.get("is_valid", False)
    except Exception as e:
        print(f"HEALTH_CHECK_YT_ERROR: {e}")
        
    return health

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
