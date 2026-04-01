from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import os
import json
import logging

from core.config import get_settings

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

def get_token_path():
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(project_root, "meta_token.json")

@router.get("/status")
async def get_meta_status():
    """Check Facebook/Instagram token status."""
    token_file = get_token_path()
    exists = os.path.exists(token_file)
    
    # Simple report based on file existence or .env fallback
    is_valid = exists or (bool(settings.facebook_access_token) and (bool(settings.facebook_page_id) or bool(settings.instagram_business_account_id)))
    
    return {
        "token_exists": exists,
        "is_valid": is_valid,
        "status": "active" if is_valid else "error",
        "has_env_fallback": bool(settings.facebook_access_token)
    }

@router.post("/auth")
async def update_meta_auth(data: Dict[str, Any]):
    """Update Meta (FB/IG) credentials from the UI."""
    access_token = data.get("access_token")
    page_id = data.get("page_id")
    instagram_business_id = data.get("instagram_business_id")
    
    if not access_token:
        raise HTTPException(status_code=400, detail="Access token is required")
        
    token_file = get_token_path()
    token_obj = {
        "facebook_access_token": access_token,
        "facebook_page_id": page_id,
        "instagram_business_account_id": instagram_business_id
    }
    
    try:
        with open(token_file, 'w') as f:
            json.dump(token_obj, f, indent=4)
        return {"success": True, "message": "Meta credentials updated successfully"}
    except Exception as e:
        logger.error(f"Failed to save Meta token: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save credentials: {str(e)}")

@router.delete("/auth")
async def disconnect_meta():
    """Remove Meta credentials."""
    token_file = get_token_path()
    if os.path.exists(token_file):
        os.remove(token_file)
        return {"success": True, "message": "Meta account disconnected"}
    return {"success": False, "message": "No active connection found"}
