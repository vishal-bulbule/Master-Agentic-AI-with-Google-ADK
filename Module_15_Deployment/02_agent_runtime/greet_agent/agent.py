# Author: Vishal Bulbule
# Date: 2026-09-22

"""Minimal agent deployed to Agent Runtime with `adk deploy agent_engine`.

It greets a person and nothing else, so the deployment is what you look at.
Nothing in the code is specific to Agent Runtime: the CLI packages the folder,
builds the container, and wires managed sessions (`agentengine://`) for you.
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
