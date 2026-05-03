import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/doctor", tags=["doctor-portal"])

JWT_EXPIRY_HOURS = 24


def _jwt_secret() -> str:
    return os.getenv("JWT_SECRET", "medagent_jwt_secret_2026")


class LoginRequest(BaseModel):
    email: str
    password: str


class StatusUpdate(BaseModel):
    status: str  # pending | in_progress | resolved


def _verify_token(authorization: Optional[str]) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization[7:]
    try:
        return jwt.decode(token, _jwt_secret(), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired — please log in again")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/login")
async def doctor_login(req: LoginRequest):
    from backend.services.supabase_client import get_client
    try:
        client = get_client()
        result = client.table("doctors").select("*").eq("email", req.email).limit(1).execute()
        if not result.data:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        doctor = result.data[0]
        pw_hash = (doctor.get("password_hash") or "").encode()
        if not pw_hash or not bcrypt.checkpw(req.password.encode(), pw_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        payload = {
            "doctor_id": str(doctor["id"]),
            "email": doctor["email"],
            "name": doctor["name"],
            "city": doctor["city"],
            "specialty": doctor["specialty"],
            "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
        }
        token = jwt.encode(payload, _jwt_secret(), algorithm="HS256")
        return {
            "token": token,
            "doctor": {
                "id": str(doctor["id"]),
                "name": doctor["name"],
                "email": doctor["email"],
                "city": doctor["city"],
                "specialty": doctor["specialty"],
                "rating": doctor["rating"],
                "is_available": doctor["is_available"],
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"doctor_login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.get("/me")
async def get_doctor_profile(authorization: Optional[str] = Header(None)):
    claims = _verify_token(authorization)
    from backend.services.supabase_client import get_client
    try:
        client = get_client()
        result = client.table("doctors").select("*").eq("id", claims["doctor_id"]).limit(1).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Doctor not found")
        doc = result.data[0]
        doc.pop("password_hash", None)
        return doc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_doctor_profile error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch profile")


@router.get("/cases")
async def get_doctor_cases(authorization: Optional[str] = Header(None)):
    claims = _verify_token(authorization)
    from backend.services.supabase_client import get_client
    try:
        client = get_client()
        result = (
            client.table("activity_logs")
            .select("*, patients(name, phone, city)")
            .eq("doctor_id", claims["doctor_id"])
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )
        return {
            "cases": result.data or [],
            "doctor": {"name": claims["name"], "city": claims["city"], "specialty": claims["specialty"]},
        }
    except Exception as e:
        logger.error(f"get_doctor_cases error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch cases")


@router.patch("/cases/{log_id}/status")
async def update_case_status(
    log_id: str,
    body: StatusUpdate,
    authorization: Optional[str] = Header(None),
):
    claims = _verify_token(authorization)
    if body.status not in {"pending", "in_progress", "resolved"}:
        raise HTTPException(status_code=400, detail="Status must be: pending | in_progress | resolved")
    from backend.services.supabase_client import get_client
    try:
        client = get_client()
        client.table("activity_logs").update({"status": body.status}).eq("id", log_id).eq("doctor_id", claims["doctor_id"]).execute()
        return {"updated": True, "log_id": log_id, "status": body.status}
    except Exception as e:
        logger.error(f"update_case_status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update status")
