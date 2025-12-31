# Voice Agent Ops - Backend# Voice Agent Ops - Backend



FastAPI backend for an AI-powered outbound calling system for car dealerships in Kuwait.Production-quality FastAPI backend for AI voice agent operations in automotive dealerships.



## 🚀 Quick Start## Features



```bash- **Campaign Management**: Create and manage outbound calling campaigns

# Install dependencies- **ElevenLabs Integration**: Batch calling via ElevenLabs Agents Platform

pip install -r requirements.txt- **Webhook Processing**: Secure post-call webhook handling with signature verification

- **Analytics Dashboard**: KPIs, call metrics, and outcome tracking

# Copy environment template- **Real-time Updates**: Server-Sent Events for live dashboard updates

cp .env.example .env- **Compliance**: DNC list management and recording disclosure tracking



# Edit .env with your credentials## Tech Stack

nano .env

- **Framework**: FastAPI + Uvicorn

# Run server- **Database**: PostgreSQL with SQLAlchemy 2.0 (async)

python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload- **Migrations**: Alembic

```- **Auth**: JWT-based authentication

- **Background Jobs**: Redis + RQ

Server will be available at: **http://localhost:8000**- **HTTP Client**: HTTPX for external API calls



## 📁 Project Structure## Quick Start



```### Prerequisites

backend/

├── main.py                  # FastAPI app entry point- Python 3.11+

├── requirements.txt         # Python dependencies- PostgreSQL 14+

├── .env.example            # Environment variables template- Redis 7+

├── .gitignore              # Git ignore rules

│### Setup

├── app/

│   ├── core/               # Core utilities```bash

│   │   ├── config.py       # Settings & environment config# Create virtual environment

│   │   ├── logging.py      # Structured loggingpython -m venv venv

│   │   ├── files.py        # File I/O (atomic writes, locking)source venv/bin/activate  # On Windows: venv\Scripts\activate

│   │   └── time.py         # Time & phone normalization

│   │# Install dependencies

│   ├── models/             # Data modelspip install -e ".[dev]"

│   │   └── domain.py       # Pydantic models (Campaign, Call, etc.)

│   │# Copy environment variables

│   ├── services/           # Business logiccp .env.example .env

│   │   ├── storage.py      # JSON file storage# Edit .env with your configuration

│   │   ├── sheets.py       # Google Sheets integration

│   │   ├── elevenlabs.py   # ElevenLabs API client# Run database migrations

│   │   ├── analytics.py    # KPIs & metricsalembic upgrade head

│   │   ├── campaign.py     # Campaign management

│   │   ├── rules.py        # Needs-attention rules# Seed initial data (optional)

│   │   └── webhook_verify.py  # HMAC signature verificationpython -m app.db.seed

│   │

│   └── api/# Start the server

│       └── routes/         # API endpointsuvicorn app.main:app --reload --port 8000

│           ├── health.py```

│           ├── campaigns.py

│           ├── calls.py## API Documentation

│           ├── overview.py

│           ├── sheets.pyOnce running, visit:

│           └── webhooks.py- Swagger UI: http://localhost:8000/docs

│- ReDoc: http://localhost:8000/redoc

├── tests/                  # Unit & integration tests

│   ├── conftest.py## Development

│   ├── test_storage_atomic.py

│   ├── test_webhook_idempotent.py```bash

│   ├── test_sheet_mapping.py# Run tests

│   └── test_analytics.pypytest

│

├── docs/# Run with coverage

│   └── backend_mvp.md      # Complete documentationpytest --cov=app

│

├── data/                   # JSON file storage (gitignored)# Type checking

│   ├── campaigns.jsonmypy app

│   ├── calls.jsonl

│   ├── call_index.json# Linting

│   ├── sheet_cache.jsonruff check app

│   └── webhook_dedup.json```

│

└── logs/                   # Application logs (gitignored)## Webhook Setup (Local Dev)

    └── server.log

``````bash

# Install ngrok

## 🔧 Environment Variablesbrew install ngrok



Create a `.env` file with:# Start tunnel

ngrok http 8000

```env

# Application# Use the HTTPS URL in ElevenLabs webhook config:

APP_ENV=development          # development | production# https://xxxx.ngrok.io/webhooks/elevenlabs/post-call

DATA_DIR=./data             # Path to JSON storage```

LOG_LEVEL=INFO              # DEBUG | INFO | WARNING | ERROR

## License

# Google Sheets

