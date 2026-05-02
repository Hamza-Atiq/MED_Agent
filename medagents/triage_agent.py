import json
import logging
from openai import AsyncOpenAI
import os

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a medical triage AI. Analyze patient symptom descriptions and classify the emergency.

RULES:
- NEVER say "you have [disease]" — say "symptoms suggest possible [condition]"
- Always be calm and factual
- When uncertain, escalate urgency

Return ONLY valid JSON in this exact format:
{
  "emergency_type": "cardiac" | "trauma" | "neuro" | "general",
  "urgency": "critical" | "moderate" | "low",
  "reasoning": "Plain English explanation of why you classified it this way (2-3 sentences)",
  "key_symptoms": ["symptom1", "symptom2"],
  "confidence": "high" | "medium" | "low",
  "triage_flags": ["flag1", "flag2"]
}

emergency_type definitions:
- cardiac: chest pain, heart palpitations, shortness of breath, left arm pain
- trauma: accidents, falls, injuries, burns, bleeding, fractures
- neuro: headache (severe), confusion, numbness, stroke symptoms, seizures
- general: fever, nausea, vomiting, general pain, unknown symptoms

urgency definitions:
- critical: life-threatening, needs doctor within minutes
- moderate: needs attention within hours
- low: can wait for regular appointment

triage_flags examples: "chest_pain_keyword", "multiple_symptoms", "urgency_escalated", "pediatric_mention", "elderly_mention"
"""


async def triage(message: str, client: AsyncOpenAI, model: str) -> dict:
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Patient message: {message}"},
            ],
            temperature=0.1,
            max_tokens=400,
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)
        required = {"emergency_type", "urgency", "reasoning", "key_symptoms", "confidence", "triage_flags"}
        if not required.issubset(result.keys()):
            raise ValueError(f"Missing keys: {required - result.keys()}")
        return result
    except Exception as e:
        logger.error(f"triage_agent error: {e}")
        return _keyword_fallback(message)


def _keyword_fallback(message: str) -> dict:
    msg = message.lower()
    if any(w in msg for w in ["chest", "heart", "cardiac", "breathing", "breath"]):
        return {
            "emergency_type": "cardiac",
            "urgency": "critical",
            "reasoning": "Keywords 'chest' or 'breathing' detected, indicating possible cardiac emergency. Classified as critical due to life-threatening potential.",
            "key_symptoms": ["chest pain", "breathing difficulty"],
            "confidence": "medium",
            "triage_flags": ["cardiac_keyword", "fallback_used"],
        }
    elif any(w in msg for w in ["accident", "fall", "injury", "bleed", "burn", "fracture"]):
        return {
            "emergency_type": "trauma",
            "urgency": "moderate",
            "reasoning": "Trauma keywords detected. Classified as moderate urgency pending more details.",
            "key_symptoms": ["physical injury"],
            "confidence": "medium",
            "triage_flags": ["trauma_keyword", "fallback_used"],
        }
    elif any(w in msg for w in ["headache", "head", "confused", "numb", "seizure", "stroke"]):
        return {
            "emergency_type": "neuro",
            "urgency": "moderate",
            "reasoning": "Neurological keywords detected. Classified as moderate urgency.",
            "key_symptoms": ["neurological symptom"],
            "confidence": "low",
            "triage_flags": ["neuro_keyword", "fallback_used"],
        }
    return {
        "emergency_type": "general",
        "urgency": "low",
        "reasoning": "No specific emergency keywords detected. Classified as general with low urgency.",
        "key_symptoms": [],
        "confidence": "low",
        "triage_flags": ["no_keywords", "fallback_used"],
    }
