# Author: Vishal Bulbule
# Date: 2026-09-22

"""BROKEN on purpose: this folder has no __init__.py.

In ADK 2.9, `adk web` and `adk run` still load this agent: the loader imports
`broken_no_init.agent` directly, and Python treats a folder without
`__init__.py` as a namespace package. The missing file breaks tools that load
the package through `__init__.py`, such as `adk eval`. See FIX.md.
"""

from google.adk.agents import LlmAgent


def ping() -> dict:
    """Returns a health-check response.

    Returns:
        dict with `status` and `message`.
    """
    return {"status": "success", "message": "pong"}


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="broken_no_init",
    description="Demonstrates the missing __init__.py failure.",
    instruction="Call the ping tool to respond.",
    tools=[ping],
)
