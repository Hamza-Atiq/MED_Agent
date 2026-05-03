import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

_client: Client | None = None
_client_key: str | None = None


def get_client() -> Client:
    global _client, _client_key
    url = os.getenv("SUPABASE_URL")
    # Prefer service role key (bypasses RLS for backend operations)
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env")
    if _client is None or _client_key != key:
        _client = create_client(url, key)
        _client_key = key
    return _client


async def find_doctor(specialty: str, city: str = "Lahore") -> dict | None:
    try:
        client = get_client()
        result = (
            client.table("doctors")
            .select("*")
            .eq("specialty", specialty)
            .eq("city", city)
            .eq("is_available", True)
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]
        # Fallback: any city
        result = (
            client.table("doctors")
            .select("*")
            .eq("specialty", specialty)
            .eq("is_available", True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"find_doctor error: {e}")
        return None


async def get_or_create_patient(phone: str, name: str = None, city: str = "Lahore") -> dict:
    try:
        client = get_client()
        result = client.table("patients").select("*").eq("phone", phone).limit(1).execute()
        if result.data:
            return result.data[0]
        insert_data = {"phone": phone, "city": city}
        if name:
            insert_data["name"] = name
        result = client.table("patients").insert(insert_data).execute()
        return result.data[0]
    except Exception as e:
        logger.error(f"get_or_create_patient error: {e}")
        return {"id": None, "phone": phone}


async def save_activity_log(log_data: dict) -> str | None:
    try:
        client = get_client()
        result = client.table("activity_logs").insert(log_data).execute()
        return result.data[0]["id"] if result.data else None
    except Exception as e:
        logger.error(f"save_activity_log error: {e}")
        return None


async def get_all_doctors() -> list:
    try:
        client = get_client()
        result = client.table("doctors").select("*").order("rating", desc=True).execute()
        return result.data or []
    except Exception as e:
        logger.error(f"get_all_doctors error: {e}")
        return []


async def get_activity_logs(limit: int = 20) -> list:
    try:
        client = get_client()
        result = (
            client.table("activity_logs")
            .select("*, patients(name, phone, city), doctors(name, specialty, city)")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    except Exception as e:
        logger.error(f"get_activity_logs error: {e}")
        return []


async def create_appointment(data: dict) -> dict | None:
    try:
        client = get_client()
        result = client.table("appointments").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"create_appointment error: {e}")
        return None


async def increment_doctor_cases(doctor_id: str) -> None:
    try:
        client = get_client()
        doc = client.table("doctors").select("total_cases").eq("id", doctor_id).limit(1).execute()
        if doc.data:
            current = doc.data[0].get("total_cases", 0) or 0
            client.table("doctors").update({"total_cases": current + 1}).eq("id", doctor_id).execute()
    except Exception as e:
        logger.error(f"increment_doctor_cases error: {e}")


async def set_doctor_availability(doctor_id: str, available: bool) -> None:
    try:
        client = get_client()
        client.table("doctors").update({"is_available": available}).eq("id", doctor_id).execute()
    except Exception as e:
        logger.error(f"set_doctor_availability error: {e}")


async def update_appointment_status(appointment_id: str, status: str) -> None:
    try:
        client = get_client()
        client.table("appointments").update({"status": status}).eq("id", appointment_id).execute()
    except Exception as e:
        logger.error(f"update_appointment_status error: {e}")


async def get_session(phone: str) -> dict | None:
    try:
        client = get_client()
        result = client.table("sessions").select("*").eq("phone", phone).limit(1).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"get_session error: {e}")
        return None


async def save_session(phone: str, updates: dict) -> None:
    from datetime import datetime, timezone
    try:
        client = get_client()
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        existing = client.table("sessions").select("phone").eq("phone", phone).limit(1).execute()
        if existing.data:
            client.table("sessions").update(updates).eq("phone", phone).execute()
        else:
            client.table("sessions").insert({"phone": phone, **updates}).execute()
    except Exception as e:
        logger.error(f"save_session error: {e}")
