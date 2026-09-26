# Author: Vishal Bulbule
# Date: 2026-09-22

"""PlanReActPlanner: explicit plan, act, reason, answer steps on any model.

`PlanReActPlanner` works by prompting, not by a model feature, so it runs on
Gemini, Claude through LiteLLM, or any other model. It asks the model to
write a plan, call tools, reason over the results, and give a final answer,
each under a tagged heading.

Use it when the model has no native thinking, when you want plans you can
log and grade, or when you need the same reasoning shape across providers.
The planner marks the PLANNING and REASONING text as thought parts, so only
the FINAL_ANSWER section reads as the reply.
"""

from datetime import date

from google.adk.agents import LlmAgent
from google.adk.planners import PlanReActPlanner


def get_weather(city: str) -> dict:
    """Returns a canned weather forecast for a city.

    Args:
        city: City name, for example "Tokyo".

    Returns:
        A dict with `status` "success" plus `city`, `temp_c`, and `summary`,
        or `status` "error" for a city with no data.
    """
    canned = {
        "pune": {"temp_c": 32, "summary": "sunny"},
        "london": {"temp_c": 14, "summary": "cloudy"},
        "tokyo": {"temp_c": 22, "summary": "light rain"},
        "san francisco": {"temp_c": 18, "summary": "foggy"},
    }
    info = canned.get(city.lower())
    if not info:
        return {"status": "error", "error_message": f"No data for {city}."}
    return {"status": "success", "city": city, **info}


def get_local_time(city: str) -> dict:
    """Returns the UTC offset for a city (canned data, no timezone lookup).

    Args:
        city: City name, for example "Tokyo".

    Returns:
        A dict with `status` "success" plus `city` and `utc_offset`, or
        `status` "error" for an unknown city.
    """
    offsets = {
        "pune": "+05:30",
        "london": "+00:00",
        "tokyo": "+09:00",
        "san francisco": "-08:00",
    }
    offset = offsets.get(city.lower())
    if not offset:
        return {"status": "error", "error_message": f"Unknown city: {city}."}
    return {"status": "success", "city": city, "utc_offset": offset}


def suggest_clothing(temp_c: float, summary: str) -> dict:
    """Recommends clothing for a temperature and a short weather summary.

    Args:
        temp_c: Temperature in degrees Celsius.
        summary: Short weather description, for example "light rain".

    Returns:
        A dict with `status` "success" and a `suggestion` string.
    """
    if temp_c >= 28:
        outfit = "T-shirt and shorts"
    elif temp_c >= 18:
        outfit = "Light jacket and jeans"
    else:
        outfit = "Warm coat, scarf, and long pants"
    if "rain" in summary.lower():
        outfit += ", plus an umbrella"
    return {"status": "success", "suggestion": outfit}


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="react_travel_agent",
    description=(
        "Plans short trip-day advice: pulls weather, local time, and a "
        "clothing suggestion using a plan, act, reason, answer loop."
    ),
    instruction=(
        "## Who you are\n"
        "You are a travel-day assistant.\n\n"
        "## Task\n"
        "For each user question about a city, gather (a) weather, "
        "(b) local time offset, then (c) a clothing suggestion. Combine the "
        "three into a single short paragraph answer.\n\n"
        "## Tools\n"
        "- `get_weather(city)`\n"
        "- `get_local_time(city)`\n"
        "- `suggest_clothing(temp_c, summary)`: call this AFTER weather.\n\n"
        f"Today is {date.today().isoformat()}."
    ),
    tools=[get_weather, get_local_time, suggest_clothing],
    # No thinking budget here: the planner works purely through its prompt.
    planner=PlanReActPlanner(),
)
