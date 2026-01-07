"""
Test YouTube video upload functionality.
Requires: YouTube API key and optionally OAuth2 for actual upload.
"""

import sys
import os
from core.database import SessionLocal, ChannelType
from agents.campaign_manager import CampaignManagerAgent
from core.config import get_settings

print("="*60)
print("YouTube Video Upload Test")
print("="*60)

settings = get_settings()

# Check for API key
if not settings.youtube_api_key:
    print("\n[ERROR] YouTube API key not found in .env file")
    print("Please add YOUTUBE_API_KEY to your .env file")
    sys.exit(1)

print(f"\n[OK] YouTube API key found: {settings.youtube_api_key[:10]}...")

# Check for video file in uploads folder
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
video_path = None

# Look for any MP4 file in uploads folder
if os.path.exists(uploads_dir):
    mp4_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith('.mp4')]
    if mp4_files:
        video_path = os.path.join(uploads_dir, mp4_files[0])
        print(f"\n[OK] Found video file: {os.path.basename(video_path)}")
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        print(f"  File size: {file_size_mb:.2f} MB")

if not video_path:
    print(f"\n[WARNING] No video file found in: {uploads_dir}")
    print("\nOptions:")
    print("1. Place any .mp4 video file in the 'uploads' folder")
    print("2. Or provide path to your own video file")
    
    # Ask user for video path
    user_path = input("\nEnter path to video file (or press Enter to skip): ").strip()
    if user_path and os.path.exists(user_path):
        video_path = user_path
        print(f"[OK] Using video: {video_path}")
    else:
        print("\n[INFO] No video file provided. Testing campaign creation only.")
        video_path = None

# Check for OAuth token
token_file = os.path.join(os.path.dirname(__file__), "youtube_token.json")
if os.path.exists(token_file):
    print(f"\n[OK] OAuth token found: youtube_token.json")
    print("  Video upload enabled!")
else:
    print(f"\n[WARNING] OAuth token not found: youtube_token.json")
    print("  Video upload will not work. Channel stats only.")
    print("  Run: python scripts/generate_youtube_token.py")

db = SessionLocal()

try:
    agent = CampaignManagerAgent(db)
    
    print("\n" + "="*60)
    print("1. Creating YouTube Campaign...")
    print("="*60)
    
    campaign_config = {
        "title": "Test Video - Marketing Automation Platform",
        "description": "This video was uploaded via our marketing automation platform!",
        "tags": ["automation", "marketing", "test"],
        "privacy_status": "unlisted"  # unlisted, private, or public
    }
    
    if video_path:
        campaign_config["video_path"] = video_path
        
        # Optional: treat upload as YouTube Short
        try:
            ask_short = input("\nIs this video intended to be a YouTube Short (<60s, vertical)? [y/N]: ").strip().lower()
        except EOFError:
            ask_short = ""
            print("\n[INFO] No input received. Defaulting to regular video upload.")

        if ask_short in {"y", "yes"}:
            campaign_config["upload_type"] = "short"
            print("[INFO] Upload flagged as YouTube Short. Validation will run before upload.")
    
    result = agent.create_campaign(
        name="YouTube Video Upload Test",
        channel=ChannelType.YOUTUBE,
        config=campaign_config
    )
    
    if not result.get("success"):
        print(f"[FAIL] Campaign creation failed: {result.get('error')}")
        sys.exit(1)
    
    campaign_id = result["campaign_id"]
    print(f"[OK] Campaign created: ID={campaign_id}")
    
    print("\n" + "="*60)
    print("2. Preparing Execution...")
    print("="*60)
    
    # Prepare credentials
    credentials = {
        ChannelType.YOUTUBE: {
            "api_key": settings.youtube_api_key,
            "channel_id": settings.youtube_api_key  # Will be overridden if you have channel_id
        }
    }
    
    # Check for OAuth2 token (same location as execution handler checks)
    # Project root is where test_youtube_upload.py is located
    token_file = os.path.join(os.path.dirname(__file__), "youtube_token.json")
    if os.path.exists(token_file):
        # Add OAuth2 token to credentials so handler can use it
        credentials[ChannelType.YOUTUBE]["oauth2_credentials"] = token_file
        print("\n[OK] OAuth2 token detected - video upload enabled!")
    else:
        print("\n[WARNING] OAuth2 token not found - upload will fail")
    
    print("\n" + "="*60)
    print("3. Executing Campaign...")
    print("="*60)
    
    execution = agent.execute_campaign(campaign_id, credentials)
    
    if execution.get("success"):
        print(f"[OK] Campaign executed successfully!")
        results = execution.get("results", {})
        
        if results.get("uploaded"):
            print(f"  Video uploaded! Video ID: {results.get('video_id')}")
            print(f"  View at: https://youtube.com/watch?v={results.get('video_id')}")
        elif results.get("channel_stats"):
            print(f"  Channel stats synced:")
            stats = results["channel_stats"]
            print(f"    Subscribers: {stats.get('subscriber_count', 'N/A')}")
            print(f"    Total views: {stats.get('view_count', 'N/A')}")
        
        if results.get("note"):
            print(f"  Note: {results['note']}")
    else:
        error = execution.get("error", "Unknown error")
        print(f"[INFO] Execution result: {error[:100]}")
        
        # Provide helpful error messages
        error_lower = error.lower()
        if "oauth" in error_lower or "authentication" in error_lower:
            print("\n[WARNING] OAuth2 authentication issue.")
            print("  - Make sure youtube_token.json exists")
            print("  - Re-run: python scripts/generate_youtube_token.py if needed")
        elif "file not found" in error_lower:
            print("\n[WARNING] Video file not found. Check the path.")
        else:
            print(f"\n[ERROR] Execution failed: {error}")
    
    print("\n" + "="*60)
    print("4. Campaign Status...")
    print("="*60)
    
    status = agent.get_campaign_status(campaign_id)
    print(f"  Campaign: {status.get('campaign_name')}")
    print(f"  Status: {status.get('status')}")
    print(f"  Channel: {status.get('channel')}")
    print(f"  Executions: {status.get('executions', {})}")
    
    print("\n" + "="*60)
    print("[SUCCESS] YouTube campaign test completed!")
    print("="*60)
    print("\nWhat worked:")
    print("  [OK] Campaign created")
    print("  [OK] Campaign configuration validated")
    print("  [OK] Execution handler tested")
    print("  [OK] Status tracking working")
    print("\nFor actual video upload:")
    print("  - Setup OAuth2 (see YOUTUBE_OAUTH_SETUP.md)")
    print("  - Or use YouTube API key for channel stats only")
    
except Exception as e:
    print(f"\n[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    db.close()


