# Quick Start Guide - Module 1

## One-Command Setup (After Prerequisites)

```bash
# 1. Install uv (if not installed)
# Windows:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Setup project
uv venv && .\venv\Scripts\activate && uv pip install -r requirements.txt && docker compose up -d && python scripts/init_db.py
```
```

## Essential Commands

### Virtual Environment
```bash
# Create (uv)
uv venv

# Create (standard)
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Deactivate
deactivate
```

### Dependencies
```bash
# Install with uv (faster)
uv pip install -r requirements.txt

# Install with pip
pip install -r requirements.txt
```

### Docker Services
```bash
# Start PostgreSQL & Redis
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# Check status
docker compose ps
```

**Note:** Use `docker compose` (space) for Docker Desktop. For older versions, use `docker-compose` (hyphen).

### Database
```bash
# Initialize database
python scripts/init_db.py

# Test database connection
python -c "from core.database import engine; engine.connect(); print('OK')"
```

### Testing
```bash
# Run full test suite
python test_module1.py

# Test individual components (see SETUP.md)
python -c "from core.config import get_settings; print(get_settings().database_url)"
```

### Ollama (LLM) - OPTIONAL
```powershell
# Install: Download from https://ollama.ai/download
# IMPORTANT: Restart terminal after installation!

# Verify installation
ollama --version

# Pull model (~4.7 GB download)
ollama pull llama3

# List models
ollama list

# Test connection (PowerShell)
Invoke-WebRequest http://localhost:11434/api/tags

# See OLLAMA_SETUP.md for detailed instructions
```

**Note:** Ollama is optional. You can test Module 1 basics without it!

## Environment Variables

Create `.env` file from template:
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

**Minimum required for testing:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/marketing_cdp
REDIS_URL=redis://localhost:6379/0
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
```

**For API testing, add:**
```env
YOUTUBE_API_KEY=your_key_here
INSTAGRAM_ACCESS_TOKEN=your_token_here
FACEBOOK_ACCESS_TOKEN=your_token_here
SENDGRID_API_KEY=your_key_here
```

## Troubleshooting Quick Fixes

| Issue | Solution |
|-------|----------|
| Database connection error | `docker compose up -d` |
| Module not found | Activate venv: `.\venv\Scripts\activate` |
| Ollama connection error | Install from https://ollama.ai/download, then **restart terminal** |
| Port already in use | Change ports in `docker-compose.yml` or `.env` |
| Import errors | `uv pip install -r requirements.txt` |

## Next Steps After Setup

1. ✅ Run tests: `python test_module1.py`
2. ✅ Configure API keys in `.env` (optional)
3. ✅ Test CDP functionality
4. ✅ Review [SETUP.md](SETUP.md) for detailed testing

## Module 1 Test Checklist

- [ ] Configuration loads correctly
- [ ] Database connects and tables exist
- [ ] CDP creates and retrieves customers
- [ ] Integration classes import correctly
- [ ] DataIntegrationAgent initializes
- [ ] Celery scheduler setup works

Run `python test_module1.py` to verify all items automatically.

