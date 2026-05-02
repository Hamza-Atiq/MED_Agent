import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from backend.services.supabase_client import find_doctor as _db_find_doctor

logger = logging.getLogger(__name__)

SPECIALTY_MAP = {
    "cardiac": "cardiology",
    "trauma": "trauma",
    "neuro": "neurology",
    "general": "general",
}

_FALLBACK_DOCTORS = {
    "cardiology": {"doctor_id": "fallback-1", "name": "Dr. Ahmed Khan", "phone": "+923001111111", "whatsapp_id": "923001111111", "specialty": "cardiology", "city": "Lahore"},
    "trauma":     {"doctor_id": "fallback-2", "name": "Dr. Bilal Hussain", "phone": "+923003333333", "whatsapp_id": "923003333333", "specialty": "trauma", "city": "Lahore"},
    "neurology":  {"doctor_id": "fallback-3", "name": "Dr. Usman Sheikh", "phone": "+923005555555", "whatsapp_id": "923005555555", "specialty": "neurology", "city": "Lahore"},
    "general":    {"doctor_id": "fallback-4", "name": "Dr. Zainab Noor", "phone": "+923008888888", "whatsapp_id": "923008888888", "specialty": "general", "city": "Lahore"},
}


async def find_doctor(emergency_type: str, city: str = "Lahore") -> dict:
    specialty = SPECIALTY_MAP.get(emergency_type.lower(), "general")
    doctor = await _db_find_doctor(specialty, city)
    if doctor:
        return {
            "doctor_id": str(doctor.get("id", "")),
            "name": doctor.get("name", "Unknown"),
            "phone": doctor.get("phone", ""),
            "whatsapp_id": doctor.get("whatsapp_id", ""),
            "specialty": doctor.get("specialty", specialty),
            "city": doctor.get("city", city),
            "rating": doctor.get("rating", 5.0),
        }
    logger.warning(f"No DB doctor found for {specialty}/{city}, using fallback")
    return _FALLBACK_DOCTORS.get(specialty, _FALLBACK_DOCTORS["general"])
