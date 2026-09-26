# Author: Vishal Bulbule
# Date: 2026-09-22

"""Observability callback: log every model call and return None.

The simplest useful callback. It reads the outgoing request, writes one log
line, and returns None so the run is unchanged. The same hook is where you
would send structured records to Cloud Logging, BigQuery, or OpenTelemetry.

The logged input grows on each turn because llm_request.contents carries the
whole conversation history, not just the latest message.
"""

import logging
from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse

logger = logging.getLogger("observability")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(_handler)
    logger.propagate = False


def log_calls(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Logs agent name, input size, and a preview of the request text."""
    text_in = [
        part.text
        for content in llm_request.contents or []
        for part in content.parts or []
        if part.text
    ]
    logger.info(
        "model_call agent=%s input_chars=%d preview=%r",
        callback_context.agent_name,
        sum(len(t) for t in text_in),
        " | ".join(text_in)[:120],
    )
    return None


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="observability_agent",
    description="Logs every model call from a before_model callback.",
    instruction="You are a helpful assistant. Answer briefly.",
    before_model_callback=log_calls,
)
