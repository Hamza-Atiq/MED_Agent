import logging
import os
import httpx

logger = logging.getLogger(__name__)

def _is_simulated() -> bool:
    token = os.getenv("META_WA_TOKEN", "")
    return not token or token in ("simulated", "") or token.startswith("EAA...") or len(token) < 20


async def send_message(to_number: str, message: str) -> bool:
    """Returns True if sent (or simulated), False if real send failed."""
    token = os.getenv("META_WA_TOKEN", "")
    pid = os.getenv("META_PHONE_NUMBER_ID", "")

    if _is_simulated():
        logger.info(f"[SIMULATED WhatsApp → {to_number}]: {message[:80]}...")
        return True

    try:
        url = f"https://graph.facebook.com/v18.0/{pid}/messages"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": message},
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"WhatsApp send failed: {e}")
        return False


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
