# Author: Vishal Bulbule
# Date: 2026-09-22

"""The agent loop made visible: every step printed as it happens.

Three callbacks and one print inside each tool write a line to the terminal
that runs `adk web` (or `adk run`) at each step of the loop:

  1. Reasoning: the model reads the prompt and history (no output)
  2. Selection: the model emits a function_call ("[MODEL] selected")
  3. Invocation: ADK runs the tool function ("TOOL  >>")
  4. Observation: the tool result goes back to the model ("[OBS  ]")
  5. Finalization: the model writes the user-facing answer ("[FINAL]")

The callbacks only print and return None, so they do not change what the
agent does. The same steps appear as numbered rows in the `adk web` Events
view.
"""

from datetime import datetime
from typing import Any, Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.adk.tools import BaseTool, ToolContext


def _log_call(tool_name: str, **kwargs) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    args_str = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
    print(f"[{ts}] TOOL  >> {tool_name}({args_str})")


def get_attractions(city: str) -> dict:
    """Returns top attractions for a city.

    Args:
        city: City name such as "Tokyo".

    Returns:
        dict with `status` and either `attractions` (a list) or `error_message`.
    """
    _log_call("get_attractions", city=city)
    db = {
        "tokyo": ["Senso-ji Temple", "Shibuya Crossing", "Tsukiji Outer Market"],
        "paris": ["Louvre", "Eiffel Tower", "Montmartre"],
        "mumbai": ["Gateway of India", "Marine Drive", "Elephanta Caves"],
    }
    attractions = db.get(city.lower())
    if attractions:
        return {"status": "success", "city": city, "attractions": attractions}
    return {"status": "error", "error_message": f"No attractions for {city}."}


def get_food_recommendation(city: str) -> dict:
    """Returns a famous food for a city.

    Args:
        city: City name such as "Tokyo".

    Returns:
        dict with `status` and either `must_try` or `error_message`.
    """
    _log_call("get_food_recommendation", city=city)
    db = {
        "tokyo": "Tsukemen noodles at Rokurinsha",
        "paris": "Croissant at Du Pain et des Idees",
        "mumbai": "Vada pav at Ashok Vada Pav",
    }
    food = db.get(city.lower())
    if food:
        return {"status": "success", "city": city, "must_try": food}
    return {"status": "error", "error_message": f"No food data for {city}."}


def _print_user_message(callback_context: CallbackContext) -> None:
    """Prints the user message that starts this invocation."""
    content = callback_context.user_content
    if content and content.parts:
        text = "".join(p.text or "" for p in content.parts)
        print(f"\n[USER ] {text}\n")


def _print_model_step(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Prints each function call the model selected, or its final text."""
    # With streaming on, partial chunks also reach this callback; print only
    # the final, complete response.
    if llm_response.partial or not llm_response.content or not llm_response.content.parts:
        return None
    for part in llm_response.content.parts:
        if part.function_call:
            fc = part.function_call
            print(f"[MODEL] selected -> {fc.name}({dict(fc.args or {})})")
        elif part.text and not part.thought:
            print(f"\n[FINAL] {part.text}\n")
    return None


def _print_observation(
    tool: BaseTool, args: dict[str, Any], tool_context: ToolContext, tool_response: dict
) -> Optional[dict]:
    """Prints the tool result that goes back to the model."""
    print(f"[OBS  ] {tool.name} returned {tool_response}")
    return None


root_agent = LlmAgent(
    name="loop_trace_agent",
    model="gemini-3.5-flash",
    description="Trip planner that visibly logs every tool invocation.",
    instruction=(
        "You are a trip planner. For any city the user mentions, call BOTH "
        "`get_attractions` and `get_food_recommendation`. Then write a short "
        "one-paragraph itinerary using the results. Always use the tools; "
        "never answer from memory."
    ),
    tools=[get_attractions, get_food_recommendation],
    before_agent_callback=_print_user_message,
    after_model_callback=_print_model_step,
    after_tool_callback=_print_observation,
)
