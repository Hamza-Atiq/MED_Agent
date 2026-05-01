# MedAgent — Task Assignments
# HEC Hackathon | 48 Hours | Team of 6

---

# PERSON A — Hamza (Team Leader & Integrator)

---

# PERSON B — Backend Developer

## Your Role
FastAPI backend. The glue between WhatsApp, agents, and database.

## Tech You Need
```bash
pip install fastapi uvicorn python-dotenv supabase httpx
```

## Your Tasks (in order)

### Phase 1: Dummy Mode (Hour 0-8)
Build the server with hardcoded responses. No database yet.

```python
# backend/main.py — start here
from fastapi import FastAPI
app = FastAPI(title="MedAgent API")

# Test this first
@app.get("/health")
def health():
    return {"status": "MedAgent is running"}

# Dummy webhook — returns hardcoded response
@app.post("/webhook")
async def webhook(data: dict):
    return {"response": "Please stay calm. Help is coming."}
```

### Phase 2: Real Connections (Hour 8-20)
- Connect Supabase (use `services/supabase_client.py`)
- Connect WhatsApp webhook (receive + send messages)
- Connect agent runner (call `run_agent()` from agents/)

### Phase 3: All Routes (Hour 20-32)
```
GET  /api/doctors              → list all doctors from Supabase
GET  /api/activity-logs        → list recent patient cases
POST /api/appointments         → create new appointment
GET  /api/doctors/{id}         → single doctor profile
```

## Your Input
- Supabase credentials from Person E
- `run_agent()` function signature from Person C (agents)

## Your Output
A running FastAPI server deployed on Railway with:
- `/webhook` working (receives WhatsApp, calls agents, replies)
- `/api/doctors` returning doctor list
- `/api/activity-logs` returning case logs

## Your Deployed URL format
```
https://medagent-backend.up.railway.app
```
Share this URL with Person D (frontend) and Person F (WhatsApp).

---

# PERSON C — Agent Developer (Most Important Role)

## Your Role
Build all 5 AI agents using OpenAI Agents SDK.
This is the brain of the entire system.

## Tech You Need
```bash
pip install openai-agents python-dotenv supabase
```

## Your Model Strategy (Free, No Cost)
```python
# Primary model — use for main + triage agents
MODEL_PRIMARY = "meta-llama/llama-4-maverick:free"

# Secondary model — use for dispatch + guidance agents  
MODEL_SECONDARY = "google/gemini-2.0-flash-exp:free"

# Connect via OpenRouter (2 line change from OpenAI)
from openai import AsyncOpenAI
client = AsyncOpenAI(
    api_key="OPENROUTER_API_KEY",
    base_url="https://openrouter.ai/api/v1"
)
```

## The 5 Agents You Build

### Agent 1 — Main Orchestrator
```python
# Collects: name, phone, problem description
# Gives: instant calm response
# Then: hands off to Triage Agent
# Tone: like a calm nurse at a reception desk
```

### Agent 2 — Triage Agent
```python
# Input: patient's described symptoms
# Output: classification + urgency score
# Classes: "cardiac" | "trauma" | "neuro" | "general"
# Urgency: "critical" | "moderate" | "low"
# Rule: NEVER say "you have [disease]"
# Say: "symptoms suggest possible cardiac emergency"
```

### Agent 3 — Dispatch Agent
```python
# Input: emergency_type + patient city
# Calls: find_doctor() tool → gets doctor from Supabase
# Calls: send_alert() tool → WhatsApp message to doctor
# Output: doctor name + ETA
```

### Agent 4 — Medical Guidance Agent
```python
# Input: emergency_type
# Output: 3-5 clear first-aid steps
# Rule: simple language, no medical jargon
# Rule: always add disclaimer at end
# Example output for cardiac:
# "1. Help him sit upright
#  2. Loosen tight clothing around chest
#  3. Do not give food or water
#  4. Stay with him, keep him calm
#  ⚠️ This is not medical advice..."
```

### Agent 5 — Logging Agent
```python
# Runs in parallel (not in sequence)
# Saves to Supabase: conversation, classification, doctor assigned
# Input: full context dict
# Output: log_id (confirmation it saved)
```

## Your Main Entry Point (backend calls this)
```python
# agents/runner.py
async def run_agent(message: str, patient_phone: str) -> dict:
    # orchestrate all agents
    # return this exact structure — do not change keys
    return {
        "response": str,
        "emergency_type": str,
        "urgency": str,
        "doctor_assigned": str,
        "disclaimer": str
    }
```

## Your Input
- `find_doctor()` tool stub from Person E (or use dummy data)

## Your Output
`agents/runner.py` with `run_agent()` working.
Test it with this before saying done:
```python
result = await run_agent("my father has chest pain", "+923001234567")
print(result)  # must return all 5 keys
```

---

# PERSON D — Frontend Developer

## Your Role
Build the mobile-first web app. Two pages: Patient Chat + Doctor Dashboard.

