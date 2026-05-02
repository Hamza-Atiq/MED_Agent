from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WebhookRequest(BaseModel):
    message: str
    phone: str = "demo-user"
    name: Optional[str] = None
    city: Optional[str] = "Lahore"


class AgentResponse(BaseModel):
    response: str
    emergency_type: str
    urgency: str
    doctor_assigned: str
    disclaimer: str
    reasoning: str
    key_symptoms: list[str]
    confidence: str
    triage_flags: list[str]


class AppointmentRequest(BaseModel):
    patient_phone: str
    doctor_id: str
    problem_description: str
    emergency_type: Optional[str] = "general"
    urgency_level: Optional[str] = "low"
    is_home_visit: bool = True
    scheduled_at: Optional[datetime] = None
