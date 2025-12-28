# Voice Agent Ops

Enterprise-grade AI voice agent platform for automotive dealerships. Automate outbound customer calls for vehicle pickup scheduling, service reminders, and follow-ups.

## Features

- **Intelligent Call Management**: Automated outbound calling with AI voice agents powered by ElevenLabs
- **Real-time Analytics**: Track call metrics, answer rates, booking conversions, and sentiment analysis
- **Campaign Management**: Create and manage targeted calling campaigns
- **Appointment Scheduling**: Seamless pickup time and date booking with calendar integration
- **Customer & Vehicle Tracking**: Comprehensive CRM for dealership operations
- **QA & Review**: Call quality monitoring, transcript review, and performance optimization
- **Compliance Built-in**: DNC list management and recording disclosure compliance

## Tech Stack

- **Frontend**: React + TypeScript + Vite
- **UI**: Tailwind CSS + Radix UI + Framer Motion
- **State Management**: TanStack Query
- **Charts**: Recharts
- **Integrations**: Twilio (calling) + ElevenLabs (voice AI)

## Project Structure

```
callyala/
├── frontend/          # React application
│   ├── src/          # Source code
│   ├── public/       # Static assets
│   └── package.json  # Frontend dependencies
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
