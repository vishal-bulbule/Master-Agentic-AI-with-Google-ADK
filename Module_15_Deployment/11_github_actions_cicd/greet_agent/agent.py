# Author: Vishal Bulbule
# Date: 2026-09-22

"""Greeter agent deployed by the GitHub Actions pipeline in this topic.

The pipeline runs the tests in `tests/` (unit tests of the tool and a small
eval) and only runs `adk deploy cloud_run` when they pass.
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
