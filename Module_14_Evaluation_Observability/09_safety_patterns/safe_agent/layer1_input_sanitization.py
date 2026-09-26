# Author: Vishal Bulbule
# Date: 2026-09-22

"""Layer 1: input sanitization in a before_model_callback.

Scans the user's latest message for contact details (email, phone) and common
jailbreak phrases. On a hit it returns an LlmResponse, which makes ADK skip the
model call entirely and use that response instead.

It checks `callback_context.user_content` (the message that started this turn),
not every entry in `llm_request.contents`. Scanning the whole history would
refuse every later turn once one message had tripped a pattern.
"""

import re
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\+?\d[\d\-\s().]{7,}\d")

JAILBREAK_PATTERNS = [
    r"ignore (all |any )?previous instructions",
    r"\bDAN\b",
    r"developer mode",
    r"jailbreak",
    r"pretend you have no rules",
]
JAILBREAK_RE = re.compile("|".join(JAILBREAK_PATTERNS), re.IGNORECASE)


def _text_of(content: Optional[types.Content]) -> str:
    """Joins the text parts of a Content, ignoring non-text parts."""
    if content is None or not content.parts:
        return ""
    return "\n".join(part.text for part in content.parts if part.text)


def _refuse(text: str) -> LlmResponse:
    return LlmResponse(content=types.Content(role="model", parts=[types.Part(text=text)]))


def input_sanitizer(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Refuses the turn if the user message contains contact details or a jailbreak phrase."""
    text = _text_of(callback_context.user_content)

    if EMAIL_RE.search(text) or PHONE_RE.search(text):
        print("[layer1] contact details detected, refusing")
        return _refuse(
            "I can't process messages that contain personal contact details such as "
            "emails or phone numbers. Please rephrase without them."
        )

    if JAILBREAK_RE.search(text):
        print("[layer1] jailbreak pattern detected, refusing")
        return _refuse("I can't follow instructions that try to override my safety rules.")

    return None
