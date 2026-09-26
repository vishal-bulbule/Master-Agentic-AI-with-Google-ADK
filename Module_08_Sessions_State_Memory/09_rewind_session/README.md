<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 09 Rewind a session

## What this shows

`Runner.rewind_async` rolls a session back to the point before a given
invocation (one user turn). It appends a rewind event that restores session
state and artifacts to what they were then. Earlier events stay in the log,
so the history remains auditable. Rewind restores session-level state and
artifacts only: `app:` and `user:` state, and anything a tool changed outside
ADK (a database row, a sent email), are not rolled back.

The agent sets `state["color"]` on every turn, so each invocation leaves a
visible change. The dev UI and the `adk web` REST API have no rewind action,
so rewind itself is shown as Python below.

## Prerequisites

Repository setup ([SETUP.md](../../SETUP.md)) and a `.env` with your Gemini
settings (see `rewind_agent/.env.example`; on Agent Platform use
`GOOGLE_CLOUD_LOCATION=global`).

## Run it

1. `cd Module_08_Sessions_State_Memory/09_rewind_session`
2. `adk web --session_service_uri=memory:// --artifact_service_uri=memory:// --memory_service_uri=memory://`
3. Open http://localhost:8000 and select `rewind_agent` in the agent dropdown.
4. Send: "Set the color to red.", then "Set the color to green.", then
   "Set the color to blue."

## What to look for

- Each turn is one invocation. In the Events view, click any row: the raw
  JSON view in the side panel shows its `invocationId`, and the three turns
  have three different IDs.
- The State tab shows `color` changing red, green, blue. These are the
  points a rewind can return to.

## Using this from Python

To rewind to before the "green" turn, pass that turn's invocation ID to
`rewind_async`. Run this from this folder (so `rewind_agent` is importable)
with your `.env` loaded:

```python
import asyncio

from google.adk.runners import InMemoryRunner
from google.genai import types

from rewind_agent.agent import root_agent


async def main() -> None:
    runner = InMemoryRunner(agent=root_agent, app_name="rewind_agent")
    session = await runner.session_service.create_session(app_name="rewind_agent", user_id="u1")

    invocation_ids = {}
    for color in ("red", "green", "blue"):
        message = types.Content(role="user", parts=[types.Part(text=f"Set the color to {color}.")])
        async for event in runner.run_async(user_id="u1", session_id=session.id, new_message=message):
            invocation_ids[color] = event.invocation_id

    # Undo the "green" turn and everything after it.
    await runner.rewind_async(
        user_id="u1", session_id=session.id, rewind_before_invocation_id=invocation_ids["green"]
    )
    session = await runner.session_service.get_session(
        app_name="rewind_agent", user_id="u1", session_id=session.id
    )
    print(session.state)  # {'color': 'red'}
    await runner.close()


asyncio.run(main())
```

Rewinding to before the green turn undoes both the green and the blue
changes, because both came after that point.
