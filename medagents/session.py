"""
medagents/session.py
WhatsApp conversation state machine.

States:
  new        → first contact, ask for name + city
  ask_intake → waiting for name/city reply, then run original message
  active     → full conversation with memory
"""
import logging
import re

logger = logging.getLogger(__name__)

INTAKE_QUESTION = (
    "Assalam o Alaikum! I'm MedAgent — AI Emergency Healthcare 🏥\n\n"
    "To connect you with the nearest doctor, please tell me:\n"
    "1. Your *name*\n"
    "2. Your *city* (e.g. Lahore, Karachi, Islamabad, Rawalpindi)\n\n"
    "Example: _My name is Ahmed and I am in Rawalpindi_\n\n"
    "⚠️ For life-threatening emergencies call 1122 (Punjab Rescue) or 115 (Edhi) immediately."
)

KNOWN_CITIES = [
    "lahore", "karachi", "islamabad", "rawalpindi", "peshawar",
    "multan", "faisalabad", "quetta", "hyderabad", "sialkot",
    "gujranwala", "bahawalpur", "sargodha", "sukkur", "larkana",
]


async def handle_whatsapp_message(phone: str, text: str) -> str:
    """
    State machine entry point — returns reply string to send to patient.
    """
    from backend.services.supabase_client import get_session, save_session

    session = await get_session(phone) or {}
    state = session.get("state", "new")
    raw_history = session.get("history", [])
    # Supabase returns JSONB as Python list; guard against legacy string values
    if isinstance(raw_history, str):
        import json
        try:
            raw_history = json.loads(raw_history)
        except Exception:
            raw_history = []
    history: list = raw_history or []

    if state == "new":
        await save_session(phone, {
            "state": "ask_intake",
            "first_msg": text[:500],
            "name": "Patient",
            "city": "",
            "history": [],
        })
        return INTAKE_QUESTION

    if state == "ask_intake":
        name, city = _extract_name_city(text)
        first_msg = session.get("first_msg") or text
        await save_session(phone, {
            "state": "active",
            "name": name,
            "city": city,
        })
        reply = await _run_and_save(first_msg, phone, name, city, [], session_phone=phone)
        return reply

    # active
    name = session.get("name", "Patient")
    city = session.get("city", "Lahore")
    reply = await _run_and_save(text, phone, name, city, history, session_phone=phone)
    return reply


async def _run_and_save(
    message: str,
    patient_phone: str,
    name: str,
    city: str,
    history: list,
    session_phone: str,
) -> str:
    from medagents.runner import run_agent
    from backend.services.supabase_client import save_session

    result = await run_agent(message, patient_phone, patient_name=name, city=city, history=history)
    reply = result["response"]

    new_history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": reply},
    ]
    await save_session(session_phone, {"history": new_history[-12:]})
    return reply


def _extract_name_city(text: str) -> tuple[str, str]:
    """
    Pull name and city out of a free-text intake reply.
    Falls back to ('Patient', 'Lahore') if neither found.
    """
    text_lower = text.lower()
    city = "Lahore"
    name = "Patient"

    for c in KNOWN_CITIES:
        if c in text_lower:
            city = c.capitalize()
            break

    name_patterns = [
        r"my name is ([a-z]+)",
        r"\bname[: ]+([a-z]+)",
        r"\bi(?:'?m| am) ([a-z]+)",
        r"mera naam ([a-z]+)",
        r"([a-z]+) (?:from|in) [a-z]+",  # "Ahmed from Rawalpindi"
    ]
    for pat in name_patterns:
        m = re.search(pat, text_lower)
        if m:
            candidate = m.group(1).capitalize()
            if len(candidate) >= 2 and candidate.lower() not in ("from", "in", "and", "the"):
                name = candidate
                break

    return name, city
