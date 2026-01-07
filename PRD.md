# Product Requirements Document (PRD)
## CrewAI Marketing Automation Platform

**Version:** 1.0  
**Date:** November 2025  
**Status:** Module 1 & 2 Complete, Module 3+ Pending

---

## 1. Executive Summary

### 1.1 Product Overview
The CrewAI Marketing Automation Platform is a unified, AI-powered marketing automation system that enables businesses to orchestrate cross-channel marketing campaigns, synchronize customer data from multiple platforms, and automate content delivery across YouTube, Instagram, Facebook, Email, and SMS channels. The platform leverages CrewAI agents for intelligent orchestration, a centralized Customer Data Platform (CDP) for unified customer profiles, and free-tier APIs to minimize operational costs.

### 1.2 Key Value Propositions
- **Unified Multi-Channel Management**: Single platform to manage campaigns across 5+ marketing channels
- **AI-Powered Automation**: CrewAI agents intelligently orchestrate data sync and campaign execution
- **Cost-Effective**: Built on free-tier APIs (YouTube, Instagram, Facebook, SendGrid, Twilio) and local LLM (Ollama)
- **Real-Time Analytics**: Centralized CDP tracks customer engagement across all channels
- **Scalable Architecture**: FastAPI backend, PostgreSQL database, Celery task queue for async operations
- **Developer-Friendly**: Local-first development with Docker Compose, comprehensive documentation

### 1.3 Target Users
- **Marketing Teams**: Create, schedule, and monitor multi-channel campaigns
- **Data Analysts**: Access unified customer profiles and cross-channel analytics
- **Developers**: Extensible architecture for custom integrations and workflows
- **Small to Medium Businesses**: Cost-effective alternative to enterprise marketing platforms

---

## 2. Product Goals & Objectives

### 2.1 Primary Goals
1. **Automate Multi-Channel Campaign Execution**: Enable one-click campaign deployment across YouTube, Instagram, Facebook, Email, and SMS
2. **Unify Customer Data**: Aggregate customer interactions from all channels into a single CDP
3. **Reduce Manual Work**: Automate scheduling, execution, monitoring, and retry logic
4. **Minimize Costs**: Leverage free-tier APIs and local LLM to keep operational costs near zero
5. **Enable AI-Powered Personalization**: Use local LLM (Ollama) for content generation and optimization

### 2.2 Success Metrics
- **Campaign Execution Success Rate**: >95% successful campaign executions
- **Data Sync Frequency**: Hourly incremental syncs, daily full syncs
- **API Rate Limit Compliance**: 100% adherence to platform rate limits
- **System Uptime**: >99% availability for scheduled campaigns
- **Cost Efficiency**: <$10/month operational costs (excluding infrastructure)

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Streamlit Dashboard (Module 3 - Planned)           │  │
│  │  - Campaign Management UI                            │  │
│  │  - Analytics & Reporting                             │  │
│  │  - Real-time Monitoring                              │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    API Layer                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  FastAPI REST API                                   │  │
│  │  - Campaign CRUD endpoints                          │  │
│  │  - Data sync endpoints                              │  │
│  │  - Analytics endpoints                              │  │
│  │  - Authentication & Authorization                  │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Agent Layer (CrewAI)                      │
│  ┌──────────────────────┐  ┌──────────────────────────────┐  │
│  │ DataIntegrationAgent │  │ CampaignManagerAgent         │  │
│  │ - Sync channel data  │  │ - Create campaigns           │  │
│  │ - Transform to CDP   │  │ - Execute campaigns          │  │
│  │ - Handle rate limits │  │ - Monitor status             │  │
│  └──────────────────────┘  └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Campaign     │  │ CDP Service  │  │ Execution        │  │
│  │ Service      │  │              │  │ Handlers         │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Integration Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ YouTube │  │Instagram │  │ Facebook │  │ Email/SMS   │  │
│  │ API v3  │  │ Graph API│  │ Graph API│  │ (SendGrid/  │  │
│  │         │  │          │  │          │  │  Twilio)    │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Data & Task Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ PostgreSQL   │  │ Redis        │  │ Celery           │  │
│  │ (CDP Data)   │  │ (Task Queue) │  │ (Async Tasks)    │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Technology Stack

