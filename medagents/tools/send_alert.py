import logging
import os
import httpx

logger = logging.getLogger(__name__)

META_WA_TOKEN = os.getenv("META_WA_TOKEN", "")
META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID", "")
SIMULATED = not META_WA_TOKEN or META_WA_TOKEN in ("simulated", "") or META_WA_TOKEN.startswith("EAA...") or len(META_WA_TOKEN) < 20


async def send_alert(doctor: dict, patient_message: str, emergency_type: str, urgency: str) -> dict:
    alert_text = (
        f"🚨 MedAgent Alert\n\n"
        f"Emergency: {emergency_type.upper()} / {urgency.upper()}\n"
        f"Patient message: \"{patient_message}\"\n\n"
        f"Please contact the patient immediately.\n"
        f"⚠️ This is an automated alert from MedAgent."
    )

    if SIMULATED:
        logger.info(f"[SIMULATED WhatsApp] → {doctor['name']} ({doctor.get('whatsapp_id', 'unknown')}): {alert_text[:80]}...")
        return {"status": "simulated", "doctor": doctor["name"], "message_preview": alert_text[:100]}

    try:
        url = f"https://graph.facebook.com/v18.0/{META_PHONE_NUMBER_ID}/messages"
        headers = {"Authorization": f"Bearer {META_WA_TOKEN}", "Content-Type": "application/json"}
        payload = {
            "messaging_product": "whatsapp",
            "to": doctor["whatsapp_id"],
            "type": "text",
            "text": {"body": alert_text},
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        logger.info(f"WhatsApp alert sent to {doctor['name']}")
        return {"status": "sent", "doctor": doctor["name"]}
    except Exception as e:
        logger.error(f"send_alert error: {e}")
        return {"status": "failed", "error": str(e)}
