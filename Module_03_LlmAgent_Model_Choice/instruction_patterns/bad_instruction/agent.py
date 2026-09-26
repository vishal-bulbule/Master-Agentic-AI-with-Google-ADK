# Author: Vishal Bulbule
# Date: 2026-09-22

"""Anti-pattern: a vague instruction with no role, tool rules, or format.

The tool is identical to the one in `good_instruction`. Only the instruction
changes. With "You help with countries." the model has to guess what to do
when the tool fails or the question is open-ended. Ask for the capital of
Germany (not in the tool's data): the tool returns an error and this agent
answers from memory anyway. Compare the same prompt against `good_instruction`.
"""

from google.adk.agents import LlmAgent


def get_capital(country: str) -> dict:
    """Returns the capital city of a country.

    Args:
        country: Country name in English, for example "France".

    Returns:
        A dict with `status` "success" plus `country` and `capital`, or
        `status` "error" with an `error_message` for an unknown country.
    """
    capitals = {
        "france": "Paris",
        "japan": "Tokyo",
        "canada": "Ottawa",
        "india": "New Delhi",
    }
    capital = capitals.get(country.lower())
    if not capital:
        return {"status": "error", "error_message": f"Unknown country: {country}"}
    return {"status": "success", "country": country, "capital": capital}


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="bad_instruction_agent",
    description="A capital-city helper with a deliberately vague instruction.",
    # Deliberately vague: no role, no rules about tool use, no output format.
    instruction="You help with countries.",
    tools=[get_capital],
)
