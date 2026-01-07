# Setup and Testing Guide - Module 1

## Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose (for PostgreSQL and Redis)
- `uv` package manager (optional, but recommended)
- Ollama (for free local LLM) - [Install Ollama](https://ollama.ai)

## Step 1: Install uv (Optional but Recommended)

`uv` is a fast Python package installer and resolver.

### Windows:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### macOS/Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify installation:
```bash
uv --version
```

## Step 2: Create Virtual Environment

### Option A: Using uv (Recommended)
```bash
# Create virtual environment
uv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Option B: Using Python's venv
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

## Step 3: Install Dependencies

### Option A: Using uv (Faster)
```bash
# Install dependencies
uv pip install -r requirements.txt
```

### Option B: Using pip
```bash
# Upgrade pip first
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Setup Environment Variables

1. Copy the example environment file:
```bash
# Windows:
copy .env.example .env
# macOS/Linux:
cp .env.example .env
```

2. Edit `.env` file and configure:

**Required for testing:**
- `DATABASE_URL`: PostgreSQL connection string (default: `postgresql://user:password@localhost:5432/marketing_cdp`)
- `REDIS_URL`: Redis connection string (default: `redis://localhost:6379/0`)

**API Keys (for actual API testing):**
- `YOUTUBE_API_KEY`: Get from [Google Cloud Console](https://console.cloud.google.com/)
- `INSTAGRAM_ACCESS_TOKEN`: See [FACEBOOK_INSTAGRAM_API_SETUP.md](FACEBOOK_INSTAGRAM_API_SETUP.md) for detailed steps
- `FACEBOOK_ACCESS_TOKEN`: See [FACEBOOK_INSTAGRAM_API_SETUP.md](FACEBOOK_INSTAGRAM_API_SETUP.md) for detailed steps
- `FACEBOOK_APP_ID` & `FACEBOOK_APP_SECRET`: See [FACEBOOK_INSTAGRAM_API_SETUP.md](FACEBOOK_INSTAGRAM_API_SETUP.md)
- `SENDGRID_API_KEY`: Get from [SendGrid](https://sendgrid.com/)

**LLM Configuration (Free):**
- `LLM_PROVIDER=ollama` (default, free local)
- `OLLAMA_BASE_URL=http://localhost:11434` (default)
- `OLLAMA_MODEL=llama3` (default)

**Note:** For initial testing, you can skip API keys and test database/CDP functionality first.

## Step 5: Start Docker Services

Start PostgreSQL and Redis using Docker Compose:

```bash
docker compose up -d
```

Verify containers are running:
```bash
docker compose ps
```

You should see:
- `marketing_postgres` (running on port 5432)
- `marketing_redis` (running on port 6379)

## Step 6: Initialize Database

Run the database initialization script:

```bash
python scripts/init_db.py
```

Expected output:
```
Initializing database: postgresql://user:password@localhost:5432/marketing_cdp
Database tables created successfully!
```

## Step 7: Install and Start Ollama (OPTIONAL - For Full LLM Testing)

**⚠️ IMPORTANT: Ollama is OPTIONAL for Module 1 testing!**
- You can test database, CDP, and integration classes without Ollama
- Ollama is only needed for full DataIntegrationAgent AI functionality
- Skip this step if you want to test basics first

**📖 For detailed Ollama setup instructions, see [OLLAMA_SETUP.md](OLLAMA_SETUP.md)**

### Quick Installation (Windows):

1. **Download Ollama:**
   - Visit: https://ollama.ai/download
   - Download and run the Windows installer
   - **Restart your terminal/PowerShell after installation**

2. **Verify installation:**
   ```powershell
   ollama --version
   ```

3. **Pull the default model** (downloads ~4.7 GB):
   ```powershell
   ollama pull llama3
   ```

4. **Verify Ollama is running:**
   ```powershell
   ollama list
   ```

### If Ollama Command Not Found:

- Restart your terminal/PowerShell
- Check installation completed successfully
- See [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for troubleshooting

## Step 8: Test Module 1 Components

### Test 1: Configuration Loading

```bash
python -c "from core.config import get_settings; s = get_settings(); print(f'Database URL: {s.database_url}'); print(f'LLM Provider: {s.llm_provider}')"
```

Expected output:
```
Database URL: postgresql://user:password@localhost:5432/marketing_cdp
LLM Provider: ollama
```

### Test 2: Database Connection

Create a test file `test_db.py`:

```python
from core.database import engine, Base, Customer, CDPService
from sqlalchemy.orm import Session
from core.database import SessionLocal

# Test database connection
try:
    with engine.connect() as conn:
        print("✓ Database connection successful!")
except Exception as e:
    print(f"✗ Database connection failed: {e}")
    exit(1)

# Test creating a customer
db = SessionLocal()
try:
    cdp = CDPService(db)
    customer = cdp.get_or_create_customer(
        email="test@example.com",
        phone="+1234567890",
        attributes={"test": True}
    )
    print(f"✓ Customer created: ID={customer.customer_id}, Email={customer.email}")
    
    # Get unified profile
    profile = cdp.get_unified_customer_profile(customer.customer_id)
    print(f"✓ Unified profile retrieved: {profile['email']}")
finally:
    db.close()
```

Run:
```bash
python test_db.py
```

### Test 3: Base Integration Class

Create `test_integration.py`:

```python
from api_integrations.base import BaseIntegration, RateLimiter
from typing import Dict, Any
from datetime import datetime

# Test RateLimiter
limiter = RateLimiter(max_calls=5, period_seconds=1)
print("Testing rate limiter...")
for i in range(7):
    limiter.wait_if_needed()
    print(f"  Call {i+1} allowed")

print("✓ Rate limiter works correctly")
```

Run:
```bash
python test_integration.py
```

### Test 4: YouTube Integration (Mock/Without API Key)

Create `test_youtube.py`:

```python
from api_integrations.youtube import YouTubeIntegration

# Test without API key (will fail initialization, which is expected)
try:
    integration = YouTubeIntegration({"api_key": None})
except ValueError as e:
    print(f"✓ YouTube integration correctly validates API key: {e}")

# Test with dummy key (will fail connection, but structure is correct)
try:
    integration = YouTubeIntegration({"api_key": "test_key_123"})
    result = integration.test_connection()
    print(f"YouTube connection test result: {result}")
    print("✓ YouTube integration structure is correct")
except Exception as e:
    print(f"Note: Connection test failed (expected without valid key): {e}")
```

Run:
```bash
python test_youtube.py
```

### Test 5: DataIntegrationAgent (Basic)

Create `test_agent.py`:

```python
from core.database import SessionLocal
from agents.data_integration import DataIntegrationAgent

db = SessionLocal()
try:
    # Initialize agent
    agent = DataIntegrationAgent(db)
    print("✓ DataIntegrationAgent initialized successfully")
    print(f"✓ Agent role: {agent.agent.role}")
    print(f"✓ Agent goal: {agent.agent.goal}")
finally:
    db.close()
```

Run:
```bash
python test_agent.py
```

### Test 6: CDP Service Full Test

Create `test_cdp_full.py`:

```python
from core.database import SessionLocal, ChannelType
from core.cdp import CDPService

db = SessionLocal()
try:
    cdp = CDPService(db)
    
    # Create customer
    customer = cdp.get_or_create_customer(
        email="john.doe@example.com",
        phone="+1234567890",
        attributes={"name": "John Doe", "city": "New York"}
    )
    print(f"✓ Created customer: {customer.customer_id}")
    
    # Add channel-specific data
    cdp.unify_customer_data(
        customer.customer_id,
        ChannelType.INSTAGRAM,
        {"followers": 1000, "posts": 50, "engagement_rate": 4.5}
    )
    print("✓ Added Instagram data")
    
    cdp.unify_customer_data(
        customer.customer_id,
        ChannelType.FACEBOOK,
        {"likes": 500, "posts": 30}
    )
    print("✓ Added Facebook data")
    
    # Add events
    cdp.add_customer_event(
        customer.customer_id,
        "click",
        ChannelType.EMAIL,
        {"campaign_id": 1, "link": "https://example.com"}
    )
    print("✓ Added customer event")
    
    # Get unified profile
    profile = cdp.get_unified_customer_profile(customer.customer_id)
    print(f"\n✓ Unified Profile:")
    print(f"  Customer ID: {profile['customer_id']}")
    print(f"  Email: {profile['email']}")
    print(f"  Channels: {list(profile['channels'].keys())}")
    print(f"  Recent Events: {len(profile['recent_events'])}")
    
finally:
    db.close()
```

Run:
```bash
python test_cdp_full.py
```

## Step 9: Test with Real API Keys (Optional)

Once you have API keys configured:

### Test YouTube Sync:
```python
from core.database import SessionLocal
from agents.data_integration import DataIntegrationAgent
from core.database import ChannelType
from core.config import get_settings

settings = get_settings()

db = SessionLocal()
try:
    agent = DataIntegrationAgent(db)
    
    if settings.youtube_api_key:
        result = agent.sync_youtube_data(
            credentials={"api_key": settings.youtube_api_key},
            since=None
        )
        print(f"YouTube Sync Result: {result.get('success', False)}")
        if result.get('success'):
            print(f"  Channel Stats: {result.get('channel_stats', {})}")
    else:
        print("YouTube API key not configured")
finally:
    db.close()
```

## Step 10: Test Celery Scheduler (Optional)

### Start Redis (if not already running):
```bash
docker compose up -d redis
```

### Start Celery Worker:
```bash
celery -A services.scheduler worker --loglevel=info
```

### Start Celery Beat (for scheduled tasks):
```bash
celery -A services.scheduler beat --loglevel=info
```

### Test sync task manually:
```python
from services.scheduler import sync_all_channels_task

result = sync_all_channels_task.delay(force_full_sync=False)
print(f"Task ID: {result.id}")
print(f"Result: {result.get()}")
```

## Troubleshooting

### Database Connection Issues
- Ensure Docker containers are running: `docker compose ps`
- Check database URL in `.env` matches Docker Compose configuration
- Try: `docker compose logs postgres`

### Ollama Connection Issues
- **Note:** Ollama is optional! Tests will work without it (except full agent functionality)
- Verify Ollama is installed: Download from https://ollama.ai/download
- **After installation, restart terminal/PowerShell** (important!)
- Verify Ollama is running: `ollama list`
- Check `OLLAMA_BASE_URL` in `.env` (default: `http://localhost:11434`)
- Test: `curl http://localhost:11434/api/tags` or `Invoke-WebRequest http://localhost:11434/api/tags` (PowerShell)
- See [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for detailed troubleshooting

### Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt` (or `uv pip install -r requirements.txt`)
- Check Python version: `python --version` (should be 3.10+)

### API Key Issues
- Most integrations will work without API keys for structure testing
- API connection tests will fail without valid keys (this is expected)
- Add API keys to `.env` file for full functionality

## Next Steps

After successful testing of Module 1:
1. Verify all tests pass
2. Review logs for any warnings
3. Configure API keys for actual channel testing
4. Proceed to Module 2: CampaignManagerAgent

