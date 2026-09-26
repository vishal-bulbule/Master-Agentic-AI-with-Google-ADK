# Author: Vishal Bulbule
# Date: 2026-09-22

"""before_model returns None, so the model call proceeds normally.

This is the default path for every callback. The callback logs that it saw the
request and hands control back to ADK unchanged.
"""

from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse


def passthrough(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    print("[before_model] returning None, model call proceeds")
    return None


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="return_none_agent",
    description="before_model returns None, so the model runs as usual.",
    instruction="You are a friendly assistant. Answer the user's question briefly.",
    before_model_callback=passthrough,
)
