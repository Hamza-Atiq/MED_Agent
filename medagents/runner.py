"""
medagents/runner.py
The single entry point the backend calls for every patient message.

Flow:
  1. XAI Triage  (our custom code)  → emergency_type + reasoning + symptoms
  2. SDK Runner.run(main_agent)     → specialist handles guidance + dispatch + logging
  3. Combine everything             → full response dict with XAI fields
"""
import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
import re
from agents import Runner

load_dotenv()
logger = logging.getLogger(__name__)

DISCLAIMER = (
    "⚠️ This guidance is for informational purposes only and does not "
    "constitute medical advice. Please consult a qualified healthcare professional. "
    "In life-threatening emergencies, call 1122 (Punjab Rescue) or 115 (Edhi) immediately."
)


async def run_agent(
    message: str,
    patient_phone: str,
    patient_name: str = "Patient",
    city: str = "Lahore",
    history: list | None = None,
) -> dict:
    """
    Main entry point — backend calls this for every patient message.

    Returns dict with:
        greeting, response, emergency_type, urgency, doctor_assigned,
        disclaimer, reasoning, key_symptoms, confidence, triage_flags
    """
    if not message or not message.strip():
        return _empty_response()

    # ── Step 1: XAI Triage ────────────────────────────────────────────────────
    from medagents.triage import run_triage, _keyword_fallback
    from medagents.config import get_groq_client, get_openrouter_client, GROQ_MODEL, OPENROUTER_MODEL

    triage_result = None
    try:
        triage_result = await run_triage(message, get_groq_client(), GROQ_MODEL)
    except Exception as e:
        logger.warning(f"Groq triage failed: {e}, trying OpenRouter")
        try:
            triage_result = await run_triage(message, get_openrouter_client(), OPENROUTER_MODEL)
        except Exception as e2:
            logger.warning(f"OpenRouter triage also failed: {e2}, keyword fallback")
            triage_result = _keyword_fallback(message)

    emergency_type = triage_result["emergency_type"]
    urgency = triage_result["urgency"]

    # ── Step 2: Build SDK input with context ──────────────────────────────────
    if history:
        history_str = "\n".join(
            f"{'Patient' if m['role'] == 'user' else 'MedAgent'}: {m['content']}"
            for m in history[-6:]
        )
        sdk_input = (
            f"Conversation so far:\n{history_str}\n\n"
            f"Patient: {patient_name} | City: {city}\n"
            f"Latest message: {message}\n"
            f"Triage result: {emergency_type.upper()} / {urgency.upper()}\n"
            f"Please provide first-aid guidance and dispatch a doctor."
        )
    else:
        sdk_input = (
            f"Patient: {patient_name} | City: {city}\n"
            f"Message: {message}\n"
            f"Triage result: {emergency_type.upper()} / {urgency.upper()}\n"
            f"Please provide first-aid guidance and dispatch a doctor."
        )

    # ── Step 3: Run the specialist agent for guidance text only ─────────────────
    # Agents generate first-aid text; tool calls happen directly below (Step 4)
    from medagents.specialists import (
        cardiac_agent, trauma_agent, neuro_agent,
        respiratory_agent, gynae_agent, pediatric_agent, general_agent,
    )

    _AGENT_MAP = {
        "cardiac": cardiac_agent,
        "trauma": trauma_agent,
        "neuro": neuro_agent,
        "respiratory": respiratory_agent,
        "gynae": gynae_agent,
        "pediatric": pediatric_agent,
        "general": general_agent,
    }
    specialist = _AGENT_MAP.get(emergency_type, general_agent)

    sdk_response = ""
    try:
        result = await Runner.run(specialist, sdk_input)
        sdk_response = result.final_output or ""
    except Exception as e:
        logger.error(f"SDK Runner failed: {e}")
        sdk_response = _static_guidance(emergency_type)

    # ── Step 4: Find doctor + save log directly (no LLM tool-call round-trip) ──
    from medagents.tools import SPECIALTY_MAP, _FALLBACK_DOCTORS
    from backend.services.supabase_client import find_doctor as db_find_doctor

    specialty = SPECIALTY_MAP.get(emergency_type, "general")
    doctor_assigned = "Searching..."
    doctor_info = None
    try:
        doctor_info = await db_find_doctor(specialty, city)
    except Exception:
        pass
    if not doctor_info:
        doctor_info = _FALLBACK_DOCTORS.get(specialty, _FALLBACK_DOCTORS["general"])
    doctor_assigned = doctor_info.get("name", "Dr. Ahmed Khan")

    # Send WhatsApp alert to doctor (background — non-blocking)
    asyncio.create_task(_alert_doctor(doctor_info, patient_name, patient_phone, emergency_type, urgency, sdk_response))

    # Save activity log (background — non-blocking)
    asyncio.create_task(_save_log(
        patient_phone, doctor_info, emergency_type, urgency, message, sdk_response, triage_result
    ))

    return {
        "greeting": f"Assalam o Alaikum {patient_name}! I'm MedAgent. Please stay calm — help is being arranged now.",
        "response": sdk_response,
        "emergency_type": emergency_type,
        "urgency": urgency,
        "doctor_assigned": doctor_assigned,
        "disclaimer": DISCLAIMER,
        "reasoning": triage_result["reasoning"],
        "key_symptoms": triage_result["key_symptoms"],
        "confidence": triage_result["confidence"],
        "triage_flags": triage_result["triage_flags"],
    }


