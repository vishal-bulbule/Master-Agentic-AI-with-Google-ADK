# Author: Vishal Bulbule
# Date: 2026-09-22

"""Greeter agent served by the custom FastAPI app in `main.py`.

The agent code does not change for a custom image. What changes is the wrapper:
`get_fast_api_app` discovers every package under `agents/` and serves it, so
more agents can be added next to this one in the same service.
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