#### Backend Framework
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and settings management

#### Database & Storage
- **PostgreSQL**: Primary database for CDP, campaigns, executions, analytics
- **Redis**: Task queue broker and result backend for Celery

#### Task Queue & Scheduling
- **Celery**: Distributed task queue for async operations
- **Celery Beat**: Periodic task scheduler

#### AI/LLM Layer
- **CrewAI**: Multi-agent orchestration framework
- **Ollama**: Local LLM (free, unlimited usage)
- **LangChain**: LLM integration and tooling

#### API Integrations
- **YouTube Data API v3**: Channel analytics, video uploads (OAuth2)
- **Instagram Graph API**: Content publishing, analytics
- **Facebook Graph API**: Page management, analytics
- **SendGrid**: Email delivery (100 emails/day free tier)
- **Twilio**: SMS delivery

#### Frontend (Planned)
- **Streamlit**: Dashboard and monitoring interface

#### Infrastructure
- **Docker Compose**: Local development environment
- **Python 3.10+**: Runtime environment

---

## 4. Core Features & Functionality

### 4.1 Customer Data Platform (CDP)

#### 4.1.1 Customer Management
- **Unified Customer Profiles**: Single source of truth for customer data across all channels
- **Customer Attributes**: Flexible JSON storage for custom attributes
- **Customer Events**: Track engagement events (opens, clicks, views, subscribes) across channels
- **Data Unification**: Merge data from multiple channels into unified profiles

#### 4.1.2 Data Models
- **Customers Table**: Core customer information (email, phone, attributes)
- **Customer Events Table**: Event tracking (event_type, channel, timestamp, data)
- **Analytics Snapshots Table**: Time-series metrics for campaigns

#### 4.1.3 Data Sync Capabilities
- **Incremental Sync**: Hourly syncs of new data since last sync
- **Full Sync**: Daily complete data refresh
- **Channel-Specific Sync**: Individual channel sync on demand
- **Rate Limit Handling**: Automatic rate limit compliance per API

### 4.2 Campaign Management

#### 4.2.1 Campaign Lifecycle
1. **Draft**: Campaign created but not scheduled
2. **Scheduled**: Campaign scheduled for future execution
3. **Running**: Campaign execution in progress
4. **Paused**: Campaign temporarily paused
5. **Completed**: Campaign successfully executed
6. **Failed**: Campaign execution failed (with retry capability)

#### 4.2.2 Campaign Configuration
- **Channel Selection**: YouTube, Instagram, Facebook, Email, SMS
- **Content Configuration**: Channel-specific content (titles, descriptions, media, tags)
- **Scheduling**: Immediate or scheduled execution
- **Targeting**: Audience segmentation (future enhancement)
- **Privacy Settings**: Channel-specific privacy controls

#### 4.2.3 Campaign Execution
- **Channel-Specific Handlers**: Dedicated execution handlers per channel
- **Validation**: Pre-execution config validation
- **Error Handling**: Comprehensive error capture and reporting
- **Retry Logic**: Automatic retry for failed executions (configurable max retries)
- **Result Tracking**: Detailed execution results stored in database

### 4.3 YouTube Integration

#### 4.3.1 Features
- **Video Upload**: Upload videos to YouTube (requires OAuth2)
- **YouTube Shorts Support**: Automatic validation for Shorts (≤60s, vertical 9:16)
- **Channel Analytics**: Sync subscriber count, view count, video count
- **Video Analytics**: Track views, likes, comments per video
- **Privacy Controls**: Public, unlisted, or private uploads

#### 4.3.2 Authentication
- **API Key**: Required for read operations (channel stats, analytics)
- **OAuth2**: Required for video uploads (token stored in `youtube_token.json`)

#### 4.3.3 Rate Limits
- **Daily Quota**: 10,000 units/day (free tier)
- **Automatic Rate Limiting**: Built-in rate limit handler

### 4.4 Instagram Integration

