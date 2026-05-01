# MedAgent — CLAUDE.md
# AI Emergency Response Orchestrator for Home Healthcare
# HEC Hackathon 2026 | Team of 6 | 48 Hours

---

## WHAT IS THIS PROJECT?

MedAgent is a WhatsApp-first AI emergency response system.
A patient messages on WhatsApp describing their emergency.
The AI responds instantly with calm first-aid guidance.
Simultaneously, it finds the nearest available doctor and sends them an alert.
The doctor contacts the patient and can book a home visit.
Everything is logged and shown on a live dashboard.

---

## CRITICAL RULES — READ BEFORE WRITING ANY CODE

1. NEVER make the AI diagnose disease. Say "symptoms may need attention" NOT "you have a heart attack"
2. NEVER use `print()` for logging. Use Python `logging` module always
3. NEVER hardcode API keys. Always use `.env` file + `python-dotenv`
4. ALWAYS handle errors with try/except and return meaningful messages
5. NEVER push to `main` branch directly. Always use your feature branch
6. ALL agent responses must include a disclaimer: "This is not medical advice"
7. ALWAYS test your piece with dummy data before saying it is done

---

## TECH STACK

| Layer | Tool | Why |
|---|---|---|
| Agent Framework | OpenAI Agents SDK | Provider-agnostic, built-in handoffs |
| LLM | OpenRouter (free models) | Free, OpenAI-compatible |
| LLM Backup | Groq API | 14,400 free req/day, fast |
| WhatsApp | Meta Cloud API + pywa | Free within 24h session |
| Backend | FastAPI (Python) | Async, fast, you know Python |
| Database | Supabase (PostgreSQL) | Free tier, relational, real-time |
| Frontend | Next.js | Vercel deploy, mobile-first |
| Deployment | Vercel (frontend) + Railway (backend) | Both free tier |

---

## FOLDER STRUCTURE

```
medagent/
├── CLAUDE.md                  ← YOU ARE HERE
├── .env.example               ← copy this to .env, fill your keys
├── .gitignore
├── README.md
│
├── backend/                   ← Person B owns this
│   ├── main.py                ← FastAPI app entry point
│   ├── requirements.txt
│   ├── routers/
│   │   ├── webhook.py         ← WhatsApp webhook routes
│   │   ├── doctors.py         ← Doctor CRUD routes
│   │   └── appointments.py    ← Appointment routes
│   ├── services/
│   │   ├── supabase_client.py ← DB connection
│   │   └── whatsapp.py        ← Send WhatsApp messages
│   └── models/
│       └── schemas.py         ← Pydantic models (shared contracts)
│
├── agents/                    ← Person C owns this
│   ├── main_agent.py          ← Orchestrator agent
│   ├── triage_agent.py        ← Classifies emergency type
│   ├── dispatch_agent.py      ← Finds doctor, sends alert
│   ├── guidance_agent.py      ← First-aid instructions
│   ├── logging_agent.py       ← Saves everything to DB
│   ├── tools/
│   │   ├── find_doctor.py     ← Tool: query Supabase for doctors
│   │   ├── send_alert.py      ← Tool: send WhatsApp to doctor
│   │   └── save_log.py        ← Tool: save activity log
│   └── runner.py              ← Entry point: run_agent(message, phone)
│
├── frontend/                  ← Person D owns this
│   ├── app/
│   │   ├── page.tsx           ← Landing / patient chat page
│   │   ├── dashboard/
│   │   │   └── page.tsx       ← Live doctor dashboard
│   │   └── doctors/
│   │       └── page.tsx       ← Doctor profile page
│   ├── components/
│   │   ├── ChatWidget.tsx     ← Patient chat UI
│   │   ├── AlertCard.tsx      ← Incoming patient alert card
│   │   └── DoctorProfile.tsx  ← Doctor stats card
│   └── lib/
│       └── supabase.ts        ← Frontend Supabase client
│
├── database/                  ← Person E owns this
│   ├── schema.sql             ← All CREATE TABLE statements
│   ├── dummy_data.sql         ← 10 doctors, 5 patients seed data
│   └── README.md              ← How to run migrations
│
└── docs/                      ← Person F (you/leader) owns this
    ├── architecture.html      ← Team architecture document
    ├── demo_script.md         ← Exact demo flow for judges
    └── task_board.md          ← Who is doing what
```

---

## API CONTRACTS (READ THIS — prevents merge conflicts)

### 1. Agent Runner (agents/runner.py)
```python
# This is the ONLY function backend calls into agents
async def run_agent(message: str, patient_phone: str) -> dict:
    return {
        "response": str,          # message to send back to patient
        "emergency_type": str,    # "cardiac" | "trauma" | "neuro" | "general"
        "urgency": str,           # "critical" | "moderate" | "low"
        "doctor_assigned": str,   # doctor name or "searching..."
        "disclaimer": str         # always include this
    }
```

### 2. Backend Webhook (backend/routers/webhook.py)
```python
# WhatsApp sends POST here when patient messages
# This calls run_agent() and replies back on WhatsApp
POST /webhook
```

### 3. Doctor Lookup (agents/tools/find_doctor.py)
```python
# Returns doctor from Supabase based on specialty + city
async def find_doctor(specialty: str, city: str) -> dict:
    return {
        "doctor_id": str,
        "name": str,
        "phone": str,
        "whatsapp_id": str
    }
```

### 4. Frontend Dashboard API
```
GET /api/activity-logs     → list of recent patient cases
GET /api/doctors           → list of all doctors
POST /api/appointments     → book an appointment
```

---

## ENVIRONMENT VARIABLES

```bash
# copy .env.example to .env — never commit .env to GitHub

OPENROUTER_API_KEY=sk-or-...
GROQ_API_KEY=gsk_...
META_WA_TOKEN=EAA...
META_PHONE_NUMBER_ID=1234...
META_VERIFY_TOKEN=medagent_secret_2026
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

---

## DUMMY DATA FIRST — ALWAYS

Before connecting real APIs, every person must make their piece
work with dummy data. This means:

- Agents: respond to hardcoded test messages first
- Backend: return hardcoded JSON before connecting Supabase  
- Frontend: render hardcoded doctor/patient data before API calls
- Database: seed script must run before anyone else starts

---

## GIT WORKFLOW

```bash
# Each person works on their own branch
git checkout -b feature/your-name-task

# Commit often with clear messages
git commit -m "feat: add triage agent classification logic"
git commit -m "fix: handle empty patient message"
git commit -m "docs: add doctor schema"

# When done, open Pull Request to main
# Hamza (leader) reviews and merges
```

---

## EMERGENCY CONTACT (Integration Issues)

If your piece is blocked because you need something from another person:
1. Message Hamza immediately — do not wait
2. Use dummy data and keep building

---

## THE DEMO FLOW (memorize this)

1. Patient sends WhatsApp: "My father has chest pain"
2. Main Agent replies instantly with first-aid + calm message
3. Triage Agent classifies: CARDIAC / CRITICAL
4. Dispatch Agent finds nearest cardiologist in Supabase
5. Doctor receives WhatsApp alert with patient info
6. Dashboard shows live: patient card, AI triage, assigned doctor, timer
7. Patient can book appointment through the app

**This 7-step flow must work end-to-end before Hour 40.**

---

## MEDICAL DISCLAIMER (use in every agent response)

"⚠️ This guidance is for informational purposes only and does not
constitute medical advice. Please consult a qualified healthcare
professional. In life-threatening emergencies, call emergency services."