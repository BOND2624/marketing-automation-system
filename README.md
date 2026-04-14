# Marketing Automation System

A **unified workspace** for social and marketing workflows: one dashboard to manage uploads, publish to **Facebook**, **Instagram**, and **YouTube**, track performance, work with a simple **customer CDP**, and use **AI-assisted copy** (via Ollama) before anything goes live.

Instead of opening each network’s app and repeating the same steps, you configure integrations once and operate from a single place.

---

## What you can do

- **Dashboard** — Channel stats, health, and quick insights  
- **Social Publish** — Create posts; YouTube Short vs standard video checks; optional AI title, caption, tags  
- **Media Command** — Upload queue and publish pipeline (with Celery where used)  
- **Integrations** — Meta and YouTube tokens / API setup  
- **Customer CDP** — Customer-centric view and activity concepts  
- **Social performance** — Cross-channel metrics where APIs allow  

---

## Stack (simple view)

| Layer | Technology |
|--------|------------|
| **Web app** | Next.js 15, React 18, Tailwind CSS |
| **Auth** | Clerk |
| **API** | FastAPI (`python -m api.main`, port **8000**) |
| **Data** | PostgreSQL + Redis (Docker) |
| **Background jobs** | Celery |
| **AI copy (optional)** | Ollama + LangChain (`services/personalization_service.py`) |

The browser talks to the API at **`http://localhost:8000/api`** (see `src/services/api.ts`).

---

## Prerequisites

- **Docker Desktop** (for Postgres + Redis)  
- **Python 3.10+**  
- **Node.js 18+**  

---

## Quick start

1. **Clone** the repo and open the folder as your project root.  
2. **Create `.env`** in the root (see table below). Copy from your secrets; never commit real keys.  
3. **Python venv** (PowerShell example):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python scripts\init_db.py
   ```

4. **Start databases:**

   ```powershell
   docker compose up -d
   ```

5. **API** (venv active):

   ```powershell
   python -m api.main
   ```

   Open [http://localhost:8000/docs](http://localhost:8000/docs) and [http://localhost:8000/api/status](http://localhost:8000/api/status).

6. **Celery** (new terminal, venv active; on Windows use `solo` pool):

   ```powershell
   celery -A services.scheduler worker --loglevel=info --pool=solo
   ```

7. **Frontend:**

   ```powershell
   npm install
   npx next dev
   ```

   Open [http://localhost:3000](http://localhost:3000) and sign in with Clerk.

**Windows-specific tips, Clerk troubleshooting, and full step-by-step:** **[SETUP_AND_TEST.md](./SETUP_AND_TEST.md)**.

On macOS/Linux, use `source .venv/bin/activate` instead of `Activate.ps1`, and you can often use Celery’s default pool instead of `--pool=solo`.

---

## Environment variables (minimum)

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk (frontend) |
| `CLERK_SECRET_KEY` | Clerk (server) |
| `DATABASE_URL` | e.g. `postgresql://user:password@localhost:5432/marketing_cdp` |
| `REDIS_URL` | e.g. `redis://localhost:6379/0` |

**Recommended:** `ENABLE_NGROK=false` for local dev unless you need a public API URL.

**Integrations:** YouTube API key, Meta tokens, Ollama URL/model, etc. are documented in **`core/config.py`** and **SETUP_AND_TEST.md**.

---

## Project layout (where things live)

| Path | Role |
|------|------|
| `src/` | Next.js app: dashboard, views, API client |
| `api/` | FastAPI app and route modules |
| `core/` | Config, database, models |
| `services/` | Celery, personalization, campaign execution, analytics |
| `agents/` | Campaign manager and related agents |
| `api_integrations/` | YouTube, Meta, email/SMS helpers |
| `scripts/` | DB init, token helpers |
| `uploads/` | Default local upload directory (configurable) |

---

## More docs

- **[SETUP_AND_TEST.md](./SETUP_AND_TEST.md)** — Full local setup (especially Windows + PowerShell)  
- **[DB_COMMANDS.md](./DB_COMMANDS.md)** — Handy SQL for the Docker Postgres container  

---

## Scripts (npm)

- `npm run build` — Production build  
- `npm run start` — Run production server (after `build`)  
- `npm run lint` — ESLint  

On Windows, prefer **`npx next dev`** for development instead of `npm run dev` if `dev.sh` is not available in your shell.
