import logging
import os
import httpx

logger = logging.getLogger(__name__)


def _is_simulated() -> bool:
    token = os.getenv("META_WA_TOKEN", "")
    return not token or token in ("simulated", "") or token.startswith("EAA...") or len(token) < 20


async def send_alert(
    doctor: dict,
    patient_message: str,
    emergency_type: str,
    urgency: str,
    patient_name: str = "Patient",
    patient_phone: str = "",
) -> dict:
    alert_text = (
        f"🚨 *MedAgent Emergency Alert*\n\n"
        f"*Type:* {emergency_type.upper()} | *Priority:* {urgency.upper()}\n"
        f"*Patient:* {patient_name}\n"
        f"*Message:* \"{patient_message[:250]}\"\n\n"
        f"Please contact the patient immediately.\n"
        f"⚠️ Automated alert — MedAgent AI Emergency System"
    )

    wa_sent = False
    if _is_simulated():
        logger.info(f"[SIMULATED WhatsApp] → {doctor['name']}: {alert_text[:80]}...")
        wa_sent = True
    else:
        token = os.getenv("META_WA_TOKEN", "")
        pid = os.getenv("META_PHONE_NUMBER_ID", "")
        try:
            url = f"https://graph.facebook.com/v18.0/{pid}/messages"
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            payload = {
                "messaging_product": "whatsapp",
                "to": doctor.get("whatsapp_id", ""),
                "type": "text",
                "text": {"body": alert_text},
            }
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            logger.info(f"WhatsApp alert sent to {doctor['name']}")
            wa_sent = True
        except Exception as e:
            logger.error(f"WhatsApp send_alert failed: {e} — falling back to Discord")

    # Discord alert (runs alongside WhatsApp, not just as fallback)
    discord_sent = False
    try:
        from backend.services.discord import send_discord_alert
        discord_sent = await send_discord_alert(
            doctor=doctor,
            patient_message=patient_message,
            emergency_type=emergency_type,
            urgency=urgency,
            patient_name=patient_name,
            patient_phone=patient_phone,
        )
    except Exception as e:
        logger.warning(f"Discord alert error: {e}")

    return {
        "status": "sent" if (wa_sent or discord_sent) else "failed",
        "whatsapp": wa_sent,
        "discord": discord_sent,
        "doctor": doctor["name"],
    }
