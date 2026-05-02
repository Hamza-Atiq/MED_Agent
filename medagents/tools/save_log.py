import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from backend.services.supabase_client import save_activity_log

logger = logging.getLogger(__name__)


async def save_log(
    patient_id: str,
    doctor_id: str,
    patient_message: str,
    ai_response: str,
    emergency_type: str,
    urgency_level: str,
    doctor_notified: bool,
    reasoning: str,
    key_symptoms: list,
    confidence: str,
    triage_flags: list,
) -> str | None:
    log_data = {
        "patient_id": patient_id if patient_id else None,
        "doctor_id": doctor_id if doctor_id else None,
        "agent_used": "main_agent",
        "emergency_type": emergency_type,
        "urgency_level": urgency_level,
        "patient_message": patient_message,
        "ai_response": ai_response,
        "doctor_notified": doctor_notified,
        "reasoning": reasoning,
        "key_symptoms": key_symptoms,
        "confidence": confidence,
        "triage_flags": triage_flags,
    }
    log_id = await save_activity_log(log_data)
    if log_id:
        logger.info(f"Activity log saved: {log_id}")
    else:
        logger.warning("Activity log could not be saved (DB unavailable, continuing)")
    return log_id
