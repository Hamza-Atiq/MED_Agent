"""
medagents/main_agent.py
Main Orchestrator Agent — receives patient message, hands off to the right specialist.
Uses OpenAI Agents SDK with Groq as the LLM provider.
"""
from agents import Agent, handoff
from medagents.config import DEFAULT_MODEL
from medagents.specialists import (
    cardiac_agent,
    trauma_agent,
    neuro_agent,
    respiratory_agent,
    gynae_agent,
    pediatric_agent,
    general_agent,
)

ORCHESTRATOR_INSTRUCTIONS = """You are MedAgent — a calm, professional AI emergency healthcare coordinator
serving patients in Pakistan via WhatsApp and web chat.

## Your Role
You are the FIRST point of contact. Your job is to:
1. Give an immediate calm acknowledgment (1-2 sentences max — patient is scared)
2. Understand the problem quickly
3. Hand off to the correct specialist agent immediately

## Handoff Decision Rules
Based on what the patient describes, hand off to the right specialist:
- Chest pain, heart palpitations, left arm pain, sweating → CardiacSpecialist
- Accident, fall, injury, bleeding, burn, fracture → TraumaSpecialist
- Severe headache, confusion, numbness, stroke signs, seizure → NeuroSpecialist
- Fever, cough, breathing difficulty, infection, temperature → RespiratorySpecialist
- Women's health, pregnancy, pelvic pain, gynaecological → GynaeSpecialist
- Child or infant is the patient (any age under 16) → PediatricSpecialist
- Anything else, unclear, or general pain → GeneralPractitioner

## Critical Rules
- ALWAYS hand off — do not try to handle everything yourself
- NEVER diagnose — say "symptoms suggest" not "you have"
- Be calm and reassuring — the patient may be panicking
- Use simple English — avoid medical jargon
- If life-threatening: say "Call 1122 (Punjab Rescue) or 115 (Edhi) immediately" FIRST
- Respond in the same language the patient uses (Urdu or English)
"""

main_agent = Agent(
    name="MedAgentOrchestrator",
    model=DEFAULT_MODEL,
    instructions=ORCHESTRATOR_INSTRUCTIONS,
    handoffs=[
        handoff(cardiac_agent,     tool_description_override="Chest pain, heart palpitations, cardiac symptoms, left arm pain"),
        handoff(trauma_agent,      tool_description_override="Injuries, accidents, bleeding, fractures, burns, head injury"),
        handoff(neuro_agent,       tool_description_override="Headache, seizure, numbness, stroke signs, confusion, unconscious"),
        handoff(respiratory_agent, tool_description_override="Fever, cough, breathing difficulty, infection, high temperature"),
        handoff(gynae_agent,       tool_description_override="Women's health, pregnancy, gynaecological concerns, pelvic pain"),
        handoff(pediatric_agent,   tool_description_override="Child or infant is the patient, paediatric concerns"),
        handoff(general_agent,     tool_description_override="General health issues, unclear symptoms, anything else"),
    ],
)
