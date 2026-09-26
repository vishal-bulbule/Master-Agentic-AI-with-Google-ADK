# Author: Vishal Bulbule
# Date: 2026-09-22

"""Required vs optional tool parameters.

`city` has a type hint and no default, so ADK marks it required and the model
must ask the user when it is missing. `unit` has a default, so it is optional
and the model can leave it out.

Anti-pattern: a default on data the user must supply
(`destination: str = "Paris"`). The model will use the default instead of
asking, and every booking goes to Paris.
"""

from google.adk.agents import LlmAgent


def get_weather(city: str, unit: str = "celsius") -> dict:
    """Returns the current weather for a city.

    Args:
        city: The city to look up. Required; ask the user if it is not given.
        unit: Temperature unit, "celsius" or "fahrenheit". Defaults to
            "celsius". Only override when the user explicitly asks for
            Fahrenheit or names a US city.

    Returns:
        `{"status": "success", "city": ..., "temp": ..., "unit": ...}`, or
        `status` "error" with an `error_message` for an unknown city.
    """
    fake_db = {
        "mumbai": 33,
        "paris": 18,
        "tokyo": 24,
        "new york": 21,
    }
    temp_c = fake_db.get(city.lower())
    if temp_c is None:
        return {"status": "error", "error_message": f"No weather data for {city!r}."}
    temp = temp_c if unit == "celsius" else round(temp_c * 9 / 5 + 32, 1)
    return {"status": "success", "city": city, "temp": temp, "unit": unit}


root_agent = LlmAgent(
    name="weather_agent",
    model="gemini-3.5-flash",
    description="Reports the weather; demonstrates required and optional params.",
    instruction=(
        "Help the user get weather. "
        "The 'city' parameter is required: if the user does not name a city, ask them. "
        "Pass unit='fahrenheit' ONLY when the user explicitly asks for Fahrenheit "
        "or names a US city; otherwise leave it to default to Celsius."
    ),
    tools=[get_weather],
)
