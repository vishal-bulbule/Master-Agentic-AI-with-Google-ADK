# Author: Vishal Bulbule
# Date: 2026-09-22

"""GuardrailPlugin: PII block, token budget, and output filter in one plugin.

A plugin is a BasePlugin subclass registered once on the App. Its callbacks
run for every agent, model call, and tool call in that App, so the same
guardrails cover a multi-agent system without wiring callbacks on each agent.

Plugin callbacks run before the agent's own callbacks. If a plugin callback
returns a value, the agent-level callbacks for that step are skipped.
"""

import re
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.plugins import BasePlugin
from google.genai import types

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\-\s().]{7,}\d)")
DEFAULT_FORBIDDEN = {"damn", "hell", "crap", "stupid", "idiot"}
TOKENS_STATE_KEY = "guardrail_tokens_used"


def _refusal(text: str) -> LlmResponse:
    return LlmResponse(
        content=types.Content(role="model", parts=[types.Part(text=text)])
    )


def _latest_user_text(llm_request: LlmRequest) -> str:
    for content in reversed(llm_request.contents or []):
        if content.role == "user":
            return "\n".join(p.text for p in content.parts or [] if p.text)
    return ""


def _approx_tokens(llm_request: LlmRequest) -> int:
    chars = sum(
        len(part.text)
        for content in llm_request.contents or []
        for part in content.parts or []
        if part.text
    )
    return max(1, chars // 4)


class GuardrailPlugin(BasePlugin):
    """Blocks PII, caps tokens per session, and filters forbidden words."""

    def __init__(
        self,
        token_budget: int = 10_000,
        forbidden_words: Optional[set[str]] = None,
    ) -> None:
        super().__init__(name="guardrail_plugin")
        self.token_budget = token_budget
        words = forbidden_words or DEFAULT_FORBIDDEN
        self._forbidden_re = re.compile(
            r"\b(" + "|".join(re.escape(w) for w in words) + r")\b",
            re.IGNORECASE,
        )

    async def before_model_callback(
        self, *, callback_context: CallbackContext, llm_request: LlmRequest
    ) -> Optional[LlmResponse]:
        user_text = _latest_user_text(llm_request)
        if EMAIL_RE.search(user_text) or PHONE_RE.search(user_text):
            print("[GuardrailPlugin] PII blocked")
            return _refusal("I can't process personal contact information.")

        # The counter lives in session state, not on the plugin instance: one
        # plugin instance serves every session, and an instance counter would
        # make all users share a single budget.
        used = callback_context.state.get(TOKENS_STATE_KEY, 0)
        incoming = _approx_tokens(llm_request)
        if used + incoming > self.token_budget:
            print(
                f"[GuardrailPlugin] token budget exhausted "
                f"({used}+{incoming} > {self.token_budget})"
            )
            return _refusal("This session has used its token budget.")
        callback_context.state[TOKENS_STATE_KEY] = used + incoming
        return None

    async def after_model_callback(
        self, *, callback_context: CallbackContext, llm_response: LlmResponse
    ) -> Optional[LlmResponse]:
        if not llm_response.content or not llm_response.content.parts:
            return None

        new_parts = []
        hits = 0
        for part in llm_response.content.parts:
            if part.text:
                scrubbed, n = self._forbidden_re.subn("[FILTERED]", part.text)
                hits += n
                new_parts.append(types.Part(text=scrubbed))
            else:
                new_parts.append(part)

        if hits == 0:
            return None
        print(f"[GuardrailPlugin] filtered {hits} word(s)")
        return LlmResponse(
            content=types.Content(
                role=llm_response.content.role or "model", parts=new_parts
            )
        )
