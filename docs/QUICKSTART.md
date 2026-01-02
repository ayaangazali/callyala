# 🚀 Quick Start - Backend Setup (5 Minutes)

## What You Have Now

✅ **Complete backend implementation** for making real AI-powered calls
✅ **All mock data removed** - ready for production APIs  
✅ **Hardcoded to +96550525011** for safe demo testing
✅ **AI analysis** with Claude for every call
✅ **Automatic transcript storage** via webhooks

---

## What You Need (API Keys)

You need 4 API keys to make this work:

1. **Anthropic API Key** - For AI analysis (~$0.02/call)
2. **ElevenLabs API Key** - For voice AI
3. **ElevenLabs Agent ID** - Your conversation agent
4. **ElevenLabs Phone Number ID** - For making calls

---

## Setup Steps (Choose Your Path)

### 🏃 Super Quick (Just Test It)

1. **Get Anthropic Key** (2 min)
   - Go to: https://console.anthropic.com
   - Create account → Get API key
   - Add to `backend/.env`: `ANTHROPIC_API_KEY=sk-ant-...`

2. **Get ElevenLabs Keys** (3 min)
   - Go to: https://elevenlabs.io
   - Create account → Settings → API Keys
   - Add to `backend/.env`: `ELEVENLABS_API_KEY=...`

3. **Create Agent** (See `REAL_BACKEND_SETUP.md` for details)

4. **Start Backend**
   ```bash
   cd backend
   python3 main.py
   ```

5. **Test**
   ```bash
   python3 test_call.py
   ```

---

### 📚 Detailed Setup (Production Ready)

See **`REAL_BACKEND_SETUP.md`** - Complete step-by-step guide with:
- API key setup
- Agent configuration
- Webhook setup
- Testing instructions
- Troubleshooting

---

## Files You Created

```
backend/
├── .env                              ← ADD YOUR API KEYS HERE
├── REAL_BACKEND_SETUP.md            ← Full setup guide
├── ELEVENLABS_AGENT_SETUP.py        ← Agent configuration
├── check_setup.py                    ← Verify your setup
├── test_call.py                      ← Test making calls
├── main.py                           ← (Updated) Main server
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── pickup.py             ← (NEW) Calling endpoints
│   │       └── webhooks_pickup.py    ← (NEW) Webhook handler
│   └── services/
│       └── storage.py                ← (Updated) Call storage
```

---

## API Endpoints

Once running on `http://localhost:8000`:

### Make a Call
```bash
POST /api/pickup/call
```
Body:
```json
{
  "customer_name": "Ahmed",
  "vehicle_make": "Toyota",
  "vehicle_model": "Camry",
  "service_type": "oil change",
  "service_notes": "Service completed"
}
```

### Get Call Status
```bash
GET /api/pickup/status/{call_id}
```
Returns: transcript, AI analysis, pickup time, sentiment

### List All Calls
```bash
GET /api/pickup/calls
```

### Webhook (for ElevenLabs)
```bash
POST /api/webhooks/pickup/elevenlabs
```

### Docs
```bash
GET /docs
```

---

## Test Your Setup

### 1. Check Configuration
```bash
cd backend
python3 check_setup.py
```

Should show all green checkmarks ✅

### 2. Start Backend
```bash
python3 main.py
```

Or:
```bash
uvicorn main:app --reload --port 8000
```

### 3. Verify Running
Open: http://localhost:8000

Should see:
```json
{
  "service": "Call Yala API",
  "version": "2.0.0"
}
```

### 4. View API Docs
Open: http://localhost:8000/docs

Interactive Swagger documentation

### 5. Make Test Call
```bash
python3 test_call.py
```

This will:
- ✅ Check backend is running
- ✅ Make a call to +96550525011
- ✅ Show call ID and status
- ✅ Display transcript (when available)
- ✅ Show AI analysis

---

## What Happens When You Call

```
1. POST /api/pickup/call
   └─> Backend sends request to ElevenLabs
       └─> ElevenLabs calls +96550525011
           └─> AI greets customer
               └─> Asks about car pickup
                   └─> Answers service questions
                       └─> Confirms pickup time
                           └─> Call ends
                               └─> ElevenLabs sends webhook
                                   └─> Backend stores transcript
                                       └─> Claude analyzes call
                                           └─> Extracts pickup time
                                               └─> Stores everything
                                                   └─> Frontend can retrieve it!
```

---

## Current Status

✅ **Backend Code**: 100% Complete  
⏳ **API Keys**: You need to add them  
⏳ **Agent Setup**: You need to create it  
⏳ **Testing**: Ready when you are

---

## Key Features

🎯 **Hardcoded Phone**: All calls → `+96550525011` (safe for demo)  
🤖 **AI-Powered**: Claude analyzes every transcript  
🎙️ **Voice AI**: ElevenLabs handles the conversation  
📝 **Auto-Storage**: Transcripts saved automatically  
🔄 **Webhook-Driven**: Updates happen in real-time  
📊 **Full API**: RESTful endpoints for everything  
🔒 **No Mock Data**: Real APIs only

---

## Cost Estimate

**Per Call:**
- ElevenLabs: ~$0.10 - $0.50
- Claude: ~$0.01 - $0.03
- **Total**: ~$0.11 - $0.53

**10 Test Calls**: ~$1 - $5

---

## Next Steps

1. ☐ Add API keys to `backend/.env`
2. ☐ Create ElevenLabs agent (see `ELEVENLABS_AGENT_SETUP.py`)
3. ☐ Run `python3 check_setup.py` to verify
4. ☐ Start backend: `python3 main.py`
5. ☐ Test call: `python3 test_call.py`
6. ☐ Check API docs: http://localhost:8000/docs
7. ☐ Connect your frontend

---

## Get Help

- **Full Guide**: `REAL_BACKEND_SETUP.md`
- **Agent Setup**: `ELEVENLABS_AGENT_SETUP.py`
- **API Docs**: http://localhost:8000/docs
- **Check Setup**: `python3 check_setup.py`
- **Test Calls**: `python3 test_call.py`

---

## TL;DR

```bash
# 1. Add API keys to backend/.env
nano backend/.env

# 2. Check setup
cd backend && python3 check_setup.py

# 3. Start backend
python3 main.py

# 4. Test call
python3 test_call.py

# 5. View docs
open http://localhost:8000/docs
```

**That's it!** Backend ready. Add keys. Make calls. 🎉
