import logging
import os
import httpx

logger = logging.getLogger(__name__)

META_WA_TOKEN = os.getenv("META_WA_TOKEN", "")
META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID", "")
SIMULATED = not META_WA_TOKEN or META_WA_TOKEN in ("simulated", "") or META_WA_TOKEN.startswith("EAA...") or len(META_WA_TOKEN) < 20


async def send_message(to_number: str, message: str) -> dict:
    if SIMULATED:
        logger.info(f"[SIMULATED WhatsApp → {to_number}]: {message[:80]}...")
        return {"status": "simulated", "to": to_number}

    try:
        url = f"https://graph.facebook.com/v18.0/{META_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {META_WA_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": message},
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return {"status": "sent", "to": to_number}
    except Exception as e:
        logger.error(f"WhatsApp send failed: {e}")
        return {"status": "failed", "error": str(e)}


def parse_whatsapp_webhook(data: dict) -> tuple[str, str] | tuple[None, None]:
    """Extract (message_text, sender_phone) from Meta WhatsApp webhook payload."""
    try:
        entry = data["entry"][0]
        change = entry["changes"][0]["value"]
        msg = change["messages"][0]
        phone = msg["from"]
        text = msg["text"]["body"]
        return text, phone
    except (KeyError, IndexError):
        return None, None
