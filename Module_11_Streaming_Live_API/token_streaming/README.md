<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Token streaming

## What this shows

A plain text agent whose answer arrives in chunks while the model generates
it, the typewriter effect of a chat UI. This is not the Live API: the prompt
goes in as one text turn over `run_async()` with
`RunConfig(streaming_mode=StreamingMode.SSE)`, on a standard Gemini model
(`gemini-3.5-flash`). Streaming is a property of the run, not the agent;
`agent.py` has nothing streaming-specific, and the **Streaming** checkbox
under More options in `adk web` switches it per request.

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)).
- Credentials in `.env` (copy `.env.example` in this folder). On Agent
  Platform (formerly Vertex AI) use `GOOGLE_CLOUD_LOCATION=global`;
  `gemini-3.5-flash` is not served from regional locations.

## Run it

1. `cd Module_11_Streaming_Live_API`
2. `adk web`
3. Open http://localhost:8000 and select `token_streaming`.
4. Open **More options** (the vertical dots, top right of the main panel),
   tick **Streaming**, then send:
   "Explain Python decorators".

Terminal alternative: `adk run token_streaming`. It prints only the final
answer, not the chunks.

## What to look for

- With Streaming ticked, the answer grows on screen in several bursts. With
  it unticked, it appears in one piece. Same agent, same prompt.
- With Streaming ticked, the dev UI calls `/run_sse` with `"streaming": true`.
  The server then yields partial events (`partial: true`), each with a text
  chunk, and one final event with the full text. A client that printed both
  would show the answer twice.
- Use this instead of the Live API when the UI is text-only and the user
  finishes typing before the model answers. For voice, interruptions or
  video, see `../minimal_live_agent/`.

## Using this from Python

```python
from google.adk.agents.run_config import RunConfig, StreamingMode

async for event in runner.run_async(
    user_id=user_id,
    session_id=session.id,
    new_message=content,
    run_config=RunConfig(streaming_mode=StreamingMode.SSE),
):
    if event.partial and event.content and event.content.parts:
        for part in event.content.parts:
            if part.text and not part.thought:
                print(part.text, end="", flush=True)
```

Print only the partial events; the final event repeats the whole text.

## Common errors

| Symptom | Cause |
|---|---|
| `404 NOT_FOUND` for `gemini-3.5-flash` on Agent Platform | `GOOGLE_CLOUD_LOCATION` is a region; set it to `global` |
| Same 404 while Live topics work | The shell sets `GOOGLE_CLOUD_LOCATION=us-central1` for the Live topics; run this topic in a separate `adk web` without that override |
