# Author: Vishal Bulbule
# Date: 2026-09-22

"""Layer 3: output review in an after_model_callback.

Runs on every model response before ADK emits it:
1. If the text contains something shaped like a US SSN (NNN-NN-NNNN), the whole
   response is replaced with a refusal. This guards against the model leaking
   data it saw in context.
2. A short list of banned words is masked. The list is a placeholder; in
   production call a safety classifier or Sensitive Data Protection here.

Returning an LlmResponse replaces the model's response; returning None keeps it.
For destructive actions, add a human approval step before the action runs;
the hook point is a callback like this one.
"""

import re
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types

SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
BANNED_WORDS = {"damn", "hell"}


def _replace(text: str) -> LlmResponse:
    return LlmResponse(content=types.Content(role="model", parts=[types.Part(text=text)]))


def output_review(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Refuses SSN-shaped output and masks banned words in the model's text."""
    if llm_response.content is None or not llm_response.content.parts:
        return None

    # Responses that are only a function call have no text; leave them alone.
    text = "".join(part.text or "" for part in llm_response.content.parts)
    if not text:
        return None

    if SSN_RE.search(text):
        print("[layer3] SSN-shaped output, replacing response")
        return _replace(
            "I noticed sensitive personal data in my draft response and stopped. "
            "Please rephrase your question."
        )

    cleaned = text
    for word in BANNED_WORDS:
        cleaned = re.sub(rf"\b{re.escape(word)}\b", "***", cleaned, flags=re.IGNORECASE)
    if cleaned != text:
        print("[layer3] banned word masked")
        return _replace(cleaned)

    return None
