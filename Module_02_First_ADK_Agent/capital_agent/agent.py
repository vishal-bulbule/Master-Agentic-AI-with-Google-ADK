# Author: Vishal Bulbule
# Date: 2026-09-22

"""The minimal ADK agent: one LlmAgent, one tool.

ADK finds this agent because the folder has an `__init__.py` that imports
`agent`, and `agent.py` defines a variable named `root_agent`. ADK turns
`get_capital` into a tool declaration from its signature and docstring, so
the type hints and the Args section are what the model reads.

Run from Module_02_First_ADK_Agent/:
    adk run capital_agent
"""

from google.adk.agents import LlmAgent


def get_capital(country: str) -> dict:
    """Returns the capital city of the given country.

    Args:
        country: The country name in English (case-insensitive).

    Returns:
        A dict with `status` (`success` or `not_found`) and either
        `capital` or `error_message`.
    """
    capitals = {
        "france": "Paris",
        "japan": "Tokyo",
        "india": "New Delhi",
        "germany": "Berlin",
        "brazil": "Brasilia",
        "australia": "Canberra",
    }
    capital = capitals.get(country.lower())
    if capital is None:
        return {
            "status": "not_found",
            "error_message": f"No capital on record for '{country}'.",
        }
    return {"status": "success", "capital": capital}


# ADK discovers the agent by this exact variable name.
root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="capital_agent",
    description="Answers 'what is the capital of X?' questions.",
    instruction=(
        "You answer questions about country capitals. "
        "Always call the get_capital tool; never rely on your own memory. "
        "If the tool returns status='not_found', apologize and say you don't know."
    ),
    tools=[get_capital],
)
