import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/doctors", tags=["doctors"])


class AvailabilityUpdate(BaseModel):
    available: bool


@router.get("")
async def get_doctors():
    from backend.services.supabase_client import get_all_doctors
    doctors = await get_all_doctors()
    if not doctors:
        doctors = [
            {"id": "1", "name": "Dr. Ahmed Khan",    "specialty": "cardiology", "city": "Lahore",    "rating": 4.9, "is_available": True, "total_cases": 312},
            {"id": "2", "name": "Dr. Sara Malik",    "specialty": "cardiology", "city": "Karachi",   "rating": 4.8, "is_available": True, "total_cases": 198},
            {"id": "3", "name": "Dr. Bilal Hussain", "specialty": "trauma",     "city": "Lahore",    "rating": 4.7, "is_available": True, "total_cases": 245},
            {"id": "4", "name": "Dr. Fatima Ali",    "specialty": "trauma",     "city": "Islamabad", "rating": 4.9, "is_available": True, "total_cases": 176},
            {"id": "5", "name": "Dr. Usman Sheikh",  "specialty": "neurology",  "city": "Lahore",    "rating": 4.6, "is_available": True, "total_cases": 134},
        ]
    return {"doctors": doctors}


@router.get("/{doctor_id}")
async def get_doctor(doctor_id: str):
    from backend.services.supabase_client import get_client
    try:
        client = get_client()
        result = client.table("doctors").select("*").eq("id", doctor_id).limit(1).execute()
        if result.data:
            return result.data[0]
        raise HTTPException(status_code=404, detail="Doctor not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_doctor error: {e}")
        raise HTTPException(status_code=500, detail="Database error")


@router.patch("/{doctor_id}/availability")
async def toggle_availability(doctor_id: str, body: AvailabilityUpdate):
    """Toggle doctor on/off duty — called from the dashboard."""
    from backend.services.supabase_client import set_doctor_availability
    await set_doctor_availability(doctor_id, body.available)
    return {"updated": True, "doctor_id": doctor_id, "available": body.available}
