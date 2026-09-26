# Author: Vishal Bulbule
# Date: 2026-09-22

"""Time-lookup agent used to demonstrate OpenTelemetry traces.

Nothing in this file is tracing-specific. ADK emits spans for the agent run,
each model call, and each tool call on its own; `adk web` shows them in the
Traces view, and `--trace_to_cloud` sends them to Cloud Trace. Tracing is
wiring, not a code change in the agent.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import LlmAgent

_TZ = {
    "london": "Europe/London",
    "new york": "America/New_York",
    "tokyo": "Asia/Tokyo",
    "bengaluru": "Asia/Kolkata",
    "pune": "Asia/Kolkata",
}


def get_time(city: str) -> dict:
    """Returns the current local time in a city.

    Args:
        city: City name (case-insensitive), for example "Tokyo".

    Returns:
        Dict with `status` (`success` or `not_found`) and either `city`,
        `time_iso`, and `human`, or `error_message`.
    """
    tz_name = _TZ.get(city.lower())
    if tz_name is None:
        return {"status": "not_found", "error_message": f"No timezone on file for '{city}'."}
    now = datetime.now(ZoneInfo(tz_name))
    return {
        "status": "success",
        "city": city.title(),
        "time_iso": now.isoformat(timespec="seconds"),
        "human": now.strftime("%a %d %b %Y, %H:%M %Z"),
    }


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="traced_agent",
    description="Tells the time in a city. Used to demonstrate OpenTelemetry traces.",
    instruction=(
        "When the user asks for the time in a city, call get_time(city) and reply with "
        "the `human` field verbatim. If status is not_found, say so politely."
    ),
    tools=[get_time],
)
