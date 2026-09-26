# Author: Vishal Bulbule
# Date: 2026-09-22

"""How NOT to write a tool: the same order lookup as `../agent`, done badly.

`do_thing` reads the same kind of order book as `lookup_order_status` in
`../agent/agent.py`, but breaks all five rules:
    1. Vague name (`do_thing`): nothing says it is about orders.
    2. No type hints: the declaration has no parameter types, so the model
       guesses what to pass.
    3. No docstring: the declaration has no description, so the model has no
       reason to call it and no hint about when.
    4. No `status` field: it returns the raw record or None.
    5. No error message: a miss is a bare None the model cannot act on.

The agent instruction is deliberately neutral about which tool to use, so
the model has only the tool declaration to go on. Send the same prompts to
this agent and to `agent` in `adk web` and compare.

`stop_runaway_calls` is not part of the lesson. With no declaration to go on,
the model can keep guessing arguments for dozens of calls; the cap ends the
turn after a few tries so the demo cannot run up a bill.
"""

from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types

MAX_TOOL_CALLS = 5

_ORDERS = {
    "A-1001": {"item": "Mechanical keyboard", "status": "shipped", "eta": "2026-05-25"},
    "A-1002": {"item": "USB-C hub", "status": "processing", "eta": "2026-05-28"},
    "A-1003": {"item": "Standing desk", "status": "delivered", "eta": "2026-05-19"},
}


# Intentionally bad: see the module docstring. Do not copy this pattern.
def do_thing(x, y=None):
    if y:
        return _ORDERS.get(f"{x}-{y}")
    return _ORDERS.get(str(x))


def stop_runaway_calls(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Ends the turn once the model has called tools MAX_TOOL_CALLS times.

    Args:
        callback_context: Gives access to this invocation's state.
        llm_request: The request about to be sent to the model.

    Returns:
        A final reply that ends the turn when the cap is reached, else None.
    """
    calls = sum(
        1
        for content in llm_request.contents
        for part in content.parts or []
        if part.function_response
    )
    if calls < MAX_TOOL_CALLS:
        return None
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(text=(
                f"Stopped after {calls} tool calls without an answer. The tool "
                "declaration gives the model nothing to go on; compare with `agent`."
            ))],
        )
    )


root_agent = LlmAgent(
    name="bad_tool_agent",
    model="gemini-3.5-flash",
    description="Same order-status job as `agent`, with a badly written tool.",
    instruction=(
        "You help customers check the status of their orders. "
        "Use your tools when they help."
    ),
    tools=[do_thing],
    before_model_callback=stop_runaway_calls,
)
