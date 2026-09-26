# Author: Vishal Bulbule
# Date: 2026-09-22

"""Output filter: an after_model callback that rewrites forbidden words.

The callback scans each text part of the model's response and replaces any
word from FORBIDDEN with [FILTERED]. Returning a new LlmResponse from
after_model replaces what the model produced; returning None keeps it.

Non-text parts (function calls, for example) are passed through untouched so
the filter never breaks tool calling.
"""

import re
from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types

# Mild stand-ins keep the sample safe to run anywhere. Put your real list here.
FORBIDDEN = {"damn", "hell", "crap", "stupid", "idiot"}
_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in FORBIDDEN) + r")\b", re.IGNORECASE
)


def profanity_filter(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Returns a scrubbed copy of the response, or None if it was clean."""
    if not llm_response.content or not llm_response.content.parts:
        return None

    new_parts = []
    total_hits = 0
    for part in llm_response.content.parts:
        if part.text:
            scrubbed, hits = _PATTERN.subn("[FILTERED]", part.text)
            total_hits += hits
            new_parts.append(types.Part(text=scrubbed))
        else:
            new_parts.append(part)

    if total_hits == 0:
        return None

    print(f"[profanity_filter] replaced {total_hits} word(s)")
    return LlmResponse(
        content=types.Content(
            role=llm_response.content.role or "model", parts=new_parts
        )
    )


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="profanity_filter_agent",
    description="after_model callback rewrites forbidden words to [FILTERED].",
    instruction=(
        "You are a candid, informal assistant. Casual language such as 'damn' "
        "or 'hell' is fine when it fits the tone the user asks for."
    ),
    after_model_callback=profanity_filter,
)
