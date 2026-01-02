# 🚀 Real Backend Setup Guide - NO MOCK DATA

## Overview
Your backend is now configured to make **real outbound calls** using:
- **ElevenLabs** for voice AI calling
- **Anthropic Claude** for transcript analysis and intelligence
- **Local JSON storage** for call data

**DEMO MODE**: All calls go to `+96550525011` (hardcoded for demo)

---

## ✅ What's Been Created

### 1. **Main Calling Endpoint**: `/api/pickup/call`
- Makes real outbound calls via ElevenLabs
- AI asks when customer can pick up their car
- Can answer questions about service/repairs
- Stores transcript and extracts pickup time

### 2. **Webhook Handler**: `/api/webhooks/pickup/elevenlabs`
- Receives call events from ElevenLabs
- Stores transcripts automatically
- Runs Claude AI analysis
- Extracts pickup time and sentiment

### 3. **Status Endpoint**: `/api/pickup/status/{call_id}`
- Get call status, transcript, and AI analysis
- Shows pickup time scheduled
- Customer sentiment analysis

### 4. **List Calls**: `/api/pickup/calls`
- View all calls with summaries

### 5. **Storage System**
- Calls stored in `data/pickup_calls.json`
- Transcripts, sentiments, pickup times preserved
- No mock data - all real

---

## 🔧 Setup Instructions

### Step 1: Get Anthropic API Key

1. Go to: https://console.anthropic.com/settings/keys
2. Create an API key
3. Copy it to your `.env` file:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...your-key...
```

**Pricing**: ~$3 per million input tokens, ~$15 per million output tokens
**Usage**: Analyzing call transcripts (typically 500-2000 tokens per call)

---

### Step 2: Get ElevenLabs API Key

1. Go to: https://elevenlabs.io/app/settings/api-keys
2. Create an API key
3. Copy it to your `.env`:
```bash
ELEVENLABS_API_KEY=...your-key...
```

**Pricing**: Pay-as-you-go (check their pricing page)
- Text-to-Speech: ~$0.30 per 1000 characters
- Conversational AI: Custom pricing

---

### Step 3: Create ElevenLabs Conversational AI Agent

#### 3.1. Create Agent
1. Go to: https://elevenlabs.io/app/conversational-ai
2. Click **"Create New Agent"**
3. Name: `Car Service Pickup Assistant`

#### 3.2. Set System Prompt
Copy the prompt from `ELEVENLABS_AGENT_SETUP.py` and paste it into the agent's system prompt field.

Key points:
- Agent introduces itself as calling from your service center
- Asks when customer can pick up their car
- Can answer questions about service/repairs
- Confirms pickup time before ending call

#### 3.3. Configure Settings
- **Allow Interruptions**: ✅ Enabled (natural conversation)
- **Response Latency**: Low (faster responses)
- **Sentiment Analysis**: ✅ Enabled
- **Max Call Duration**: 5 minutes

#### 3.4. Choose Voice
Recommended voices:
- **Rachel** (Female, professional)
- **Adam** (Male, friendly)
- Test and pick what works best

#### 3.5. Get Agent ID
- After creating, copy the **Agent ID**
- Add to `.env`:
```bash
ELEVENLABS_AGENT_ID=...agent-id...
```

---

### Step 4: Configure Phone Number

#### 4.1. Get a Phone Number
1. Go to: https://elevenlabs.io/app/conversational-ai/phone-numbers
2. Purchase or configure a phone number for outbound calls
3. Link it to your agent

#### 4.2. Get Phone Number ID
- Copy the **Phone Number ID**
- Add to `.env`:
```bash
ELEVENLABS_PHONE_NUMBER_ID=...phone-number-id...
```

---

### Step 5: Set Up Webhooks

#### 5.1. Configure Webhook URL
1. In your agent settings, go to **Webhooks**
2. Add webhook URL: `https://your-domain.com/api/webhooks/pickup/elevenlabs`
   - For local testing with ngrok: `https://xxxx.ngrok.io/api/webhooks/pickup/elevenlabs`

