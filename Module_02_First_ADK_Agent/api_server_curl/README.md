<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Calling an agent over HTTP

## What this shows

`adk api_server` serves every agent folder under the directory it starts in as
a REST and SSE service. Every client uses the same two calls:

1. `POST /apps/{app}/users/{user}/sessions` creates a session.
2. `POST /run_sse` sends a message and streams the agent's events back.

The demo script runs them against `weather_jokes_agent`, so the output
includes real tool calls.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials in a `.env` at the repository root (see
      [`../weather_jokes_agent/.env.example`](../weather_jokes_agent/.env.example)).
      For Agent Platform (formerly Vertex AI) set
      `GOOGLE_CLOUD_LOCATION=global`.
- [ ] `bash` and `curl`.
- [ ] Port 8000 free (or set `ADK_HOST` to where the server runs).

## Run it

1. Terminal 1: `cd Module_02_First_ADK_Agent`, then `adk api_server`
2. Terminal 2: `cd Module_02_First_ADK_Agent/api_server_curl`, then `./run_demo.sh`

The script lists the apps, creates a new session, sends "What is the weather
in Tokyo?" and "Tell me a joke." to `/run_sse`, prints both event streams,
and prints the final session. Set `ADK_HOST` if the server is not on
`http://localhost:8000`. Stop the server with Ctrl+C when you are done.

## What to look for

Abridged output for the weather question:

```text
data: {"content":{"parts":[{"functionCall":{"id":"call_...","args":{"city":"Tokyo"},"name":"get_weather"}}],"role":"model"}, ...}
data: {"content":{"parts":[{"functionResponse":{"id":"call_...","name":"get_weather","response":{"status":"success","report":"The weather in Tokyo is mild with scattered clouds, around 22 degrees C."}}}],"role":"user"}, ...}
data: {"content":{"parts":[{"text":"The weather in Tokyo is mild with scattered clouds, around 22 degrees C."}],"role":"model"}, ...}
```

Each `data:` line is one event: the function call the model emits, the
function response ADK records after running your tool, and the final model
text. The `thoughtSignature` fields on model parts are opaque tokens Gemini
uses to keep its reasoning across turns; clients pass them through unchanged.

## Useful endpoints

| Method | Path | Use |
|---|---|---|
| `GET` | `/list-apps` | Which agents ADK discovered |
| `POST` | `/apps/{app}/users/{u}/sessions` | Create a session; body `{"session_id": ..., "state": {...}}`, both optional |
| `PATCH` | `/apps/{app}/users/{u}/sessions/{s}` | Change session state without running the agent: `{"state_delta": {...}}` |
| `GET` | `/apps/{app}/users/{u}/sessions/{s}` | Read the full session (events and state) |
| `POST` | `/run` | Send a message, get all events in one JSON array |
| `POST` | `/run_sse` | Send a message, receive events as Server-Sent Events |
| `GET` | `/docs` | Swagger UI for every endpoint |

## Common errors

| Symptom | Fix |
|---|---|
| `Connection refused` | Start `adk api_server` in the other terminal first. |
| `Session already exists` | The script uses a new session ID on every run; if you call the API by hand, change the ID. |
| `404` or app not found | Start `adk api_server` from `Module_02_First_ADK_Agent/`, not from a subfolder. Check `/list-apps`. |
