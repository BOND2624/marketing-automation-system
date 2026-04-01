import os
import sys
import json
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_integrations.youtube import YouTubeIntegration
from core.config import get_settings

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("api_integrations.youtube")
logger.setLevel(logging.INFO)

def debug_analytics():
    print("="*60)
    print("🔍 YouTube Analytics Debugger (Authenticated)")
    print("="*60)
    
    # 1. Initialize Integration
    settings = get_settings()
    token_file = "youtube_token.json"
    
    creds = {"api_key": settings.youtube_api_key}
    if os.path.exists(token_file):
        creds["oauth2_credentials"] = token_file
    
    integration = YouTubeIntegration(creds)
    if integration.youtube_oauth:
        client = integration.youtube_oauth
        print("✅ OAuth Client Initialized")
    else:
        client = integration.youtube
        print("❌ OAuth Client FAILED - falling back to Public Key")
        
    print(f"👉 Using Client type: {'OAuth' if client == integration.youtube_oauth else 'Public Key'}")
    
    # 2. Get Channel Info (via mine=True)
    try:
        if integration.youtube_oauth:
            print("\n📡 Fetching Channel (mine=True)...")
            request = integration.youtube_oauth.channels().list(
                part="contentDetails,statistics,snippet",
                mine=True
            )
        else:
            channel_id = settings.youtube_channel_id or "UCsMU3PgG7ku7Y6M5tWnahDQ"
            print(f"\n📡 Fetching Channel (id={channel_id})...")
            request = client.channels().list(
                part="contentDetails,statistics,snippet",
                id=channel_id
            )
            
        response = request.execute()
        items = response.get("items", [])
        
        if not items:
            print("❌ No channel found.")
            return

        channel = items[0]
        title = channel["snippet"]["title"]
        stats = channel["statistics"]
        uploads_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]
        
        print(f"✅ Channel: {title}")
        print(f"📊 Stats: {json.dumps(stats, indent=2)}")
        print(f"📺 Uploads Playlist: {uploads_id}")
        
        # 3. Fetch Playlist Items
        print(f"\n📑 Fetching Playlist Items from: {uploads_id}...")
        playlist_request = client.playlistItems().list(
            part="snippet,contentDetails,status",
            playlistId=uploads_id,
            maxResults=50
        )
        playlist_response = playlist_request.execute()
        
        playlist_items = playlist_response.get("items", [])
        print(f"✅ Found {len(playlist_items)} items in playlist.")
        
        video_ids = []
        for i, item in enumerate(playlist_items):
            vid_title = item["snippet"]["title"]
            vid_id = item["contentDetails"]["videoId"]
            vid_status = item.get("status", {}).get("privacyStatus", "unknown")
            print(f"  {i+1}. [{vid_status}] {vid_title} ({vid_id})")
            video_ids.append(vid_id)
            
        # 4. Fetch Video Details
        if video_ids:
            print(f"\n🎥 Fetching details for {len(video_ids)} videos...")
            videos_request = client.videos().list(
                part="statistics,snippet,status",
                id=",".join(video_ids)
            )
            videos_response = videos_request.execute()
            video_items = videos_response.get("items", [])
            
            print(f"✅ API returned details for {len(video_items)} videos.")
            
            # Match them up
            returned_ids = [v["id"] for v in video_items]
            missing_ids = set(video_ids) - set(returned_ids)
            
            for v in video_items:
                print(f"  - OK: {v['snippet']['title']} (Starts: {v['statistics'].get('viewCount', 'N/A')})")
                
            if missing_ids:
                print(f"\n❌ Missing details for IDs: {missing_ids}")
                print("   (These are likely deleted or private videos that even the owner can't query via this endpoint?)")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_analytics()
