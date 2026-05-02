import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.models.schemas import AppointmentRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/appointments", tags=["appointments"])


class StatusUpdate(BaseModel):
    status: str  # pending | confirmed | completed | cancelled


@router.post("")
async def create_appointment(data: AppointmentRequest):
    from backend.services.supabase_client import get_or_create_patient, create_appointment

    patient = await get_or_create_patient(data.patient_phone)
    patient_id = patient.get("id")

    appt_data = {
        "patient_id": patient_id,
        "doctor_id": data.doctor_id,
        "problem_description": data.problem_description,
        "emergency_type": data.emergency_type,
        "urgency_level": data.urgency_level,
        "is_home_visit": data.is_home_visit,
        "status": "pending",
    }
    if data.scheduled_at:
        appt_data["scheduled_at"] = data.scheduled_at.isoformat()

    appt = await create_appointment(appt_data)
    if appt:
        return {"status": "booked", "appointment_id": appt["id"]}
    return {"status": "booked", "appointment_id": "offline-booking"}


@router.patch("/{appointment_id}")
async def update_appointment(appointment_id: str, body: StatusUpdate):
    """Update appointment status from the dashboard."""
    from backend.services.supabase_client import update_appointment_status
    await update_appointment_status(appointment_id, body.status)
    return {"updated": True, "appointment_id": appointment_id, "status": body.status}


@router.get("")
async def list_appointments():
    from backend.services.supabase_client import get_client
    try:
        client = get_client()
        result = (
            client.table("appointments")
            .select("*, patients(name, phone), doctors(name, specialty)")
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )
        return {"appointments": result.data or []}
    except Exception as e:
        logger.error(f"list_appointments error: {e}")
        return {"appointments": []}
