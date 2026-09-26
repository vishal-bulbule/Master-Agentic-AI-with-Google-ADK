# Author: Vishal Bulbule
# Date: 2026-09-22

"""Lab: smart router that sends math to Pro and everything else to Flash.

One agent, one `compute` tool, two models:
    - Flash (gemini-3.5-flash): cheap and fast
    - Pro (gemini-2.5-pro by default): more reasoning capacity

`route_model` (a `before_model_callback`) calls `pick_model` on the user
message and sets `llm_request.model` before every model request, so all
calls in one turn, tool round trips included, go to the same model.
`record_usage` (an `after_model_callback`) adds each call's token counts to
the `token_usage` state key, per model, so the dev UI State tab shows the
running cost comparison.

Set `ROUTER_PRO_MODEL` to override the Pro model id, for example when your
project cannot use Pro models.
"""

import os
import re
from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types

from .tools import compute

FLASH = "gemini-3.5-flash"
PRO = os.environ.get("ROUTER_PRO_MODEL", "gemini-2.5-pro")

MATH_KEYWORDS = (
    "calculate", "compute", "evaluate", "solve", "math", "arithmetic",
    "sum", "product", "difference", "quotient", "result of",
)

# Digits next to an operator or a parenthesis, for example "12 * 3" or "(7".
# Operators are matched only next to digits: a bare "-" keyword would send
# "sci-fi" to Pro.
_DIGITS_AND_OPS = re.compile(r"\d+\s*[\+\-\*\/%\^]\s*\d+|\d+\s*\(|\(\s*\d+")


def _looks_mathy(query: str) -> bool:
    if _DIGITS_AND_OPS.search(query):
        return True
    return any(keyword in query.lower() for keyword in MATH_KEYWORDS)


def pick_model(query: str) -> str:
    """Routes math or long queries to Pro and everything else to Flash.

    Args:
        query: The user's question.

    Returns:
        The model id to use for this query.
    """
    if len(query) >= 250:
        return PRO
    if _looks_mathy(query):
        return PRO
    return FLASH


def _user_text(callback_context: CallbackContext) -> str:
    content = callback_context.user_content
    if not content or not content.parts:
        return ""
    return "".join(p.text or "" for p in content.parts)


def route_model(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Sends this model request to the model `pick_model` chooses.

    Args:
        callback_context: Context of the current invocation.
        llm_request: The request about to be sent. Its `model` is replaced.

    Returns:
        None, so the request goes ahead with the new model.
    """
    model = pick_model(_user_text(callback_context))
    llm_request.model = model
    callback_context.state["routed_model"] = model
    return None


def record_usage(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Adds this call's token counts to `token_usage[model]` in state.

    Args:
        callback_context: Context of the current invocation.
        llm_response: The response just received from the model.

    Returns:
        None, so the response is used unchanged.
    """
    usage = llm_response.usage_metadata
    # With streaming on, partial chunks also reach this callback; count only
    # the final, complete response of each call.
    if llm_response.partial or usage is None:
        return None
    model = callback_context.state.get("routed_model", FLASH)
    # Copy and reassign: state records a change only on assignment, not on
    # in-place mutation of a nested dict.
    totals = dict(callback_context.state.get("token_usage", {}))
    row = dict(totals.get(model, {"model_calls": 0, "prompt_tokens": 0, "output_tokens": 0}))
    row["model_calls"] += 1
    row["prompt_tokens"] += usage.prompt_token_count or 0
    row["output_tokens"] += (usage.candidates_token_count or 0) + (usage.thoughts_token_count or 0)
    totals[model] = row
    callback_context.state["token_usage"] = totals
    return None


root_agent = LlmAgent(
    model=FLASH,
    name="smart_router_agent",
    description="Answers any question; routes math to Pro and uses `compute` for arithmetic.",
    instruction=(
        "## Who you are\n"
        "You are a careful assistant.\n\n"
        "## Task\n"
        "Answer the user's question concisely. If the question involves "
        "any arithmetic, call the `compute` tool to get the exact value, "
        "then state the answer in plain English.\n\n"
        "## Output\n"
        "Plain text, one short paragraph max."
    ),
    tools=[compute],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.0,
        # Thinking tokens count against this cap on Gemini 3.x.
        max_output_tokens=2048,
    ),
    before_model_callback=route_model,
    after_model_callback=record_usage,
)
