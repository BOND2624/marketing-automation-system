# CrewAI Marketing Automation Platform

A unified marketing automation platform powered by CrewAI, integrating YouTube, Instagram, Facebook, and Email/SMS APIs for campaign automation, personalization, and analytics.

## Features

- Multi-channel marketing automation (YouTube, Instagram, Facebook, Email/SMS)
- AI-powered personalization and optimization
- Centralized Customer Data Platform (CDP)
- Real-time analytics and dashboards
- Role-based access control and security

## Tech Stack

- **Framework**: CrewAI, FastAPI, Streamlit
- **Database**: PostgreSQL
- **Task Queue**: Celery + Redis
- **LLM**: Ollama (free tier, local) or Groq/Hugging Face

## Quick Start

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Ollama (for local LLM) or API keys for Groq/Hugging Face
- `uv` (optional, but recommended for faster package installation)

### Setup

**📖 For detailed setup instructions, see [SETUP.md](SETUP.md)**

Quick setup:

1. Install uv (optional):
```bash
# Windows:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create virtual environment:
```bash
# Using uv (recommended):
uv venv
# Or using Python:
python -m venv venv
```

3. Activate virtual environment:
```bash
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

4. Install dependencies:
```bash
# Using uv (faster):
uv pip install -r requirements.txt
# Or using pip:
pip install -r requirements.txt
```

5. Setup environment variables:
```bash
cp .env.example .env  # Windows: copy .env.example .env
# Edit .env with your API keys and configuration
```

6. Start Docker services:
```bash
docker compose up -d
```

**Note:** If `docker compose` doesn't work, try `docker-compose` (older Docker versions)

7. Initialize database:
```bash
python scripts/init_db.py
```

8. Test Module 1:
```bash
python test_module1.py
```

## Free API Tiers

- **YouTube Data API v3**: 10,000 units/day
- **Instagram Graph API**: Free (requires Facebook Developer account)
- **Facebook Graph API**: Free (requires Facebook Developer account)
- **SendGrid**: 100 emails/day
- **Ollama**: Completely free, unlimited usage (local)

## Project Structure

See the implementation plan for detailed architecture.

## Development Status

✅ **Module 1 Complete**: Foundation & DataIntegrationAgent
- Database models and CDP core
- API integrations (YouTube, Instagram, Facebook, Email/SMS)
- DataIntegrationAgent with CrewAI
- Celery scheduler for periodic syncs

✅ **Module 2 Complete**: CampaignManagerAgent
- Campaign creation and management
- Multi-channel execution handlers
- Campaign scheduling and automation
- Status monitoring and retry logic
- **Tested and working with YouTube!**

📋 **See [SETUP.md](SETUP.md) for setup and testing instructions**