#### 5.2. Enable Events
Enable these events:
- ✅ `call.started` / `conversation.started`
- ✅ `call.ended` / `conversation.ended`
- ✅ `call.failed` / `call.error`
- ✅ `call.no_answer`
- ✅ `call.busy`

#### 5.3. Get Webhook Secret
- Copy the **Webhook Secret**
- Add to `.env`:
```bash
ELEVENLABS_WEBHOOK_SECRET=...secret...
```

---

### Step 6: For Local Testing (Optional)

If you're testing locally, you need to expose your backend to the internet for webhooks:

#### Using ngrok:
```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8000
```

This will give you a public URL like: `https://xxxx-xx-xx-xxx-xxx.ngrok.io`

Use this URL for your webhook configuration:
`https://xxxx-xx-xx-xxx-xxx.ngrok.io/api/webhooks/pickup/elevenlabs`

---

## 🚀 Running the Backend

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Verify .env Configuration
Check that all keys are filled in:
```bash
cat .env
```

Should see:
- `ANTHROPIC_API_KEY=sk-ant-...`
- `ELEVENLABS_API_KEY=...`
- `ELEVENLABS_AGENT_ID=...`
- `ELEVENLABS_PHONE_NUMBER_ID=...`
- `ELEVENLABS_WEBHOOK_SECRET=...`
- `MOCK_MODE=false`

### 3. Start the Server
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --port 8000
```

### 4. Verify It's Running
```bash
curl http://localhost:8000/
```

Should return:
```json
{
  "service": "Call Yala API",
  "version": "2.0.0",
  "docs": "/docs",
  "features": [
    "Dynamic Google Sheets (any format)",
    "ElevenLabs Voice AI Calling",
    "Anthropic Claude Intelligence"
  ]
}
```

---

## 📞 Making Your First Call

### Via API (cURL):
```bash
curl -X POST http://localhost:8000/api/pickup/call \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Ahmed",
    "vehicle_make": "Toyota",
    "vehicle_model": "Camry",
    "service_type": "oil change and brake inspection",
    "service_notes": "Everything looks good, no issues found"
  }'
