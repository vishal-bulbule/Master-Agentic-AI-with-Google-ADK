# Author: Vishal Bulbule
# Date: 2026-09-22

"""Token budget kill switch enforced by a before_model callback.

The callback estimates the tokens in each outgoing request, adds them to a
running total in session state, and returns a refusal LlmResponse once the
total would pass TOKEN_BUDGET. Because the total lives in session state, it is
per session and survives restarts when a persistent session service is used.

The estimate (4 characters per token) is enough for a kill switch. For exact
counts read llm_response.usage_metadata in an after_model callback instead.
"""

from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types

TOKEN_BUDGET = 10_000
STATE_KEY = "tokens_used"


def _approx_tokens(llm_request: LlmRequest) -> int:
    chars = sum(
        len(part.text)
        for content in llm_request.contents or []
        for part in content.parts or []
        if part.text
    )
    return max(1, chars // 4)


def token_killswitch(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Refuses the model call once the session would exceed TOKEN_BUDGET."""
    used = callback_context.state.get(STATE_KEY, 0)
    incoming = _approx_tokens(llm_request)
    projected = used + incoming

    if projected > TOKEN_BUDGET:
        print(
            f"[killswitch] BUDGET EXCEEDED used={used} "
            f"+incoming={incoming} > {TOKEN_BUDGET}"
        )
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text=(
                            "This session has reached its token budget "
                            f"({TOKEN_BUDGET:,} tokens). Start a new session "
                            "or send shorter messages."
                        )
                    )
                ],
            )
        )

    callback_context.state[STATE_KEY] = projected
    print(f"[killswitch] OK used={projected}/{TOKEN_BUDGET}")
    return None


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="token_budget_agent",
    description="Agent with a 10,000-token session budget enforced by a callback.",
    instruction="You are a helpful assistant. Answer briefly.",
    before_model_callback=token_killswitch,
)
