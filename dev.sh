#!/bin/bash

# Unified Marketing Automation System - Development Manager
# This script orchestrates Docker, the FastAPI Backend, and the Next.js Frontend.

# Function to handle shutdown
cleanup() {
    echo ""
    echo "🛑 Shutting down Unified Marketing Automation System..."
    
    # Kill any processes matching api.main or next dev
    pkill -f "api.main" 2>/dev/null
    pkill -f "next-dev" 2>/dev/null
    
    echo "Stopping Docker containers..."
    docker compose stop
    
    echo "✅ Shutdown complete."
    exit 0
}

# Trap Ctrl+C (SIGINT) and SIGTERM
trap cleanup SIGINT SIGTERM

echo "🚀 Starting Unified Marketing Automation System..."
rm -f backend.log

# 1. Start Docker services
echo "📦 Starting Docker services (PostgreSQL, Redis)..."
docker compose up -d

# 2. Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
MAX_RETRIES=30
COUNT=0
until docker exec marketing_postgres pg_isready -U user > /dev/null 2>&1 || [ $COUNT -eq $MAX_RETRIES ]; do
    sleep 1
    COUNT=$((COUNT + 1))
done

if [ $COUNT -eq $MAX_RETRIES ]; then
    echo "❌ PostgreSQL failed to start in time. Check docker logs."
    cleanup
fi

# 3. Initialize Database
echo "🔧 Initializing database tables..."
./venv/bin/python3 scripts/init_db.py

# 4. Start FastAPI Backend in background
echo "🔥 Starting FastAPI Backend API..."
./venv/bin/python3 -m api.main > backend.log 2>&1 &
BACKEND_PID=$!

# Give backend a moment to start
sleep 2
if ! ps -p $BACKEND_PID > /dev/null; then
    echo "❌ FastAPI Backend failed to start. Check backend.log"
    cleanup
fi

echo "✅ Backend running on http://localhost:8000"

# 5. Start Next.js Frontend
echo "💻 Starting Next.js Frontend..."
# We use npx next dev directly to avoid recursion if called via npm run dev
npx next dev

# Keep script alive and wait for frontend process
wait
