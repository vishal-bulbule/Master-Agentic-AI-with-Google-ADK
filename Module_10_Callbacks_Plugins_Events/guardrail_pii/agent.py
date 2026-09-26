# Author: Vishal Bulbule
# Date: 2026-09-22

"""PII guardrail: refuse requests that contain an email or phone number.

A before_model callback scans the text of the latest user message. If it finds
PII it returns an LlmResponse with a refusal, so the model never sees the
input. Otherwise it returns None and the call goes ahead.

Only the latest user turn is checked. Scanning the whole history would keep
refusing every later message once PII had appeared once.
"""

import re
from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\-\s().]{7,}\d)")


def _latest_user_text(llm_request: LlmRequest) -> str:
    for content in reversed(llm_request.contents or []):
        if content.role == "user":
            return "\n".join(p.text for p in content.parts or [] if p.text)
    return ""


def has_pii(text: str) -> bool:
    return bool(EMAIL_RE.search(text) or PHONE_RE.search(text))


def pii_block(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Returns a refusal when the latest user message contains PII."""
    if has_pii(_latest_user_text(llm_request)):
        print("[pii_block] PII detected, refusing without calling the model")
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text=(
                            "I can't process messages that contain personal "
                            "contact information such as email addresses or "
                            "phone numbers. Please rephrase without it."
                        )
                    )
                ],
            )
        )
    return None


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="pii_guardrail_agent",
    description="Refuses any request containing an email or phone number.",
    instruction="You are a helpful assistant. Answer the user's question briefly.",
    before_model_callback=pii_block,
)
