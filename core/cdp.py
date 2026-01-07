"""Customer Data Platform (CDP) core logic."""

from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_

from core.database import Customer, CustomerEvent, ChannelType


class CDPService:
    """Service for managing unified customer data."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_customer(
        self,
        email: str,
        phone: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> Customer:
        """Get existing customer or create a new one."""
        customer = self.db.query(Customer).filter(Customer.email == email).first()
        
        if not customer:
            customer = Customer(
                email=email,
                phone=phone,
                attributes=attributes or {}
            )
            self.db.add(customer)
            self.db.commit()
            self.db.refresh(customer)
        else:
            # Update existing customer
            updated = False
            if phone and customer.phone != phone:
                customer.phone = phone
                updated = True
            if attributes:
                # Merge attributes
                customer.attributes = {**customer.attributes, **attributes}
                updated = True
            if updated:
                customer.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(customer)
        
        return customer
    
    def update_customer_attributes(
        self,
        customer_id: int,
        attributes: Dict[str, Any],
        merge: bool = True
    ) -> Optional[Customer]:
        """Update customer attributes."""
        customer = self.db.query(Customer).filter(Customer.customer_id == customer_id).first()
        
        if not customer:
            return None
        
        if merge:
            customer.attributes = {**customer.attributes, **attributes}
        else:
            customer.attributes = attributes
        
        customer.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(customer)
        
        return customer
    
    def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """Get customer by email."""
        return self.db.query(Customer).filter(Customer.email == email).first()
    
    def get_customer_by_id(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID."""
        return self.db.query(Customer).filter(Customer.customer_id == customer_id).first()
    
    def search_customers(
        self,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Customer]:
        """Search customers by email or phone."""
        query = self.db.query(Customer)
        
        if email:
            query = query.filter(Customer.email.ilike(f"%{email}%"))
        if phone:
            query = query.filter(Customer.phone.ilike(f"%{phone}%"))
        
        return query.offset(offset).limit(limit).all()
    
    def unify_customer_data(
        self,
        customer_id: int,
        channel: ChannelType,
        channel_data: Dict[str, Any]
    ) -> Optional[Customer]:
        """
        Unify customer data from different channels.
        Merges channel-specific data into customer attributes.
        """
        customer = self.get_customer_by_id(customer_id)
        if not customer:
            return None
        
        # Merge channel-specific data
        channel_key = f"{channel.value}_data"
        if channel_key not in customer.attributes:
            customer.attributes[channel_key] = {}
        
        customer.attributes[channel_key] = {
            **customer.attributes[channel_key],
            **channel_data,
            "last_synced": datetime.utcnow().isoformat()
        }
        
        customer.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(customer)
        
        return customer
    
    def add_customer_event(
        self,
        customer_id: int,
        event_type: str,
        channel: ChannelType,
        data: Optional[Dict[str, Any]] = None
    ) -> CustomerEvent:
        """Add a customer event."""
        event = CustomerEvent(
            customer_id=customer_id,
            event_type=event_type,
            channel=channel,
            data=data or {},
            timestamp=datetime.utcnow()
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        return event
    
    def get_customer_events(
        self,
        customer_id: int,
        channel: Optional[ChannelType] = None,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[CustomerEvent]:
        """Get customer events with optional filtering."""
        query = self.db.query(CustomerEvent).filter(
            CustomerEvent.customer_id == customer_id
        )
        
        if channel:
            query = query.filter(CustomerEvent.channel == channel)
        if event_type:
            query = query.filter(CustomerEvent.event_type == event_type)
        
        return query.order_by(CustomerEvent.timestamp.desc()).limit(limit).all()
    
    def get_unified_customer_profile(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get unified customer profile with all channel data and events."""
        customer = self.get_customer_by_id(customer_id)
        if not customer:
            return None
        
        # Get recent events
        events = self.get_customer_events(customer_id, limit=50)
        
        # Build unified profile
        profile = {
            "customer_id": customer.customer_id,
            "email": customer.email,
            "phone": customer.phone,
            "attributes": customer.attributes,
            "channels": {},
            "recent_events": [
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "channel": event.channel.value,
                    "timestamp": event.timestamp.isoformat(),
                    "data": event.data
                }
                for event in events
            ],
            "created_at": customer.created_at.isoformat(),
            "updated_at": customer.updated_at.isoformat()
        }
        
        # Extract channel-specific data from attributes
        for key, value in customer.attributes.items():
            if key.endswith("_data") and isinstance(value, dict):
                channel_name = key.replace("_data", "")
                profile["channels"][channel_name] = value
        
        return profile

