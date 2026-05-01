# agents/runner.py
# Person C owns this file
# This is the ONLY function the backend calls — do not change the signature

import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# ── Model Config (free via OpenRouter) ──
MODEL_PRIMARY = "meta-llama/llama-4-maverick:free"
MODEL_SECONDARY = "google/gemini-2.0-flash-exp:free"
OPENROUTER_BASE = "https://openrouter.ai/api/v1"


async def run_agent(message: str, patient_phone: str) -> dict:
    """
    Main entry point. Backend calls this with every patient message.
    
    Args:
        message: what the patient typed
        patient_phone: their WhatsApp number
    
    Returns:
        dict with exactly these keys (do NOT rename them):
        {
            "response": str,          # send this back to patient on WhatsApp
            "emergency_type": str,    # "cardiac" | "trauma" | "neuro" | "general"
            "urgency": str,           # "critical" | "moderate" | "low"
            "doctor_assigned": str,   # doctor name or "searching..."
            "disclaimer": str         # always include
        }
    """

    # ── PHASE 1: Dummy response (so backend can test immediately) ──
    # Delete this block when real agents are ready
    logger.info(f"[DUMMY MODE] Processing: {message}")
    return {
        "response": _get_dummy_response(message),
        "emergency_type": "cardiac",
        "urgency": "critical",
        "doctor_assigned": "Dr. Ahmed Khan (Cardiology, Lahore)",
        "disclaimer": "⚠️ This guidance is for informational purposes only. Please consult a qualified healthcare professional."
    }

    # ── PHASE 2: Real agents (uncomment when ready) ──
    # from agents.main_agent import main_agent
    # from agents import Runner
    # result = await Runner.run(main_agent, message)
    # return result.final_output


def _get_dummy_response(message: str) -> str:
    """Temporary keyword-based response for testing"""
    msg = message.lower()
    if any(w in msg for w in ["chest", "heart", "cardiac", "breathing"]):
        return ("Please stay calm. Help the patient sit upright and loosen "
                "any tight clothing around the chest. Do not give food or water. "
                "A cardiac specialist is being contacted now.")
    elif any(w in msg for w in ["accident", "fall", "injury", "bleeding", "pain"]):
        return ("Please stay calm. Do not move the patient unnecessarily. "
                "Apply gentle pressure to any bleeding wound. "
                "An emergency doctor is being contacted.")
    elif any(w in msg for w in ["fever", "temperature", "hot"]):
        return ("Please keep the patient hydrated with small sips of water. "
                "Apply a cool damp cloth to the forehead. "
                "A doctor is being contacted.")
    else:
        return ("I understand you need help. Please describe the symptoms clearly. "
                "A medical professional is being alerted right now.")