## Tech You Need
```bash
npx create-next-app@latest frontend --typescript --tailwind
cd frontend
npm install @supabase/supabase-js
```

## Page 1 — Patient Chat (/)
Simple, clean, mobile-first chat interface.

```
┌─────────────────────────────┐
│  🏥 MedAgent                │
│  Emergency Healthcare       │
├─────────────────────────────┤
│                             │
│  [AI bubble]: Hello! I'm    │
│  MedAgent. What is your     │
│  emergency?                 │
│                             │
│  [Patient bubble]: My       │
│  father has chest pain      │
│                             │
│  [AI bubble]: Please stay   │
│  calm. Make him sit         │
│  upright... 🫀              │
│                             │
├─────────────────────────────┤
│  [Type your message...] [→] │
└─────────────────────────────┘
```

### Phase 1 Dummy (Hour 0-8):
Hardcode 3 messages. Show the UI working. No API calls yet.

### Phase 2 Real (Hour 8-20):
```typescript
// Call backend webhook
const response = await fetch(`${BACKEND_URL}/webhook`, {
  method: 'POST',
  body: JSON.stringify({ message, phone: "demo-user" })
})
```

## Page 2 — Doctor Dashboard (/dashboard)
Live updates. This is the "wow" moment for judges.

```
┌──────────────────────────────────────────────────┐
│  📊 MedAgent Dashboard          🟢 Live          │
├──────────────┬───────────────────────────────────┤
│ INCOMING     │  Patient: Muhammad Ali            │
│ CASES        │  Problem: Chest pain              │
│              │  AI Triage: 🔴 CARDIAC/CRITICAL   │
│ 🔴 Ali (2m) │  Doctor: Dr. Ahmed (Cardiology)   │
│ 🟡 Sara (8m)│  Status: ✅ Doctor Notified        │
│ 🟢 Zaid(15m)│  Response Time: 00:01:23          │
└──────────────┴───────────────────────────────────┘
```

### Use Supabase real-time for live updates:
```typescript
// frontend/lib/supabase.ts
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)

// Subscribe to new activity logs
supabase
  .channel('activity_logs')
  .on('postgres_changes', { event: 'INSERT', schema: 'public' }, 
    (payload) => updateDashboard(payload.new))
  .subscribe()
```

## Your Input
- Backend URL from Person B
- Supabase credentials from Person E
- Agent response structure from Person C

## Your Output
- Working Next.js app deployed on Vercel
- Both pages functional with dummy data first
- Share Vercel URL with Hamza 

---

# PERSON E — Database & Dummy Data

## Your Role
Set up Supabase, create all tables, seed dummy data.
This is the foundation everyone else builds on.
You must finish first so others can start.

## PRIORITY: Finish by Hour 4

## Tech You Need
```bash
pip install supabase python-dotenv
```

## Step 1 — Create Tables (database/schema.sql)

```sql
-- Run this in Supabase SQL Editor

CREATE TABLE patients (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  phone TEXT UNIQUE NOT NULL,
  whatsapp_id TEXT,
  city TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE doctors (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  specialty TEXT NOT NULL,  -- 'cardiology','trauma','neurology','general'
  phone TEXT NOT NULL,
  whatsapp_id TEXT,
  city TEXT NOT NULL,
  is_available BOOLEAN DEFAULT TRUE,
  rating FLOAT DEFAULT 5.0,
  total_cases INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE appointments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  patient_id UUID REFERENCES patients(id),
  doctor_id UUID REFERENCES doctors(id),
  problem_description TEXT,
  emergency_type TEXT,
  urgency_level TEXT,
  status TEXT DEFAULT 'pending',
  is_home_visit BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE activity_logs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  patient_id UUID REFERENCES patients(id),
  doctor_id UUID REFERENCES doctors(id),
  agent_used TEXT,
  emergency_type TEXT,
  urgency_level TEXT,
  patient_message TEXT,
  ai_response TEXT,
  doctor_notified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## Step 2 — Seed Dummy Data (database/dummy_data.sql)

```sql
-- 10 Doctors across Pakistan cities
INSERT INTO doctors (name, specialty, phone, whatsapp_id, city, rating) VALUES
('Dr. Ahmed Khan', 'cardiology', '+923001111111', '923001111111', 'Lahore', 4.9),
('Dr. Sara Malik', 'cardiology', '+923002222222', '923002222222', 'Karachi', 4.8),
('Dr. Bilal Hussain', 'trauma', '+923003333333', '923003333333', 'Lahore', 4.7),
('Dr. Fatima Ali', 'trauma', '+923004444444', '923004444444', 'Islamabad', 4.9),
('Dr. Usman Sheikh', 'neurology', '+923005555555', '923005555555', 'Lahore', 4.6),
('Dr. Ayesha Raza', 'neurology', '+923006666666', '923006666666', 'Karachi', 4.8),
('Dr. Imran Qureshi', 'general', '+923007777777', '923007777777', 'Peshawar', 4.5),
('Dr. Zainab Noor', 'general', '+923008888888', '923008888888', 'Lahore', 4.7),
('Dr. Hassan Baig', 'cardiology', '+923009999999', '923009999999', 'Rawalpindi', 4.8),
('Dr. Mariam Iqbal', 'general', '+923010101010', '923010101010', 'Multan', 4.6);
```

## Step 3 — Python Helper (backend/services/supabase_client.py)
Write this so Person B and C can import it:

```python
# backend/services/supabase_client.py
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

