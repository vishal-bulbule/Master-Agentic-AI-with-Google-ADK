# Author: Vishal Bulbule
# Date: 2026-09-22

"""Response cache: answer repeated questions without calling the model.

before_model hashes the latest user message and looks it up in a dict. On a
hit it returns the stored text as an LlmResponse and the model call is
skipped. On a miss it returns None and remembers the key; after_model then
stores the model's answer under that key.

The key is kept in `temp:` state, which lives for one invocation only and is
never written to the session. That is the right scope for data passed from a
before_* callback to its matching after_* callback.
"""

import hashlib
from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types

# Process-local and unbounded. Use Memorystore (Redis) with a TTL in production.
_CACHE: dict[str, str] = {}
CACHE_KEY_STATE = "temp:cache_key"


def _latest_user_text(llm_request: LlmRequest) -> str:
    for content in reversed(llm_request.contents or []):
        if content.role == "user":
            return "\n".join(p.text for p in content.parts or [] if p.text)
    return ""


def cache_lookup(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Returns the cached answer on a hit, None on a miss."""
    question = _latest_user_text(llm_request).strip().lower()
    key = hashlib.sha256(question.encode("utf-8")).hexdigest()
    hit = _CACHE.get(key)
    if hit is not None:
        print(f"[cache] HIT  key={key[:8]}, model call skipped")
        return LlmResponse(
            content=types.Content(role="model", parts=[types.Part(text=hit)])
        )
    print(f"[cache] MISS key={key[:8]}, calling model")
    callback_context.state[CACHE_KEY_STATE] = key
    return None


def cache_store(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Stores the model's text answer under the key from cache_lookup."""
    # With streaming on (More options > Streaming in the dev UI), after_model
    # also sees each partial chunk. Cache only the complete response.
    if llm_response.partial:
        return None
    key = callback_context.state.get(CACHE_KEY_STATE)
    if not key or not llm_response.content or not llm_response.content.parts:
        return None
    text = "".join(p.text or "" for p in llm_response.content.parts)
    if text:
        _CACHE[key] = text
        print(f"[cache] STORE key={key[:8]} (chars={len(text)})")
    return None


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="cache_agent",
    description="Answers repeated questions from an in-memory cache.",
    instruction="You are a concise assistant. Always answer in one short sentence.",
    before_model_callback=cache_lookup,
    after_model_callback=cache_store,
)
