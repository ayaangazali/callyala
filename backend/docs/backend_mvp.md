# Voice Agent Ops - Backend MVP

## Overview

FastAPI backend for "Voice Agent Ops" - an AI-powered outbound calling system for car dealerships. This MVP uses local JSON file storage (no database required) with Google Sheets integration for lead management and ElevenLabs for AI voice calling.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Frontend       │────▶│  FastAPI Backend │────▶│  Google Sheets  │
│  (Vite + React) │     │  (Port 8000)     │     │  (Leads Source) │
└─────────────────┘     └────────┬─────────┘     └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
            ┌───────────┐ ┌───────────┐ ┌───────────┐
            │ ./data/   │ │ ElevenLabs│ │ Webhooks  │
            │ JSON Files│ │ API       │ │ (Results) │
            └───────────┘ └───────────┘ └───────────┘
```

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Google Cloud service account with Sheets API enabled
- ElevenLabs account with Conversational AI access

### 2. Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR: venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 3. Configure Environment

Edit `.env` with your settings:

```env
# Application
APP_ENV=development
DATA_DIR=./data
LOG_LEVEL=INFO

# Google Sheets
GOOGLE_SERVICE_ACCOUNT_FILE=./service-account.json
GOOGLE_DEFAULT_SHEET_ID=your-sheet-id

# ElevenLabs
ELEVENLABS_API_KEY=your-api-key
ELEVENLABS_AGENT_ID=your-agent-id
ELEVENLABS_WEBHOOK_SECRET=your-webhook-secret

# Development
MOCK_MODE=true  # Set to false for production
```

### 4. Run Server

```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `APP_ENV` | Environment (development/production) | No | development |
| `DATA_DIR` | Directory for JSON data files | No | ./data |
| `LOG_LEVEL` | Logging level | No | INFO |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | Path to GCP service account JSON | Yes* | - |
| `GOOGLE_DEFAULT_SHEET_ID` | Default Google Sheet ID | No | - |
| `ELEVENLABS_API_KEY` | ElevenLabs API key | Yes* | - |
| `ELEVENLABS_AGENT_ID` | ElevenLabs agent ID | Yes* | - |
| `ELEVENLABS_WEBHOOK_SECRET` | Webhook signature secret | No | - |
| `MOCK_MODE` | Enable mock mode (no real API calls) | No | false |

\* Not required if `MOCK_MODE=true`

## API Endpoints

### Health & Status

```bash
# Health check
curl http://localhost:8000/api/health

# Response:
# {"status": "healthy", "timestamp": "...", "version": "1.0.0"}
```

### Overview / Dashboard

```bash
# Get KPIs and dashboard data
curl "http://localhost:8000/api/overview"

# With date filtering
curl "http://localhost:8000/api/overview?from_date=2024-01-01&to_date=2024-01-31"

# Response:
# {
#   "kpis": {
#     "total_calls": 150,
#     "successful_calls": 120,
#     "success_rate": 80.0,
#     "avg_duration_seconds": 145.5,
#     "total_campaigns": 5,
#     "active_campaigns": 2
#   },
#   "calls_over_time": [...],
#   "outcome_distribution": {...},
#   "needs_attention": [...]
# }
```

### Campaigns

```bash
# List all campaigns
curl http://localhost:8000/api/campaigns

# Get single campaign
curl http://localhost:8000/api/campaigns/{campaign_id}

# Create campaign from Google Sheet
curl -X POST http://localhost:8000/api/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "name": "January Leads",
    "sheet_id": "your-google-sheet-id",
    "sheet_range": "Leads!A:Z"
  }'

# Start campaign (begins calling)
curl -X POST http://localhost:8000/api/campaigns/{campaign_id}/start

# Pause campaign
curl -X POST http://localhost:8000/api/campaigns/{campaign_id}/pause

# Get campaign progress
curl http://localhost:8000/api/campaigns/{campaign_id}/progress
```

### Calls

```bash
# List calls (with pagination)
curl "http://localhost:8000/api/calls?limit=50&offset=0"

# Filter by campaign
curl "http://localhost:8000/api/calls?campaign_id={campaign_id}"

# Filter by status
curl "http://localhost:8000/api/calls?status=completed"

# Filter by outcome
curl "http://localhost:8000/api/calls?outcome=success"

# Get single call
curl http://localhost:8000/api/calls/{call_id}
```

### Google Sheets

```bash
# Validate sheet (check columns, preview data)
curl -X POST http://localhost:8000/api/sheets/validate \
  -H "Content-Type: application/json" \
  -d '{
    "sheet_id": "your-sheet-id",
    "range": "Sheet1!A:Z"
  }'

# Response:
# {
#   "valid": true,
#   "columns": ["Name", "Phone", "Email", ...],
#   "row_count": 150,
#   "preview": [{"Name": "John", "Phone": "55123456", ...}, ...],
#   "warnings": ["Missing email in row 5"]
# }
```

### Webhooks

