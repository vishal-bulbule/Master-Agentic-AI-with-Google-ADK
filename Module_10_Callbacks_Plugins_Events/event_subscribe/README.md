<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Event stream

## What this shows

Every step of an ADK run is recorded as an `Event`: model text, tool calls,
tool results, state changes, agent transfers. The dev UI's Events view is a
view of that stream, and in your own code `runner.run_async` yields the same
events in order as they happen, which is how you drive a live UI, emit traces,
or debug a run without callbacks. The agent here is a plain weather agent; the
tool is there so one turn produces a function call, a function response, and
a final answer. An `Event` has no single type field, so you classify it from
what is set:

| Check | Meaning |
|---|---|
| `event.get_function_calls()` | The model asked for a tool call |
| `event.get_function_responses()` | A tool returned a result |
| `event.actions.transfer_to_agent` | Control moved to another agent |
| `event.actions.state_delta` | The event changed session state |
| `event.is_final_response()` | The agent's answer for this turn |
| `event.partial` | A streaming chunk (only with streaming on) |

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials go in a `.env` at the repository root or in the agent folder; `.env.example` in this folder lists the variables (a Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_10_Callbacks_Plugins_Events`
2. `adk web`
3. Open http://localhost:8000 and select `event_subscribe` in the agent dropdown.
4. Send: `What's the weather in Pune?`

Terminal alternative: `adk run event_subscribe`.

## What to look for

- Events view: three numbered rows for the turn, `get_weather` function call,
  function response, and the final text. Click one and open the raw JSON view
  in the side panel: `author`, `content.parts`, `actions`, `invocation_id`.
- The function response is authored by the agent (`event_demo_agent`), not by
  the tool.
- Only the last event is a final response. A UI that shows only final
  responses hides tool activity; one that shows everything gives a live trace.

## Using this from Python

Iterating the runner's events yourself looks like this. Save it as a script
in `Module_10_Callbacks_Plugins_Events/` (so `event_subscribe` is importable)
and run it with `python`. The user's message is saved to the session as an
event too, but `run_async` does not yield it back to you.

```python
import asyncio

from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai import types

load_dotenv()

from event_subscribe.agent import root_agent  # noqa: E402

async def main() -> None:
    runner = InMemoryRunner(agent=root_agent, app_name="event_subscribe")
    session = await runner.session_service.create_session(
        app_name="event_subscribe", user_id="u1"
    )
    message = types.Content(
        role="user", parts=[types.Part(text="What's the weather in Pune?")]
    )
    async for event in runner.run_async(
        user_id="u1", session_id=session.id, new_message=message
    ):
        if event.get_function_calls():
            print("function_call    ", event.get_function_calls()[0].name)
        elif event.get_function_responses():
            print("function_response", event.get_function_responses()[0].response)
        elif event.is_final_response():
            print("final_response   ", event.content.parts[0].text)

asyncio.run(main())
```

## Clean up

`adk web` and `adk run` keep sessions in `event_subscribe/.adk/session.db`. Delete it to start clean: `rm -rf event_subscribe/.adk`
