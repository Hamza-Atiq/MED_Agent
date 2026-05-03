import logging
import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import PlainTextResponse
from backend.services.whatsapp import send_message, parse_whatsapp_webhook

logger = logging.getLogger(__name__)
router = APIRouter()

VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "medagent_secret_2026")


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
async def receive_message(request: Request):
    """
    Accepts:
    1. Real Meta WhatsApp payload
    2. Simple JSON {message, phone, name, city} for testing
    """
    from medagents.runner import run_agent

    data = await request.json()

    # Try Meta WhatsApp format first
    text, phone = parse_whatsapp_webhook(data)
    if text and phone:
        result = await run_agent(text, phone)
        await send_message(phone, result["greeting"] + "\n\n" + result["response"])
        logger.info(f"WhatsApp flow complete for {phone}")
        return {"status": "ok"}

    # Simple test/frontend format
    message = data.get("message", "")
    phone = data.get("phone", "demo-user")
    name = data.get("name", "Patient")
    city = data.get("city", "Lahore")

    if not message:
        raise HTTPException(status_code=400, detail="message field is required")

    result = await run_agent(message, phone, patient_name=name, city=city)
    logger.info(f"Webhook processed: type={result['emergency_type']} urgency={result['urgency']}")
    return result
