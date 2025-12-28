# Voice Agent Ops - Backend Documentation

## Overview

Voice Agent Ops is a production-ready FastAPI backend for managing AI voice agents in automotive dealerships. It integrates with ElevenLabs Conversational AI to enable automated outbound calling campaigns for service reminders, sales follow-ups, and more.

## Architecture

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py          # Dependency injection (auth, db)
│   │   └── routes/          # API route handlers
│   ├── core/
│   │   ├── config.py        # Pydantic Settings
│   │   ├── logging.py       # Structured logging
│   │   └── security.py      # JWT, password hashing, RBAC
│   ├── db/
│   │   ├── base.py          # SQLAlchemy Base, mixins
│   │   ├── migrations/      # Alembic migrations
│   │   ├── seed.py          # Development data seeder
│   │   └── session.py       # Async engine & session
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response
│   ├── services/            # External service clients
│   └── main.py              # FastAPI application
├── alembic.ini              # Alembic configuration
├── pyproject.toml           # Dependencies & project metadata
└── .env.example             # Environment variables template
```

## Tech Stack

- **Python 3.11+**
- **FastAPI** - Modern async web framework
- **SQLAlchemy 2.0** - Async ORM with asyncpg driver
- **PostgreSQL** - Primary database
- **Alembic** - Database migrations
- **Pydantic v2** - Data validation & settings
- **Redis** - Background job queue (via RQ)
- **HTTPX** - Async HTTP client for ElevenLabs API

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis (for background jobs)

### Installation

1. **Clone and navigate to backend:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   # or: venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Seed development data (optional):**
   ```bash
   python -m app.db.seed
   ```

7. **Start the server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `JWT_SECRET` | Secret key for JWT tokens | Required |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | `30` |
| `ELEVENLABS_API_KEY` | ElevenLabs API key | Required |
| `ELEVENLABS_WEBHOOK_SECRET` | Webhook signature secret | Required |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | `*` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Data Model

### Core Entities

| Entity | Description |
|--------|-------------|
| `Organization` | Multi-tenant root (dealership group) |
| `Branch` | Physical location within org |
| `User` | Staff member with role-based access |
| `Customer` | Contact for outreach |
| `Vehicle` | Customer's vehicle(s) |
| `Job` | Service/job codes |
| `Script` | AI conversation configuration |
| `Campaign` | Outreach campaign |
| `CampaignTarget` | Customer queued for campaign |
| `Call` | Individual call record |
| `Appointment` | Booked service appointment |
| `DncEntry` | Do-not-call list |
| `QaReview` | Call quality review |
| `AuditLog` | System audit trail |

### Relationships

```
Organization
├── Branches
├── Users
├── Customers
│   └── Vehicles
├── Jobs
├── Scripts
├── Campaigns
│   ├── CampaignTargets
│   └── Calls
│       └── Appointments
└── DncEntries
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login, receive JWT token |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/users` | Create new user (admin) |

### Dashboard Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/overview/kpis` | Get key performance indicators |
| GET | `/api/overview/calls-over-time` | Call volume time series |
| GET | `/api/overview/outcomes` | Outcome distribution |
| GET | `/api/overview/needs-attention` | Calls requiring review |

### Calls

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/calls` | List calls with filters |
| GET | `/api/calls/{id}` | Get call details |
| POST | `/api/calls/{id}/resolve` | Mark call as resolved |

### Campaigns

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/campaigns` | List campaigns |
| POST | `/api/campaigns` | Create campaign |
| GET | `/api/campaigns/{id}` | Get campaign details |
| PATCH | `/api/campaigns/{id}` | Update campaign |
| DELETE | `/api/campaigns/{id}` | Delete campaign |
| POST | `/api/campaigns/{id}/targets` | Upload target CSV |
| POST | `/api/campaigns/{id}/start` | Start calling |
| POST | `/api/campaigns/{id}/pause` | Pause campaign |
| POST | `/api/campaigns/{id}/resume` | Resume campaign |

### Appointments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/appointments` | List appointments |
| POST | `/api/appointments` | Create appointment |
| GET | `/api/appointments/{id}` | Get appointment |
| PATCH | `/api/appointments/{id}` | Update appointment |
| DELETE | `/api/appointments/{id}` | Delete appointment |

### Customers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/customers` | List customers |
| POST | `/api/customers` | Create customer |
| GET | `/api/customers/{id}` | Get customer |
| PATCH | `/api/customers/{id}` | Update customer |
| DELETE | `/api/customers/{id}` | Delete customer |
| POST | `/api/customers/{id}/vehicles` | Add vehicle |

