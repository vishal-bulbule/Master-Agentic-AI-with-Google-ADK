<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 02 InMemorySessionService

## What this shows

`InMemorySessionService` keeps sessions in a Python dict inside the server
process. It suits local development and tests. Every session is lost when the
process stops, so it is not for anything a user relies on. You select it with
`--session_service_uri=memory://`. In ADK 2.x, `adk web` and `adk run` default
to a per-agent SQLite file under `<agent>/.adk/` when no URI is given, so "no
URI" no longer means in-memory.

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)) and a `.env` with your Gemini
  settings (see `inmemory_agent/.env.example`; on Agent Platform use
  `GOOGLE_CLOUD_LOCATION=global`).
- `curl`, for listing sessions after the restart.

## Run it

1. `cd Module_08_Sessions_State_Memory/02_inmemory_session`
2. `adk web --session_service_uri=memory:// --artifact_service_uri=memory:// --memory_service_uri=memory://`
3. Open http://localhost:8000 and select `inmemory_agent` in the agent dropdown.
4. Send: "I'd like an espresso.", then "Make that a double."

## Try it

1. After the two messages, check the State tab.
2. Stop `adk web` with Ctrl+C and start it again with the same command.
3. List the sessions (the dev UI user is `user`):

   ```bash
   curl http://127.0.0.1:8000/apps/inmemory_agent/users/user/sessions
   ```

## What to look for

- Two `place_order` calls in the Events view; `state["order"]` goes from
  `espresso` to `double espresso`.
- After the restart the sessions list is `[]`, and the dev UI session
  dropdown is empty.
- Run plain `adk web` (no URIs) and repeat: the session survives, because
  it went to `inmemory_agent/.adk/session.db`.

## Clean up

`rm -rf inmemory_agent/.adk` if you ran `adk web` without the URIs.
