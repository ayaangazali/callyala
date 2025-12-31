#!/bin/bash#!/bin/bash

# Start the Voice Agent Ops backend server# Voice Agent Ops - Backend Startup Script



cd "$(dirname "$0")"set -e



# Colorsecho "🚀 Starting Voice Agent Ops Backend..."

GREEN='\033[0;32m'

BLUE='\033[0;34m'# Check if virtual environment is activated

RED='\033[0;31m'if [ -z "$VIRTUAL_ENV" ]; then

NC='\033[0m' # No Color    echo "⚠️  Virtual environment not activated. Activating..."

    source venv/bin/activate

echo -e "${BLUE}🚀 Starting Voice Agent Ops Backend...${NC}"fi



# Check if .env exists# Check if .env exists

if [ ! -f .env ]; thenif [ ! -f ".env" ]; then

    echo -e "${RED}❌ .env file not found!${NC}"    echo "❌ .env file not found! Please create it from .env.example"

    echo "Please copy .env.example to .env and configure it:"    exit 1

    echo "  cp .env.example .env"fi

    exit 1

fiecho "✅ Environment ready"

echo "📊 Starting server on http://localhost:8000"

# Check if virtual environment existsecho "📖 API docs available at http://localhost:8000/docs"

if [ -d "venv" ]; thenecho ""

    echo -e "${GREEN}✓ Activating virtual environment${NC}"

    source venv/bin/activate# Start uvicorn

fiuvicorn app.main:app --reload --port 8000


# Create necessary directories
mkdir -p data logs

# Kill any existing server on port 8000
if lsof -ti :8000 > /dev/null 2>&1; then
    echo -e "${BLUE}🔄 Killing existing server on port 8000...${NC}"
    lsof -ti :8000 | xargs kill -9 2>/dev/null
    sleep 1
fi

# Start server
echo -e "${GREEN}✓ Starting server on http://0.0.0.0:8000${NC}"
echo -e "${BLUE}📝 Logs: logs/server.log${NC}"
echo ""

python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
