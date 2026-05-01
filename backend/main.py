# backend/main.py
# Person B owns this file
# Run: uvicorn main:app --reload --port 8000

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MedAgent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "MedAgent is running", "version": "1.0.0"}


# ── PHASE 1: Dummy webhook (replace with real in Phase 2) ──
@app.post("/webhook")
async def webhook(data: dict):
    """
    WhatsApp sends messages here.
    Phase 1: returns dummy response
    Phase 2: calls run_agent() from agents/runner.py
    """
    message = data.get("message", "")
    logger.info(f"Received message: {message}")

    # TODO Phase 2: replace this with real agent call
    # from agents.runner import run_agent
    # result = await run_agent(message, data.get("phone", ""))

    dummy_result = {
        "response": "Please stay calm. A specialist is being contacted now.",
        "emergency_type": "cardiac",
        "urgency": "critical",
        "doctor_assigned": "Dr. Ahmed Khan",
        "disclaimer": "⚠️ This is not medical advice."
    }
    return dummy_result


# ── API Routes (connect to Supabase in Phase 2) ──
@app.get("/api/doctors")
async def get_doctors():
    """Returns all available doctors"""
    # TODO: replace with Supabase query
    return {"doctors": [
        {"id": "1", "name": "Dr. Ahmed Khan", "specialty": "cardiology", "city": "Lahore", "rating": 4.9},
        {"id": "2", "name": "Dr. Sara Malik", "specialty": "cardiology", "city": "Karachi", "rating": 4.8},
    ]}


@app.get("/api/activity-logs")
async def get_activity_logs():
    """Returns recent patient cases for dashboard"""
    # TODO: replace with Supabase query
    return {"logs": []}


@app.post("/api/appointments")
async def create_appointment(data: dict):
    """Book a new appointment"""
    # TODO: save to Supabase
    return {"status": "booked", "appointment_id": "dummy-123"}