```

### Response:
```json
{
  "success": true,
  "call_id": "conv_abc123...",
  "message": "Call initiated to +96550525011 for Ahmed",
  "actual_phone_called": "+96550525011",
  "customer_name": "Ahmed",
  "vehicle_info": "Toyota Camry",
  "started_at": "2026-01-02T..."
}
```

### Via Swagger UI:
1. Go to: http://localhost:8000/docs
2. Find **POST /api/pickup/call**
3. Click "Try it out"
4. Fill in the form
5. Click "Execute"

---

## 📊 Checking Call Status

### Get Call Status:
```bash
curl http://localhost:8000/api/pickup/status/{call_id}
```

### Response includes:
- Call status (queued, in-progress, completed, failed, no-answer, busy)
- Duration
- Full transcript
- AI summary
- Customer sentiment (positive, neutral, negative)
- **Pickup time scheduled** (extracted by Claude)
- Recording URL

---

## 🔍 What Happens During a Call

1. **Call Initiated**
   - Your backend calls `/api/pickup/call`
   - ElevenLabs places the call to `+96550525011`
   - Call ID returned immediately

2. **Call Starts**
   - ElevenLabs sends webhook: `call.started`
   - Status updated to "in-progress"

3. **Conversation Happens**
   - AI agent greets the customer
   - Asks when they can pick up their car
   - Answers any questions about the service
   - Confirms pickup time

4. **Call Ends**
   - ElevenLabs sends webhook: `call.ended`
   - Includes full transcript
   - Status updated to "completed"

5. **AI Analysis Runs**
   - Claude analyzes the transcript
   - Extracts key information:
     * Pickup time scheduled
     * Customer sentiment
     * Action items
     * Call outcome
   - Results stored in `data/pickup_calls.json`

6. **Frontend Retrieves Data**
   - Call `/api/pickup/status/{call_id}` to get everything
   - Display transcript, pickup time, sentiment
   - Show in your dashboard

---

## 📁 API Endpoints Reference

### Making Calls
- **POST** `/api/pickup/call` - Initiate a pickup reminder call
- **GET** `/api/pickup/calls` - List all calls
- **GET** `/api/pickup/status/{call_id}` - Get call status and analysis
- **GET** `/api/pickup/transcript/{call_id}` - Get just the transcript

### Webhooks (for ElevenLabs)
- **POST** `/api/webhooks/pickup/elevenlabs` - Receive call events
- **GET** `/api/webhooks/pickup/test` - Test webhook is alive

### Documentation
- **GET** `/docs` - Interactive API documentation (Swagger UI)
- **GET** `/redoc` - Alternative API documentation

---

## 🐛 Troubleshooting

### Problem: "ELEVENLABS_API_KEY not configured"
**Solution**: Add your API key to `.env` file

### Problem: "ELEVENLABS_AGENT_ID not configured"
**Solution**: Create an agent and add the ID to `.env`

### Problem: Call initiated but no webhook received
**Solutions**:
1. Check webhook URL is correct in ElevenLabs dashboard
2. If testing locally, use ngrok and update the webhook URL
3. Check webhook events are enabled
4. Verify webhook secret matches `.env`

### Problem: "AI analysis failed"
**Solutions**:
1. Check `ANTHROPIC_API_KEY` is valid
2. Check you have credits in your Anthropic account
3. Look at logs: `tail -f backend.log`

### Problem: Call fails immediately
**Solutions**:
1. Verify phone number format: `+96550525011` (international format)
2. Check ElevenLabs account has calling credits
3. Verify phone number ID is correct
4. Check agent ID is correct

### Check Logs:
```bash
# Backend logs
tail -f backend.log

# Or check console output when running with:
python main.py
```

---

## 💰 Cost Estimates (Demo Usage)

**Per Call:**
- ElevenLabs call: ~$0.10 - $0.50 (depends on duration and plan)
- Claude analysis: ~$0.01 - $0.03 (depends on transcript length)
- **Total per call**: ~$0.11 - $0.53

**For Testing (10 calls):**
- Total: ~$1 - $5

**For Production (1000 calls/month):**
- Total: ~$110 - $530/month

*Actual costs depend on your ElevenLabs plan and call duration*

---

## 🎯 Next Steps

1. ✅ Fill in all API keys in `.env`
2. ✅ Create and configure ElevenLabs agent
3. ✅ Set up phone number and webhooks
4. ✅ Test with a single call to `+96550525011`
5. ✅ Verify transcript appears in `/api/pickup/status/{call_id}`
6. ✅ Check AI analysis extracted pickup time
7. 🔜 Integrate with your frontend dashboard
8. 🔜 Remove hardcoded phone number when ready for production

---

## 📝 Production Checklist

Before going live:
- [ ] Replace hardcoded `+96550525011` with dynamic phone numbers
- [ ] Set up proper error handling and retries
- [ ] Add authentication to API endpoints
- [ ] Set up CORS for your frontend domain
- [ ] Configure proper logging and monitoring
- [ ] Set up database instead of JSON file storage
- [ ] Add rate limiting
- [ ] Set up backup and recovery
- [ ] Test extensively with real phone numbers
- [ ] Get user consent for automated calls (legal requirement!)

---

## 🆘 Getting Help

- ElevenLabs Docs: https://elevenlabs.io/docs
- Anthropic Claude Docs: https://docs.anthropic.com
- FastAPI Docs: https://fastapi.tiangolo.com

**Your backend is ready! 🎉**
- NO MOCK DATA
- Real ElevenLabs calls
- Real Claude AI analysis
- All transcripts and data stored
- Ready to integrate with frontend

Just add your API keys and start calling!
