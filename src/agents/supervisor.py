from langchain_core.messages import AIMessage
from src.state import TravelState, KNOWN_AGENTS, AGENT_ORDER, get_empty_constraints
from src.core.llm import llm_text, json_from_llm
from src.agents.prompts import (
    SUPERVISOR_SYSTEM_PROMPT,
    SUPERVISOR_USER_PROMPT_TEMPLATE,
    GUARDRAIL_DEFAULT_BLOCK_MESSAGE,
)
from src.agents.guardrail import evaluate_input_guardrail


def supervisor_agent(state: TravelState) -> dict:
    """
    Supervisor Agent that:
    1. Validates input via Guardrails.
    2. Decomposes the user prompt and selects specialist agents dynamically.
    3. Extracts structured trip constraints.
    """
    query = state["user_query"]
    llm_calls = state.get("llm_calls", 0)

    # 1. Input Guardrail Verification
    allowed, guardrail_reason = evaluate_input_guardrail(query)
    llm_calls += 1

    if not allowed:
        reason = guardrail_reason or GUARDRAIL_DEFAULT_BLOCK_MESSAGE
        return {
            "guardrail_allowed": False,
            "guardrail_reason": reason,
            "selected_agents": [],
            "trip_constraints": get_empty_constraints(),
            "supervisor_reasoning": reason,
            "final_response": reason,
            "messages": [AIMessage(content=f"Guardrail blocked request: {reason}")],
            "llm_calls": llm_calls,
        }

    # 2. Dynamic Agent Selection & Constraints Extraction
    supervisor_prompt = SUPERVISOR_USER_PROMPT_TEMPLATE.format(query=query)

    try:
        supervisor_raw = llm_text(
            SUPERVISOR_SYSTEM_PROMPT,
            supervisor_prompt,
        )
        parsed = json_from_llm(supervisor_raw)
        requested_agents = parsed.get("selected_agents", [])

        # Maintain canonical agent order for selected agents
        selected_agents = [
            name for name in AGENT_ORDER
            if name in requested_agents and name in KNOWN_AGENTS
        ]

        # The itinerary agent integrates whichever specialist results were selected
        if "itinerary_agent" not in selected_agents:
            selected_agents.append("itinerary_agent")

        constraints = get_empty_constraints()
        parsed_constraints = parsed.get("trip_constraints", {})
        if isinstance(parsed_constraints, dict):
            constraints.update(parsed_constraints)

        reasoning = str(parsed.get("reasoning", "")).strip()
        llm_calls += 1
    except Exception as exc:
        print(f"Supervisor fallback activated: {exc}")
        selected_agents = AGENT_ORDER.copy()
        constraints = get_empty_constraints()
        reasoning = (
            "Supervisor parsing failed, so the full travel workflow was selected as a safe fallback."
        )

    return {
        "guardrail_allowed": True,
        "guardrail_reason": guardrail_reason,
        "selected_agents": selected_agents,
        "trip_constraints": constraints,
        "supervisor_reasoning": reasoning,
        "messages": [AIMessage(content="Supervisor created the agent execution plan.")],
        "llm_calls": llm_calls,
    }
