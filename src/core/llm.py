import json
from typing import Any
from functools import lru_cache
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import settings

_llm_instance: ChatGroq | None = None


def get_llm(model: str | None = None) -> ChatGroq:
    """
    Get or initialize the Groq Chat model client.
    Lazy initialization avoids import-time failure if the key is loaded dynamically.
    """
    global _llm_instance
    if _llm_instance is None or (model and _llm_instance.model_name != model):
        api_key = settings.require("GROQ_API_KEY", settings.GROQ_API_KEY)
        _llm_instance = ChatGroq(
            model=model or settings.DEFAULT_LLM_MODEL,
            api_key=api_key,
        )
    return _llm_instance


def llm_text(system_prompt: str, user_prompt: str, model: str | None = None) -> str:
    """Helper to invoke the LLM with a system and human message pair."""
    client = get_llm(model)
    response = client.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    )
    return str(response.content)


def json_from_llm(text: str) -> dict[str, Any]:
    """Extract and parse the first valid JSON object found in text."""
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise ValueError("The model did not return a valid JSON object.")

    return json.loads(text[start : end + 1])