async def _alert_doctor(doctor: dict, patient_name: str, patient_phone: str,
                        emergency_type: str, urgency: str, first_aid: str) -> None:
    """Send WhatsApp alert to assigned doctor."""
    import os, httpx
    token = os.getenv("META_WA_TOKEN", "")
    pid = os.getenv("META_PHONE_NUMBER_ID", "")
    simulated = not token or token.startswith("EAA...") or len(token) < 20
    msg = (
        f"🚨 MedAgent Emergency Alert\n\n"
        f"Patient: {patient_name} | {patient_phone}\n"
        f"Emergency: {emergency_type.upper()} / {urgency.upper()}\n\n"
        f"First Aid:\n{first_aid[:300]}\n\n"
        f"Please contact the patient immediately."
    )
    if simulated:
        logger.info(f"[SIMULATED WA] Alert to Dr. {doctor.get('name')} — {emergency_type}/{urgency}")
        return
    try:
        url = f"https://graph.facebook.com/v18.0/{pid}/messages"
        async with httpx.AsyncClient(timeout=10) as c:
            await c.post(url, json={
                "messaging_product": "whatsapp",
                "to": doctor.get("phone", "").replace("+", ""),
                "type": "text",
                "text": {"body": msg},
            }, headers={"Authorization": f"Bearer {token}"})
    except Exception as e:
        logger.error(f"WA alert failed: {e}")


async def _save_log(patient_phone: str, doctor: dict, emergency_type: str, urgency: str,
                    patient_message: str, ai_response: str, triage_result: dict) -> None:
    """Save activity log with XAI fields included."""
    from backend.services.supabase_client import get_or_create_patient, save_activity_log as db_save
    _UUID_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)
    doctor_id = doctor.get("id")
    safe_doctor_id = doctor_id if doctor_id and _UUID_RE.match(str(doctor_id)) else None
    try:
        patient = await get_or_create_patient(patient_phone)
        patient_id = patient.get("id")
        await db_save({
            "patient_id": patient_id,
            "doctor_id": safe_doctor_id,
            "agent_used": "sdk_specialist",
            "emergency_type": emergency_type,
            "urgency_level": urgency,
            "patient_message": patient_message,
            "ai_response": ai_response,
            "doctor_notified": True,
            "reasoning": triage_result["reasoning"],
            "key_symptoms": triage_result["key_symptoms"],
            "confidence": triage_result["confidence"],
            "triage_flags": triage_result["triage_flags"],
        })
    except Exception as e:
        logger.warning(f"Log save failed: {e}")


def _empty_response() -> dict:
    return {
        "greeting": "Assalam o Alaikum! I'm MedAgent. Please describe what is happening.",
        "response": "Please describe the emergency clearly and I will help you immediately.",
        "emergency_type": "general",
        "urgency": "low",
        "doctor_assigned": "Searching...",
        "disclaimer": DISCLAIMER,
        "reasoning": "Empty message received.",
        "key_symptoms": [],
        "confidence": "low",
        "triage_flags": ["empty_message"],
    }


def _static_guidance(emergency_type: str) -> str:
    guides = {
        "cardiac":     "1. Help patient sit upright.\n2. Loosen tight clothing.\n3. Do NOT give food or water.\n4. Keep calm. A cardiac specialist is being contacted now.",
        "trauma":      "1. Do NOT move patient if spine injury suspected.\n2. Apply firm pressure to any bleeding.\n3. Keep warm and still. An emergency doctor is being contacted.",
        "neuro":       "1. Lay patient on their side.\n2. Note the time symptoms started.\n3. Do NOT give food or water. A neurologist is being contacted.",
        "respiratory": "1. Sit patient upright.\n2. Open windows for fresh air.\n3. Monitor temperature. A doctor is being contacted.",
        "gynae":       "1. Help patient rest comfortably.\n2. Do NOT exert.\n3. A gynaecologist is being contacted.",
        "pediatric":   "1. Keep child calm and comfortable.\n2. Check temperature.\n3. A paediatrician is being contacted.",
        "general":     "1. Help patient rest.\n2. Keep warm and calm.\n3. A doctor is being contacted shortly.",
    }
    return guides.get(emergency_type, guides["general"])
