<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Streaming tool

## What this shows

A tool that keeps producing results while the conversation continues. An
`async` function typed to return `AsyncGenerator` becomes a streaming tool in
a live session:

```python
async def watch_stock(symbol: str) -> AsyncGenerator[dict, None]:
    price = 100.0
    for tick in range(TICKS):
        price += random.uniform(-5.0, 5.0)
        yield {"status": "success", "symbol": symbol, "price": round(price, 2), "tick": tick}
        await asyncio.sleep(TICK_INTERVAL_S)
```

When the model calls it, ADK starts it as a background task and immediately
returns a "pending" function response. Each `yield` is then sent to the model
as another function response, and the model decides whether to say anything
about it. Two rules: the function must be `async`, and its return annotation
must be `AsyncGenerator[...]`. Streaming tools only run under
`runner.run_live()`, so the agent uses a Live model and you talk to it through
the `adk web` call (phone) button. `stop_streaming` is ADK's reserved tool name
for cancelling a running stream; ADK handles the call by name, and the
function body is never used.

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)).
- Chrome or Edge with microphone access, and speakers or headphones.
- A Live model: copy `.env.example` to `.env` in this folder and set
  `LIVE_MODEL` and the location for your backend. Gemini API:
  `gemini-2.5-flash-native-audio-preview-12-2025`. Agent Platform (formerly
  Vertex AI): `gemini-live-2.5-flash-native-audio` on a region such as
  `us-central1` (not `global`), with the model allowed by your organization
  policy. Details in `../minimal_live_agent/README.md`.

## Run it

1. `cd Module_11_Streaming_Live_API`
2. `adk web` (on Agent Platform: `GOOGLE_CLOUD_LOCATION=us-central1 adk web`)
3. Open http://localhost:8000 and select `streaming_tool`.
4. Click the call (phone) button in the message box, allow microphone
   access, and say: "Watch TSLA for me."

## Try it

- "Watch TSLA for me." then stay quiet for ten seconds.
- "Stop watching." (the agent should call `stop_streaming`)
- "Watch NVDA." while the first stream is still running.

## What to look for

- The session's events include one `watch_stock` function call and its
  immediate response:
  `{"status": "The function is running asynchronously and the results are pending."}`.
- The terminal running `adk web` prints a `[tool-yield]` line for each of the
  five updates, two seconds apart. The updates go from ADK straight to the
  model; the client never receives them as events. What you hear is the
  agent's reaction to them.
- The agent may stay quiet on dull ticks. Filtering what is worth saying is
  the point of letting the model watch the stream.
- Other uses: log tails, sensor readings, progress of a long job. A tool with
  an `input_stream: LiveRequestQueue` parameter receives the user's live audio
  or video frames; see the ADK docs page on live tools.

## Common errors

| Symptom | Cause |
|---|---|
| `1008 ... was not found` or `1007 ... Organization Policy` in the terminal | Live model or location problem; see `../minimal_live_agent/README.md` |
| An error when typing in the chat box | Live models only answer in a voice session; use the call (phone) button |
