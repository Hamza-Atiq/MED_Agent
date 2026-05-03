import logging
import os
import httpx

logger = logging.getLogger(__name__)


async def send_discord_alert(
    doctor: dict,
    patient_message: str,
    emergency_type: str,
    urgency: str,
    patient_name: str = "Patient",
    patient_phone: str = "",
) -> bool:
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
    if not webhook_url:
        logger.info("[Discord] DISCORD_WEBHOOK_URL not set — skipping")
        return False

    color = {"critical": 0xFF0000, "moderate": 0xFF8C00, "low": 0x00C851}.get(urgency, 0x808080)
    type_emoji = {
        "cardiac": "🫀", "trauma": "🩹", "neuro": "🧠",
        "respiratory": "🫁", "gynae": "👩‍⚕️", "pediatric": "👶", "general": "🏥",
    }.get(emergency_type, "🏥")

    payload = {
        "content": "@here 🚨 **New Emergency Case**",
        "embeds": [{
            "title": f"{type_emoji} {emergency_type.upper()} — {urgency.upper()} PRIORITY",
            "description": f"**Patient:** {patient_name}\n**Message:** {patient_message[:400]}",
            "color": color,
            "fields": [
                {"name": "Assigned Doctor", "value": doctor.get("name", "Unknown"), "inline": True},
                {"name": "City", "value": doctor.get("city", "Unknown"), "inline": True},
                {"name": "Specialty", "value": doctor.get("specialty", "Unknown"), "inline": True},
                {"name": "Contact", "value": patient_phone or "N/A", "inline": True},
            ],
            "footer": {"text": "MedAgent — AI Emergency Response | 1122 Rescue | 115 Edhi"},
        }],
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(webhook_url, json=payload)
        resp.raise_for_status()
        logger.info(f"Discord alert sent for Dr. {doctor.get('name')}")
        return True
    except Exception as e:
        logger.error(f"Discord alert failed: {e}")
        return False
