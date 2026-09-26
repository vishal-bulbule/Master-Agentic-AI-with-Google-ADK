# Author: Vishal Bulbule
# Date: 2026-09-22

"""A plain tool-using agent whose event stream you inspect in the dev UI.

Nothing here is event-specific. Any agent produces the same stream of events;
the tool is there so one turn includes a function call, a function response,
and a final text response. The Events view in `adk web` lists each one as a
numbered row.
"""

from google.adk.agents import LlmAgent


def get_weather(city: str) -> dict:
    """Returns the current weather for a city. Canned data in this sample.

    Args:
        city: City name.

    Returns:
        A dict with status, city, temp_c, and summary.
    """
    return {"status": "success", "city": city, "temp_c": 28, "summary": "sunny"}


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="event_demo_agent",
    description="Weather agent used to show the ADK event stream.",
    instruction=(
        "You are a weather assistant. Call get_weather for any weather "
        "question, then summarize the result in one short sentence."
    ),
    tools=[get_weather],
)
