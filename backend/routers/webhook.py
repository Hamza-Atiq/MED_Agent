import logging
import os
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
from backend.services.whatsapp import send_message, parse_whatsapp_webhook

logger = logging.getLogger(__name__)
router = APIRouter()

VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "medagent_secret_2026")

# Track processed message IDs to prevent duplicates on Meta retries
_processed_ids: set[str] = set()


@router.get("/webhook")
async def verify_webhook(request: Request):
    """Meta WhatsApp webhook verification handshake."""
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified")
        return PlainTextResponse(content=challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def receive_message(request: Request, background_tasks: BackgroundTasks):
    """
    Accepts:
    1. Real Meta WhatsApp payload  → processes in background, returns 200 immediately
    2. Simple JSON {message, phone, name, city} for web UI / testing
    """
    data = await request.json()

    # ── Meta WhatsApp format ──────────────────────────────────────────────────
    text, phone = parse_whatsapp_webhook(data)
    if text and phone:
        # Extract message ID for deduplication
        msg_id = _extract_message_id(data)
        if msg_id and msg_id in _processed_ids:
            logger.info(f"Duplicate webhook ignored: {msg_id}")
            return PlainTextResponse("ok")
        if msg_id:
            _processed_ids.add(msg_id)
            if len(_processed_ids) > 500:   # prevent unbounded growth
                _processed_ids.clear()

        # Return 200 immediately so Meta doesn't retry
        background_tasks.add_task(_handle_whatsapp, text, phone)
        return PlainTextResponse("ok")

    # ── Web UI / frontend format ──────────────────────────────────────────────
    from medagents.runner import run_agent

    message = data.get("message", "")
    phone   = data.get("phone", "demo-user")
    name    = data.get("name", "Patient")
    city    = data.get("city", "Lahore")

    if not message:
        raise HTTPException(status_code=400, detail="message field is required")

    result = await run_agent(message, phone, patient_name=name, city=city)
    logger.info(f"Chat processed: type={result['emergency_type']} urgency={result['urgency']}")
    return result


async def _handle_whatsapp(text: str, phone: str) -> None:
    """Background task: run session state machine and reply to patient on WhatsApp."""
    from medagents.session import handle_whatsapp_message
    try:
        reply = await handle_whatsapp_message(phone, text)
        await send_message(phone, reply)
        logger.info(f"WhatsApp reply sent to {phone}")
    except Exception as e:
        logger.error(f"WhatsApp background handler failed: {e}")


def _extract_message_id(data: dict) -> str | None:
    """Pull the wamid from a Meta webhook payload."""
    try:
        messages = data["entry"][0]["changes"][0]["value"]["messages"]
        return messages[0].get("id")
    except (KeyError, IndexError, TypeError):
        return None