async def find_doctor_by_specialty(specialty: str, city: str = "Lahore") -> dict:
    result = supabase.table("doctors")\
        .select("*")\
        .eq("specialty", specialty)\
        .eq("city", city)\
        .eq("is_available", True)\
        .limit(1)\
        .execute()
    return result.data[0] if result.data else None

async def save_activity_log(log_data: dict) -> str:
    result = supabase.table("activity_logs").insert(log_data).execute()
    return result.data[0]["id"]
```

## Your Input
- Supabase project 

## Your Output
Share with team by Hour 4:
- Supabase URL
- Supabase Anon Key
- Confirmation that all 4 tables exist
- Confirmation that 10 doctors are seeded
- `supabase_client.py` pushed to GitHub

---

# PERSON F — WhatsApp Integration & Demo

## Your Role
Connect the WhatsApp webhook. Own the demo script.
Make sure the demo looks perfect for judges.

## Tech You Need
```bash
pip install pywa fastapi uvicorn
```

## Task 1 — WhatsApp Setup (Hour 0-6)
Follow these exact steps:
1. Go to developers.facebook.com
2. Create new app → Business → WhatsApp
3. Get Phone Number ID and Access Token
4. Set Verify Token to: `medagent_secret_2026`
5. Set Webhook URL to Person B's Railway URL + `/webhook`

## Task 2 — Test WhatsApp (Hour 6-16)
```python
# Test sending a WhatsApp message
import httpx

async def send_whatsapp(to_number: str, message: str):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {META_WA_TOKEN}"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message}
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
    return response.json()
```

## Task 3 — Demo Script (Hour 16-40)
Write the exact demo flow in `docs/demo_script.md`:

```
JUDGE DEMO — 3 MINUTES

[0:00] Show the web app on phone (mobile view)
[0:15] Send WhatsApp message: "My father has severe chest pain"  
[0:25] Show AI response arriving instantly on WhatsApp
[0:40] Switch to dashboard — show case appearing live
[1:00] Show AI triage: CARDIAC / CRITICAL
[1:10] Show doctor assigned: Dr. Ahmed Khan
[1:20] Show doctor WhatsApp alert received
[1:35] Book appointment through the app
[1:50] Show activity log updated
[2:00] Talk about impact: 3B WhatsApp users, home healthcare gap
[2:30] Q&A ready
```

## Task 4 — Demo Video (Hour 44-48)
Record the full demo using your phone screen recording.
Keep it under 3 minutes.
Upload to YouTube unlisted and add link to Devpost.

## Your Input
- Railway backend URL from Person B
- Supabase credentials from Person E

## Your Output
- WhatsApp webhook connected and tested
- `send_whatsapp()` function working
- Demo script complete
- Demo video recorded

---

# INTEGRATION CHECKPOINTS

## Checkpoint 1 — Hour 8
- [ ] Person E: Database tables + dummy data done ✓
- [ ] Person B: `/health` endpoint live on Railway ✓
- [ ] Person C: `run_agent()` returns correct structure with dummy LLM ✓
- [ ] Person D: Chat UI renders with hardcoded messages ✓

## Checkpoint 2 — Hour 20
- [ ] Person B: `/webhook` calls `run_agent()` and returns response ✓
- [ ] Person C: All 5 agents connected to real OpenRouter models ✓
- [ ] Person D: Chat page calls real backend ✓
- [ ] Person F: WhatsApp sends and receives test messages ✓

## Checkpoint 3 — Hour 32
- [ ] Full flow works: WhatsApp → Backend → Agents → DB → WhatsApp ✓
- [ ] Dashboard shows live data from Supabase ✓
- [ ] Doctor receives WhatsApp alert ✓

## Checkpoint 4 — Hour 40 (NO NEW FEATURES AFTER THIS)
- [ ] End-to-end demo works perfectly ✓
- [ ] Deployed on Vercel + Railway ✓
- [ ] Demo script rehearsed ✓

---

# IF YOU ARE STUCK

1. Read CLAUDE.md again
2. Use dummy data and keep moving
3. Open Claude Code — it has read CLAUDE.md and knows the full project
4. Message Hamza immediately — do not wait silently
5. Your branch is independent — a bug in your piece does not block others

---

# REMEMBER

The judges are not testing if you used 10 agents.
They are testing: does it work? does it solve a real problem? can you explain it?

Build simple. Build working. Build impressive demo.