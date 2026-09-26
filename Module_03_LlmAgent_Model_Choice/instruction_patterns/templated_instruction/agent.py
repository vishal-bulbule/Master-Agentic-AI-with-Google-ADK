# Author: Vishal Bulbule
# Date: 2026-09-22

"""Instruction templating: fill placeholders from session state.

ADK treats `instruction` as a template. Two placeholder forms:
    {var}    required; the run fails if `var` is missing from state
    {var?}   optional; resolves to an empty string when missing

Here `{user_name?}` is read from session state. The dev UI cannot edit
state, so `set_default_state` (a before_agent_callback) writes a default
`user_name` when the session has none, and the first reply already greets
by name. A real app sets the name when it creates the session; the
callback leaves any existing value alone. Without the callback and without
a value the agent still works, because of the trailing `?`.
"""

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext

# Defaults for the state keys the instruction template reads.
DEFAULT_STATE = {"user_name": "Guest"}


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


def set_default_state(callback_context: CallbackContext) -> None:
    """Writes DEFAULT_STATE keys that the session does not have yet.

    Runs before the instruction template is rendered, so the placeholders
    resolve on the first turn. Values set at session creation win.

    Args:
        callback_context: Context of the current invocation; its `state` is
            the session state.

    Returns:
        None, so the agent runs normally.
    """
    for key, value in DEFAULT_STATE.items():
        if key not in callback_context.state:
            callback_context.state[key] = value


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="templated_instruction_agent",
    description="Capital-city expert that greets the user by name.",
    instruction=(
        "## Who you are\n"
        "You are a friendly capital-city expert. The user's name is "
        "'{user_name?}'. If a name is present, greet them by name on the FIRST "
        "reply only.\n\n"
        "## Task\n"
        "Answer the user's capital-city questions.\n\n"
        "## Tools\n"
        "Always call `get_capital`. Never answer from memory.\n\n"
        "## Output\n"
        "One short sentence, plain text."
    ),
    tools=[get_capital],
    before_agent_callback=set_default_state,
)
