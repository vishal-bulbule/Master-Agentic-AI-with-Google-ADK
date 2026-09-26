# Author: Vishal Bulbule
# Date: 2026-09-22

"""before_agent returns Content, so the agent itself does not run.

No model call and no tool calls happen. The returned Content becomes the
agent's response. Use this for maintenance switches, feature flags, or
rejecting a request before any model cost is spent.
"""

from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types


def skip_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    print("[before_agent] returning Content, agent skipped")
    return types.Content(
        role="model",
        parts=[types.Part(text="This agent is offline for maintenance. Try again later.")],
    )


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="return_content_agent",
    description="before_agent returns Content, bypassing the whole agent.",
    instruction="You are a friendly assistant. Answer the user's question briefly.",
    before_agent_callback=skip_agent,
)
