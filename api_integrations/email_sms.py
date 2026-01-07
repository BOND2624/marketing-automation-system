"""Email and SMS API integration (SendGrid for email)."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import requests

from api_integrations.base import BaseIntegration

logger = logging.getLogger(__name__)


class EmailSMSIntegration(BaseIntegration):
    """Integration with SendGrid (email) and Twilio (SMS)."""
    
    def __init__(self, credentials: Dict[str, Any]):
        """
        Initialize Email/SMS integration.
        
        Args:
            credentials: Should contain 'sendgrid_api_key' for email,
                        and optionally 'twilio_account_sid' and 'twilio_auth_token' for SMS
        """
        super().__init__(credentials, rate_limit_calls=100, rate_limit_period=86400)  # 100/day for SendGrid free tier
        self.sendgrid_api_key = credentials.get("sendgrid_api_key")
        self.twilio_account_sid = credentials.get("twilio_account_sid")
        self.twilio_auth_token = credentials.get("twilio_auth_token")
        
        if not self.sendgrid_api_key:
            raise ValueError("SendGrid API key is required for email functionality")
        
        try:
            self.sendgrid_client = SendGridAPIClient(self.sendgrid_api_key)
        except Exception as e:
            logger.error(f"Failed to initialize SendGrid client: {e}")
            self.sendgrid_client = None
    
    def _make_twilio_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to Twilio API."""
        if not self.twilio_account_sid or not self.twilio_auth_token:
            raise ValueError("Twilio credentials are required")
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/{endpoint}"
        auth = (self.twilio_account_sid, self.twilio_auth_token)
        
        try:
            self._handle_rate_limit()
            response = requests.get(url, auth=auth, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Twilio API request failed: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test Email/SMS API connections."""
        email_ok = False
        sms_ok = False
        
        # Test SendGrid
        if self.sendgrid_client:
            try:
                # Test by checking API key validity (get user info)
                response = self.sendgrid_client.client.user.get()
                if response.status_code == 200:
                    email_ok = True
            except Exception as e:
                logger.error(f"SendGrid connection test failed: {e}")
        
        # Test Twilio (if credentials provided)
        if self.twilio_account_sid and self.twilio_auth_token:
            try:
                self._make_twilio_request("Messages.json", params={"PageSize": 1})
                sms_ok = True
            except Exception as e:
                logger.warning(f"Twilio connection test failed: {e}")
        else:
            sms_ok = True  # SMS not configured is OK
        
        return email_ok or sms_ok
    
    def sync_email_stats(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Sync email statistics from SendGrid.
        
        Args:
            start_date: Start date for stats (default: 7 days ago)
            end_date: End date for stats (default: now)
        """
        if not self.sendgrid_client:
            return {"error": "SendGrid client not initialized"}
        
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=7)
        if not end_date:
            end_date = datetime.utcnow()
        
        try:
            # SendGrid Stats API
            params = {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "aggregated_by": "day"
            }
            
            response = self.sendgrid_client.client.stats.get(query_params=params)
            
            if response.status_code != 200:
                return {"error": f"SendGrid API error: {response.status_code}"}
            
            stats_data = response.body
            
            # Aggregate stats
            total_sends = 0
            total_opens = 0
            total_clicks = 0
            total_bounces = 0
            total_delivered = 0
            
            for stat in stats_data:
                total_sends += stat.get("stats", [{}])[0].get("metrics", {}).get("delivered", 0) + \
                              stat.get("stats", [{}])[0].get("metrics", {}).get("bounces", 0)
                total_delivered += stat.get("stats", [{}])[0].get("metrics", {}).get("delivered", 0)
                total_bounces += stat.get("stats", [{}])[0].get("metrics", {}).get("bounces", 0)
                
                opens = stat.get("stats", [{}])[0].get("metrics", {}).get("opens", 0)
                clicks = stat.get("stats", [{}])[0].get("metrics", {}).get("clicks", 0)
                
                total_opens += opens
                total_clicks += clicks
            
            return {
                "total_sends": total_sends,
                "total_delivered": total_delivered,
                "total_bounces": total_bounces,
                "total_opens": total_opens,
                "total_clicks": total_clicks,
                "open_rate": (total_opens / total_delivered * 100) if total_delivered > 0 else 0,
                "click_rate": (total_clicks / total_delivered * 100) if total_delivered > 0 else 0,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "synced_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return self._handle_error(e, "sync_email_stats")
    
    def sync_email_events(self, limit: int = 100) -> Dict[str, Any]:
        """
        Sync email events (opens, clicks, bounces, etc.).
        
        Args:
            limit: Maximum number of events to fetch
        """
        if not self.sendgrid_client:
            return {"error": "SendGrid client not initialized"}
        
        try:
            # Note: SendGrid Events API requires webhook setup for real-time events
            # For now, we'll get recent activity from messages
            # In production, you'd use the Events API with webhooks
            
            params = {
                "limit": min(limit, 1000),
                "query": "last_event_time BETWEEN TIMESTAMP '{}' AND TIMESTAMP '{}'".format(
                    (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d"),
                    datetime.utcnow().strftime("%Y-%m-%d")
                )
            }
            
            # This is a simplified version - full implementation would use Events API
            events = []
            
            return {
                "events": events,
                "total_events": len(events),
                "note": "Full event sync requires SendGrid Events API webhook setup",
                "synced_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return self._handle_error(e, "sync_email_events")
    
    def sync_sms_stats(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Sync SMS statistics from Twilio.
        
        Args:
            start_date: Start date for stats
            end_date: End date for stats
        """
        if not self.twilio_account_sid or not self.twilio_auth_token:
            return {"error": "Twilio credentials not configured", "note": "SMS sync requires Twilio setup"}
        
        try:
            params = {}
            if start_date:
                params["DateSent>"] = start_date.strftime("%Y-%m-%d")
            if end_date:
                params["DateSent<"] = end_date.strftime("%Y-%m-%d")
            
            response = self._make_twilio_request("Messages.json", params=params)
            
            messages = response.get("messages", [])
            
            total_sent = len(messages)
            total_delivered = sum(1 for msg in messages if msg.get("status") == "delivered")
            total_failed = sum(1 for msg in messages if msg.get("status") in ["failed", "undelivered"])
            
            return {
                "total_sent": total_sent,
                "total_delivered": total_delivered,
                "total_failed": total_failed,
                "delivery_rate": (total_delivered / total_sent * 100) if total_sent > 0 else 0,
                "period": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                },
                "synced_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return self._handle_error(e, "sync_sms_stats")
    
    def sync_data(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Sync all Email/SMS data.
        
        Args:
            since: Only sync data since this datetime
        
        Returns:
            Dictionary with all synced data
        """
        result = {
            "channel": "email_sms",
            "email_stats": {},
            "email_events": {},
            "sms_stats": {},
            "success": True,
            "errors": [],
            "synced_at": datetime.utcnow().isoformat()
        }
        
        # Sync email stats
        try:
            email_stats = self.sync_email_stats(since)
            if "error" in email_stats:
                result["success"] = False
                result["errors"].append(email_stats["error"])
            else:
                result["email_stats"] = email_stats
        except Exception as e:
            result["success"] = False
            result["errors"].append(str(e))
        
        # Sync email events
        try:
            email_events = self.sync_email_events()
            if "error" in email_events:
                result["errors"].append(email_events["error"])
            else:
                result["email_events"] = email_events
        except Exception as e:
            result["errors"].append(f"Email events error: {str(e)}")
        
        # Sync SMS stats (if configured)
        if self.twilio_account_sid:
            try:
                sms_stats = self.sync_sms_stats(since)
                if "error" not in sms_stats:
                    result["sms_stats"] = sms_stats
            except Exception as e:
                result["errors"].append(f"SMS stats error: {str(e)}")
        
        return result

