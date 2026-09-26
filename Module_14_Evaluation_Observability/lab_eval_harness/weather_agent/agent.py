# Author: Vishal Bulbule
# Date: 2026-09-22

"""Weather agent evaluated by the lab eval harness.

A little richer than topic 01: more cities, input validation, and an
instruction to handle several cities in one question. The 15 eval cases in
`tests/` cover the happy path, not-found and empty input, a typo, and a
two-city question.
"""

from google.adk.agents import LlmAgent

_WEATHER = {
    "paris": {"temp_c": 22, "conditions": "sunny"},
    "london": {"temp_c": 12, "conditions": "drizzly"},
    "tokyo": {"temp_c": 19, "conditions": "cloudy"},
    "mumbai": {"temp_c": 31, "conditions": "humid with showers"},
    "new york": {"temp_c": 18, "conditions": "clear"},
    "sydney": {"temp_c": 24, "conditions": "warm and breezy"},
    "bengaluru": {"temp_c": 26, "conditions": "pleasant"},
}


def get_weather(city: str) -> dict:
    """Returns the current weather for a city.

    Args:
        city: City name (case-insensitive). An empty string returns invalid_input.

    Returns:
        Dict with `status` (`success`, `not_found`, or `invalid_input`) and
        either `report` or `error_message`.
    """
    if not city or not city.strip():
        return {"status": "invalid_input", "error_message": "Please tell me which city."}
    info = _WEATHER.get(city.strip().lower())
    if info is None:
        return {"status": "not_found", "error_message": f"I don't have weather data for '{city}'."}
    return {
        "status": "success",
        "report": f"{info['conditions'].title()}, {info['temp_c']} C.",
    }


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="weather_agent",
    description="Looks up the current weather for one or more cities.",
    instruction=(
        "When the user asks about weather, call get_weather(city) once for each city "
        "in the question, using the city name exactly as the user wrote it. Combine "
        "the results into one short reply that names each city.\n"
        "- If status is success, give the conditions and the temperature in C.\n"
        "- If status is not_found, say briefly that you have no weather data for that "
        "city and ask the user to check the name.\n"
        "- If the user gives no city, do not call the tool; ask which city they mean.\n"
        "You only know current conditions. Never invent forecasts or any data that "
        "get_weather did not return."
    ),
    tools=[get_weather],
)
