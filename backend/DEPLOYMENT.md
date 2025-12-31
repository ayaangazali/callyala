# 🚀 Deployment Guide

## Current Status

✅ **Server Running**: http://localhost:8000  
✅ **Tests Passing**: 45/45  
✅ **Mock Mode**: Enabled (perfect for frontend development)  

## Quick Commands

```bash
# Start server
./run.sh

# Or manually:
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
pytest

# Check server
curl http://localhost:8000/health
```

## Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/overview` | GET | Dashboard KPIs & charts |
| `/api/campaigns` | GET/POST | List/create campaigns |
| `/api/campaigns/{id}` | GET | Campaign details |
| `/api/campaigns/{id}/start` | POST | Start campaign calling |
| `/api/campaigns/{id}/pause` | POST | Pause campaign |
| `/api/calls` | GET | List calls (filtered) |
| `/api/calls/{id}` | GET | Call details |
| `/api/sheets/validate` | POST | Validate Google Sheet |
| `/api/webhooks/elevenlabs/call-completed` | POST | ElevenLabs webhook |

## Test Endpoints

```bash
# Health
curl http://localhost:8000/health

# Dashboard overview
curl http://localhost:8000/api/overview

# List campaigns
curl http://localhost:8000/api/campaigns

# List calls
curl http://localhost:8000/api/calls?limit=10

# Create campaign
curl -X POST http://localhost:8000/api/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "name": "January Leads",
    "sheet_id": "your-sheet-id",
    "sheet_range": "Sheet1!A:Z"
  }'
```

## Environment Setup

### Required for Production
1. **Google Sheets**
   - Service account JSON file
   - Sheet ID and range
   
2. **ElevenLabs**
   - API key
   - Agent ID
   - Webhook secret

### Development Mode
Set `MOCK_MODE=true` in `.env` to bypass real API calls.

## File Structure

```
backend/
├── 📄 main.py              # App entry point
├── 📄 requirements.txt     # Dependencies
├── 📄 .env                 # Environment config (not in git)
├── 📄 .env.example         # Template
├── 📄 run.sh              # Start script
├── 📁 app/                # Application code
├── 📁 tests/              # 45 passing tests
├── 📁 docs/               # Full documentation
├── 📁 data/               # JSON storage (gitignored)
└── 📁 logs/               # Server logs (gitignored)
```

## Production Deployment

### Option 1: Simple
```bash
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Option 2: Gunicorn
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Option 3: Docker (coming soon)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Monitoring

```bash
# Watch logs
tail -f logs/server.log

# Check data files
ls -lh data/

# Test webhook signature
curl -X POST http://localhost:8000/api/webhooks/elevenlabs/call-completed \
  -H "Content-Type: application/json" \
  -H "X-ElevenLabs-Signature: test" \
  -d '{"event_type": "call.ended", "data": {"call_id": "test"}}'
```

## Troubleshooting

### Server won't start
```bash
# Kill existing process
lsof -ti :8000 | xargs kill -9

# Check imports
python3 -c "from main import app; print('OK')"
```

### Tests failing
```bash
# Clean cache
find . -type d -name "__pycache__" -exec rm -rf {} +
rm -rf .pytest_cache

# Reinstall
pip install -r requirements.txt --force-reinstall
```

### Data corruption
```bash
# Backup and reset
mv data data.backup
mkdir data
# Server will recreate files on startup
```

## Next Steps

1. ✅ Backend is running and tested
2. 🔄 Connect frontend to API endpoints
3. 📝 Configure real Google Sheets
4. 🎙️ Set up ElevenLabs agent
5. 🚀 Deploy to production

---

**Current Status**: ✅ Ready for development  
**Mock Mode**: ✅ Enabled  
**Tests**: ✅ 45/45 passing  
**Server**: ✅ Running on port 8000
