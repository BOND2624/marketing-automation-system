"""
Test Instagram publish functionality using real APIs.

This script:
- Creates a simple Instagram campaign and publishes one media item.

Requirements:
- Valid Instagram access token and business account ID in environment variables.
- Media URL must be publicly accessible (CDN, public HTTP URL, etc.).
"""

import os
import sys
from typing import Optional

from core.database import SessionLocal, ChannelType
from agents.campaign_manager import CampaignManagerAgent
from core.config import get_settings


def get_env(name: str) -> Optional[str]:
    """Helper to read env variables safely."""
    value = os.getenv(name)
    return value.strip() if isinstance(value, str) and value.strip() else None


def run_instagram_test(agent: CampaignManagerAgent) -> None:
    print("\n" + "=" * 60)
    print("INSTAGRAM PUBLISH TEST")
    print("=" * 60)

    settings = get_settings()

    ig_token = get_env("INSTAGRAM_ACCESS_TOKEN") or settings.instagram_access_token
    ig_business_id = get_env("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    media_url = get_env("INSTAGRAM_TEST_MEDIA_URL")

    if not ig_token or not ig_business_id:
        print("\n[WARNING] Instagram credentials missing.")
        print("  - INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ACCOUNT_ID are required.")
        print("  - See FACEBOOK_INSTAGRAM_API_SETUP.md for setup steps.")
        return

    if not media_url:
        print("\n[INFO] INSTAGRAM_TEST_MEDIA_URL not set.")
        try:
            user_input = input(
                "Enter a public image/video URL for Instagram (or press Enter to skip): "
            ).strip()
        except EOFError:
            user_input = ""
            print("[INFO] No input received; skipping Instagram test.")

        if not user_input:
            print("[INFO] Skipping Instagram publish test.")
            return
        media_url = user_input

    # Build campaign config
    campaign_config = {
        "content": "Instagram publish test from marketing automation platform.",
        "media_url": media_url,
        "media_type": "IMAGE",  # or VIDEO / REELS if your URL is a video
    }

    print("\n[STEP] Creating Instagram campaign...")
    create_result = agent.create_campaign(
        name="Instagram Publish Test",
        channel=ChannelType.INSTAGRAM,
        config=campaign_config,
    )

    if not create_result.get("success"):
        print(f"[FAIL] Instagram campaign creation failed: {create_result.get('error')}")
        return

    campaign_id = create_result["campaign_id"]
    print(f"[OK] Instagram campaign created. ID={campaign_id}")

    credentials = {
        ChannelType.INSTAGRAM: {
            "access_token": ig_token,
            "instagram_business_account_id": ig_business_id,
        }
    }

    print("\n[STEP] Executing Instagram campaign (publishing)...")
    exec_result = agent.execute_campaign(campaign_id, credentials)

    if exec_result.get("success"):
        print("[OK] Instagram campaign executed successfully.")
        results = exec_result.get("results", {})
        print(f"  posted: {results.get('posted')}")
        print(f"  post_id (media_id): {results.get('post_id')}")
        if results.get("details"):
            print(f"  details: {results['details']}")
    else:
        error = exec_result.get("error", "Unknown error")
        print(f"[FAIL] Instagram execution failed: {error}")
        details = exec_result.get("results") or exec_result.get("details")
        if details:
            print(f"  details: {details}")


def main() -> int:
    print("=" * 60)
    print("Instagram Publish Test")
    print("=" * 60)

    db = SessionLocal()
    try:
        agent = CampaignManagerAgent(db)

        run_instagram_test(agent)

        print("\n" + "=" * 60)
        print("[INFO] Instagram publish test script finished.")
        print("=" * 60)
        return 0
    except Exception as exc:
        print(f"\n[ERROR] Instagram test script failed: {exc}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())

