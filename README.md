# Call Yala - AI Voice Agent Platform

> **🎉 ALL FEATURES COMPLETE!** Language switcher working, call buttons wired, Arabic translation complete, TypeScript build passing!

Enterprise-grade AI voice agent platform for automotive dealerships. Automate outbound customer calls for vehicle pickup scheduling, service reminders, and follow-ups.

## ✨ Key Features

- **🌐 Bilingual Support**: Full English & Arabic with RTL layout support
- **📞 Intelligent Call Management**: Automated outbound calling with AI voice agents (ElevenLabs)
- **📊 Real-time Analytics**: Track call metrics, answer rates, booking conversions, sentiment analysis
- **🤖 AI Analysis**: Anthropic Claude AI analyzes call transcripts and extracts insights
- **📅 Appointment Scheduling**: Seamless pickup time/date booking
- **👥 Customer & Vehicle Tracking**: Comprehensive CRM for dealerships
- **✅ Production Ready**: TypeScript build passing, error boundaries active, clean code

## 🚀 Quick Start

```bash
# Backend
cd backend
python3 main.py

# Frontend (in new terminal)
cd frontend
npm run dev
```

Open http://localhost:5173

**Test language switcher**: Click 🌐 icon (top right) → switch English ↔ Arabic!

## 🛠️ Tech Stack

- **Frontend**: React 18 + TypeScript + Vite
- **UI**: Tailwind CSS + shadcn/ui (Radix UI) + Framer Motion
- **State**: TanStack Query + React hooks
- **i18n**: react-i18next with lazy loading
- **Backend**: FastAPI + Python 3
- **AI**: ElevenLabs (voice) + Anthropic Claude (analysis)
- **Storage**: Local JSON files

## 📁 Project Structure

```
callyala/
├── frontend/              # React + TypeScript
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── pages/         # Page components
│   │   ├── lib/           # API client, utilities
│   │   └── i18n.ts        # Translation config
│   └── public/
│       └── locales/       # en.json, ar.json (200+ keys)
├── backend/               # FastAPI + Python
│   ├── app/
│   │   ├── api/           # Routes (pickup, calls, etc.)
│   │   └── services/      # ElevenLabs, Claude
│   └── .env               # API keys
└── docs/                  # Documentation
    ├── TASKS_COMPLETE.md  # ✅ All tasks done!
    ├── COMPLETE_ANALYSIS.md
    └── ...more docs
├── backend/          # (Coming soon) Node.js/Express API
└── README.md         # This file
```

## Getting Started

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

The application will be available at `http://localhost:8080`

### Building for Production

```bash
cd frontend
npm run build
```

## Development

- Frontend runs on port 8080
- Built with modern React practices and performance optimizations
- Component library based on shadcn/ui
- Fully responsive design (13" to ultrawide monitors)
- Accessibility-first approach (WCAG AA compliant)

## License

Proprietary - All rights reserved
