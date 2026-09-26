# Author: Vishal Bulbule
# Date: 2026-09-22

"""Greeter agent for the production deploy lab.

The agent code is the same as in the earlier topics. The production concerns
live outside it: the API key comes from Secret Manager, access is limited by
IAM, and traces are exported with `adk deploy cloud_run --trace_to_cloud`, so
no tracing code is needed here.
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
