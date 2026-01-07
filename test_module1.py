"""
Comprehensive test suite for Module 1: Foundation & DataIntegrationAgent
Run this script to test all components of Module 1.
"""

import sys
from datetime import datetime

def test_config():
    """Test configuration loading."""
    print("\n" + "="*60)
    print("TEST 1: Configuration Loading")
    print("="*60)
    try:
        from core.config import get_settings
        settings = get_settings()
        print(f"✓ Configuration loaded successfully")
        print(f"  Database URL: {settings.database_url}")
        print(f"  LLM Provider: {settings.llm_provider}")
        print(f"  Redis URL: {settings.redis_url}")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_database():
    """Test database connection and models."""
    print("\n" + "="*60)
    print("TEST 2: Database Connection & Models")
    print("="*60)
    try:
        from core.database import engine, Base, Customer, SessionLocal
        from sqlalchemy import inspect
        
        # Test connection
        with engine.connect() as conn:
            print("✓ Database connection successful")
        
        # Test models exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        required_tables = ['customers', 'campaigns', 'customer_events', 'channel_credentials']
        for table in required_tables:
            if table in tables:
                print(f"✓ Table '{table}' exists")
            else:
                print(f"✗ Table '{table}' not found")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        print("  Make sure PostgreSQL is running: docker compose up -d")
        return False

