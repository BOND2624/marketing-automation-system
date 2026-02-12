# Complete Team Setup Guide

**Welcome!** This guide will help you set up the Marketing Automation Platform from scratch. Follow each section step-by-step.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Project Setup](#2-project-setup)
3. [Environment Configuration](#3-environment-configuration)
4. [Database Setup](#4-database-setup)
5. [YouTube OAuth Setup (For Video Uploads)](#5-youtube-oauth-setup-for-video-uploads)
6. [Instagram & Facebook Setup](#6-instagram--facebook-setup)
7. [Ollama Setup (Optional - For AI Features)](#7-ollama-setup-optional---for-ai-features)
8. [Testing Your Setup](#8-testing-your-setup)
9. [Common Issues & Troubleshooting](#9-common-issues--troubleshooting)
10. [Quick Reference](#10-quick-reference)

---

## 1. Prerequisites

### 1.1 Required Software

Install these before proceeding:

#### Python 3.10 or Higher
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **macOS**: `brew install python3` or download from python.org
- **Linux**: `sudo apt-get install python3 python3-pip` (Ubuntu/Debian)

**Verify installation:**
```bash
python --version
# Should show: Python 3.10.x or higher
```

#### Docker Desktop
- **Download**: [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
- **Windows/macOS**: Download and install the installer
- **Linux**: Follow [Docker installation guide](https://docs.docker.com/engine/install/)

**Verify installation:**
```bash
docker --version
docker compose version
```

#### Git
- **Windows**: Download from [git-scm.com](https://git-scm.com/download/win)
- **macOS**: `brew install git` or download from git-scm.com
- **Linux**: `sudo apt-get install git`

**Verify installation:**
```bash
git --version
```

### 1.2 Optional (But Recommended)

#### uv Package Manager (Faster Dependency Installation)
- **Windows PowerShell:**
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **macOS/Linux:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

**Verify installation:**
```bash
uv --version
```

---

## 2. Project Setup

### 2.1 Clone the Repository

```bash
# Navigate to your desired directory
cd C:\Users\YourName\Projects  # Windows
# or
cd ~/Projects  # macOS/Linux

# Clone the repository
git clone <repository-url>
cd final-year-project
```

### 2.2 Create Virtual Environment

**Option A: Using uv (Recommended - Faster)**
```bash
# Create virtual environment
uv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

**Option B: Using Python venv**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

**You should see `(venv)` in your terminal prompt after activation.**

### 2.3 Install Dependencies

**Option A: Using uv (Faster)**
```bash
uv pip install -r requirements.txt
```

**Option B: Using pip**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**This may take a few minutes. Wait for completion.**

---

## 3. Environment Configuration

### 3.1 Create `.env` File

Create a `.env` file in the project root:

**Windows:**
```bash
copy .env.example .env
```

**macOS/Linux:**
```bash
cp .env.example .env
```

### 3.2 Configure Environment Variables

Open `.env` in a text editor and set these values:

```env
# Database Configuration (Default - usually works as-is)
DATABASE_URL=postgresql://user:password@localhost:5432/marketing_cdp
REDIS_URL=redis://localhost:6379/0

# YouTube API (Required for YouTube features)
YOUTUBE_API_KEY=your_youtube_api_key_here

# Instagram & Facebook (Optional - see Section 6)
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
FACEBOOK_ACCESS_TOKEN=your_facebook_token
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret

# Email/SMS (Optional)
SENDGRID_API_KEY=your_sendgrid_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token

# LLM Configuration (Default - works with Ollama)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# Security (Change in production!)
JWT_SECRET_KEY=change-this-secret-key-in-production
ENCRYPTION_KEY=your-32-character-encryption-key-here
```

**For now, you only need:**
- `DATABASE_URL` (default is fine)
- `REDIS_URL` (default is fine)
- `YOUTUBE_API_KEY` (get from Section 5.1)

---

## 4. Database Setup

### 4.1 Start Docker Services

Make sure Docker Desktop is running, then:

```bash
# Start PostgreSQL and Redis containers
docker compose up -d

# Verify containers are running
docker compose ps
```

**Expected output:**
```
NAME                STATUS
marketing_postgres  Up
marketing_redis     Up
```

### 4.2 Initialize Database

```bash
python scripts/init_db.py
```

**Expected output:**
```
Initializing database: postgresql://user:password@localhost:5432/marketing_cdp
Database tables created successfully!
```

**If you see errors:**
- Make sure Docker containers are running: `docker compose ps`
- Check Docker Desktop is running
- See [Troubleshooting](#9-common-issues--troubleshooting)

---

## 5. YouTube OAuth Setup (For Video Uploads)

**⚠️ IMPORTANT:** To upload videos to YouTube, you need:
1. YouTube API Key (for reading data)
2. OAuth2 Credentials (for uploading videos)

### 5.1 Get YouTube API Key

1. **Go to Google Cloud Console**
   - Visit: [console.cloud.google.com](https://console.cloud.google.com/)
   - Sign in with your Google account

2. **Create a New Project** (or select existing)
   - Click the project dropdown at the top
   - Click "New Project"
   - Name: `Marketing Automation Platform`
   - Click "Create"

3. **Enable YouTube Data API v3**
   - Go to: [console.cloud.google.com/apis/library](https://console.cloud.google.com/apis/library)
   - Search for "YouTube Data API v3"
   - Click on it
   - Click "Enable"

4. **Create API Key**
   - Go to: [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials)
   - Click "Create Credentials" → "API Key"
   - Copy the API key
   - (Optional) Click "Restrict Key" → Select "YouTube Data API v3" → Save

5. **Add API Key to `.env`**
   ```env
   YOUTUBE_API_KEY=your_api_key_here
   ```

### 5.2 Set Up OAuth2 for Video Uploads

**This is required to upload videos to your YouTube channel.**

#### Step 1: Create OAuth 2.0 Client ID

1. **Go to Credentials Page**
   - Visit: [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials)
   - Make sure your project is selected

2. **Configure OAuth Consent Screen** (First Time Only)
   - Click "OAuth consent screen" in the left sidebar
   - Select "External" (unless you have Google Workspace)
   - Click "Create"
   - Fill in:
     - **App name**: `Marketing Automation Platform`
     - **User support email**: Your email
     - **Developer contact email**: Your email
   - Click "Save and Continue"
   - **Scopes**: Click "Add or Remove Scopes"
     - Search for "YouTube Data API v3"
     - Check: `.../auth/youtube.upload`
     - Click "Update" → "Save and Continue"
   - **Test users**: Click "Add Users"
     - Add your Google account email (the one you'll use to upload)
     - Click "Add" → "Save and Continue"
   - Review and click "Back to Dashboard"

3. **Create OAuth 2.0 Client ID**
   - Go back to: [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials)
   - Click "Create Credentials" → "OAuth 2.0 Client ID"
   - **Application type**: Select "Desktop app" (or "Web application" if preferred)
   - **Name**: `YouTube Upload Client`
   - Click "Create"

4. **Download Credentials JSON**
   - **IMPORTANT:** After creating the client, a popup appears
   - Look for a **"Download JSON"** button in the popup
   - Click it to download the file
   - **OR** if you missed it:
     - Click on your OAuth 2.0 Client ID in the credentials list
     - Look for "Download JSON" button
     - Click to download

5. **Save Credentials File**
   - Rename the downloaded file to: `youtube_oauth_credentials.json`
   - Move it to the project root directory (same folder as `README.md`)

#### Step 2: Configure Authorized Redirect URIs

1. **Edit OAuth Client**
   - Go to: [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials)
   - Click on your OAuth 2.0 Client ID (the one you just created)

2. **Add Redirect URIs**
   - Scroll to "Authorized redirect URIs"
   - Click "Add URI"
   - Add these URIs (one at a time):
     ```
     http://localhost:8080
     http://localhost
     ```
   - Click "Save"

#### Step 3: Generate OAuth Token

1. **Run Setup Script** (if credentials file is missing)
   ```bash
   python scripts/setup_youtube_oauth.py
   ```
   - This will guide you through manual setup if needed

2. **Generate Token**
   ```bash
   python scripts/generate_youtube_token.py
   ```

3. **Follow the Browser Flow**
   - A browser window will open
   - Sign in with your Google account (the one you added as a test user)
   - Click "Allow" to grant YouTube upload permission
   - You'll be redirected back automatically
   - Token will be saved to `youtube_token.json`

**✅ You're done!** The token will be reused automatically for future uploads.

### 5.3 Troubleshooting YouTube OAuth

#### Error: `redirect_uri_mismatch`
**Solution:**
1. Go to Google Cloud Console → Credentials
2. Edit your OAuth 2.0 Client ID
3. Add `http://localhost:8080` and `http://localhost` to "Authorized redirect URIs"
4. Save and try again

#### Error: `access_denied` or "App is being tested"
**Solution:**
1. Go to Google Cloud Console → OAuth consent screen
2. Scroll to "Test users"
3. Add your Google account email
4. Save and try again

#### Error: `invalid_grant: Token has been expired or revoked`
**Solution:**
1. Delete `youtube_token.json` from project root
2. Run `python scripts/generate_youtube_token.py` again
3. Re-authenticate in the browser

#### Can't Find "Download JSON" Button
**Solution:**
1. Go to Credentials page
2. Click on your OAuth 2.0 Client ID (click the name, not edit icon)
3. In the details page, look for "Download JSON" button
4. **OR** use manual setup:
   - Copy Client ID and Client Secret from the details page
   - Run `python scripts/setup_youtube_oauth.py`
   - Choose option 2 (Manual setup)
   - Paste your credentials

---

## 6. Instagram & Facebook Setup

**Note:** Instagram and Facebook APIs require a Facebook Developer account and app setup. This is optional for basic testing.

### 6.1 Create Facebook App

1. **Go to Facebook Developers**
   - Visit: [developers.facebook.com](https://developers.facebook.com/)
   - Sign in with your Facebook account

2. **Create App**
   - Click "My Apps" → "Create App"
   - Select "Business" → "Next"
   - Fill in:
     - **App Name**: `Marketing Automation Platform`
     - **App Contact Email**: Your email
   - Click "Create App"

3. **Add Products**
   - Find "Instagram Basic Display" → Click "Set Up"
   - Find "Instagram Graph API" → Click "Set Up"
   - Find "Facebook Login" → Click "Set Up"

### 6.2 Get Access Tokens

**This process is complex and requires:**
- App review (for production)
- Test users (for development)
- Page/Instagram account linking

**For detailed instructions, see:** [FACEBOOK_INSTAGRAM_API_SETUP.md](FACEBOOK_INSTAGRAM_API_SETUP.md)

**Quick Summary:**
1. Go to App Dashboard → Settings → Basic
2. Copy `App ID` and `App Secret`
3. Add to `.env`:
   ```env
   FACEBOOK_APP_ID=your_app_id
   FACEBOOK_APP_SECRET=your_app_secret
   ```
4. Generate access tokens via Graph API Explorer or OAuth flow
5. Add tokens to `.env`:
   ```env
   INSTAGRAM_ACCESS_TOKEN=your_token
   FACEBOOK_ACCESS_TOKEN=your_token
   ```

**Note:** Instagram/Facebook setup is optional. You can test YouTube features without them.

---

## 7. Ollama Setup (Optional - For AI Features)

**Ollama is only needed for AI-powered features (content generation, personalization).**

### 7.1 Install Ollama

1. **Download**
   - Visit: [ollama.ai/download](https://ollama.ai/download)
   - Download installer for your OS
   - Run the installer

2. **⚠️ IMPORTANT: Restart Your Terminal**
   - Close and reopen your terminal/PowerShell
   - This is required for `ollama` command to be available

3. **Verify Installation**
   ```bash
   ollama --version
   ```

### 7.2 Download Model

```bash
# Download llama3 model (~4.7 GB - may take time)
ollama pull llama3

# Verify model is installed
ollama list
```

**Expected output:**
```
NAME    ID              SIZE    MODIFIED
llama3  abc123...       4.7GB   2 hours ago
```

### 7.3 Test Ollama

```bash
# Test connection (PowerShell)
Invoke-WebRequest http://localhost:11434/api/tags

# Or test with curl (macOS/Linux)
curl http://localhost:11434/api/tags
```

**If Ollama is not running:**
- Windows: Ollama should start automatically. Check Task Manager.
- macOS/Linux: Run `ollama serve` in a separate terminal

---

## 8. Testing Your Setup

### 8.1 Quick Test

```bash
# Test configuration loading
python -c "from core.config import get_settings; s = get_settings(); print(f'Database: {s.database_url}')"
```

**Expected output:**
```
Database: postgresql://user:password@localhost:5432/marketing_cdp
```

### 8.2 Test Database Connection

```bash
# Test database
python -c "from core.database import engine; engine.connect(); print('[OK] Database connected!')"
```

### 8.3 Run Full Test Suite

```bash
# Test Module 1 (Foundations)
python test_module1.py

# Test Module 2 (Campaign Management)
python test_module2.py
```

### 8.4 Test YouTube Upload (If OAuth is Set Up)

```bash
# Make sure you have a video file in uploads/ folder
# Then run:
python test_youtube_upload.py
```

**Expected flow:**
1. Creates a test campaign
2. Uploads video to YouTube
3. Returns video ID and URL
4. Updates campaign status

---

## 9. Common Issues & Troubleshooting

### 9.1 Database Connection Error

**Error:** `connection to server at "localhost" (...) port 5432 failed`

**Solution:**
```bash
# Check Docker is running
docker compose ps

# If containers are stopped, start them
docker compose up -d

# Check logs
docker compose logs postgres
```

### 9.2 Module Not Found Errors

**Error:** `ModuleNotFoundError: No module named 'core'`

**Solution:**
```bash
# Make sure virtual environment is activated
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### 9.3 Ollama Connection Error

**Error:** `Connection refused` or `ollama: command not found`

**Solution:**
1. Install Ollama from [ollama.ai/download](https://ollama.ai/download)
2. **Restart your terminal** (important!)
3. Verify: `ollama --version`
4. Start Ollama: `ollama serve` (if not auto-starting)

**Note:** Ollama is optional. Tests will work without it (except AI features).

### 9.4 Port Already in Use

**Error:** `Port 5432 is already in use` or similar

**Solution:**
```bash
# Stop existing containers
docker compose down

# Or change ports in docker-compose.yml
# Edit docker-compose.yml and change port mappings
```

### 9.5 YouTube OAuth Errors

See [Section 5.3](#53-troubleshooting-youtube-oauth) for detailed solutions.

### 9.6 Import Errors After Cloning

**Solution:**
```bash
# Make sure you're in project root
cd final-year-project

# Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 10. Quick Reference

### Essential Commands

```bash
# Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Start Docker services
docker compose up -d

# Stop Docker services
docker compose down

# Initialize database
python scripts/init_db.py

# Run tests
python test_module1.py
python test_module2.py
python test_youtube_upload.py
```

### File Locations

- **Environment variables**: `.env` (project root)
- **YouTube OAuth credentials**: `youtube_oauth_credentials.json` (project root)
- **YouTube token**: `youtube_token.json` (project root)
- **Database**: PostgreSQL in Docker container
- **Logs**: Check `docker compose logs`

### Getting Help

1. Check this guide first
2. Check `SETUP.md` for detailed testing
3. Check `QUICK_START.md` for quick commands
4. Check `DB_COMMANDS.md` for database operations
5. Review error messages carefully
6. Check Docker logs: `docker compose logs`

---

## ✅ Setup Checklist

Before you start working, verify:

- [ ] Python 3.10+ installed
- [ ] Docker Desktop installed and running
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created and configured
- [ ] Docker containers running (`docker compose up -d`)
- [ ] Database initialized (`python scripts/init_db.py`)
- [ ] YouTube API key added to `.env` (for YouTube features)
- [ ] YouTube OAuth credentials set up (for video uploads)
- [ ] YouTube token generated (`python scripts/generate_youtube_token.py`)
- [ ] Tests passing (`python test_module1.py`)

**Once all checkboxes are checked, you're ready to start developing! 🎉**

---

## Next Steps

After setup:
1. Read `PROJECT_OVERVIEW.md` to understand the architecture
2. Read `AGENTS_OVERVIEW.md` to understand how agents work
3. Explore the codebase structure
4. Run tests to verify everything works
5. Start contributing! 🚀

---

**Last Updated:** November 2025  
**Questions?** Check the troubleshooting section or ask the team lead.

