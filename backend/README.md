# Voice Agent Ops - Backend

Production-quality FastAPI backend for AI voice agent operations in automotive dealerships.

## Features

- **Campaign Management**: Create and manage outbound calling campaigns
- **ElevenLabs Integration**: Batch calling via ElevenLabs Agents Platform
- **Webhook Processing**: Secure post-call webhook handling with signature verification
- **Analytics Dashboard**: KPIs, call metrics, and outcome tracking
- **Real-time Updates**: Server-Sent Events for live dashboard updates
- **Compliance**: DNC list management and recording disclosure tracking

## Tech Stack

- **Framework**: FastAPI + Uvicorn
- **Database**: PostgreSQL with SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Auth**: JWT-based authentication
- **Background Jobs**: Redis + RQ
- **HTTP Client**: HTTPX for external API calls

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Seed initial data (optional)
python -m app.db.seed

# Start the server
uvicorn app.main:app --reload --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Type checking
mypy app

# Linting
ruff check app
```

## Webhook Setup (Local Dev)

```bash
# Install ngrok
brew install ngrok

# Start tunnel
ngrok http 8000

# Use the HTTPS URL in ElevenLabs webhook config:
# https://xxxx.ngrok.io/webhooks/elevenlabs/post-call
```

## License

Proprietary - All rights reserved
