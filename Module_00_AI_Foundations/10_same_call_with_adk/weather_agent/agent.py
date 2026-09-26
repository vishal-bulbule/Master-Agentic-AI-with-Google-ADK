# Author: Vishal Bulbule
# Date: 2026-09-22

"""The same weather task as `../04_function_calling/`, written as an ADK agent.

`function_calling.py` runs the tool loop by hand: read the `function_call`
part, run the function, append a `function_response` part, call the model
again. This file declares the tool and the instruction and stops there. ADK
runs that loop, for as many rounds as the model needs.

The tool is unchanged from the raw SDK version. What disappears is the
plumbing: history management, thought signatures, and the second model call.
"""

from google.adk.agents import LlmAgent

_FAKE_DB = {
    "paris": {"temp_c": 18, "condition": "cloudy"},
    "mumbai": {"temp_c": 33, "condition": "humid"},
    "tokyo": {"temp_c": 24, "condition": "clear"},
}


def get_weather(city: str) -> dict:
    """Returns current weather for a city.

    Args:
        city: City name, for example "Mumbai".

    Returns:
        dict with `status` and either `temp_c` and `condition`, or
        `error_message`.
    """
    weather = _FAKE_DB.get(city.strip().lower())
    if weather is None:
        return {"status": "error", "error_message": f"No weather data for {city}."}
    return {"status": "success", **weather}


root_agent = LlmAgent(
    name="weather_agent",
    model="gemini-3.5-flash",
    description="Answers weather questions from the get_weather tool.",
    instruction=(
        "You answer questions about the weather. Call get_weather for the city "
        "the user names and answer from its result. If the tool returns an "
        "error, say you have no data for that city. Never guess a temperature."
    ),
    tools=[get_weather],
)