#### 4.4.1 Features
- **Content Publishing**: Post images/videos to Instagram
- **Stories Support**: Post to Instagram Stories (planned)
- **Account Analytics**: Sync follower count, engagement metrics
- **Post Analytics**: Track likes, comments, reach per post

#### 4.4.2 Authentication
- **Access Token**: Facebook/Instagram Graph API access token
- **App Credentials**: Facebook App ID and App Secret

### 4.5 Facebook Integration

#### 4.5.1 Features
- **Page Posting**: Publish posts to Facebook Pages
- **Page Insights**: Sync page likes, reach, engagement
- **Post Analytics**: Track post performance metrics

#### 4.5.2 Authentication
- **Access Token**: Facebook Graph API access token
- **App Credentials**: Facebook App ID and App Secret

### 4.6 Email/SMS Integration

#### 4.6.1 Email (SendGrid)
- **Email Sending**: Send transactional and marketing emails
- **Delivery Tracking**: Track sent, delivered, opened, clicked
- **Free Tier**: 100 emails/day

#### 4.6.2 SMS (Twilio)
- **SMS Sending**: Send SMS messages to recipients
- **Delivery Tracking**: Track sent and delivered status
- **Free Tier**: Trial credits available

### 4.7 Data Integration Agent

#### 4.7.1 Responsibilities
- **Multi-Channel Sync**: Orchestrate data sync from all channels
- **Data Transformation**: Convert channel-specific data to unified CDP format
- **Rate Limit Management**: Handle API rate limits intelligently
- **Error Recovery**: Retry failed syncs with exponential backoff

#### 4.7.2 Sync Workflow
1. Initialize channel integrations with credentials
2. Test API connections
3. Fetch data from each channel (respecting rate limits)
4. Transform data to unified format
5. Store in CDP (customers, events, analytics)
6. Log sync results and errors

### 4.8 Campaign Manager Agent

#### 4.8.1 Responsibilities
- **Campaign Creation**: Validate and create new campaigns
- **Campaign Execution**: Orchestrate campaign execution across channels
- **Status Monitoring**: Track campaign and execution status
- **Failure Handling**: Manage retries and error recovery

#### 4.8.2 Execution Workflow
1. Validate campaign configuration
2. Create execution record
3. Get channel-specific execution handler
4. Execute campaign (upload video, send email, post content, etc.)
5. Update execution status and results
6. Update campaign status
7. Log execution details

### 4.9 Task Scheduling & Automation

#### 4.9.1 Celery Tasks
- **sync_all_channels**: Hourly incremental sync, daily full sync
- **sync_single_channel**: On-demand single channel sync
- **execute_campaign**: Execute a specific campaign
- **execute_scheduled_campaigns**: Check and execute scheduled campaigns (every 5 minutes)
- **retry_failed_campaigns**: Retry failed executions (hourly, max 3 retries)

#### 4.9.2 Scheduled Jobs
- **Hourly Data Sync**: Incremental sync from all channels
- **Daily Full Sync**: Complete data refresh
- **Campaign Execution Check**: Every 5 minutes for scheduled campaigns
- **Failed Campaign Retry**: Hourly retry of failed campaigns

---

## 5. Database Schema

### 5.1 Core Tables

#### Customers
- `customer_id` (PK)
- `email` (unique, indexed)
- `phone` (indexed)
- `attributes` (JSON)
- `created_at`, `updated_at`

#### Campaigns
- `campaign_id` (PK)
- `name`
- `channel` (enum: youtube, instagram, facebook, email, sms)
- `status` (enum: draft, scheduled, running, paused, completed, failed)
- `schedule` (datetime, nullable)
- `config` (JSON - channel-specific configuration)
- `created_by` (FK to users)
- `created_at`, `updated_at`

#### Campaign Executions
- `execution_id` (PK)
- `campaign_id` (FK)
- `status` (enum: pending, running, success, failed, cancelled)
- `started_at`, `completed_at`
- `results` (JSON - execution results)
- `error_message` (text, nullable)
- `created_at`