```bash
# ElevenLabs post-call webhook
curl -X POST http://localhost:8000/api/webhooks/elevenlabs/call-completed \
  -H "Content-Type: application/json" \
  -H "X-ElevenLabs-Signature: {hmac_signature}" \
  -d '{
    "event_type": "call.ended",
    "data": {
      "call_id": "...",
      "status": "completed",
      "duration": 120,
      "transcript": "...",
      "summary": "...",
      "sentiment": "positive"
    }
  }'
```

## Data Storage

All data is stored in JSON files under `./data/`:

```
data/
├── campaigns.json      # Campaign metadata
├── calls.jsonl         # Call records (append-only)
├── call_index.json     # Quick call lookup index
├── sheet_cache.json    # Cached sheet data
└── webhook_dedup.json  # Webhook idempotency tracking
```

### Atomic Writes

All JSON writes use atomic operations:
1. Write to temporary file
2. Sync to disk
3. Rename to target (atomic on POSIX)

This ensures data integrity even during crashes.

### File Locking

JSONL appends use file locking (`portalocker`) to handle concurrent webhook writes safely.

## Google Sheets Setup

### 1. Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project or select existing
3. Enable Google Sheets API
4. Create service account
5. Download JSON key file
6. Set `GOOGLE_SERVICE_ACCOUNT_FILE` to path

### 2. Share Sheet

Share your Google Sheet with the service account email (found in JSON file).

### 3. Expected Sheet Format

| Name | Phone | Email | Car Interest | Notes |
|------|-------|-------|--------------|-------|
| John Doe | 55123456 | john@example.com | SUV | Preferred morning |
| Jane Smith | 55654321 | jane@example.com | Sedan | Budget conscious |

**Required columns:**
- `Name` (or `Full Name`, `Customer Name`)
- `Phone` (or `Mobile`, `Tel`, `Phone Number`)

**Optional columns:**
- `Email`
- `Car Interest` / `Interest` / `Vehicle`
- `Notes` / `Comments`
- Any additional metadata columns

## ElevenLabs Setup

### 1. Create Agent

1. Go to [ElevenLabs](https://elevenlabs.io)
2. Navigate to Conversational AI
3. Create new agent with your script
4. Copy Agent ID

### 2. Configure Webhook

Set webhook URL to: `https://your-domain.com/api/webhooks/elevenlabs/call-completed`

### 3. Get API Key

Copy your ElevenLabs API key from account settings.

## Phone Number Normalization

Kuwait numbers are automatically normalized to E.164 format:

- `55123456` → `+96555123456`
- `+96555123456` → `+96555123456`
- `0096555123456` → `+96555123456`
- `55 12 34 56` → `+96555123456`

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run specific test file
pytest tests/test_storage_atomic.py

# Run with verbose output
pytest -v

# Run with coverage
pip install pytest-cov
pytest --cov=app --cov-report=html
```

## Troubleshooting

### Server won't start

```bash
# Check if port is in use
lsof -i :8000

# Kill existing process
kill -9 $(lsof -t -i:8000)
```

### Google Sheets errors

1. Verify service account file path
2. Check sheet is shared with service account email
3. Ensure Sheets API is enabled in GCP project

### ElevenLabs errors

1. Verify API key is valid
2. Check agent ID exists
3. Ensure account has Conversational AI access
4. Set `MOCK_MODE=true` for testing without API

### Webhook not receiving data

1. Check webhook URL is publicly accessible
2. Verify HMAC secret matches
3. Check server logs for signature validation errors

### Data file issues

```bash
# Reset all data
rm -rf ./data/*

# Server will recreate empty files on startup
```

## Development

### Project Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── app/
│   ├── core/
│   │   ├── config.py      # Settings management
│   │   ├── logging.py     # Logging setup
│   │   ├── files.py       # File I/O utilities
│   │   └── time.py        # Time/phone utilities
│   ├── models/
│   │   └── domain.py      # Pydantic models
│   ├── services/
│   │   ├── storage.py     # JSON storage operations
│   │   ├── sheets.py      # Google Sheets integration
│   │   ├── elevenlabs.py  # ElevenLabs API client
│   │   ├── analytics.py   # KPI calculations
│   │   ├── campaign.py    # Campaign management
│   │   ├── rules.py       # Needs attention rules
│   │   └── webhook_verify.py  # HMAC verification
│   └── api/
│       └── routes/
│           ├── health.py
│           ├── campaigns.py
│           ├── calls.py
│           ├── overview.py
│           ├── sheets.py
│           └── webhooks.py
├── tests/
│   ├── conftest.py
│   ├── test_storage_atomic.py
│   ├── test_webhook_idempotent.py
│   ├── test_sheet_mapping.py
│   └── test_analytics.py
└── docs/
    └── backend_mvp.md     # This file
```

### Adding New Endpoints

1. Create route file in `app/api/routes/`
2. Add router to `main.py`
3. Add corresponding service logic
4. Add tests

### Mock Mode

When `MOCK_MODE=true`:
- Google Sheets returns sample data
- ElevenLabs API calls are simulated
- Webhooks are accepted without signature verification
- Great for frontend development!

## License

MIT
