#!/bin/bash
# Voice Agent Ops - Backend Startup Script

set -e

echo "🚀 Starting Voice Agent Ops Backend..."

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated. Activating..."
    source venv/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found! Please create it from .env.example"
    exit 1
fi

echo "✅ Environment ready"
echo "📊 Starting server on http://localhost:8000"
echo "📖 API docs available at http://localhost:8000/docs"
echo ""

# Start uvicorn
uvicorn app.main:app --reload --port 8000
