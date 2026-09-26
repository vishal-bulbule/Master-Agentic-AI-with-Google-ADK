# Author: Vishal Bulbule
# Date: 2026-09-22

"""BROKEN on purpose: the agent variable is `my_agent` instead of `root_agent`.

ADK looks for a module-level symbol named exactly `root_agent` (or an `App`
named `app`). Any other name is invisible to the loader. See FIX.md.
"""

from google.adk.agents import LlmAgent


def ping() -> dict:
    """Returns a health-check response.

    Returns:
        dict with `status` and `message`.
    """
    return {"status": "success", "message": "pong"}


# WRONG: this should be root_agent.
my_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="broken_wrong_name",
    description="Demonstrates the wrong-variable-name failure.",
    instruction="Call the ping tool to respond.",
    tools=[ping],
)
