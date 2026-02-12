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

## 5. Completed Steps (Summary)

- **Module 1**: Database/CDP, API integrations (read/sync), `DataIntegrationAgent`, Celery sync tasks.
- **Module 2**: `CampaignManagerAgent`, execution handlers, Celery campaign execution & retries.
- **YouTube**: Full setup (OAuth credentials, token script, docs) and **real upload** (videos + Shorts validation); tested via `test_youtube_upload.py`.
- **Instagram & Facebook – setup**: Brief setup in `TEAM_SETUP_GUIDE.md` (Section 6); detailed guide in `FACEBOOK_INSTAGRAM_API_SETUP.md`. API integrations for **read/sync** (account info, posts, insights). Execution handlers exist but **do not yet publish** (simulated post only).
- **Instagram & Facebook – upload/publish**: **Not implemented**. Handlers return a simulated `post_id`; real Instagram Graph API (container → publish) and Facebook Graph API (page post) calls are pending.
- **Docs**: `SETUP.md`, `QUICK_START.md`, `TEAM_SETUP_GUIDE.md`, `FACEBOOK_INSTAGRAM_API_SETUP.md`, `FIX_*` guides, `DB_COMMANDS.md`, `OLLAMA_SETUP.md`.
- **Infrastructure**: Docker Compose (PostgreSQL + Redis), uv/venv instructions.

## 6. Remaining Steps

1. **Facebook & Instagram upload/publish**: Implement real posting (Instagram: create container → publish; Facebook: page post) in `api_integrations` and `execution_handlers`; add token/credential flow if needed.
2. **Module 3** (next): Streamlit dashboards for analytics and monitoring.
3. Add automated tests for Instagram/Facebook/Twilio/SendGrid once credentials are ready.
4. **Module 4**: Personalization engine (Ollama).
5. **Module 5**: Full automation & workflows.

## 7. Demo Checklist

1. Start infrastructure: `docker compose up -d`.
2. Run backend (`uvicorn`) & Celery worker.
3. Execute tests: `python test_module1.py`, `python test_module2.py`.
4. Run `python test_youtube_upload.py` for a real upload (ensure fresh `youtube_token.json`, short/standard mode).
5. Inspect database via `DB_COMMANDS.md` commands or connect with pgAdmin/DBeaver.

Use this as a quick read to understand what the platform is, how it’s built, and what’s planned next.

