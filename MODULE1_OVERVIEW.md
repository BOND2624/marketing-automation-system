# Module 1: Foundation & DataIntegrationAgent - Complete Overview

## 🎯 What Module 1 Does

Module 1 establishes the **foundation** of the marketing automation platform and implements the **DataIntegrationAgent**, which synchronizes data from multiple marketing channels (YouTube, Instagram, Facebook, Email/SMS) into a unified Customer Data Platform (CDP).

## 📋 Core Components Built

### 1. **Database Foundation** (`core/database.py`)

**What it does:**
- Defines all database models (tables) using SQLAlchemy
- Manages database connections and sessions
- Stores: customers, campaigns, events, credentials, analytics

**Key Models:**
- `Customer` - Customer profiles in CDP
- `Campaign` - Marketing campaigns
- `CustomerEvent` - Customer engagement events (clicks, opens, views)
- `ChannelCredential` - Encrypted API credentials
- `AnalyticsSnapshot` - Campaign performance metrics
- `User` - User accounts for authentication

**Location:** `core/database.py`

**Test it:**
```python
from core.database import Customer, SessionLocal
db = SessionLocal()
customer = Customer(email="test@example.com")
db.add(customer)
db.commit()
```

---

### 2. **Configuration Management** (`core/config.py`)

**What it does:**
- Loads all environment variables from `.env` file
- Provides centralized settings for the entire application
- Supports all API keys, database URLs, LLM configuration

**Key Settings:**
- Database connection strings
- API keys (YouTube, Instagram, Facebook, SendGrid)
- LLM provider configuration (Ollama, Groq, HuggingFace)
- JWT secrets for authentication
- Encryption keys

**Location:** `core/config.py`

**Test it:**
```python
from core.config import get_settings
settings = get_settings()
print(settings.database_url)
print(settings.llm_provider)
```

---

### 3. **Customer Data Platform (CDP)** (`core/cdp.py`)

**What it does:**
- **Unifies customer data** from multiple marketing channels
- Creates/updates customer profiles
- Merges channel-specific data (e.g., Instagram followers + Facebook likes)
- Tracks customer events across all channels
- Generates unified customer profiles

**Key Features:**
- `get_or_create_customer()` - Create or find customers by email
- `unify_customer_data()` - Merge data from different channels
- `add_customer_event()` - Track engagement events
- `get_unified_customer_profile()` - Get complete customer view

**Location:** `core/cdp.py`

**Example Usage:**
```python
from core.cdp import CDPService
from core.database import SessionLocal, ChannelType

db = SessionLocal()
cdp = CDPService(db)

# Create customer
customer = cdp.get_or_create_customer(email="john@example.com")

# Add Instagram data
cdp.unify_customer_data(
    customer.customer_id,
    ChannelType.INSTAGRAM,
    {"followers": 1000, "posts": 50}
)

# Get unified profile
profile = cdp.get_unified_customer_profile(customer.customer_id)
# Returns: All customer data merged from all channels
```

---

### 4. **API Integrations**

#### Base Integration (`api_integrations/base.py`)

**What it does:**
- Provides common functionality for all API integrations
- Handles rate limiting, error handling, pagination, retries
- Base class that all channel integrations extend

**Location:** `api_integrations/base.py`

#### YouTube Integration (`api_integrations/youtube.py`)

**What it does:**
- Connects to YouTube Data API v3
- Syncs channel statistics (subscribers, views, video count)
- Syncs video analytics (views, likes, comments)

**Location:** `api_integrations/youtube.py`

**Features:**
- Channel stats sync
- Video analytics sync
- Rate limiting (10,000 units/day free quota)

#### Instagram Integration (`api_integrations/instagram.py`)

**What it does:**
- Connects to Instagram Graph API
- Syncs account info (followers, posts count)
- Syncs posts with engagement metrics
- Syncs stories

**Location:** `api_integrations/instagram.py`

**Features:**
- Account information sync
- Posts with likes/comments/insights
- Stories sync

#### Facebook Integration (`api_integrations/facebook.py`)

**What it does:**
- Connects to Facebook Graph API
- Syncs page insights (fans, impressions, engagement)
- Syncs page posts with engagement
- Syncs ad performance (if ad account configured)

