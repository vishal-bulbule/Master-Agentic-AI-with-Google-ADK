# Author: Vishal Bulbule
# Date: 2026-09-22

"""A single agent that picks Flash or Pro for each user message.

The agent is declared with Flash, and `route_model` (a
`before_model_callback` in router.py) replaces `llm_request.model` before
each request. Easy questions stay on Flash; long or math-heavy ones go to
Pro. The agent definition, instruction and history stay the same; only the
model serving each turn changes.

Each model response event records `modelVersion`, and state key
`routed_model` holds the last choice, so the dev UI shows which model
answered.
"""

from google.adk.agents import LlmAgent

from .router import FLASH, route_model

root_agent = LlmAgent(
    model=FLASH,
    name="model_router_agent",
    description="Generic helper that routes each question to Flash or Pro.",
    instruction=(
        "You are a helpful assistant. Answer the user's question concisely "
        "in plain text. For math problems, show the key steps."
    ),
    before_model_callback=route_model,
)
