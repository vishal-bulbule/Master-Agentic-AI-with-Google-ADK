# Author: Vishal Bulbule
# Date: 2026-09-22

"""Function calling by hand: the primitive that ADK automates.

The SDK can run tools for you (see function_calling_gcs.py). Here automatic
function calling is turned off so every step is visible:

  1. The model sees the tool declaration and returns a `function_call` part
     with the name and arguments it chose. It does not run anything.
  2. Your code runs the function.
  3. Your code sends the result back as a `function_response` part.
  4. The model writes the final answer from that result.

An ADK agent runs exactly this loop for you, as many rounds as needed.
"""

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

MODEL = "gemini-3.5-flash"


def get_weather(city: str) -> dict:
    """Returns current weather for a city.

    Args:
        city: City name, for example "Mumbai".

    Returns:
        dict with `status` and either `temp_c` and `condition`, or `error_message`.
    """
    fake_db = {
        "paris": {"temp_c": 18, "condition": "cloudy"},
        "mumbai": {"temp_c": 33, "condition": "humid"},
        "tokyo": {"temp_c": 24, "condition": "clear"},
    }
    if city.lower() in fake_db:
        return {"status": "success", **fake_db[city.lower()]}
    return {"status": "error", "error_message": f"No weather data for {city}."}


config = types.GenerateContentConfig(
    tools=[get_weather],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)

history = [types.Content(role="user", parts=[types.Part(text="What's the weather in Mumbai?")])]

# Step 1: the model decides to call the tool and returns structured arguments.
response = client.models.generate_content(model=MODEL, contents=history, config=config)
call = response.function_calls[0]
print(f"Model requested: {call.name}({dict(call.args)})")

# Step 2: our code runs the function. The model never executes code itself.
result = get_weather(**call.args)
print(f"Tool returned  : {result}")

# Step 3: send the model's turn and the tool result back. Keeping the model's
# own content (not a rebuilt copy) preserves its thought signature, which
# Gemini 3.x requires on multi-turn function calling.
history.append(response.candidates[0].content)
history.append(
    types.Content(
        role="user",
        parts=[types.Part.from_function_response(name=call.name, response=result)],
    )
)

# Step 4: the model turns the tool result into the final answer.
final = client.models.generate_content(model=MODEL, contents=history, config=config)
print(f"Final answer   : {final.text}")
