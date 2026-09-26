# Author: Vishal Bulbule
# Date: 2026-09-22

"""BROKEN on purpose: the tool parameter has no type hint.

ADK builds the tool's JSON schema from the function signature. Without a hint,
`country` is declared with no type at all, so nothing tells the model what to
send. With one obvious string argument the model usually guesses right, which
makes this bug easy to miss. See FIX.md for how to see it.
"""

from google.adk.agents import LlmAgent


# WRONG: `country` has no type hint, and there is no return annotation.
def get_capital(country):
    """Returns the capital city of the given country.

    Args:
        country: The country name in English.
    """
    capitals = {"france": "Paris", "japan": "Tokyo", "india": "New Delhi"}
    return {
        "status": "success",
        "capital": capitals.get(country.lower(), "Unknown"),
    }


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="broken_no_type_hint",
    description="Demonstrates the missing-type-hint failure.",
    instruction="Always use get_capital to answer. Never guess.",
    tools=[get_capital],
)
