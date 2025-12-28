# Voice Agent Ops - Backend Quick Start

## ✅ Installation Complete!

All dependencies have been installed successfully.

## 🚀 Quick Start

### 1. Database Setup

You need PostgreSQL running. Install it if you haven't:

```bash
# macOS with Homebrew
brew install postgresql@14
brew services start postgresql@14

# Create the database
createdb voice_agent_ops
```

Or use a cloud database and update `DATABASE_URL` in `.env`

### 2. Configure Environment

Edit `.env` and update these values:
- `DATABASE_URL` - Your PostgreSQL connection string
- `JWT_SECRET` - Change to a secure random string
- `ELEVENLABS_API_KEY` - Your ElevenLabs API key
- `ELEVENLABS_WEBHOOK_SECRET` - Your webhook secret

### 3. Run Database Migrations

```bash
alembic upgrade head
```

### 4. Seed Development Data (Optional)

```bash
python3 -m app.db.seed
```

This creates:
- Demo organization
- 2 branches
- 3 users (admin, manager, agent)
- 5 customers with vehicles
- Sample campaign with calls

**Demo Login Credentials:**
- Admin: `admin@demo-auto.com` / `admin123`
- Manager: `manager@demo-auto.com` / `manager123`
- Agent: `agent@demo-auto.com` / `agent123`

### 5. Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

Or use the helper script:
```bash
./run.sh
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📝 Available API Endpoints

### Authentication
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Dashboard
- `GET /api/overview/kpis` - Key performance indicators
- `GET /api/overview/calls-over-time` - Call volume chart
- `GET /api/overview/outcomes` - Outcome distribution
- `GET /api/overview/needs-attention` - Calls needing review

### Calls
- `GET /api/calls` - List all calls
- `GET /api/calls/{id}` - Get call details
- `POST /api/calls/{id}/resolve` - Mark call resolved

### Campaigns
- `GET /api/campaigns` - List campaigns
- `POST /api/campaigns` - Create campaign
- `POST /api/campaigns/{id}/start` - Start campaign
- `POST /api/campaigns/{id}/pause` - Pause campaign

### Appointments, Customers, Scripts
- Full CRUD operations available
- See `/docs` for complete API reference

## 🔧 Development Commands

```bash
# Format code
ruff format app tests

# Lint code
ruff check app tests

# Type check
mypy app

# Run tests
pytest

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🐛 Troubleshooting

### Database Connection Error
- Make sure PostgreSQL is running: `brew services list`
- Check `DATABASE_URL` in `.env`
- Test connection: `psql $DATABASE_URL`

### Import Errors
- Ensure you're in the virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Port Already in Use
- Change the port: `uvicorn app.main:app --reload --port 8001`
- Or kill the process: `lsof -ti:8000 | xargs kill -9`

## 📚 Documentation

- Full API docs: http://localhost:8000/docs
- Backend architecture: `docs/backend.md`
- Project README: `README.md`

## 🎯 Next Steps

1. Update `.env` with your actual ElevenLabs credentials
2. Set up a PostgreSQL database (local or cloud)
3. Run migrations and seed data
4. Start the server and test the API
5. Connect your frontend application

---

**Need help?** Check `docs/backend.md` for detailed documentation.
