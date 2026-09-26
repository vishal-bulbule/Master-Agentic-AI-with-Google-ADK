# Author: Vishal Bulbule
# Date: 2026-09-22

"""Minimal weather agent used as the target of an ADK test file.

One tool with hardcoded data, so the tool trajectory and the final response
are predictable enough to compare against a reference in
`tests/weather.test.json`. The agent exists to make the test-file shape easy
to read, not to be a real weather service.
"""

from google.adk.agents import LlmAgent

_WEATHER = {
    "paris": {"temp_c": 22, "conditions": "sunny"},
    "london": {"temp_c": 12, "conditions": "drizzly"},
    "tokyo": {"temp_c": 19, "conditions": "cloudy"},
}


def get_weather(city: str) -> dict:
    """Returns the current weather for a city.

    Args:
        city: City name (case-insensitive).

    Returns:
        Dict with `status` (`success` or `not_found`) and either `report`
        or `error_message`.
    """
    info = _WEATHER.get(city.lower())
    if info is None:
        return {"status": "not_found", "error_message": f"No data for '{city}'."}
    return {
        "status": "success",
        "report": f"{info['conditions'].title()}, {info['temp_c']} C.",
    }


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="weather_agent",
    description="Looks up weather for a city via the get_weather tool.",
    instruction=(
        "When the user asks about weather, call get_weather(city) and reply with "
        "the report verbatim. If status is not_found, reply exactly: "
        "Sorry, I don't have weather data for <city>."
    ),
    tools=[get_weather],
)