def test_cdp():
    """Test CDP service."""
    print("\n" + "="*60)
    print("TEST 3: Customer Data Platform (CDP)")
    print("="*60)
    try:
        from core.database import SessionLocal, ChannelType
        from core.cdp import CDPService
        
        db = SessionLocal()
        try:
            cdp = CDPService(db)
            
            # Create customer
            customer = cdp.get_or_create_customer(
                email=f"test_{datetime.now().timestamp()}@example.com",
                phone="+1234567890",
                attributes={"test": True, "name": "Test User"}
            )
            print(f"✓ Customer created: ID={customer.customer_id}")
            
            # Unify data
            cdp.unify_customer_data(
                customer.customer_id,
                ChannelType.INSTAGRAM,
                {"followers": 1000, "posts": 50}
            )
            print("✓ Data unified from Instagram channel")
            
            # Add event
            event = cdp.add_customer_event(
                customer.customer_id,
                "click",
                ChannelType.EMAIL,
                {"campaign_id": 1}
            )
            print(f"✓ Event added: {event.event_id}")
            
            # Get unified profile
            profile = cdp.get_unified_customer_profile(customer.customer_id)
            assert profile is not None
            assert profile['customer_id'] == customer.customer_id
            print(f"✓ Unified profile retrieved")
            print(f"  Channels: {list(profile['channels'].keys())}")
            print(f"  Events: {len(profile['recent_events'])}")
            
            return True
        finally:
            db.close()
    except Exception as e:
        print(f"✗ CDP test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integrations():
    """Test API integration classes."""
    print("\n" + "="*60)
    print("TEST 4: API Integration Classes")
    print("="*60)
    
    tests_passed = 0
    total_tests = 4
    
    # Test base integration
    try:
        from api_integrations.base import BaseIntegration, RateLimiter
        limiter = RateLimiter(max_calls=5, period_seconds=1)
        limiter.wait_if_needed()
        print("✓ BaseIntegration rate limiter works")
        tests_passed += 1
    except Exception as e:
        print(f"✗ BaseIntegration test failed: {e}")
    
    # Test YouTube integration structure
    try:
        from api_integrations.youtube import YouTubeIntegration
        # Should fail without API key (expected)
        try:
            YouTubeIntegration({"api_key": None})
            print("✗ YouTubeIntegration should require API key")
        except ValueError:
            print("✓ YouTubeIntegration validates API key")
            tests_passed += 1
    except Exception as e:
        print(f"✗ YouTubeIntegration test failed: {e}")
    
    # Test Instagram integration structure
    try:
        from api_integrations.instagram import InstagramIntegration
        try:
            InstagramIntegration({"access_token": None})
            print("✗ InstagramIntegration should require access token")
        except ValueError:
            print("✓ InstagramIntegration validates access token")
            tests_passed += 1
    except Exception as e:
        print(f"✗ InstagramIntegration test failed: {e}")
    
    # Test Email/SMS integration structure
    try:
        from api_integrations.email_sms import EmailSMSIntegration
        try:
            EmailSMSIntegration({"sendgrid_api_key": None})
            print("✗ EmailSMSIntegration should require SendGrid API key")
        except ValueError:
            print("✓ EmailSMSIntegration validates API key")
            tests_passed += 1
    except Exception as e:
        print(f"✗ EmailSMSIntegration test failed: {e}")
    
    print(f"\n  Results: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests

def test_data_integration_agent():
    """Test DataIntegrationAgent."""
    print("\n" + "="*60)
    print("TEST 5: DataIntegrationAgent")
    print("="*60)
    try:
        from core.database import SessionLocal
        from agents.data_integration import DataIntegrationAgent
        
        db = SessionLocal()
        try:
            agent = DataIntegrationAgent(db)
            print("✓ DataIntegrationAgent initialized")
            print(f"  Role: {agent.agent.role}")
            print(f"  Goal: {agent.agent.goal[:50]}...")
            
            # Test integration dictionary is empty initially
            assert len(agent.integrations) == 0
            print("✓ Integration storage initialized correctly")
            
            return True
        finally:
            db.close()
    except Exception as e:
        print(f"✗ DataIntegrationAgent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_scheduler():
    """Test Celery scheduler setup."""
    print("\n" + "="*60)
    print("TEST 6: Celery Scheduler")
    print("="*60)
    try:
        from services.scheduler import celery_app, sync_all_channels_task, sync_single_channel_task
        
        print("✓ Celery app initialized")
        print(f"  Broker: {celery_app.conf.broker_url}")
        print(f"  Backend: {celery_app.conf.result_backend}")
        
        # Check tasks are registered
        tasks = celery_app.tasks.keys()
        assert 'sync_all_channels' in tasks
        assert 'sync_single_channel' in tasks
        print("✓ Sync tasks registered")
        
        # Check beat schedule
        beat_schedule = celery_app.conf.beat_schedule
        assert len(beat_schedule) > 0
        print(f"✓ Beat schedule configured ({len(beat_schedule)} tasks)")
        
        return True
    except Exception as e:
        print(f"✗ Scheduler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pydantic_models():
    """Test Pydantic schemas."""
    print("\n" + "="*60)
    print("TEST 7: Pydantic Models")
    print("="*60)
    try:
        from core.models import (
            CustomerCreate, Customer, CampaignCreate, Campaign,
            CustomerEventCreate, SyncDataRequest
        )
        from core.database import ChannelType
        
        # Test customer creation
        customer_data = CustomerCreate(
            email="test@example.com",
            phone="+1234567890",
            attributes={"test": True}
        )
        print("✓ CustomerCreate schema validates")
        
        # Test campaign creation
        campaign_data = CampaignCreate(
            name="Test Campaign",
            channel=ChannelType.EMAIL,
            config={"content": "Test"}
        )
        print("✓ CampaignCreate schema validates")
        
        # Test sync request
        sync_request = SyncDataRequest(
            channel=ChannelType.YOUTUBE,
            force_full_sync=False
        )
        print("✓ SyncDataRequest schema validates")
        
        return True
    except Exception as e:
        print(f"✗ Pydantic models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("MODULE 1: Foundation & DataIntegrationAgent - Test Suite")
    print("="*60)
    
    tests = [
        ("Configuration", test_config),
        ("Database", test_database),
        ("CDP", test_cdp),
        ("API Integrations", test_integrations),
        ("DataIntegrationAgent", test_data_integration_agent),
        ("Scheduler", test_scheduler),
        ("Pydantic Models", test_pydantic_models),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Module 1 is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

