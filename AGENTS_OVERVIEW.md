# CrewAI & Agent Overview

## 1. CrewAI in a Nutshell

- **CrewAI** is a Python framework for building cooperative AI agents that can plan tasks, call tools (APIs, databases, code), and work together.
- Agents share a “memory” (state) and can hand off work to each other through task queues or direct messaging.
- Each agent has:
  - A **role** (what it is responsible for)
  - A **toolkit** (functions it can call)
  - Optional **instructions/prompts** that shape how it reasons
  - An **LLM backend** (here: Ollama for free/local inference)

In our platform, CrewAI agents run inside the FastAPI backend. They orchestrate workflows (e.g., syncing data, managing campaigns) while the rest of the stack handles persistence, scheduling, and API calls.

## 2. How AI Agents Work Here

1. **Receive a task**: e.g., “sync all channel data” or “launch this campaign.”
2. **Plan**: break the request into smaller steps (what data to read, which APIs to call).
3. **Use tools**: call helper functions (database queries, integrations) rather than hallucinating.
4. **Update state**: write results back to the database, log outcomes, trigger follow-up tasks.
5. **Hand off** (optional): if another agent is better suited for the next step, delegate through Celery or direct function calls.

Because we rely on deterministic integrations (SQLAlchemy, YouTube API, etc.), agents mostly act as orchestrators rather than pure text generators.

## 3. Agents We’ve Built

### DataIntegrationAgent (`agents/data_integration.py`)

- **Role**: Gather customer and campaign activity from external platforms and push into the CDP.
- **Tools**:
  - YouTube/Instagram/Facebook API integrations (`api_integrations/*.py`)
  - CDP helpers (`core/cdp.py`) to upsert customers, events, analytics snapshots.
- **Typical flow**:
  1. Fetch latest metrics or events from each channel.
  2. Normalize data into a consistent customer-event structure.
  3. Store events in `customer_events`, update `analytics_snapshots`, refresh customer profiles.
  4. Schedule periodic syncs via Celery (`services/scheduler.py`).
- **LLM usage**: Minimal; may use Ollama for deduplication heuristics or interpreting text fields later.

### CampaignManagerAgent (`agents/campaign_manager.py`)

- **Role**: Create campaigns, schedule executions, and coordinate channel-specific tasks.
- **Tools**:
  - Campaign service (`services/campaign_service.py`) for CRUD operations.
  - Execution handlers (`services/execution_handlers.py`) for YouTube, Instagram, Facebook, Email, SMS.
  - Celery tasks for async execution and retries (`services/scheduler.py`).
- **Typical flow**:
  1. Validate campaign configs (channel, media, schedule).
  2. Persist campaign in the database (`campaigns` table).
  3. When triggered, call the appropriate execution handler (e.g., `YouTubeExecutionHandler`) with credentials.
  4. Update execution results in `campaign_executions`, including video IDs, stats, errors.
  5. Optionally report back to other services (dashboard, alerts).
- **LLM usage**: For future personalization (e.g., generating captions); currently relies on deterministic logic.

## 4. CrewAI Workflow Inside the App

1. **API Request**: FastAPI endpoint receives a request (e.g., `/campaigns/create`).
2. **Agent Invocation**: The request triggers the relevant CrewAI agent method.
3. **Agent Reasoning**: The agent decides which tools/services to call.
4. **Execution**: Tools run (SQL, API calls). Results stored in PostgreSQL.
5. **Response**: Agent (or service) returns structured data to the API/CLI/test script.

Celery + Redis handle background tasks initiated by agents (e.g., scheduled syncs, delayed campaign execution). This lets agents stay focused on orchestration while workers handle long-running jobs.

## 5. Future Agent Enhancements

- **Personalization Agent**: Generate tailored email/Instagram captions using Ollama.
- **Analytics Agent**: Summarize KPI trends, highlight anomalies, recommend actions.
- **Workflow Agent**: Automate cross-channel journeys (if customer clicks email → send follow-up SMS, etc.).

These agents will reuse the same CrewAI infrastructure, tool libraries, and database models already in place. The groundwork laid in Modules 1 & 2 makes it easy to slot in new agents as we expand functionality.

