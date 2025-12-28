#!/bin/bash
# Voice Agent Ops - Complete Setup Script

set -e

echo "🎯 Voice Agent Ops - Backend Setup"
echo "=================================="
echo ""

# Check Python version
echo "1️⃣  Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found Python $PYTHON_VERSION"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo ""
    echo "2️⃣  Creating virtual environment..."
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
else
    echo ""
    echo "2️⃣  Virtual environment already exists"
fi

# Activate venv
echo ""
echo "3️⃣  Activating virtual environment..."
source venv/bin/activate
echo "   ✅ Virtual environment activated"

# Install dependencies
echo ""
echo "4️⃣  Installing dependencies..."
if pip install -r requirements.txt > /dev/null 2>&1; then
    echo "   ✅ All dependencies installed"
else
    echo "   ⚠️  Some dependencies may have failed, but continuing..."
fi

# Check if .env exists
echo ""
echo "5️⃣  Checking configuration..."
if [ ! -f ".env" ]; then
    echo "   Creating .env file from template..."
    cp .env.example .env
    echo "   ✅ .env file created"
    echo "   ⚠️  Please edit .env and update DATABASE_URL and other settings"
else
    echo "   ✅ .env file exists"
fi

# Test imports
echo ""
echo "6️⃣  Testing application..."
if python3 -c "from app.main import app" 2>/dev/null; then
    echo "   ✅ Application imports successfully!"
else
    echo "   ❌ Import test failed - check dependencies"
    exit 1
fi

echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Set up PostgreSQL database:"
echo "   brew install postgresql@14"
echo "   brew services start postgresql@14"
echo "   createdb voice_agent_ops"
echo ""
echo "2. Update .env with your database URL and API keys"
echo ""
echo "3. Run database migrations:"
echo "   alembic upgrade head"
echo ""
echo "4. (Optional) Seed development data:"
echo "   python3 -m app.db.seed"
echo ""
echo "5. Start the server:"
echo "   ./run.sh"
echo "   or: uvicorn app.main:app --reload --port 8000"
echo ""
echo "📖 For detailed instructions, see QUICKSTART.md"
echo ""
