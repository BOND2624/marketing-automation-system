import os
import logging
from pyngrok import ngrok
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class NgrokService:
    """Service to manage ngrok tunnels for local development."""
    
    _instance = None
    _public_url = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NgrokService, cls).__new__(cls)
        return cls._instance
    
    def start_tunnel(self, port: int = 8000) -> str:
        """
        Start an ngrok tunnel to the specified port.
        Returns the public URL.
        """
        if self._public_url:
            return self._public_url
        
        try:
            # Check for ngrok auth token in environment
            auth_token = os.getenv("NGROK_AUTH_TOKEN")
            if auth_token:
                ngrok.set_auth_token(auth_token)
            
            # Start tunnel
            tunnel = ngrok.connect(port)
            self._public_url = tunnel.public_url
            logger.info(f"Ngrok tunnel started: {self._public_url} -> http://localhost:{port}")
            return self._public_url
        except Exception as e:
            try:
                # If tunnel already exists, try to fetch its URL
                tunnels = ngrok.get_tunnels()
                for t in tunnels:
                    # Depending on pyngrok version, addr might be in different formats
                    # Usually it's 'http://localhost:8000' or similar
                    if str(port) in t.config.get('addr', ''):
                        self._public_url = t.public_url
                        print(f"🚀 Ngrok tunnel recovered from existing session: {self._public_url}")
                        return self._public_url
            except:
                pass
            logger.error(f"Failed to start ngrok tunnel: {e}")
            return ""
            
    def stop_tunnel(self):
        """Stop all active ngrok tunnels."""
        try:
            ngrok.kill()
            self._public_url = None
            logger.info("Ngrok tunnels stopped")
        except Exception as e:
            logger.error(f"Failed to stop ngrok tunnels: {e}")

    @property
    def public_url(self) -> str:
        """
        Get the current public URL from any active tunnel provider.
        Priority: 1. Ngrok Local API (Standard) 2. Pyngrok 3. Localtunnel Log
        """
        # 1. Check Ngrok Local API (works even if started via CLI/nohup)
        try:
            import requests
            response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=1)
            if response.status_code == 200:
                data = response.json()
                if data.get("tunnels"):
                    self._public_url = data["tunnels"][0]["public_url"]
                    return self._public_url
        except:
            pass

        # 2. Check Pyngrok instance
        if self._public_url:
            return self._public_url
            
        # 3. Fallback to localtunnel log
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            lt_log = os.path.join(project_root, "lt.log")
            if os.path.exists(lt_log):
                with open(lt_log, 'r') as f:
                    content = f.read()
                    if "your url is:" in content:
                        url = content.split("your url is:")[1].strip()
                        return url
        except:
            pass
            
        return ""

# Global instance
ngrok_service = NgrokService()
