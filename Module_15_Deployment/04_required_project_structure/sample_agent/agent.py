# Author: Vishal Bulbule
# Date: 2026-09-22

"""The smallest agent folder that `adk run`, `adk web`, and `adk deploy` accept.

Three things are required:
  1. The folder name is the app name (`sample_agent`).
  2. `agent.py` defines `root_agent` at module scope.
  3. `__init__.py` contains `from . import agent`.
`requirements.txt` is optional but is what the deploy commands install.
"""

from google.adk.agents import LlmAgent


def echo(text: str) -> dict:
    """Returns the given text unchanged.

    Args:
        text: Any input string.

    Returns:
        Dict with `status` and `echoed`.
    """
    return {"status": "success", "echoed": text}


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="sample_agent",
    description="The smallest deployable agent.",
    instruction="Call the echo tool with the user's message and reply with the echoed text.",
    tools=[echo],
)
