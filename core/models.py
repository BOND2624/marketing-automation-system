"""Pydantic schemas for API validation."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, Field
from core.database import CampaignStatus, ExecutionStatus, ChannelType


# Customer Schemas
class CustomerBase(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None


class Customer(CustomerBase):
    customer_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Campaign Schemas
class CampaignBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    channel: ChannelType
    schedule: Optional[datetime] = None
    config: Dict[str, Any] = Field(default_factory=dict)


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    channel: Optional[ChannelType] = None
    status: Optional[CampaignStatus] = None
    schedule: Optional[datetime] = None
    config: Optional[Dict[str, Any]] = None


class Campaign(CampaignBase):
    campaign_id: int
    status: CampaignStatus
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Campaign Execution Schemas
class CampaignExecutionBase(BaseModel):
    campaign_id: int
    status: ExecutionStatus = ExecutionStatus.PENDING


class CampaignExecutionCreate(CampaignExecutionBase):
    pass


class CampaignExecution(CampaignExecutionBase):
    execution_id: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Customer Event Schemas
class CustomerEventBase(BaseModel):
    customer_id: int
    event_type: str = Field(..., min_length=1, max_length=100)
    channel: ChannelType
    data: Dict[str, Any] = Field(default_factory=dict)


class CustomerEventCreate(CustomerEventBase):
    timestamp: Optional[datetime] = None


class CustomerEvent(CustomerEventBase):
    event_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


# Channel Credential Schemas
class ChannelCredentialBase(BaseModel):
    channel_type: ChannelType
    encrypted_credentials: str


class ChannelCredentialCreate(ChannelCredentialBase):
    pass


class ChannelCredentialUpdate(BaseModel):
    encrypted_credentials: Optional[str] = None
    is_active: Optional[bool] = None


class ChannelCredential(ChannelCredentialBase):
    credential_id: int
    user_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Analytics Snapshot Schemas
class AnalyticsSnapshotBase(BaseModel):
    campaign_id: int
    metrics: Dict[str, Any] = Field(default_factory=dict)


class AnalyticsSnapshotCreate(AnalyticsSnapshotBase):
    timestamp: Optional[datetime] = None


class AnalyticsSnapshot(AnalyticsSnapshotBase):
    snapshot_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


# Sync Data Schemas
class SyncDataRequest(BaseModel):
    channel: ChannelType
    force_full_sync: bool = False


class SyncResult(BaseModel):
    channel: ChannelType
    success: bool
    records_synced: int
    errors: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

