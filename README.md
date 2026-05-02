# MedAgent — AI Emergency Healthcare Assistant

AI-powered emergency response system for Pakistan. A patient describes their emergency on WhatsApp or the web chat. The AI instantly provides first-aid guidance, classifies the emergency, and dispatches the nearest available doctor for a home visit.

**Built with:** OpenAI Agents SDK · Groq (llama-3.3-70b) · FastAPI · Supabase · Next.js

**HEC Generative AI Hackathon 2026** — Team of 6, 48-hour sprint.

---

## Features

- **7 specialist AI agents** — cardiac, trauma, neuro, respiratory, gynae, pediatric, general
- **XAI reasoning layer** — every triage decision explains *why* (key symptoms, confidence, flags)
- **WhatsApp-first** — works via Meta Cloud API, falls back gracefully to simulation
- **Live dashboard** — real-time case monitor with Supabase Realtime + polling fallback
- **Doctor dispatch** — finds nearest available doctor by specialty and city, sends WhatsApp alert
- **Appointment booking** — home visit booking from the chat UI

---

## Architecture

```
Patient (WhatsApp / Web)
        ↓
FastAPI Backend  (/api/chat or /webhook)
        ↓
XAI Triage  →  emergency_type + urgency + reasoning + key_symptoms
        ↓
OpenAI Agents SDK  →  Specialist Agent (Groq llama-3.3-70b)
        ↓
First-aid guidance text
        ↓
Doctor lookup (Supabase) → WhatsApp alert → Activity log
        ↓
Response to patient  +  Live dashboard update
```

---

## Quick Start (Local)

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/medagent.git
cd medagent

# Install Python deps (using uv)
pip install uv
uv sync

# Install frontend deps
cd frontend && npm install && cd ..
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Fill in your keys — see Environment Variables section below
```

### 3. Set up Supabase database

Go to your [Supabase dashboard](https://app.supabase.com) → SQL Editor, then run in order:

```sql
-- Step 1: Run database/schema.sql
-- Step 2: Run database/dummy_data.sql
```

### 4. Run backend

```bash
uv run uvicorn backend.main:app --reload --port 8000
```

### 5. Run frontend

```bash
cd frontend
npm run dev
# Open http://localhost:3000
```

---

## Environment Variables

Create a `.env` file in the project root (never commit this):

```bash
# LLM providers
GROQ_API_KEY=gsk_...              # https://console.groq.com
OPENROUTER_API_KEY=sk-or-...      # https://openrouter.ai (fallback)

# WhatsApp Meta Cloud API (leave as-is to use simulation mode)
META_WA_TOKEN=EAA...
META_PHONE_NUMBER_ID=1234...
META_VERIFY_TOKEN=medagent_secret_2026

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...  # Project Settings → API → service_role

# Frontend (Supabase public keys)
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...

# Set this to your Render backend URL after deploying
NEXT_PUBLIC_BACKEND_URL=https://medagent-backend.onrender.com
```

---

## Deployment

### Backend → Render (free)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Render auto-detects `render.yaml` — just click **Deploy**
5. Add environment variables in Render dashboard (Environment tab)
6. Copy your Render URL: `https://medagent-backend-xxxx.onrender.com`

### Frontend → Vercel

1. Go to [vercel.com](https://vercel.com) → New Project → Import your GitHub repo
2. Set **Root Directory** to `frontend`
3. Add environment variables:
   - `NEXT_PUBLIC_BACKEND_URL` = your Render URL from above
   - `NEXT_PUBLIC_SUPABASE_URL` = your Supabase URL
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = your Supabase anon key
4. Click **Deploy**

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Main chat endpoint (web UI) |
| POST | `/webhook` | WhatsApp webhook |
| GET | `/api/doctors` | List all doctors |
| GET | `/api/activity-logs` | Recent cases for dashboard |
| POST | `/api/appointments` | Book a home visit |
| GET | `/health` | Health check |

### POST /api/chat

**Request:**
```json
{
  "message": "My father has chest pain",
  "phone": "+923001234567",
  "name": "Hamza",
  "city": "Lahore",
  "history": []
}
```

**Response:**
```json
{
  "greeting": "Assalam o Alaikum Hamza! I'm MedAgent...",
  "response": "Help your father sit upright...",
  "emergency_type": "cardiac",
  "urgency": "critical",
  "doctor_assigned": "Dr. Ahmed Khan",
  "disclaimer": "⚠️ This guidance is for informational purposes only...",
  "reasoning": "Chest pain with sweating suggests possible cardiac emergency...",
  "key_symptoms": ["chest pain", "sweating"],
  "confidence": "high",
  "triage_flags": ["chest_pain_keyword", "urgency_escalated"]
}
```

---

## Project Structure

```
medagent/
├── medagents/              # AI agent layer (OpenAI Agents SDK)
│   ├── config.py           # Groq client setup
│   ├── triage.py           # XAI classification (our differentiator)
│   ├── specialists.py      # 7 specialist SDK agents
│   ├── tools/              # find_doctor, send_alert, save_log tools
│   └── runner.py           # Main entry point: run_agent()
├── backend/                # FastAPI server
│   ├── main.py             # App + /api/chat, /api/activity-logs
│   ├── routers/            # webhook, doctors, appointments
│   ├── services/           # supabase_client, whatsapp
│   └── models/             # Pydantic schemas
├── frontend/               # Next.js (deployed on Vercel)
│   ├── app/
│   │   ├── page.tsx        # Patient chat page
│   │   └── dashboard/      # Live doctor dashboard
│   └── components/
│       └── ChatWidget.tsx  # WhatsApp-style chat UI
└── database/
    ├── schema.sql           # All tables (run first in Supabase)
    └── dummy_data.sql       # 10 seed doctors (run second)
```

---

## Emergency Numbers (Pakistan)

- **1122** — Punjab Rescue
- **115** — Edhi Foundation
- **1021** — Edhi (Karachi)

---

> ⚠️ MedAgent provides informational first-aid guidance only. It does not replace professional medical advice. Always call emergency services in life-threatening situations.
