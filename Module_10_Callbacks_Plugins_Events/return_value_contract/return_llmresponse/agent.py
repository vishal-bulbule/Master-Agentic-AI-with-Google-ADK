# Author: Vishal Bulbule
# Date: 2026-09-22

"""before_model returns an LlmResponse, so the model call is skipped.

ADK treats the returned LlmResponse as if the model had produced it. Guardrails
and response caches are built on this path.
"""

from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types


def short_circuit(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    print("[before_model] returning LlmResponse, model call skipped")
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(text="Answered by the callback. The model was not called.")],
        )
    )


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="return_llmresponse_agent",
    description="before_model returns an LlmResponse, bypassing the model.",
    instruction="You are a friendly assistant. Answer the user's question briefly.",
    before_model_callback=short_circuit,
)