**Location:** `api_integrations/facebook.py`

**Features:**
- Page insights (30-day trends)
- Post engagement metrics
- Ad performance metrics

#### Email/SMS Integration (`api_integrations/email_sms.py`)

**What it does:**
- Connects to SendGrid (email) and Twilio (SMS)
- Syncs email statistics (sends, opens, clicks, bounces)
- Syncs SMS statistics (sent, delivered, failed)

**Location:** `api_integrations/email_sms.py`

**Features:**
- Email delivery stats
- Open/click rates
- SMS delivery stats

---

### 5. **DataIntegrationAgent** (`agents/data_integration.py`)

**What it does:**
- **CrewAI-powered agent** that orchestrates data synchronization
- Coordinates syncs from all marketing channels
- Transforms channel-specific data into unified format
- Stores synced data in CDP
- Handles errors and retries

**Key Features:**
- `sync_youtube_data()` - Sync YouTube channel data
- `sync_instagram_data()` - Sync Instagram account data
- `sync_facebook_data()` - Sync Facebook page data
- `sync_email_sms_data()` - Sync email/SMS stats
- `sync_all_channels()` - Sync all channels at once
- `unify_customer_data()` - Merge data from multiple channels

**Location:** `agents/data_integration.py`

**Architecture:**
```
DataIntegrationAgent (CrewAI Agent)
    ├── YouTubeIntegration → CDP
    ├── InstagramIntegration → CDP
    ├── FacebookIntegration → CDP
    └── EmailSMSIntegration → CDP
```

**Example Usage:**
```python
from agents.data_integration import DataIntegrationAgent
from core.database import SessionLocal, ChannelType

db = SessionLocal()
agent = DataIntegrationAgent(db)

# Sync all channels
credentials = {
    ChannelType.YOUTUBE: {"api_key": "your_key"},
    ChannelType.INSTAGRAM: {"access_token": "your_token"},
    # ... other channels
}

results = agent.sync_all_channels(credentials)
```

---

### 6. **Celery Scheduler** (`services/scheduler.py`)

**What it does:**
- Schedules periodic data synchronization tasks
- Runs background jobs for automated syncs
- Supports hourly incremental syncs and daily full syncs

**Key Features:**
- `sync_all_channels_task` - Celery task to sync all channels
- `sync_single_channel_task` - Celery task to sync one channel
- Beat schedule: Hourly incremental + Daily full sync

**Location:** `services/scheduler.py`

**Scheduled Tasks:**
- **Hourly:** Incremental sync (only new data since last hour)
- **Daily:** Full sync (all data)

**Usage:**
```bash
# Start Celery worker
celery -A services.scheduler worker --loglevel=info

# Start Celery beat (scheduler)
celery -A services.scheduler beat --loglevel=info
```

---

### 7. **Pydantic Models** (`core/models.py`)

**What it does:**
- Defines API request/response schemas
- Validates data before database operations
- Ensures type safety and data integrity

**Key Schemas:**
- `CustomerCreate`, `CustomerUpdate`, `Customer`
- `CampaignCreate`, `CampaignUpdate`, `Campaign`
- `CustomerEventCreate`, `CustomerEvent`
- `SyncDataRequest`, `SyncResult`

**Location:** `core/models.py`

---

## 📁 Project Structure

```
final-year-project/
├── agents/
│   └── data_integration.py       ← DataIntegrationAgent (CrewAI)
├── api_integrations/
│   ├── base.py                    ← Base integration class
│   ├── youtube.py                 ← YouTube API integration
│   ├── instagram.py               ← Instagram API integration
│   ├── facebook.py                ← Facebook API integration
│   └── email_sms.py               ← Email/SMS API integration
├── core/
│   ├── config.py                  ← Configuration management
│   ├── database.py                ← Database models & session
│   ├── cdp.py                     ← Customer Data Platform
│   └── models.py                  ← Pydantic schemas
├── services/
│   └── scheduler.py               ← Celery scheduler tasks
├── scripts/
│   └── init_db.py                 ← Database initialization
├── test_module1.py                ← Comprehensive test suite
├── requirements.txt               ← Dependencies
└── docker-compose.yml             ← PostgreSQL & Redis

```

---

## 🔄 Data Flow

