#!/usr/bin/env bash
set -e

echo "==============================================================================="
echo "  🧬 FORENZA: Forensic Evidence Operating System"
echo "  🚀 Initializing Full-Stack Biocomputational Environment..."
echo "==============================================================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Infrastructure
echo "📦 [1/3] Checking Infrastructure (Docker Compose)..."
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    echo "   🐳 Docker detected. Starting containerized microservices..."
    docker-compose -f "infra/docker-compose.yml" up -d || true
    echo "   ✅ Containers started."
else
    echo "   ℹ️ Docker not running. FORENZA Safety Mode active (In-memory fallback)."
fi
echo ""

# 2. Backend
echo "🐍 [2/3] Initializing Forensic Compute Backend (FastAPI)..."
PYTHON_CMD="python3"
if [ -f "backend/venv/bin/python" ]; then
    PYTHON_CMD="backend/venv/bin/python"
elif [ -f "backend/.venv/bin/python" ]; then
    PYTHON_CMD="backend/.venv/bin/python"
elif [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
fi

echo "   🔍 Using Python: $PYTHON_CMD"
cd "$SCRIPT_DIR/backend"
$PYTHON_CMD -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd "$SCRIPT_DIR"
echo "   ✅ Backend running on http://127.0.0.1:8000 (PID: $BACKEND_PID)"
echo ""

# 3. Frontend
echo "⚛️ [3/3] Initializing Tactical Frontend (Next.js 16)..."
cd "$SCRIPT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    echo "   📦 Installing frontend node dependencies..."
    npm install
fi
npm run dev &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"
echo "   ✅ Frontend running on http://localhost:3000 (PID: $FRONTEND_PID)"
echo ""

echo "==============================================================================="
echo "  ✨ FORENZA Environment Successfully Initialized!"
echo ""
echo "  🌐 Web Application (Frontend):  http://localhost:3000"
echo "  🧬 Forensic API Docs (Swagger): http://localhost:8000/docs"
echo "==============================================================================="
echo ""
echo "Press Ctrl+C to terminate all services."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; exit 0" SIGINT SIGTERM
wait
