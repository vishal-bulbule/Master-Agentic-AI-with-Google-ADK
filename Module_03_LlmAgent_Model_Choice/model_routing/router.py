# Author: Vishal Bulbule
# Date: 2026-09-22

"""Rule-based model routing: pick Flash or Pro per query.

`pick_model(query)` applies two cheap heuristics:
    - long queries or queries with math keywords go to the Pro model
    - everything else goes to Flash (cheaper and faster)

`route_model` is a `before_model_callback`. ADK calls it right before every
model request, and whatever it writes to `llm_request.model` is the model
that request goes to. Routing happens in plain Python before any model call,
which makes it cheap and easy to debug.

Set `ROUTER_PRO_MODEL` to override the Pro model id, for example when your
project cannot use Pro models.
"""

import os
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse

FLASH = "gemini-3.5-flash"
PRO = os.environ.get("ROUTER_PRO_MODEL", "gemini-2.5-pro")

MATH_KEYWORDS = (
    "calculate", "compute", "derivative", "integral", "solve",
    "matrix", "equation", "proof", "differentiate", "factorize",
)


def pick_model(query: str) -> str:
    """Returns the model id best suited for this query.

    Args:
        query: The user's question.

    Returns:
        `PRO` for queries of 200 characters or more, or with a math keyword;
        `FLASH` for everything else.
    """
    if len(query) >= 200:
        return PRO
    if any(keyword in query.lower() for keyword in MATH_KEYWORDS):
        return PRO
    return FLASH


def route_model(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Sends this model request to the model `pick_model` chooses.

    The choice is based on the user message that started the current turn,
    so every model call in one turn (including tool round trips) uses the
    same model. The choice is also written to state as `routed_model` so it
    shows up in the dev UI State tab.

    Args:
        callback_context: Context of the current invocation.
        llm_request: The request about to be sent. Its `model` is replaced.

    Returns:
        None, so the request goes ahead with the new model.
    """
    content = callback_context.user_content
    query = "".join(p.text or "" for p in content.parts) if content and content.parts else ""
    model = pick_model(query)
    llm_request.model = model
    callback_context.state["routed_model"] = model
    return None