```
Marketing Channels (APIs)
    ↓
API Integrations (youtube.py, instagram.py, etc.)
    ↓
DataIntegrationAgent (CrewAI Agent)
    ↓
CDP Service (cdp.py)
    ↓
Database (PostgreSQL)
    ↓
Unified Customer Profiles
```

**Example Flow:**
1. YouTube API → `YouTubeIntegration.sync_data()` → Channel stats
2. Instagram API → `InstagramIntegration.sync_data()` → Followers, posts
3. DataIntegrationAgent → `sync_all_channels()` → Orchestrates syncs
4. CDP Service → `unify_customer_data()` → Merges into customer profile
5. Database → Stores unified customer data

---

## ✅ What's Working

### Tested & Verified:
- ✅ Database connection and models
- ✅ Configuration loading
- ✅ CDP customer creation and data unification
- ✅ All API integration classes (structure validated)
- ✅ DataIntegrationAgent initialization
- ✅ Celery scheduler setup
- ✅ Pydantic model validation

### Ready to Use:
- ✅ Database tables created and working
- ✅ CDP can store and retrieve unified customer data
- ✅ API integrations are structured and ready for API keys
- ✅ Scheduler is configured for automated syncs

---

## 🚀 How to Use Module 1

### 1. **Add API Keys** (in `.env` file):
```env
YOUTUBE_API_KEY=your_key_here
INSTAGRAM_ACCESS_TOKEN=your_token_here
FACEBOOK_ACCESS_TOKEN=your_token_here
SENDGRID_API_KEY=your_key_here
```

### 2. **Sync Data Manually:**
```python
from agents.data_integration import DataIntegrationAgent
from core.database import SessionLocal, ChannelType
from core.config import get_settings

settings = get_settings()
db = SessionLocal()

agent = DataIntegrationAgent(db)

# Sync YouTube
result = agent.sync_youtube_data({
    "api_key": settings.youtube_api_key,
    "channel_id": "your_channel_id"
})
print(result)
```

### 3. **Check CDP Data:**
```python
from core.cdp import CDPService
from core.database import SessionLocal

db = SessionLocal()
cdp = CDPService(db)

# Get customer profile
profile = cdp.get_unified_customer_profile(customer_id=1)
print(profile)  # Shows all unified data from all channels
```

### 4. **Run Automated Syncs:**
```bash
# Start Celery worker
celery -A services.scheduler worker

# Start scheduler (in another terminal)
celery -A services.scheduler beat

# Syncs run automatically:
# - Every hour: Incremental sync
# - Every day: Full sync
```

---

## 📊 What Data Gets Synced

### YouTube:
- Subscriber count
- Total video views
- Video count
- Individual video metrics (views, likes, comments)

### Instagram:
- Follower count
- Post count
- Post engagement (likes, comments, insights)
- Stories

### Facebook:
- Page fans
- Page impressions
- Page engagement
- Post metrics (likes, comments, shares)
- Ad performance (if configured)

### Email/SMS:
- Total emails sent
- Delivery rate
- Open rate
- Click rate
- SMS delivery stats

---

## 🎯 Key Achievements

1. **Unified Data Platform**: All marketing channel data in one place
2. **Automated Syncs**: Scheduled background tasks for data updates
3. **Scalable Architecture**: Easy to add new channels
4. **Free Tier Support**: All APIs use free tiers
5. **Error Handling**: Robust retry logic and error management
6. **Rate Limiting**: Prevents API quota exhaustion

---

## 🔍 Where to Look for Specific Features

| Feature | File Location |
|---------|---------------|
| Database Models | `core/database.py` |
| Customer Data Management | `core/cdp.py` |
| API Connections | `api_integrations/*.py` |
| Agent Logic | `agents/data_integration.py` |
| Scheduled Syncs | `services/scheduler.py` |
| Configuration | `core/config.py` |
| Data Validation | `core/models.py` |

---

## 📝 Next Steps (Module 2)

Module 1 provides the **data foundation**. Module 2 will build:
- **CampaignManagerAgent**: Create and manage marketing campaigns
- **Campaign execution**: Actually send campaigns to channels
- **Campaign tracking**: Monitor campaign performance

Module 1's CDP and integrations are ready to support campaign management!

