"""
medagents/config.py
Groq client setup for OpenAI Agents SDK.
All agents share this client — Groq is the primary LLM (14,400 free req/day).
"""
import os
import logging
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, set_tracing_disabled
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Disable SDK tracing — we have no OpenAI API key for it
set_tracing_disabled(True)

GROQ_BASE = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.3-70b-versatile"

OPENROUTER_BASE = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "meta-llama/llama-3.3-70b-instruct:free"


def get_groq_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url=GROQ_BASE,
    )


def get_openrouter_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url=OPENROUTER_BASE,
        default_headers={"HTTP-Referer": "https://medagent.app", "X-Title": "MedAgent"},
    )


def make_model(client: AsyncOpenAI = None, model_name: str = None) -> OpenAIChatCompletionsModel:
    """Return an SDK-compatible model using Groq by default."""
    if client is None:
        client = get_groq_client()
    if model_name is None:
        model_name = GROQ_MODEL
    return OpenAIChatCompletionsModel(model=model_name, openai_client=client)


# Default model — used by all agents unless overridden
DEFAULT_MODEL = make_model()
