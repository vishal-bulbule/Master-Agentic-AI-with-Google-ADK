<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 01 Session anatomy

## What this shows

An ADK `Session` has four parts: `id` (the session identifier), `user_id` (who
owns it), `events` (an ordered log of user messages, model replies, tool
calls, and tool results), and `state` (a dict the agent and its tools read and
write). The session is the log plus the scratchpad. You chat with
`anatomy_agent` in the dev UI, then fetch the same session from the `adk web`
REST API and read those four fields directly.

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)) and a `.env` with your Gemini
  settings (see `anatomy_agent/.env.example`). On Agent Platform (formerly
  Vertex AI) the model `gemini-3.5-flash` needs `GOOGLE_CLOUD_LOCATION=global`.
- `curl`, for fetching the session.

## Run it

1. `cd Module_08_Sessions_State_Memory/01_session_anatomy`
2. `adk web --session_service_uri=memory:// --artifact_service_uri=memory:// --memory_service_uri=memory://`
3. Open http://localhost:8000 and select `anatomy_agent` in the agent dropdown.
4. Send: "Remember my favorite color is blue.", then "What color did I say?"

## Try it

Fetch the session you just used. The dev UI user is `user`; copy the session
id from the session dropdown in the top bar (or the `session=` part of the
URL):

```bash
curl http://127.0.0.1:8000/apps/anatomy_agent/users/user/sessions/<session-id>
```

The same flow entirely over REST, with a session id you choose:

```bash
curl -X POST http://127.0.0.1:8000/apps/anatomy_agent/users/user/sessions \
  -H 'Content-Type: application/json' -d '{"session_id": "s1"}'

curl -X POST http://127.0.0.1:8000/run -H 'Content-Type: application/json' -d '{
  "app_name": "anatomy_agent", "user_id": "user", "session_id": "s1",
  "new_message": {"role": "user", "parts": [{"text": "Remember my favorite color is blue."}]}}'

curl http://127.0.0.1:8000/apps/anatomy_agent/users/user/sessions/s1
```

`s1` then also appears in the dev UI session dropdown (reload the page).

## What to look for

The session JSON has `id`, `userId`, `events`, and `state` (plus `appName`
and `lastUpdateTime`). For the two turns above, `events` holds six entries:

```text
[0] user           "Remember my favorite color is blue."
[1] anatomy_agent  function call  save_color(color="blue")
[2] anatomy_agent  function response  {"status": "saved", "color": "blue"}
[3] anatomy_agent  "I have saved blue as your favorite color."
[4] user           "What color did I say?"
[5] anatomy_agent  "You said your favorite color is blue."
```

and `state` is `{"favorite_color": "blue"}`. Event [2] carries the
`actions.stateDelta` that produced that state. In the dev UI, the Events view
shows the same six events as numbered rows (click one to see its JSON in the
side panel) and the State tab shows `favorite_color`.
