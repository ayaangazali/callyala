# Voice Agent Ops - Frontend

React-based web application for the Voice Agent Ops platform.

## Quick Start

```bash
npm install
npm run dev
```

Visit `http://localhost:8080`

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Architecture

- **React 18** with TypeScript
- **Vite** for blazing-fast dev and builds
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Radix UI** for accessible components
- **TanStack Query** for data fetching
- **Recharts** for data visualization

## Project Structure

```
src/
├── components/       # UI components
│   ├── ui/          # Base UI components (buttons, cards, etc.)
│   └── *.tsx        # Feature components
├── hooks/           # Custom React hooks
├── lib/             # Utilities and helpers
│   ├── motion.ts    # Animation variants
│   └── utils.ts     # Common utilities
├── pages/           # Page components
│   ├── Index.tsx    # Dashboard/Overview
│   └── NotFound.tsx # 404 page
├── App.tsx          # Root component
└── main.tsx         # Entry point
```

## Key Features

- Premium motion system with Framer Motion
- Accessible design (WCAG AA compliant)
- Responsive layout (mobile to ultrawide)
- Dark mode support
- Command palette (⌘K)
- Real-time call monitoring
- Advanced analytics dashboard
