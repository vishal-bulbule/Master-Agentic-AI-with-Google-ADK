<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Three runtimes, one agent

## What this shows

One `root_agent` (a small clock agent) served three ways: `adk web`, `adk run`
and `adk api_server`. The agent code does not change; only the surface around
it does. The tool uses real time zones, so every answer is different and you
can tell the tool actually ran.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`.env.example`](.env.example): `GOOGLE_API_KEY`, or
      Agent Platform (formerly Vertex AI) with `GOOGLE_CLOUD_LOCATION=global`
      (`gemini-3.5-flash` is served from `global`).
- [ ] `curl` for the api_server part.

## Run it

`adk web`, the browser UI:

1. `cd Module_02_First_ADK_Agent`
2. `adk web` (if port 8000 is taken: `adk web --port 8001`)
3. Open http://localhost:8000 and select `three_runtimes_demo` in the agent dropdown.
4. Send: "What time is it in Tokyo?"

`adk run`, the terminal (from the same folder):

```bash
adk run three_runtimes_demo                               # interactive; type exit to quit
adk run three_runtimes_demo "What time is it in Tokyo?"   # one message, then exit
```

`adk api_server`, REST and SSE (stop `adk web` first, or use another port):

1. Terminal 1, from `Module_02_First_ADK_Agent`: `adk api_server`
2. Terminal 2:

```bash
# Create a session
curl -X POST http://localhost:8000/apps/three_runtimes_demo/users/u1/sessions \
  -H "Content-Type: application/json" -d '{"session_id": "s1"}'

# Send a message and stream the events back
curl -X POST http://localhost:8000/run_sse \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "three_runtimes_demo",
    "userId": "u1",
    "sessionId": "s1",
    "newMessage": {"role": "user", "parts": [{"text": "What time is it in Tokyo?"}]},
    "streaming": false
  }'
```

## What to look for

- `adk web`: the Events view lists the `get_current_time` call with
  `timezone: "Asia/Tokyo"`, the tool response, and the final answer, one
  numbered row each. Click a row to see its details in the side panel.
- `adk run`: no browser and no HTTP, only the final answer. Use it for quick
  checks after a code change and in scripts.
- `adk api_server`: three `data:` events: a `functionCall`, a
  `functionResponse`, and the model's text. That is the agent loop over HTTP.

| Runtime | Command | Best for |
|---|---|---|
| Web UI | `adk web` | Developing and debugging |
| CLI | `adk run three_runtimes_demo` | Quick checks, scripts |
| REST/SSE | `adk api_server` | Integrating with other applications |
