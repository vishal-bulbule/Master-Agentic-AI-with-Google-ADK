# Author: Vishal Bulbule
# Date: 2026-09-22

"""Generation config on an agent: temperature and an output token cap.

`generate_content_config` takes a `google.genai.types.GenerateContentConfig`
and applies it to every model call the agent makes.

The agent uses temperature 1.0, the value Gemini 3.x models are tuned for.
Lowering it to 0 makes answers more alike but not identical, and Google
recommends against it for reasoning-heavy work. The README walks through
comparing the two in `adk web`.
"""

from google.adk.agents import LlmAgent
from google.genai import types

root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="generation_config_agent",
    description="An agent with an explicit temperature and output token cap.",
    instruction="Answer in one or two short sentences.",
    generate_content_config=types.GenerateContentConfig(
        # Gemini 3.x default. Change to 0.0 to compare (see README).
        temperature=1.0,
        # Cost cap. Thinking tokens count against this limit on Gemini 3.x.
        max_output_tokens=1024,
    ),
)
