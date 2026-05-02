import logging
from agents.tools.find_doctor import find_doctor
from agents.tools.send_alert import send_alert

logger = logging.getLogger(__name__)


async def dispatch(emergency_type: str, urgency: str, patient_message: str, city: str = "Lahore") -> dict:
    doctor = await find_doctor(emergency_type, city)
    if not doctor:
        logger.warning("No doctor found, using hardcoded fallback")
        doctor = {
            "doctor_id": "fallback",
            "name": "Dr. Ahmed Khan",
            "phone": "+923001111111",
            "whatsapp_id": "923001111111",
            "specialty": "general",
            "city": "Lahore",
        }

    alert_result = await send_alert(doctor, patient_message, emergency_type, urgency)
    logger.info(f"Dispatch complete: {doctor['name']} | alert={alert_result['status']}")

    return {
        "doctor": doctor,
        "alert_status": alert_result["status"],
        "doctor_assigned": f"{doctor['name']} ({doctor.get('specialty', '').title()}, {doctor.get('city', '')})",
    }
