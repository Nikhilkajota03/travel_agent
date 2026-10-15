from langchain_core.messages import AIMessage
from src.state import TravelState
from src.core.llm import llm_text, json_from_llm
from src.agents.prompts import (
    GUARDRAIL_SYSTEM_PROMPT,
    GUARDRAIL_USER_PROMPT_TEMPLATE,
    GUARDRAIL_DEFAULT_BLOCK_MESSAGE,
)


def evaluate_input_guardrail(query: str) -> tuple[bool, str]:
    """
    Evaluate user input against safety, relevance, and policy requirements.
    Fails open gracefully if LLM evaluation encounters parsing errors.
    """
    guardrail_prompt = GUARDRAIL_USER_PROMPT_TEMPLATE.format(query=query)

    try:
        guardrail_raw = llm_text(
            GUARDRAIL_SYSTEM_PROMPT,
            guardrail_prompt,
        )
        guardrail_result = json_from_llm(guardrail_raw)
        allowed = bool(guardrail_result.get("allowed", True))
        reason = str(guardrail_result.get("reason", "")).strip()
        return allowed, reason
    except Exception as exc:
        print(f"Guardrail fallback activated: {exc}")
        return True, "Guardrail validation fallback allowed the request."


def guardrail_blocked_agent(state: TravelState) -> dict:
    """
    Handles queries blocked by the input guardrail.
    Terminates the workflow early with an informative policy explanation.
    """
    reason = (
        state.get("final_response")
        or state.get("guardrail_reason")
        or GUARDRAIL_DEFAULT_BLOCK_MESSAGE
    )
    return {
        "final_response": reason,
        "messages": [AIMessage(content=reason)],
    }
