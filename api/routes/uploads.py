from fastapi import APIRouter, UploadFile, File, HTTPException
import os
from typing import List, Dict, Any
from services.scheduler import celery_app, publish_video
from api.routes.youtube import get_youtube_status

router = APIRouter()

UPLOAD_DIR = "/Users/pranavshinde/Developer/marketing-automation-system/uploads"

@router.get("/")
async def list_uploads():
    """List .mp4 and .mov files in the uploads folder."""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        
    files = []
    for filename in os.listdir(UPLOAD_DIR):
        if filename.endswith((".mp4", ".mov")):
            path = os.path.join(UPLOAD_DIR, filename)
            stats = os.stat(path)
            files.append({
                "filename": filename,
                "size_mb": round(stats.st_size / (1024 * 1024), 2),
                "path": path,
                "created_at": stats.st_mtime
            })
    return files

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    """Upload a new video file using streaming."""
    if not file.filename.endswith((".mp4", ".mov")):
        raise HTTPException(status_code=400, detail="Only .mp4 and .mov format allowed")
        
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # Streaming write to handle large files
    try:
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024): # 1MB chunks
                buffer.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
        
    return {"filename": file.filename, "path": file_path, "success": True}

@router.post("/{filename}/publish")
async def publish_video_endpoint(filename: str, metadata: Dict[str, Any]):
    """Enqueue a YouTube publishing task."""
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found in uploads")
        
    # Check YouTube Auth status
    yt_status = await get_youtube_status()
    if not yt_status.get("is_valid"):
        raise HTTPException(status_code=401, detail="YouTube account not connected or session expired")
        
    # Trigger Celery Task
    task = publish_video.delay(file_path, metadata)
    
    return {
        "success": True,
        "task_id": task.id,
        "message": "Publishing task enqueued"
    }

@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """Check the status of a background task."""
    task_result = celery_app.AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
    }
    
    if task_result.status == "SUCCESS":
        response["result"] = task_result.result
    elif task_result.status == "FAILURE":
        response["error"] = str(task_result.result)
    elif task_result.status == "UPLOADING":
        response["meta"] = task_result.info
        
    return response
