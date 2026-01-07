# Marketing Automation Platform – Current Overview

## 1. Goal

Build a CrewAI-powered marketing automation system that unifies customer data, orchestrates cross-channel campaigns, and automates content delivery. The platform favors free-tier APIs and runs locally (FastAPI backend + Streamlit dashboard), with cloud deployment flexibility later.

## 2. Core Architecture

- **Backend**: FastAPI service exposing REST endpoints for campaign management, data sync, analytics, and agent operations.
- **Agents**: CrewAI agents coordinate data ingestion (`DataIntegrationAgent`) and campaign planning/execution (`CampaignManagerAgent`).
- **Database**: PostgreSQL stores the Customer Data Platform (CDP) entities—customers, campaigns, executions, analytics, credentials, users.
- **Task Queue**: Celery (Redis broker) handles asynchronous jobs, scheduled syncs, and campaign executions.
- **LLM Layer**: Ollama (local, free-tier) provides AI-assisted personalization; integrated via LangChain (`langchain-ollama`).
- **Frontend**: Streamlit dashboard (planned Module 3) for monitoring campaigns, analytics, and agent activity.

## 3. Key Integrations (Free-tier friendly)

- **YouTube Data API v3**: Channel analytics (API key) + video uploads (OAuth2).
- **Instagram Graph API** + **Facebook Graph API**: Content publishing & analytics.
- **SendGrid** (email) and **Twilio** (SMS): Automated messaging.
- Centralized credential management via `channel_credentials` table with per-channel handlers.

## 4. Module Progress

| Module | Scope | Status |
| ------ | ----- | ------ |
| 1. Foundations & Data Integration | Database models, CDP logic, API clients, scheduling | ✅ Complete – tested via `test_module1.py` |
| 2. Campaign Automation | Campaign manager agent, execution handlers, Celery orchestration | ✅ Complete – tested via `test_module2.py` and live YouTube upload |
| 3. Analytics & Dashboard | Streamlit dashboards, KPI tracking, alerting | ⏳ Pending |
| 4. Personalization Engine | AI-powered content suggestions, dynamic segmentation | ⏳ Pending |
| 5. Full Automation & Workflows | Multi-touch journeys, triggers, full CrewAI automation | ⏳ Pending |

## 5. What’s Done (Nov 2025)

- **Database/CDP**: SQLAlchemy models (`core/database.py`), CRUD helpers (`core/cdp.py`), Pydantic schemas.
- **Agents**: `DataIntegrationAgent` (sync all channels) and `CampaignManagerAgent` (create/execute campaigns).
- **Channel Handlers**: YouTube/Instagram/Facebook/Email/SMS integration classes with rate limiting, error handling, analytics sync.
- **Campaign Execution**:
  - Creates campaigns, stores configs & status.
  - Runs channel-specific executions via Celery (sync & retry aware).
  - Tracks executions in `campaign_executions`.
- **YouTube Upload Flow**:
  - OAuth2 setup scripts (`scripts/setup_youtube_oauth.py`, `scripts/generate_youtube_token.py`).
  - Real video uploads + Shorts validation (duration ≤60s, vertical 9:16).
  - `test_youtube_upload.py` performs full end-to-end test (campaign creation → upload → status).
- **Docs & Troubleshooting**:
  - `SETUP.md`, `QUICK_START.md`, `FACEBOOK_INSTAGRAM_API_SETUP.md`, `FIX_*` guides for OAuth issues, `DB_COMMANDS.md` for quick PostgreSQL inspection.
- **Infrastructure**: Docker Compose for PostgreSQL + Redis, uv-based dependency instructions, virtualenv workflows.

## 6. What Happens Next

1. **Module 3** (up next): Streamlit dashboards for analytics and monitoring.
2. Add automated tests for Instagram/Facebook/Twilio/SendGrid once credentials are ready.
3. Later modules: personalization workflows (Ollama) and multi-step automation.

## 7. Demo Checklist

1. Start infrastructure: `docker compose up -d`.
2. Run backend (`uvicorn`) & Celery worker.
3. Execute tests: `python test_module1.py`, `python test_module2.py`.
4. Run `python test_youtube_upload.py` for a real upload (ensure fresh `youtube_token.json`, short/standard mode).
5. Inspect database via `DB_COMMANDS.md` commands or connect with pgAdmin/DBeaver.

Use this as a quick read to understand what the platform is, how it’s built, and what’s planned next.

