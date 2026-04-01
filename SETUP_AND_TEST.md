# Marketing Automation System — Windows setup (IDE terminal)

Use the **integrated terminal** in Cursor or VS Code (default is **PowerShell**). Open the project folder as the workspace root so paths match below.

**Stack:** Next.js 15 + Clerk (port **3000**), FastAPI (port **8000**), PostgreSQL + Redis in Docker, Celery worker.

---

## Prerequisites

- **Docker Desktop** for Windows (running before you start containers)
- **Python 3.10+** on PATH (`python --version`)
- **Node.js 18+** on PATH (`node --version`)

---

## 1. Open the project root in the terminal

In the IDE: **Terminal → New Terminal**. You should be at the repo root (where `package.json` and `docker-compose.yml` live). If not:

```powershell
cd c:\Users\anish\AI\marketing-automation-system
```

(Adjust the path if your clone lives elsewhere.)

---

## 2. `.env` file

Create **`.env`** in the project root. Minimum to run the UI and local stack:

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk — from [dashboard.clerk.com](https://dashboard.clerk.com/) |
| `CLERK_SECRET_KEY` | Clerk secret |
| `DATABASE_URL` | `postgresql://user:password@localhost:5432/marketing_cdp` |
| `REDIS_URL` | `redis://localhost:6379/0` |

Recommended:

- `ENABLE_NGROK=false` — avoids ngrok on API startup unless you use it
- `JWT_SECRET_KEY` — non-default secret for anything beyond solo testing

Optional: YouTube, Meta, SendGrid, Twilio, Ollama/Groq keys as needed (see `core/config.py`). Frontend talks to **`http://localhost:8000/api`** by default (`src/services/api.ts`).

---

## 3. Python venv — do this first

**Activate the venv before any `pip`, `python`, or `celery` command.** Every new terminal that runs Python tools must run `Activate.ps1` again.

If PowerShell blocks scripts, run once:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

From the project root:

```powershell
cd c:\Users\anish\AI\marketing-automation-system
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

You should see `(.venv)` at the start of the prompt. **Keep this terminal** for Docker + API below, or repeat `cd` + `Activate.ps1` in any terminal where you run the backend.

---

## 4. Docker: Postgres + Redis

In a terminal where you are **not** required to use venv (Docker is separate). Often the **same** terminal as step 3 is fine:

```powershell
docker compose up -d
docker compose ps
```

Wait until **postgres** and **redis** show as healthy.

---

## 5. Python deps, DB init, API

**Venv must be active** (`(.venv)` in the prompt). If not:

```powershell
cd c:\Users\anish\AI\marketing-automation-system
.\.venv\Scripts\Activate.ps1
```

Then:

```powershell
pip install -r requirements.txt
python scripts\init_db.py
python -m api.main
```

Leave this terminal running. Check **http://localhost:8000/docs** and **http://localhost:8000/api/status**.

---

## 6. Celery worker

**New terminal** — **start venv first**, then Celery:

```powershell
cd c:\Users\anish\AI\marketing-automation-system
.\.venv\Scripts\Activate.ps1
celery -A services.scheduler worker --loglevel=info --pool=solo
```

Leave running. `--pool=solo` is appropriate on Windows.

---

## 7. Next.js frontend

**Another new terminal** (no Python venv needed):

```powershell
cd c:\Users\anish\AI\marketing-automation-system
npm install
npx next dev
```

Open **http://localhost:3000** and sign in with Clerk.

> `npm run dev` runs `dev.sh` (Bash), which is not ideal in PowerShell. Prefer **`npx next dev`** in the IDE terminal on Windows.

---

## 8. Quick verification

1. Docker: `docker compose ps` — postgres and redis up  
2. Browser: **http://localhost:8000/api/status** — `"database": "active"`  
3. Browser: **http://localhost:3000** — app loads, Clerk works  
4. Celery terminal: no Redis connection errors  

---

## 9. Stop everything

- **Ctrl+C** in the API, Celery, and Next terminals  
- Stop containers:

```powershell
docker compose stop
```

Wipe DB data (optional):

```powershell
docker compose down -v
```

---

## Notes (Windows)

- Optional **`UPLOAD_DIR`** in `.env` overrides the default project `uploads` folder (see `api/main.py`).  
- SQL examples for the DB container: **`DB_COMMANDS.md`**.  

### Clerk (clock skew, redirect loop, dev notices)

- **`Clock skew` / `JWT iat is in the future`:** Middleware uses **60s** JWT clock skew in development (Clerk default is 5s). Override anytime with **`CLERK_CLOCK_SKEW_IN_MS`** (milliseconds) in `.env`. Still sync Windows time: **Settings → Time & language → Date & time → Sync now**.  
- **`Infinite redirect loop`:** Usually bad or mixed keys — **`NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`** and **`CLERK_SECRET_KEY`** must be from the **same** Clerk application (Clerk Dashboard → API Keys). After fixing keys, clear site data for `localhost:3000` or use a private window.  
- **`cannot_render_single_session_enabled` (dev only):** Normal if you already have a session and the app disallows multiple sessions — modal sign-in is a no-op. Use **Sign out** in the user menu, or an incognito window, to test sign-in again; or enable multiple sessions in the Clerk Dashboard if you want that behavior.  
