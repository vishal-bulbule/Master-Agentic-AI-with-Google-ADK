<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 06 State inside the instruction

## What this shows

ADK replaces `{key}` placeholders in an `LlmAgent` instruction with values
from session state before the prompt reaches the model. A `?` suffix makes the
key optional: if it is missing, the placeholder becomes an empty string
instead of raising an error. Compared with a `recall_name` tool, this costs no
extra model round trip and the value is present on every turn. A common
pattern: tools write state, the instruction reads it.

```python
instruction="You are a friendly greeter. The user's name is {user_name?}. ..."
```

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)) and a `.env` with your Gemini
  settings (see `greeter_agent/.env.example`; on Agent Platform use
  `GOOGLE_CLOUD_LOCATION=global`).
- `curl`, for creating a session that already has state.

## Run it

1. `cd Module_08_Sessions_State_Memory/06_state_in_instruction`
2. `adk web --session_service_uri=memory:// --artifact_service_uri=memory:// --memory_service_uri=memory://`
3. Open http://localhost:8000 and select `greeter_agent` in the agent dropdown.
4. Send: "Greet me." You get a generic greeting: no `user_name` in state.

## Try it

Create a session with `user_name` already in state, for the dev UI user
`user`:

```bash
curl -X POST http://127.0.0.1:8000/apps/greeter_agent/users/user/sessions \
  -H 'Content-Type: application/json' \
  -d '{"session_id": "named", "state": {"user_name": "Vishal"}}'
```

Reload the dev UI, pick session `named` in the session dropdown (top bar),
and send
"Greet me." again.

## What to look for

- Session `named`: the reply uses the name, for example "Hello Vishal!".
- The first session: a generic greeting, and no error, because of the `?`.
- In the Events view, click the model reply row and open the side panel's
  Request view: the system instruction contains "The user's name is
  Vishal." in the `named` session.
