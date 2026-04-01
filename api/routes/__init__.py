from fastapi import APIRouter
from api.routes import campaigns, youtube, uploads

router = APIRouter()
router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
router.include_router(youtube.router, prefix="/youtube", tags=["youtube"])
router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
