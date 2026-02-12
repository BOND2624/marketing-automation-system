"""
Test Facebook publish functionality using real APIs.

This script:
- Creates a simple Facebook campaign and publishes one post (feed or photo).

Requirements:
- Valid Facebook access token and page ID in environment variables.
- Media URL must be publicly accessible (CDN, public HTTP URL, etc.) for photo posts.
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


def run_facebook_test(agent: CampaignManagerAgent) -> None:
    print("\n" + "=" * 60)
    print("FACEBOOK PUBLISH TEST")
    print("=" * 60)

    settings = get_settings()

    fb_token = get_env("FACEBOOK_ACCESS_TOKEN") or settings.facebook_access_token
    fb_page_id = get_env("FACEBOOK_PAGE_ID")
    fb_image_url = get_env("FACEBOOK_TEST_IMAGE_URL")

    if not fb_token or not fb_page_id:
        print("\n[WARNING] Facebook credentials missing.")
        print("  - FACEBOOK_ACCESS_TOKEN and FACEBOOK_PAGE_ID are required.")
        print("  - See FACEBOOK_INSTAGRAM_API_SETUP.md for setup steps.")
        return

    # Decide whether to publish a photo or a simple feed post
    if not fb_image_url:
        print("\n[INFO] FACEBOOK_TEST_IMAGE_URL not set.")
        try:
            user_input = input(
                "Enter a public image URL for Facebook photo post (or press Enter for text-only post): "
            ).strip()
        except EOFError:
            user_input = ""
            print("[INFO] No input received; defaulting to text-only post.")

        fb_image_url = user_input or None

    if fb_image_url:
        campaign_config = {
            "message": "Facebook photo publish test from marketing automation platform.",
            "media_url": fb_image_url,
        }
        print("\n[INFO] Will publish a Facebook photo post.")
    else:
        campaign_config = {
            "message": "Facebook feed publish test from marketing automation platform.",
        }
        print("\n[INFO] Will publish a Facebook text-only feed post.")

    print("\n[STEP] Creating Facebook campaign...")
    create_result = agent.create_campaign(
        name="Facebook Publish Test",
        channel=ChannelType.FACEBOOK,
        config=campaign_config,
    )

    if not create_result.get("success"):
        print(f"[FAIL] Facebook campaign creation failed: {create_result.get('error')}")
        return

    campaign_id = create_result["campaign_id"]
    print(f"[OK] Facebook campaign created. ID={campaign_id}")

    credentials = {
        ChannelType.FACEBOOK: {
            "access_token": fb_token,
            "page_id": fb_page_id,
        }
    }

    print("\n[STEP] Executing Facebook campaign (publishing)...")
    exec_result = agent.execute_campaign(campaign_id, credentials)

    if exec_result.get("success"):
        print("[OK] Facebook campaign executed successfully.")
        results = exec_result.get("results", {})
        print(f"  posted: {results.get('posted')}")
        print(f"  post_id: {results.get('post_id')}")
        if results.get("details"):
            print(f"  details: {results['details']}")
    else:
        error = exec_result.get("error", "Unknown error")
        print(f"[FAIL] Facebook execution failed: {error}")
        details = exec_result.get("results") or exec_result.get("details")
        if details:
            print(f"  details: {details}")


def main() -> int:
    print("=" * 60)
    print("Facebook Publish Test")
    print("=" * 60)

    db = SessionLocal()
    try:
        agent = CampaignManagerAgent(db)

        run_facebook_test(agent)

        print("\n" + "=" * 60)
        print("[INFO] Facebook publish test script finished.")
        print("=" * 60)
        return 0
    except Exception as exc:
        print(f"\n[ERROR] Facebook test script failed: {exc}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())

