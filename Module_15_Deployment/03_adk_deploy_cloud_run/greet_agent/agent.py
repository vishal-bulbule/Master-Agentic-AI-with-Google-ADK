# Author: Vishal Bulbule
# Date: 2026-09-22

"""Minimal agent deployed to Cloud Run with `adk deploy cloud_run`.

Same greeter as topic 02. The folder layout (`__init__.py`, `agent.py`,
`requirements.txt`) is all the CLI needs: it generates the Dockerfile, builds
the image with Cloud Build, and deploys the service.
"""

from google.adk.agents import LlmAgent


def greet(name: str) -> dict:
    """Returns a greeting for the given person.

    Args:
        name: The person's display name.

    Returns:
        Dict with `status` and either `message` or `error_message`.
    """
    if not name or not name.strip():
        return {"status": "error", "error_message": "name is required"}
    return {"status": "success", "message": f"Hello, {name.strip()}!"}


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="greet_agent",
    description="Greets the user by name.",
    instruction=(
        "You are a friendly greeter. When given a name, call the greet tool and "
        "reply with the tool's message verbatim."
    ),
    tools=[greet],
)