#### Customer Events
- `event_id` (PK)
- `customer_id` (FK)
- `event_type` (string - open, click, view, subscribe, etc.)
- `channel` (enum)
- `timestamp`
- `data` (JSON - event-specific data)

#### Channel Credentials
- `credential_id` (PK)
- `channel_type` (enum)
- `encrypted_credentials` (text - encrypted JSON)
- `user_id` (FK, nullable)
- `is_active` (boolean)
- `created_at`, `updated_at`

#### Analytics Snapshots
- `snapshot_id` (PK)
- `campaign_id` (FK)
- `metrics` (JSON - aggregated metrics)
- `timestamp`

#### Users
- `user_id` (PK)
- `username` (unique)
- `email` (unique)
- `hashed_password`
- `role` (enum: admin, manager, viewer)
- `is_active` (boolean)
- `created_at`, `updated_at`

---

## 6. API Specifications

### 6.1 Campaign Endpoints

#### Create Campaign
```
POST /api/campaigns
Body: {
  "name": "string",
  "channel": "youtube|instagram|facebook|email|sms",
  "config": { ... },
  "schedule": "datetime (optional)"
}
Response: { "campaign_id": int, "status": "draft", ... }
```

#### Get Campaign
```
GET /api/campaigns/{campaign_id}
Response: { "campaign_id": int, "name": "string", ... }
```

#### List Campaigns
```
GET /api/campaigns?status=draft&channel=youtube&limit=100
Response: { "count": int, "campaigns": [...] }
```

#### Execute Campaign
```
POST /api/campaigns/{campaign_id}/execute
Response: { "success": bool, "execution_id": int, "results": {...} }
```

#### Get Campaign Status
```
GET /api/campaigns/{campaign_id}/status
Response: {
  "campaign_id": int,
  "status": "string",
  "executions": {...},
  "metrics": {...}
}
```

### 6.2 Data Sync Endpoints

#### Sync All Channels
```
POST /api/sync/all
Body: { "force_full_sync": bool }
Response: { "overall_success": bool, "channels": {...} }
```

#### Sync Single Channel
```
POST /api/sync/{channel}
Body: { "force_full_sync": bool }
Response: { "success": bool, "records_synced": int, ... }
```

### 6.3 Analytics Endpoints

#### Get Customer Profile
```
GET /api/customers/{customer_id}/profile
Response: {
  "customer_id": int,
  "email": "string",
  "channels": {...},
  "recent_events": [...]
}
```

#### Get Campaign Analytics
```
GET /api/campaigns/{campaign_id}/analytics
Response: {
  "campaign_id": int,
  "metrics": {...},
  "executions": [...]
}
```

---

## 7. User Workflows

### 7.1 Creating and Executing a YouTube Campaign

1. **Setup OAuth2** (one-time):
   - Run `python scripts/setup_youtube_oauth.py`
   - Run `python scripts/generate_youtube_token.py`
   - Token saved to `youtube_token.json`

2. **Create Campaign**:
   - Configure campaign: name, channel (YouTube), config (title, description, video_path, tags, privacy_status)
   - Campaign created with status "draft"

3. **Execute Campaign**:
   - System validates video file exists
   - If Shorts: validates duration ≤60s and vertical 9:16 aspect ratio
   - Uploads video via YouTube API
   - Updates execution status and results
   - Returns video ID and URL

4. **Monitor Status**:
   - Check campaign status via API or dashboard
   - View execution results (video_id, channel_stats)
   - Track analytics over time

### 7.2 Data Synchronization Workflow

1. **Automatic Sync** (Celery Beat):
   - Hourly: Incremental sync (last 24 hours)
   - Daily: Full sync (all data)

2. **Manual Sync**:
   - Trigger via API endpoint
   - Select channels to sync
   - Force full sync option

3. **Sync Process**:
   - DataIntegrationAgent initializes channel integrations
   - Fetches data from each channel API
   - Transforms to unified format
   - Stores in CDP (customers, events, analytics)
   - Logs results and errors

### 7.3 Multi-Channel Campaign Workflow

