# Author: Vishal Bulbule
# Date: 2026-09-22

"""A structured instruction that answers four questions.

Every effective instruction says:
    1. Who the agent is.
    2. What the task is.
    3. Which tools exist and when to call them.
    4. What the output looks like.

Markdown headings inside the prompt make the structure easy for the model to
follow. The tool is identical to the one in `bad_instruction`.
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
    name="good_instruction_agent",
    description="Answers capital-city questions using a curated tool.",
    instruction=(
        "## Who you are\n"
        "You are a friendly capital-city expert.\n\n"
        "## Task\n"
        "Answer user questions that ask for the capital city of a country.\n\n"
        "## Tools\n"
        "- `get_capital`: call this for every country query. Pass the country "
        "name in English. Do NOT answer from memory.\n"
        "- If the tool returns `status: error`, apologize and ask the user to "
        "check the spelling of the country name.\n\n"
        "## Output format\n"
        "Reply in one short sentence, plain text, no JSON, no bullets.\n"
        "Example: 'The capital of France is Paris.'"
    ),
    tools=[get_capital],
)
