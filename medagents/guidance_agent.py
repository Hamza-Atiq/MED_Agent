import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

DISCLAIMER = (
    "\n\n⚠️ This guidance is for informational purposes only and does not "
    "constitute medical advice. Please consult a qualified healthcare professional. "
    "In life-threatening emergencies, call emergency services immediately."
)

SYSTEM_PROMPT = """You are a calm, reassuring medical guidance assistant.
Give clear, simple first-aid instructions for the described emergency type.

RULES:
- Use simple language — no medical jargon
- Number each step (1. 2. 3.)
- Maximum 5 steps
- Be calm and reassuring in tone
- Do NOT diagnose — only describe what to do right now
- End with a sentence that a doctor is being contacted
- Do NOT add a disclaimer — it will be added separately
"""

GUIDANCE_BY_TYPE = {
    "cardiac": (
        "1. Help the person sit upright or in a comfortable position — do not lay them flat.\n"
        "2. Loosen any tight clothing around the chest and neck.\n"
        "3. Do NOT give food, water, or any medication unless prescribed.\n"
        "4. Keep the person calm — avoid sudden movements or exertion.\n"
        "5. Stay with them and keep them talking. A cardiac specialist is being contacted now."
    ),
    "trauma": (
        "1. Do NOT move the person if you suspect a spinal/neck injury.\n"
        "2. Apply gentle, firm pressure to any bleeding wounds using a clean cloth.\n"
        "3. Keep the person warm and still.\n"
        "4. Do NOT remove any embedded objects from wounds.\n"
        "5. Reassure them help is coming. An emergency doctor is being contacted now."
    ),
    "neuro": (
        "1. Help the person lie down safely, on their side if they feel nauseous.\n"
        "2. Remove any objects nearby to prevent injury if they lose balance.\n"
        "3. Do NOT give food, water, or any medication.\n"
        "4. Note the time symptoms started — this is important for the doctor.\n"
        "5. Keep them calm and still. A neurologist is being contacted now."
    ),
    "general": (
        "1. Help the person rest in a comfortable position.\n"
        "2. Keep them warm and calm.\n"
        "3. Give small sips of water if they are conscious and not vomiting.\n"
        "4. Note all symptoms and when they started.\n"
        "5. A doctor is being contacted and will advise you shortly."
    ),
}


async def get_guidance(emergency_type: str, message: str, client: AsyncOpenAI, model: str) -> str:
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Emergency type: {emergency_type}\nPatient message: {message}\nProvide first-aid guidance steps."},
            ],
            temperature=0.3,
            max_tokens=300,
        )
        guidance = response.choices[0].message.content.strip()
        return guidance + DISCLAIMER
    except Exception as e:
        logger.error(f"guidance_agent LLM error: {e}, using static guidance")
        static = GUIDANCE_BY_TYPE.get(emergency_type, GUIDANCE_BY_TYPE["general"])
        return static + DISCLAIMER
