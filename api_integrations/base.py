"""Base class for API integrations with common functionality."""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, max_calls: int, period_seconds: int):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed
            period_seconds: Time period in seconds
        """
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self.calls = []  # List of timestamps
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()
        
        # Remove old calls outside the time window
        self.calls = [call_time for call_time in self.calls 
                     if now - call_time < self.period_seconds]
        
        # If at limit, wait until oldest call expires
        if len(self.calls) >= self.max_calls:
            sleep_time = self.period_seconds - (now - self.calls[0]) + 1
            if sleep_time > 0:
                logger.info(f"Rate limit reached. Waiting {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                # Clean up again after sleep
                now = time.time()
                self.calls = [call_time for call_time in self.calls 
                             if now - call_time < self.period_seconds]
        
        # Record this call
        self.calls.append(time.time())


class BaseIntegration(ABC):
    """Base class for all marketing channel integrations."""
    
    def __init__(self, credentials: Dict[str, Any], rate_limit_calls: int = 100, rate_limit_period: int = 60):
        """
        Initialize base integration.
        
        Args:
            credentials: Channel-specific API credentials
            rate_limit_calls: Maximum API calls per period
            rate_limit_period: Time period in seconds for rate limiting
        """
        self.credentials = credentials
        self.rate_limiter = RateLimiter(rate_limit_calls, rate_limit_period)
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    def _handle_rate_limit(self):
        """Handle rate limiting before API calls."""
        self.rate_limiter.wait_if_needed()
    
    def _handle_pagination(
        self,
        api_call: Callable,
        page_param: str = "page",
        items_key: Optional[str] = None,
        max_pages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Handle paginated API responses.
        
        Args:
            api_call: Function that makes the API call and returns response
            page_param: Name of the page parameter
            items_key: Key in response that contains the items list (if None, response is list)
            max_pages: Maximum number of pages to fetch (None for all)
        
        Returns:
            Combined list of all items across pages
        """
        all_items = []
        page = 1
        
        while True:
            if max_pages and page > max_pages:
                break
            
            self._handle_rate_limit()
            
            try:
                response = api_call(page=page)
                
                # Handle different response formats
                if items_key:
                    items = response.get(items_key, [])
                    has_more = response.get("has_more", False) or response.get("next_page", None) is not None
                else:
                    items = response if isinstance(response, list) else []
                    has_more = len(items) > 0
                
                if not items:
                    break
                
                all_items.extend(items)
                
                # Check if there's more data
                if not has_more or len(items) == 0:
                    break
                
                page += 1
                
            except Exception as e:
                self.logger.error(f"Error fetching page {page}: {e}")
                break
        
        return all_items
    
    def _handle_error(self, error: Exception, context: str = ""):
        """
        Handle API errors with logging.
        
        Args:
            error: The exception that occurred
            context: Additional context about the error
        """
        error_msg = f"API Error {context}: {str(error)}"
        self.logger.error(error_msg, exc_info=True)
        return {
            "error": str(error),
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _retry_request(
        self,
        func: Callable,
        max_retries: int = 3,
        retry_delay: int = 5,
        backoff_factor: int = 2
    ) -> Any:
        """
        Retry a function call with exponential backoff.
        
        Args:
            func: Function to retry
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (seconds)
            backoff_factor: Multiplier for delay on each retry
        
        Returns:
            Result of the function call
        """
        delay = retry_delay
        
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                self.logger.warning(
                    f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds..."
                )
                time.sleep(delay)
                delay *= backoff_factor
        
        return None
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test the API connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        pass
    
    @abstractmethod
    def sync_data(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Sync data from the channel.
        
        Args:
            since: Only sync data since this datetime (None for full sync)
        
        Returns:
            Dictionary with sync results and data
        """
        pass
    
    def get_channel_name(self) -> str:
        """Get the channel name."""
        return self.__class__.__name__.lower().replace("integration", "")