1. **Create Campaigns** for each channel:
   - YouTube: Video upload campaign
   - Instagram: Image/video post campaign
   - Facebook: Page post campaign
   - Email: Email blast campaign
   - SMS: SMS campaign

2. **Schedule Execution**:
   - Set execution time for each campaign
   - Or execute immediately

3. **Monitor Execution**:
   - Track status of each campaign
   - View execution results
   - Handle failures with automatic retry

---

## 8. Security & Compliance

### 8.1 Authentication & Authorization
- **JWT-based Authentication**: Secure token-based auth
- **Role-Based Access Control**: Admin, Manager, Viewer roles
- **Password Hashing**: bcrypt for password storage

### 8.2 Credential Management
- **Encrypted Storage**: Channel credentials encrypted in database
- **OAuth2 Token Management**: Secure storage of OAuth tokens
- **Credential Rotation**: Support for credential updates

### 8.3 Data Privacy
- **Customer Data Protection**: Secure storage of PII
- **API Key Security**: Environment variable storage
- **Audit Logging**: Track all campaign executions and data access

### 8.4 Rate Limit Compliance
- **Automatic Rate Limiting**: Built-in rate limit handlers per API
- **Quota Monitoring**: Track API usage against quotas
- **Graceful Degradation**: Handle rate limit errors gracefully

---

## 9. Performance Requirements

### 9.1 Response Times
- **API Endpoints**: <500ms for standard operations
- **Campaign Execution**: <5 minutes for video uploads, <30s for other channels
- **Data Sync**: <10 minutes for full channel sync

### 9.2 Scalability
- **Concurrent Campaigns**: Support 100+ concurrent campaign executions
- **Database**: PostgreSQL with connection pooling (pool_size=10, max_overflow=20)
- **Task Queue**: Celery with Redis for horizontal scaling

### 9.3 Reliability
- **Uptime**: >99% availability
- **Error Recovery**: Automatic retry for failed operations
- **Data Consistency**: ACID transactions for critical operations

---

## 10. Deployment & Infrastructure

### 10.1 Development Environment
- **Docker Compose**: PostgreSQL + Redis containers
- **Local LLM**: Ollama running locally
- **Environment Variables**: `.env` file for configuration

### 10.2 Production Deployment (Planned)
- **Container Orchestration**: Docker/Kubernetes
- **Database**: Managed PostgreSQL service
- **Task Queue**: Managed Redis service
- **Monitoring**: Application and infrastructure monitoring
- **Backup**: Automated database backups

### 10.3 CI/CD (Planned)
- **Automated Testing**: Unit and integration tests
- **Deployment Pipeline**: Automated deployment on merge
- **Version Control**: Git-based workflow

---

## 11. Future Enhancements (Roadmap)

### 11.1 Module 3: Analytics & Dashboard (Planned)
- **Streamlit Dashboard**: 
  - Campaign management UI
  - Real-time analytics visualization
  - Customer profile viewer
  - Execution monitoring
- **KPI Tracking**: 
  - Campaign performance metrics
  - Channel comparison
  - ROI calculations
- **Alerting**: 
  - Campaign failure notifications
  - Performance threshold alerts

### 11.2 Module 4: Personalization Engine (Planned)
- **AI-Powered Content Generation**: 
  - Generate captions using Ollama
  - Optimize content for each channel
  - A/B testing suggestions
- **Dynamic Segmentation**: 
  - Customer segmentation based on behavior
  - Personalized campaign targeting
- **Content Recommendations**: 
  - Suggest optimal posting times
  - Content format recommendations

### 11.3 Module 5: Full Automation & Workflows (Planned)
- **Multi-Touch Journeys**: 
  - Cross-channel customer journeys
  - Trigger-based automation
  - Conditional workflows
- **Advanced Scheduling**: 
  - Timezone-aware scheduling
  - Optimal time detection
- **Workflow Builder**: 
  - Visual workflow designer
  - Custom automation rules

### 11.4 Additional Integrations (Planned)
- **Twitter/X API**: Social media posting
- **LinkedIn API**: Professional network campaigns
- **TikTok API**: Short-form video platform
- **WhatsApp Business API**: Messaging campaigns

