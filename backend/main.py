import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

from backend.routers import webhook, doctors, appointments

app = FastAPI(
    title="MedAgent API",
    version="3.0.0",
    description="AI Emergency Response Orchestrator — OpenAI Agents SDK + Groq + XAI",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router)
app.include_router(doctors.router)
app.include_router(appointments.router)


@app.get("/health")
def health():
    return {"status": "MedAgent is running", "version": "3.0.0", "sdk": "openai-agents"}


# ── /api/chat — used by Next.js chat UI (Faheem's cleaner endpoint) ───────────

class ChatRequest(BaseModel):
    message: str
    phone: str = "demo-user"
    name: str = "Patient"
    city: str = "Lahore"
    history: list = []


@app.post("/api/chat")
async def api_chat(req: ChatRequest):
    """Web chat endpoint — runs full SDK agent pipeline."""
    from medagents.runner import run_agent
    result = await run_agent(
        message=req.message,
        patient_phone=req.phone,
        patient_name=req.name,
        city=req.city,
        history=req.history or None,
    )
    return result


# ── /api/activity-logs + /api/dashboard/logs (both work) ─────────────────────

@app.get("/api/activity-logs")
@app.get("/api/dashboard/logs")
async def get_activity_logs(limit: int = 20):
    from backend.services.supabase_client import get_activity_logs
    logs = await get_activity_logs(limit=limit)
    return {"logs": logs}
