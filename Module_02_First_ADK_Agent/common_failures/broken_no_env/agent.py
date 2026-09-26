# Author: Vishal Bulbule
# Date: 2026-09-22

"""BROKEN on purpose, when run without credentials in the environment.

The code is correct. What fails is the environment: the model client finds no
API key and no Agent Platform settings. `adk web` and `adk run` load the
nearest `.env` walking up from this folder, so with a `.env` at the repository
root this agent works. Run it with `ADK_DISABLE_LOAD_DOTENV=1` to reproduce
what happens when no `.env` is found. See FIX.md.
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
    name="broken_no_env",
    description="Demonstrates the missing-credentials failure.",
    instruction="Call the ping tool to respond.",
    tools=[ping],
)