---

## 12. Testing & Quality Assurance

### 12.1 Test Coverage
- **Unit Tests**: Core services and utilities
- **Integration Tests**: API endpoints and database operations
- **End-to-End Tests**: Full campaign execution workflows

### 12.2 Test Files
- `test_module1.py`: Foundation & DataIntegrationAgent tests
- `test_module2.py`: CampaignManagerAgent tests
- `test_youtube_upload.py`: YouTube upload end-to-end test
- `test_youtube_campaign.py`: YouTube campaign workflow test

### 12.3 Quality Metrics
- **Code Coverage**: Target >80%
- **API Response Validation**: All endpoints validated
- **Error Handling**: Comprehensive error scenarios tested

---

## 13. Documentation

### 13.1 Technical Documentation
- **README.md**: Project overview and quick start
- **SETUP.md**: Detailed setup instructions
- **PROJECT_OVERVIEW.md**: Architecture and module status
- **AGENTS_OVERVIEW.md**: CrewAI agents documentation
- **DB_COMMANDS.md**: Database inspection commands
- **QUICK_START.md**: Quick setup guide

### 13.2 API Documentation
- **OpenAPI/Swagger**: Auto-generated API docs (FastAPI)
- **Endpoint Examples**: Request/response examples
- **Authentication Guide**: OAuth2 setup for YouTube

### 13.3 User Guides
- **Campaign Creation Guide**: Step-by-step campaign setup
- **YouTube Upload Guide**: OAuth2 setup and video upload
- **Troubleshooting Guide**: Common issues and solutions

---

## 14. Success Criteria & KPIs

### 14.1 Functional Success
- ✅ **Module 1 Complete**: Database, CDP, API integrations, DataIntegrationAgent
- ✅ **Module 2 Complete**: CampaignManagerAgent, execution handlers, YouTube upload
- ⏳ **Module 3 Pending**: Streamlit dashboard, analytics visualization
- ⏳ **Module 4 Pending**: AI personalization engine
- ⏳ **Module 5 Pending**: Full automation workflows

### 14.2 Performance Success
- **Campaign Execution Rate**: >95% success rate
- **Data Sync Accuracy**: 100% data integrity
- **API Compliance**: 100% rate limit adherence
- **System Uptime**: >99% availability

### 14.3 Business Success
- **Cost Efficiency**: <$10/month operational costs
- **Time Savings**: 80% reduction in manual campaign management
- **Multi-Channel Reach**: Support for 5+ marketing channels
- **Scalability**: Support for 100+ concurrent campaigns

---

## 15. Risk Assessment & Mitigation

### 15.1 Technical Risks
- **API Rate Limits**: Mitigated by built-in rate limit handlers
- **API Changes**: Mitigated by abstraction layers and version pinning
- **Database Performance**: Mitigated by indexing and connection pooling
- **OAuth Token Expiration**: Mitigated by token refresh mechanisms

### 15.2 Operational Risks
- **Infrastructure Downtime**: Mitigated by Docker Compose and monitoring
- **Data Loss**: Mitigated by database backups and transaction logging
- **Credential Compromise**: Mitigated by encryption and secure storage

### 15.3 Business Risks
- **Free Tier Limitations**: Mitigated by quota monitoring and upgrade paths
- **Platform Policy Changes**: Mitigated by flexible architecture and abstraction

---

## 16. Appendices

### 16.1 API Rate Limits
- **YouTube Data API v3**: 10,000 units/day
- **Instagram Graph API**: Varies by endpoint
- **Facebook Graph API**: Varies by endpoint
- **SendGrid**: 100 emails/day (free tier)
- **Twilio**: Trial credits, then pay-as-you-go

### 16.2 Environment Variables
See `.env.example` for complete list of configuration options.

### 16.3 Dependencies
See `requirements.txt` for complete Python package dependencies.

---

## 17. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Nov 2025 | System | Initial PRD based on current implementation |

---

**Document Status**: This PRD reflects the current state of the system as of November 2025, with Modules 1 & 2 complete and Modules 3-5 planned for future development.

