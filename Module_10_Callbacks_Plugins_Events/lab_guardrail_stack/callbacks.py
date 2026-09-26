# Author: Vishal Bulbule
# Date: 2026-09-22

"""The four guardrail callbacks used by the customer-service agent.

Each callback does one job and prints a labeled line, so the terminal running
`adk web` shows which one fired on which turn. They are plain functions, so the same file can
be imported by any agent.
"""

import re
from typing import Any, Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools import BaseTool, ToolContext
from google.genai import types

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\-\s().]{7,}\d)")

FORBIDDEN_WORDS = {"damn", "hell", "crap", "stupid", "idiot"}
_PROFANITY_RE = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in FORBIDDEN_WORDS) + r")\b",
    re.IGNORECASE,
)

TOKEN_BUDGET = 10_000
STATE_TOKENS = "tokens_used"
STATE_COST = "total_cost_usd"

# Made-up prices. Load real ones from billing config in production.
TOOL_COSTS_USD = {
    "lookup_order": 0.002,
    "issue_refund": 0.010,
    "send_followup_email": 0.005,
}
DEFAULT_COST_USD = 0.001


def _request_text(llm_request: LlmRequest) -> str:
    return "\n".join(
        part.text
        for content in llm_request.contents or []
        for part in content.parts or []
        if part.text
    )


def pii_redaction(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Replaces emails and phone numbers in the outgoing request.

    The request is edited in place and None is returned, so the cleaned
    request goes to the model. Unlike a block, the conversation continues.
    """
    total_hits = 0
    for content in llm_request.contents or []:
        for part in content.parts or []:
            if not part.text:
                continue
            text, n_email = EMAIL_RE.subn("[REDACTED_EMAIL]", part.text)
            text, n_phone = PHONE_RE.subn("[REDACTED_PHONE]", text)
            if n_email or n_phone:
                part.text = text
                total_hits += n_email + n_phone
    if total_hits:
        print(f"[pii_redaction] redacted {total_hits} item(s) before send")
    return None


def token_budget(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Refuses the model call once the session would pass TOKEN_BUDGET."""
    incoming = max(1, len(_request_text(llm_request)) // 4)
    used = callback_context.state.get(STATE_TOKENS, 0)
    projected = used + incoming

    if projected > TOKEN_BUDGET:
        print(
            f"[token_budget] BUDGET EXCEEDED used={used} +incoming={incoming} "
            f"> {TOKEN_BUDGET}, refusing"
        )
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text=(
                            "Sorry, this chat has reached its limit of "
                            f"{TOKEN_BUDGET:,} tokens. Please start a new chat."
                        )
                    )
                ],
            )
        )

    callback_context.state[STATE_TOKENS] = projected
    print(f"[token_budget] OK used={projected}/{TOKEN_BUDGET}")
    return None


def profanity_filter(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Replaces forbidden words in the model's reply with [FILTERED]."""
    if not llm_response.content or not llm_response.content.parts:
        return None

    new_parts = []
    hits = 0
    for part in llm_response.content.parts:
        if part.text:
            scrubbed, n = _PROFANITY_RE.subn("[FILTERED]", part.text)
            hits += n
            new_parts.append(types.Part(text=scrubbed))
        else:
            new_parts.append(part)

    if hits == 0:
        return None

    print(f"[profanity_filter] replaced {hits} word(s) in model output")
    return LlmResponse(
        content=types.Content(
            role=llm_response.content.role or "model", parts=new_parts
        )
    )


def cost_logger(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
    tool_response: dict,
) -> Optional[dict]:
    """Adds the tool's estimated cost to the session total."""
    cost = TOOL_COSTS_USD.get(tool.name, DEFAULT_COST_USD)
    total = tool_context.state.get(STATE_COST, 0.0) + cost
    tool_context.state[STATE_COST] = total
    print(
        f"[cost_logger] tool={tool.name} cost=${cost:.4f} "
        f"session_total=${total:.4f}"
    )
    return None
