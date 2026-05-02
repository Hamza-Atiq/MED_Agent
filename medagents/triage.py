"""
medagents/triage.py
XAI Triage — classifies emergency AND explains WHY.
This is our unique differentiator. Not part of the SDK agent loop;
runs as a pre-step so the XAI fields can be returned in the API response.
"""
import json
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a medical triage AI. Analyze patient symptom descriptions and classify the emergency.

RULES:
- NEVER say "you have [disease]" — say "symptoms suggest possible [condition]"
- Always be calm and factual
- When uncertain, escalate urgency

Return ONLY valid JSON in this exact format:
{
  "emergency_type": "cardiac" | "trauma" | "neuro" | "respiratory" | "gynae" | "pediatric" | "general",
  "urgency": "critical" | "moderate" | "low",
  "reasoning": "Plain English explanation of why you classified it this way (2-3 sentences max)",
  "key_symptoms": ["symptom1", "symptom2"],
  "confidence": "high" | "medium" | "low",
  "triage_flags": ["flag1", "flag2"]
}

emergency_type definitions:
- cardiac: chest pain, heart palpitations, shortness of breath, left arm/jaw pain, sweating
- trauma: accidents, falls, injuries, burns, bleeding, fractures, head injury
- neuro: severe headache, confusion, numbness, stroke symptoms (face droop, arm weakness), seizures
- respiratory: fever, cough, difficulty breathing, infection, high temperature
- gynae: women's health, pregnancy concerns, heavy bleeding, pelvic pain
- pediatric: child under 16 is the patient — any symptoms, infant concerns, child fever
- general: nausea, vomiting, general pain, unknown symptoms, anything else

urgency definitions:
- critical: life-threatening, needs doctor within minutes
- moderate: needs attention within 1-2 hours
- low: can wait for regular appointment

triage_flags examples: "chest_pain_keyword", "multiple_symptoms", "urgency_escalated",
"pediatric_mention", "elderly_mention", "pregnancy_mention", "unconscious_mention"
"""


async def run_triage(message: str, client: AsyncOpenAI, model: str) -> dict:
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
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw.strip())
        required = {"emergency_type", "urgency", "reasoning", "key_symptoms", "confidence", "triage_flags"}
        if not required.issubset(result.keys()):
            raise ValueError(f"Missing keys: {required - result.keys()}")
        logger.info(f"Triage: {result['emergency_type']}/{result['urgency']} confidence={result['confidence']}")
        return result
    except Exception as e:
        logger.error(f"triage LLM error: {e}, using keyword fallback")
        return _keyword_fallback(message)


def _keyword_fallback(message: str) -> dict:
    msg = message.lower()
    if any(w in msg for w in ["chest", "heart", "cardiac", "palpitation", "left arm"]):
        return {"emergency_type": "cardiac", "urgency": "critical",
                "reasoning": "Cardiac keywords detected — chest, heart, or arm pain indicating possible cardiac emergency.",
                "key_symptoms": ["chest pain"], "confidence": "medium", "triage_flags": ["cardiac_keyword", "fallback_used"]}
    if any(w in msg for w in ["child", "baby", "infant", "son", "daughter", "year old", "months old"]):
        return {"emergency_type": "pediatric", "urgency": "moderate",
                "reasoning": "Pediatric mention detected — child or infant involved.",
                "key_symptoms": ["pediatric patient"], "confidence": "medium", "triage_flags": ["pediatric_mention", "fallback_used"]}
    if any(w in msg for w in ["pregnant", "pregnancy", "gynae", "period", "vaginal", "pelvic"]):
        return {"emergency_type": "gynae", "urgency": "moderate",
                "reasoning": "Women's health keywords detected.",
                "key_symptoms": ["gynaecological symptom"], "confidence": "medium", "triage_flags": ["gynae_keyword", "fallback_used"]}
    if any(w in msg for w in ["fever", "temperature", "cough", "infection", "breathing", "breath"]):
        return {"emergency_type": "respiratory", "urgency": "moderate",
                "reasoning": "Respiratory/fever keywords detected.",
                "key_symptoms": ["fever or breathing issue"], "confidence": "medium", "triage_flags": ["respiratory_keyword", "fallback_used"]}
    if any(w in msg for w in ["accident", "fall", "injury", "bleed", "burn", "fracture", "cut"]):
        return {"emergency_type": "trauma", "urgency": "moderate",
                "reasoning": "Trauma keywords detected.",
                "key_symptoms": ["physical injury"], "confidence": "medium", "triage_flags": ["trauma_keyword", "fallback_used"]}
    if any(w in msg for w in ["headache", "confused", "numb", "seizure", "stroke", "unconscious"]):
        return {"emergency_type": "neuro", "urgency": "moderate",
                "reasoning": "Neurological keywords detected.",
                "key_symptoms": ["neurological symptom"], "confidence": "low", "triage_flags": ["neuro_keyword", "fallback_used"]}
    return {"emergency_type": "general", "urgency": "low",
            "reasoning": "No specific emergency keywords detected. Classified as general.",
            "key_symptoms": [], "confidence": "low", "triage_flags": ["no_keywords", "fallback_used"]}
