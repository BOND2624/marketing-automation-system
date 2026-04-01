"""Database models and session management."""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, 
    Text, JSON, ForeignKey, Enum as SQLEnum, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import enum

from core.config import get_settings

Base = declarative_base()
settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CampaignStatus(str, enum.Enum):
    """Campaign status enumeration."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionStatus(str, enum.Enum):
    """Execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ChannelType(str, enum.Enum):
    """Marketing channel types."""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    EMAIL = "email"
    SMS = "sms"


class Customer(Base):
    """Customer model for CDP."""
    __tablename__ = "customers"
    
    customer_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), index=True, nullable=True)
    attributes = Column(JSON, default={})  # Flexible JSONB-like structure for additional data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    events = relationship("CustomerEvent", back_populates="customer", cascade="all, delete-orphan")


class Campaign(Base):
    """Campaign model."""
    __tablename__ = "campaigns"
    
    campaign_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    channel = Column(SQLEnum(ChannelType), nullable=False, index=True)
    status = Column(SQLEnum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False, index=True)
    schedule = Column(DateTime, nullable=True)  # Scheduled execution time
    config = Column(JSON, default={})  # Campaign configuration (content, targeting, etc.)
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    executions = relationship("CampaignExecution", back_populates="campaign", cascade="all, delete-orphan")
    analytics_snapshots = relationship("AnalyticsSnapshot", back_populates="campaign", cascade="all, delete-orphan")


class CampaignExecution(Base):
    """Campaign execution tracking."""
    __tablename__ = "campaign_executions"
    
    execution_id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"), nullable=False, index=True)
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    results = Column(JSON, default={})  # Execution results (successful sends, errors, etc.)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="executions")


class CustomerEvent(Base):
    """Customer events for tracking engagement across channels."""
    __tablename__ = "customer_events"
    
    event_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)  # open, click, view, subscribe, etc.
    channel = Column(SQLEnum(ChannelType), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    data = Column(JSON, default={})  # Additional event data
    
    # Relationships
    customer = relationship("Customer", back_populates="events")


class ChannelCredential(Base):
    """Encrypted storage for channel API credentials."""
    __tablename__ = "channel_credentials"
    
    credential_id = Column(Integer, primary_key=True, index=True)
    channel_type = Column(SQLEnum(ChannelType), nullable=False, index=True)
    encrypted_credentials = Column(Text, nullable=False)  # Encrypted JSON string
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class AnalyticsSnapshot(Base):
    """Analytics snapshots for campaigns."""
    __tablename__ = "analytics_snapshots"
    
    snapshot_id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"), nullable=False, index=True)
    metrics = Column(JSON, default={})  # Aggregated metrics (views, clicks, conversions, etc.)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="analytics_snapshots")


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="viewer", nullable=False)  # admin, manager, viewer
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