### Scripts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/scripts` | List scripts |
| POST | `/api/scripts` | Create script |
| GET | `/api/scripts/{id}` | Get script |
| PATCH | `/api/scripts/{id}` | Update script |
| DELETE | `/api/scripts/{id}` | Deactivate script |
| POST | `/api/scripts/{id}/duplicate` | Duplicate script |

### Webhooks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/webhooks/elevenlabs/post-call` | ElevenLabs post-call webhook |

## Role-Based Access Control (RBAC)

### Roles

| Role | Description |
|------|-------------|
| `owner` | Full access, can manage org settings |
| `admin` | Full access except org deletion |
| `manager` | Manage campaigns, users, view all |
| `agent` | Execute campaigns, view assigned |
| `viewer` | Read-only access |

### Permissions

```python
ROLE_PERMISSIONS = {
    UserRole.owner: ["*"],  # All permissions
    UserRole.admin: ["users:*", "campaigns:*", "calls:*", "scripts:*", ...],
    UserRole.manager: ["campaigns:*", "calls:*", "scripts:read", ...],
    UserRole.agent: ["calls:read", "calls:write", "campaigns:read"],
    UserRole.viewer: ["*:read"],
}
```

## ElevenLabs Integration

### Starting a Campaign

1. Campaign is created with script and targets
2. User clicks "Start Campaign"
3. Backend calls `POST /v1/convai/twilio/outbound-call` for batch
4. ElevenLabs processes calls asynchronously
5. Post-call webhook updates call records

### Webhook Handling

The webhook endpoint (`/webhooks/elevenlabs/post-call`) handles:

1. **HMAC Signature Verification** - Validates request authenticity
2. **Call Upsert** - Creates or updates call record
3. **Outcome Processing** - Handles DNC requests, appointments
4. **Campaign Stats** - Updates campaign completion metrics

### Webhook Payload Processing

```python
# Key fields from ElevenLabs webhook
{
    "conversation_id": "...",
    "status": "completed",
    "analysis": {
        "call_successful": true,
        "transcript_summary": "...",
        "data_collection": {
            "appointment_date": "2024-01-20",
            "appointment_time": "10:00 AM"
        },
        "evaluation_criteria_results": {
            "Do-Not-Call Request": {"result": "failure"}
        }
    },
    "metadata": {
        "conversation_id": "...",
        "start_timestamp": ...,
        "call_duration_secs": 145
    },
    "transcript": [...]
}
```

## Database Migrations

### Creating a Migration

```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "Add new field"

# Create empty migration
alembic revision -m "Custom migration"
```

### Running Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Downgrade one revision
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history
```

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_webhooks.py -v
```

### Test Categories

- **Unit Tests** - Schema validation, utilities
- **Integration Tests** - API endpoints with test DB
- **Webhook Tests** - Signature verification, payload handling

## Development

### Code Style

```bash
# Format code
black app tests
isort app tests

# Lint
ruff check app tests

# Type check
mypy app
```

### Project Structure Conventions

- **Routes** return Pydantic response models
- **Models** use mixins for common fields (timestamps, UUID)
- **Schemas** use `model_dump(exclude_unset=True)` for PATCH
- **Services** are async and handle external API calls
- **Dependencies** handle auth and DB session injection

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install .
COPY app app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Checklist

- [ ] Set strong `JWT_SECRET`
- [ ] Configure `ELEVENLABS_WEBHOOK_SECRET`
- [ ] Set specific `CORS_ORIGINS`
- [ ] Enable HTTPS only
- [ ] Configure log aggregation
- [ ] Set up database backups
- [ ] Configure Redis persistence
- [ ] Set up monitoring/alerting

## Troubleshooting

### Common Issues

**Database Connection Errors**
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Verify connection string
psql $DATABASE_URL
```

**Migration Failures**
```bash
# Check current state
alembic current

# Force revision
alembic stamp head
```

**ElevenLabs Webhook Not Working**
- Verify `ELEVENLABS_WEBHOOK_SECRET` matches dashboard
- Check webhook URL is publicly accessible
- Review logs for signature validation errors

## Contributing

1. Create feature branch from `main`
2. Write tests for new features
3. Ensure all tests pass
4. Format code with black/isort
5. Submit PR with description

## License

Proprietary - All rights reserved.
