"""
medagents/tools.py
All @function_tool definitions shared across specialist agents.
Pattern from Abdullah & Zain — tools are the agents' hands.
"""
import os
import logging
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import httpx
from agents import function_tool
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

META_WA_TOKEN = os.getenv("META_WA_TOKEN", "")
META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID", "")
_WA_SIMULATED = (
    not META_WA_TOKEN
    or META_WA_TOKEN.startswith("EAA...")
    or len(META_WA_TOKEN) < 20
)

# ── SPECIALTY MAP ─────────────────────────────────────────────────────────────

SPECIALTY_MAP = {
    "cardiac":      "cardiology",
    "trauma":       "trauma",
    "neuro":        "neurology",
    "respiratory":  "general",
    "gynae":        "general",
    "pediatric":    "general",
    "general":      "general",
}

_FALLBACK_DOCTORS = {
    "cardiology": {"id": "f1", "name": "Dr. Ahmed Khan",    "specialty": "cardiology", "city": "Lahore",    "phone": "+923001111111", "rating": 4.9},
    "trauma":     {"id": "f2", "name": "Dr. Bilal Hussain", "specialty": "trauma",     "city": "Lahore",    "phone": "+923003333333", "rating": 4.7},
    "neurology":  {"id": "f3", "name": "Dr. Usman Sheikh",  "specialty": "neurology",  "city": "Lahore",    "phone": "+923005555555", "rating": 4.6},
    "general":    {"id": "f4", "name": "Dr. Zainab Noor",   "specialty": "general",    "city": "Lahore",    "phone": "+923008888888", "rating": 4.7},
}


# ── TOOL 1: FIND DOCTOR ───────────────────────────────────────────────────────

@function_tool
async def find_doctor(emergency_type: str, city: str = "Lahore") -> str:
    """
    Find an available doctor by emergency type and city.
    Returns doctor details as a formatted string.
    """
    from backend.services.supabase_client import find_doctor as db_find

    specialty = SPECIALTY_MAP.get(emergency_type.lower(), "general")
    try:
        doctor = await db_find(specialty, city)
    except Exception:
        doctor = None

    if not doctor:
        doctor = _FALLBACK_DOCTORS.get(specialty, _FALLBACK_DOCTORS["general"])
        logger.warning(f"DB doctor not found for {specialty}/{city}, using fallback")

    return (
        f"Doctor found: {doctor['name']} | "
        f"Specialty: {doctor.get('specialty', specialty)} | "
        f"City: {doctor.get('city', city)} | "
        f"Phone: {doctor.get('phone', 'N/A')} | "
        f"Rating: {doctor.get('rating', 'N/A')} | "
        f"ID: {doctor.get('id', 'unknown')}"
    )


# ── TOOL 2: SEND WHATSAPP ALERT ───────────────────────────────────────────────

@function_tool
async def send_whatsapp_alert(
    doctor_name: str,
    doctor_phone: str,
    patient_name: str,
    patient_phone: str,
    emergency_type: str,
    urgency: str,
    first_aid_summary: str,
) -> str:
    """
    Send a WhatsApp alert to the assigned doctor with patient details.
    Returns confirmation of alert status.
    """
    message = (
        f"🚨 MedAgent Emergency Alert\n\n"
        f"👤 Patient: {patient_name} | 📞 {patient_phone}\n"
        f"🩺 Emergency: {emergency_type.upper()} / {urgency.upper()}\n\n"
        f"First Aid Given:\n{first_aid_summary}\n\n"
        f"Please contact the patient immediately.\n"
        f"⚠️ This is an automated MedAgent alert."
    )

    if _WA_SIMULATED:
        logger.info(f"[SIMULATED WhatsApp → Dr. {doctor_name} ({doctor_phone})]: alert sent")
        return f"Alert sent (simulated) to Dr. {doctor_name} at {doctor_phone}"

    try:
        url = f"https://graph.facebook.com/v18.0/{META_PHONE_NUMBER_ID}/messages"
        headers = {"Authorization": f"Bearer {META_WA_TOKEN}", "Content-Type": "application/json"}
        payload = {
            "messaging_product": "whatsapp",
            "to": doctor_phone.replace("+", ""),
            "type": "text",
            "text": {"body": message},
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return f"Alert sent to Dr. {doctor_name}"
    except Exception as e:
        logger.error(f"send_whatsapp_alert error: {e}")
        return f"Alert failed: {e} (patient must be contacted manually)"


# ── TOOL 3: SAVE ACTIVITY LOG ─────────────────────────────────────────────────

@function_tool
async def save_activity_log(
    patient_phone: str,
    doctor_id: str,
    emergency_type: str,
    urgency_level: str,
    patient_message: str,
    ai_response: str,
    doctor_notified: bool,
) -> str:
    """
    Save the full case record to the database for the live dashboard.
    Returns the log ID on success.
    """
    from backend.services.supabase_client import (
        get_or_create_patient,
        save_activity_log as db_save,
        increment_doctor_cases,
    )
    try:
        patient = await get_or_create_patient(patient_phone)
        patient_id = patient.get("id")
        log_id = await db_save({
            "patient_id": patient_id,
            "doctor_id": doctor_id if doctor_id and doctor_id != "unknown" else None,
            "agent_used": "sdk_orchestrator",
            "emergency_type": emergency_type,
            "urgency_level": urgency_level,
            "patient_message": patient_message,
            "ai_response": ai_response,
            "doctor_notified": doctor_notified,
        })
        if doctor_id and doctor_id != "unknown":
            await increment_doctor_cases(doctor_id)
        return f"Log saved: {log_id}"
    except Exception as e:
        logger.error(f"save_activity_log tool error: {e}")
        return "Log could not be saved (DB unavailable)"


# ── TOOL 4: BOOK APPOINTMENT ─────────────────────────────────────────────────

@function_tool
async def book_appointment(
    patient_phone: str,
    doctor_id: str,
    problem_description: str,
    emergency_type: str = "general",
    urgency_level: str = "low",
    is_home_visit: bool = True,
) -> str:
    """
    Book a home visit appointment between patient and doctor.
    Returns appointment ID on success.
    """
    from backend.services.supabase_client import get_or_create_patient, create_appointment
    try:
        patient = await get_or_create_patient(patient_phone)
        patient_id = patient.get("id")
        appt = await create_appointment({
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "problem_description": problem_description,
            "emergency_type": emergency_type,
            "urgency_level": urgency_level,
            "is_home_visit": is_home_visit,
            "status": "pending",
        })
        appt_id = appt.get("id", "offline") if appt else "offline"
        return f"Appointment booked successfully. ID: {appt_id}. Doctor will confirm via WhatsApp."
    except Exception as e:
        logger.error(f"book_appointment tool error: {e}")
        return "Appointment could not be booked. Please call the doctor directly."
