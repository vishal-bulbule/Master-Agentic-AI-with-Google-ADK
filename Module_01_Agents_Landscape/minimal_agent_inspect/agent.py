# Author: Vishal Bulbule
# Date: 2026-09-22

"""The smallest useful LlmAgent: one model, one tool, inspected in `adk web`.

The agent looks up the time in a few hardcoded cities. It is small enough that
every row in the `adk web` Events view can be explained: the user message,
the model's function_call, the tool's function_response and the final model
text.

Run from Module_01_Agents_Landscape/:
    adk web
Then pick `minimal_agent_inspect` and ask "What time is it in Tokyo?"
"""

from google.adk.agents import LlmAgent


def get_current_time(city: str) -> dict:
    """Returns the current time for a city.

    Args:
        city: City name, for example "Tokyo", "Paris", "Mumbai".

    Returns:
        dict with `status`, `city`, and either `time` or `error_message`.
    """
    fake_times = {
        "tokyo": "10:30 AM JST",
        "paris": "02:30 AM CET",
        "mumbai": "07:00 AM IST",
        "new york": "09:30 PM EST",
    }
    key = city.lower()
    if key in fake_times:
        return {"status": "success", "city": city, "time": fake_times[key]}
    return {
        "status": "error",
        "error_message": f"No time data for '{city}'. Try Tokyo, Paris, Mumbai, or New York.",
    }


root_agent = LlmAgent(
    name="minimal_time_agent",
    model="gemini-3.5-flash",
    description="A tiny agent that tells the current time in a few cities.",
    instruction=(
        "You tell the time in cities. When the user asks about the time in a city, "
        "call the `get_current_time` tool. Always report the city and the time. "
        "If the tool returns an error, apologize and list the cities you know about."
    ),
    tools=[get_current_time],
)
