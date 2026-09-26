# Author: Vishal Bulbule
# Date: 2026-09-22

"""One agent served by three runtimes: `adk web`, `adk run` and `adk api_server`.

Nothing in this file is specific to a runtime. The same `root_agent` is loaded
by the browser UI, the terminal REPL and the REST/SSE server; only the surface
around it changes.

The tool uses real time zones through `zoneinfo`, so the answer changes on
every run and you can tell the tool actually ran.
"""

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from google.adk.agents import LlmAgent


def get_current_time(timezone: str = "UTC") -> dict:
    """Returns the current time in the requested IANA timezone.

    Args:
        timezone: IANA timezone such as "Asia/Kolkata" or "UTC".

    Returns:
        dict with `status` and either `time` (ISO 8601 string) or
        `error_message` when the timezone is invalid.
    """
    try:
        tz = ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError):
        return {
            "status": "invalid_timezone",
            "error_message": f"'{timezone}' is not a valid IANA timezone.",
        }
    now = datetime.now(tz)
    return {
        "status": "success",
        "timezone": timezone,
        "time": now.isoformat(timespec="seconds"),
    }


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="three_runtimes_demo",
    description="A small clock agent used to compare the three ADK runtimes.",
    instruction=(
        "You tell the user the current time in any timezone they ask for. "
        "Always call get_current_time(timezone) with a valid IANA name "
        "(for example 'Asia/Kolkata', 'America/New_York', 'UTC'). "
        "If the user gives a city, map it to the most likely IANA timezone."
    ),
    tools=[get_current_time],
)
