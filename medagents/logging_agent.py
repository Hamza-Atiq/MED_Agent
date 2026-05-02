import logging
import asyncio
from agents.tools.save_log import save_log

logger = logging.getLogger(__name__)


async def log_case(
    patient_id: str,
    doctor_id: str,
    patient_message: str,
    ai_response: str,
    emergency_type: str,
    urgency: str,
    doctor_notified: bool,
    reasoning: str,
    key_symptoms: list,
    confidence: str,
    triage_flags: list,
) -> str | None:
    log_id = await save_log(
        patient_id=patient_id,
        doctor_id=doctor_id,
        patient_message=patient_message,
        ai_response=ai_response,
        emergency_type=emergency_type,
        urgency_level=urgency,
        doctor_notified=doctor_notified,
        reasoning=reasoning,
        key_symptoms=key_symptoms,
        confidence=confidence,
        triage_flags=triage_flags,
    )
    return log_id
