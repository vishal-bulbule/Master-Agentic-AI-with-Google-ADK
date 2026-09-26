# Author: Vishal Bulbule
# Date: 2026-09-22

"""Lab reference solution: an agent with two tools, weather and jokes.

The model picks the tool from the user's request: `get_weather` for weather
questions, `tell_joke` for jokes. The data is hardcoded; the point is the
wiring. Both tools return a dict with a `status` key so the model can tell
success from failure, as in the `not_found` branch for unknown cities.
"""

import random

from google.adk.agents import LlmAgent

_WEATHER = {
    "pune": {"temp_c": 32, "conditions": "sunny and dry"},
    "mumbai": {"temp_c": 30, "conditions": "humid with afternoon showers"},
    "bengaluru": {"temp_c": 26, "conditions": "pleasant with light clouds"},
    "delhi": {"temp_c": 38, "conditions": "hot and hazy"},
    "new york": {"temp_c": 18, "conditions": "cool and clear"},
    "london": {"temp_c": 12, "conditions": "overcast with drizzle"},
    "tokyo": {"temp_c": 22, "conditions": "mild with scattered clouds"},
}

_JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "I told my computer I needed a break. It said, 'No problem, I'll go to sleep.'",
    "There are 10 kinds of people in the world: those who understand binary and those who don't.",
    "Why did the developer go broke? Because he used up all his cache.",
    "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
]


def get_weather(city: str) -> dict:
    """Returns the current weather report for a city.

    Args:
        city: City name in English (case-insensitive).

    Returns:
        dict with `status` (`success` or `not_found`) and either
        `report` (a human-readable string) or `error_message`.
    """
    info = _WEATHER.get(city.lower())
    if info is None:
        return {
            "status": "not_found",
            "error_message": f"I don't have weather data for '{city}'.",
        }
    return {
        "status": "success",
        "report": (
            f"The weather in {city.title()} is {info['conditions']}, "
            f"around {info['temp_c']} degrees C."
        ),
    }


def tell_joke() -> dict:
    """Returns one random programming joke.

    Returns:
        dict with `status` set to `success` and a `joke` string.
    """
    return {"status": "success", "joke": random.choice(_JOKES)}


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="weather_jokes_agent",
    description="Tells you the weather and tells a joke when asked.",
    instruction=(
        "You are a friendly assistant with two skills.\n"
        "1. When the user asks about weather, call get_weather(city).\n"
        "2. When the user asks for a joke (or to be cheered up), call tell_joke().\n"
        "Never invent weather data or jokes yourself; always use the tools. "
        "If get_weather returns status='not_found', say so politely."
    ),
    tools=[get_weather, tell_joke],
)