GOOGLE_SERVICE_ACCOUNT_FILE=./service-account.jsonProprietary - All rights reserved

GOOGLE_DEFAULT_SHEET_ID=your-sheet-id

# ElevenLabs
ELEVENLABS_API_KEY=your-api-key
ELEVENLABS_AGENT_ID=your-agent-id
ELEVENLABS_WEBHOOK_SECRET=your-webhook-secret

# Development
MOCK_MODE=true              # Set false for production
```

## 📡 API Endpoints

### Health Check
```bash
GET /health
# Response: {"status": "healthy", "service": "voice-agent-ops"}
```

### Dashboard Overview
```bash
GET /api/overview
GET /api/overview?from_date=2024-01-01&to_date=2024-01-31

# Returns: KPIs, charts, needs-attention items
```

### Campaigns
```bash
GET    /api/campaigns                    # List all campaigns
GET    /api/campaigns/{id}               # Get campaign details
POST   /api/campaigns                    # Create from Google Sheet
POST   /api/campaigns/{id}/start         # Start calling
POST   /api/campaigns/{id}/pause         # Pause campaign
GET    /api/campaigns/{id}/progress      # Get progress
```

### Calls
```bash
GET    /api/calls                        # List calls (paginated)
GET    /api/calls/{id}                   # Get call details

# Query params: campaign_id, status, outcome, limit, offset
```

### Google Sheets
```bash
POST   /api/sheets/validate              # Validate sheet format
# Body: {"sheet_id": "...", "range": "Sheet1!A:Z"}
```

### Webhooks
```bash
POST   /api/webhooks/elevenlabs/call-completed
# ElevenLabs post-call webhook with HMAC verification
```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_storage_atomic.py -v
```

**Current test status:** ✅ 45/45 tests passing

## 🗄️ Data Storage

This MVP uses **local JSON files** (no database required):

- **campaigns.json**: Campaign metadata
- **calls.jsonl**: Call records (append-only log)
- **call_index.json**: Fast lookup index
- **sheet_cache.json**: Cached Google Sheets data
- **webhook_dedup.json**: Idempotency tracking

### Features:
- ✅ Atomic writes (temp file → fsync → rename)
- ✅ File locking for concurrent access
- ✅ JSONL append for scalable call logs
- ✅ Crash-safe operations

## 🔌 Integrations

### Google Sheets
1. Create service account in Google Cloud Console
2. Enable Sheets API
3. Download JSON key file
4. Share your sheet with service account email
5. Set `GOOGLE_SERVICE_ACCOUNT_FILE` in `.env`

**Expected sheet format:**

| Name | Phone | Email | Car Interest | Notes |
|------|-------|-------|--------------|-------|
| John Doe | 55123456 | john@example.com | SUV | Morning |

### ElevenLabs
1. Create Conversational AI agent
2. Copy Agent ID to `.env`
3. Set webhook URL: `https://your-domain.com/api/webhooks/elevenlabs/call-completed`
4. Copy API key to `.env`

## 📞 Phone Normalization

Kuwait numbers are auto-normalized to E.164:

- `55123456` → `+96555123456`
- `55-12-34-56` → `+96555123456`
- `0096555123456` → `+96555123456`

## 🔐 Security

- ✅ HMAC-SHA256 webhook signature verification
- ✅ Idempotent webhook handling (deduplication)
- ✅ Environment-based secrets
- ✅ CORS configured for frontend

## 🐛 Troubleshooting

### Port already in use
```bash
# Kill process on port 8000
lsof -ti :8000 | xargs kill -9
```

### Import errors
```bash
# Make sure you're in backend directory
cd backend
python3 -m uvicorn main:app --reload
```

### Google Sheets not working
1. Check service account file path
2. Verify sheet is shared with service account email
3. Ensure Sheets API is enabled

### Test mode
Set `MOCK_MODE=true` to test without real API calls

## 📝 Development

### Adding new endpoints
1. Create route file in `app/api/routes/`
2. Add router to `main.py`
3. Implement service logic in `app/services/`
4. Add tests in `tests/`

### Code style
- Use type hints
- Follow Pydantic v2 patterns
- Write docstrings
- Add tests for new features

## 📚 Documentation

See `docs/backend_mvp.md` for complete documentation including:
- Architecture details
- Setup instructions
- API examples with curl
- Troubleshooting guide

## 🚢 Deployment

```bash
# Production server
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# With gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📄 License

MIT

---

**Built for the Kuwait car dealership market** 🚗 🇰🇼
