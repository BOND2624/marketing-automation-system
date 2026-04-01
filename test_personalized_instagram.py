"""
Test personalized Instagram post using the Personalization Engine.

Flow:
1. User inputs a title/topic
2. PersonalizationService generates caption + hashtags for Instagram
3. Creates Instagram campaign with personalized content
4. Executes (publishes to Instagram)

Requirements:
- Ollama running with a model (e.g. llama3)
- INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ACCOUNT_ID in .env
- INSTAGRAM_TEST_MEDIA_URL or provide a public image URL when prompted
"""

import os
import sys
from typing import Optional

from core.database import SessionLocal, ChannelType
from agents.campaign_manager import CampaignManagerAgent
from services.personalization_service import PersonalizationService
from core.config import get_settings


def get_env(name: str) -> Optional[str]:
    """Helper to read env variables safely."""
    value = os.getenv(name)
    return value.strip() if isinstance(value, str) and value.strip() else None


def run_personalized_instagram_test() -> int:
    print("=" * 60)
    print("Personalized Instagram Post Test")
    print("=" * 60)

    settings = get_settings()

    # 1. Get user title/topic
    print("\n[STEP 1] Enter your post title or topic:")
    print("  (e.g. 'Summer sale 30% off' or 'New coffee blend launch')")
    try:
        user_title = input("  Title: ").strip()
    except EOFError:
        user_title = "Marketing automation test post"
        print(f"  [DEFAULT] Using: {user_title}")

    if not user_title:
        user_title = "Marketing automation test post"
        print(f"  [DEFAULT] Using: {user_title}")

    # 2. Generate personalized content (same fast path as POST /api/publish/personalize: 1 LLM call)
    print("\n[STEP 2] Generating personalized content with Ollama...")
    try:
        personalization = PersonalizationService()
        ig_bundle = personalization.suggest_for_publish(
            user_title, platform="instagram", tone="casual"
        )
    except Exception as e:
        print(f"[FAIL] Personalization failed: {e}")
        print("  Make sure Ollama is running: ollama serve")
        print("  And a model is installed: ollama pull llama3")
        return 1

    caption = ig_bundle.get("body") or ig_bundle.get("description", "")
    hashtags = ig_bundle.get("hashtags", [])

    print("\n[OK] Generated content:")
    print(f"  Caption: {caption[:100]}{'...' if len(caption) > 100 else ''}")
    if hashtags:
        print(f"  Hashtags: {', '.join(hashtags[:5])}{'...' if len(hashtags) > 5 else ''}")

    # 3. Get media URL
    media_url = get_env("INSTAGRAM_TEST_MEDIA_URL") or settings.instagram_test_media_url
    if not media_url:
        print("\n[STEP 3] Enter a public image URL for the post:")
        print("  (Must be publicly accessible - e.g. from Imgur, CDN, etc.)")
        try:
            media_url = input("  URL: ").strip()
        except EOFError:
            media_url = ""
            print("  [SKIP] No URL provided.")

    if not media_url:
        print("\n[INFO] No media URL. Showing what would be posted:")
        print(f"  Content: {caption}")
        print("\n  To actually post, set INSTAGRAM_TEST_MEDIA_URL in .env or provide URL when prompted.")
        return 0

    # 4. Check Instagram credentials
    ig_token = get_env("INSTAGRAM_ACCESS_TOKEN") or settings.instagram_access_token
    ig_business_id = get_env("INSTAGRAM_BUSINESS_ACCOUNT_ID") or settings.instagram_business_account_id

    if not ig_token or not ig_business_id:
        print("\n[WARNING] Instagram credentials missing.")
        print("  Set INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ACCOUNT_ID in .env")
        print("  See CHANNEL_SETUP_GUIDE.md for setup.")
        return 1

    # 5. Create campaign and execute
    db = SessionLocal()
    try:
        agent = CampaignManagerAgent(db)

        campaign_config = {
            "content": caption,
            "media_url": media_url,
            "media_type": "IMAGE",
        }

        print("\n[STEP 4] Creating Instagram campaign with personalized content...")
        create_result = agent.create_campaign(
            name=f"Personalized: {user_title[:40]}",
            channel=ChannelType.INSTAGRAM,
            config=campaign_config,
        )

        if not create_result.get("success"):
            print(f"[FAIL] Campaign creation failed: {create_result.get('error')}")
            return 1

        campaign_id = create_result["campaign_id"]
        print(f"[OK] Campaign created. ID={campaign_id}")

        credentials = {
            ChannelType.INSTAGRAM: {
                "access_token": ig_token,
                "instagram_business_account_id": ig_business_id,
            }
        }

        print("\n[STEP 5] Publishing to Instagram...")
        exec_result = agent.execute_campaign(campaign_id, credentials)

        if exec_result.get("success"):
            print("\n[SUCCESS] Post published to Instagram!")
            results = exec_result.get("results", {})
            print(f"  Post ID: {results.get('post_id')}")
            print(f"  Caption: {caption[:80]}...")
        else:
            print(f"\n[FAIL] Publish failed: {exec_result.get('error')}")
            return 1

    finally:
        db.close()

    print("\n" + "=" * 60)
    print("[DONE] Personalized Instagram test complete.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(run_personalized_instagram_test())
