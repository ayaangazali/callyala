# Call Yala - Quick Start Guide

## 🚀 Running the Application

### Prerequisites
- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- Google Sheets API credentials (optional, can use MOCK_MODE)
- ElevenLabs API key (optional, can use MOCK_MODE)
- Anthropic API key (optional, can use MOCK_MODE)

---

## Backend Setup

### 1. Navigate to Backend
```bash
cd backend
```

### 2. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your values
nano .env
```

### 4. Run Backend Server
```bash
# Development mode (auto-reload)
python3 main.py

# Or use the run script
chmod +x run.sh
./run.sh

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Backend will run on**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

---

## Frontend Setup

### 1. Navigate to Frontend
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Run Development Server
```bash
npm run dev
```

### 4. Build for Production
```bash
npm run build

# Preview production build
npm run preview
```

**Frontend will run on**: http://localhost:8081
- Automatically opens in browser
- Hot Module Replacement (HMR) enabled
- Fast refresh on file changes

---

## 🧪 Testing Mode (No API Keys Required)

### Backend Mock Mode
In `backend/.env`:
```bash
MOCK_MODE=true
```
This runs the backend with simulated data - no external API calls needed!

### What Mock Mode Provides:
- ✅ Simulated Google Sheets data
- ✅ Simulated ElevenLabs voice calling
- ✅ Simulated Anthropic AI responses
- ✅ Full API functionality without credentials
- ✅ Perfect for development and testing

---

## 🔑 Production Mode (With Real APIs)

### 1. Google Sheets Setup
```bash
# 1. Create Google Cloud project
# 2. Enable Google Sheets API
# 3. Create Service Account
# 4. Download JSON key to backend/secrets/service_account.json
# 5. Share your sheet with service account email

# In .env:
GOOGLE_SHEETS_SPREADSHEET_ID=your_sheet_id_here
GOOGLE_SERVICE_ACCOUNT_JSON_PATH=./secrets/service_account.json
```

### 2. ElevenLabs Setup
```bash
# 1. Sign up at https://elevenlabs.io
# 2. Get API key from Settings
# 3. Create Conversational AI agent
# 4. Get agent ID

# In .env:
ELEVENLABS_API_KEY=your_api_key_here
ELEVENLABS_AGENT_ID=your_agent_id_here
```

### 3. Anthropic Claude Setup
```bash
# 1. Sign up at https://console.anthropic.com
# 2. Create API key

# In .env:
ANTHROPIC_API_KEY=your_api_key_here
```

### 4. Disable Mock Mode
```bash
# In .env:
MOCK_MODE=false
```

---

## 📱 Using the Application

### Dashboard
- View real-time call statistics
- Monitor success rates and appointments
- Track campaign performance
- Quick actions and insights

### Language Switching
- Click the language switcher in top-right
- Switch between English (EN) and Arabic (AR)
- Full RTL support for Arabic
- Numbers automatically converted to Arabic numerals (٠-٩)

### Making Calls
1. Upload contacts via Google Sheets
2. Create a campaign
3. Configure call script
4. Click "Start Calling"
5. Monitor progress in real-time

### Managing Data
- **Calls**: View call history and outcomes
- **Appointments**: Schedule and track meetings
- **Customers**: Manage contact database
- **Scripts**: Create and edit call scripts
- **QA**: Quality assurance and review

---

## 🛠️ Development Commands

### Frontend
```bash
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Backend
```bash
python3 main.py                    # Run dev server
uvicorn main:app --reload          # Run with uvicorn
pytest                             # Run tests (if configured)
python3 -m py_compile main.py      # Check syntax
```

---

## 🐛 Troubleshooting

### Port Already in Use
**Frontend**:
- Vite will automatically try port 8081 if 8080 is taken
- Manually specify: `vite --port 3000`

**Backend**:
- Change port in `.env`: `PORT=8001`
- Or: `uvicorn main:app --port 8001`

### Dependencies Not Installing
**Frontend**:
```bash
rm -rf node_modules package-lock.json
npm install
```

**Backend**:
```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt --force-reinstall
```

### Translation Files Not Loading
```bash
# Ensure files exist
ls frontend/public/locales/
# Should show: ar.json, en.json

# If missing, copy from src
cp frontend/src/locales/*.json frontend/public/locales/
```

### API Connection Issues
1. Verify backend is running: http://localhost:8000/api/health
2. Check CORS settings in `backend/main.py`
3. Check frontend API base URL (should be auto-detected)
4. Try MOCK_MODE=true for testing

---

## 📊 Monitoring

### Backend Logs
```bash
# View logs
tail -f backend/logs/app.log

# Or use backend.log
tail -f backend/backend.log
```

### Frontend Console
- Open browser DevTools (F12)
- Check Console tab for errors
- Check Network tab for API calls

### Health Checks
```bash
# Backend health
curl http://localhost:8000/api/health

# Should return:
# {"status": "ok", "timestamp": "..."}
```

---

## 🚀 Deployment

### Frontend (Static Files)
```bash
npm run build
# Uploads dist/ folder to:
# - Netlify
# - Vercel
# - AWS S3 + CloudFront
# - Any static hosting
```

### Backend (API Server)
```bash
# Docker (recommended)
docker build -t callyala-backend .
docker run -p 8000:8000 --env-file .env callyala-backend

# Or deploy to:
# - Railway
# - Render
# - AWS EC2/ECS
# - Google Cloud Run
```

---

## 📖 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Performance Guide**: `PERFORMANCE_OPTIMIZATIONS.md`
- **Improvements Summary**: `IMPROVEMENTS_SUMMARY.md`
- **Bug Fixes Report**: `BUG_FIXES_VALIDATION.md`
- **Backend Deployment**: `backend/DEPLOYMENT.md`
- **Backend README**: `backend/README.md`

---

## 🆘 Support

### Common Issues Solved
✅ Port conflicts - Vite auto-switches ports
✅ Dependencies - All installed and validated
✅ i18n - Lazy loading configured correctly
✅ Build errors - No TypeScript or Python errors
✅ Performance - Optimized with memoization and caching

### Still Need Help?
1. Check the documentation files
2. Review error logs
3. Try MOCK_MODE for testing
4. Verify all dependencies installed
5. Check .env configuration

---

**Last Updated**: January 1, 2026  
**Status**: ✅ Fully Validated & Production Ready
