#!/bin/bash

# FORENZA Startup Script
# Starts Infrastructure, Backend, and Frontend

# Ensure we are in the script's directory
cd "$(dirname "$0")"

echo "🚀 FORENZA: Starting Development Environment..."

# 1. Infrastructure
echo -e "\n📦 [1/3] Starting Infrastructure (Docker)..."
docker-compose -f infra/docker-compose.yml up -d
if [ $? -ne 0 ]; then
    echo "❌ Failed to start Docker containers."
    exit 1
fi
echo "✅ Infrastructure running."

# Function to try opening a new terminal
open_terminal() {
    local title="$1"
    local command="$2"
    
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal --title="$title" -- bash -c "$command; exec bash"
    elif command -v xterm &> /dev/null; then
        xterm -title "$title" -e "bash -c \"$command; exec bash\"" &
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        osascript -e "tell application \"Terminal\" to do script \"$command\""
    else
        echo "⚠️  Could not detect terminal emulator. Please run manually:"
        echo "   $command"
    fi
}

# 2. Backend
echo -e "\n🐍 [2/3] Starting Backend (FastAPI)..."
BACKEND_CMD="cd $(pwd)/backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000"
open_terminal "FORENZA-Backend" "$BACKEND_CMD"

# 3. Frontend
echo -e "\n⚛️ [3/3] Starting Frontend (Next.js)..."
FRONTEND_CMD="cd $(pwd)/frontend && npm run dev"
open_terminal "FORENZA-Frontend" "$FRONTEND_CMD"

echo -e "\n✨ FORENZA Environment Prepared!"
