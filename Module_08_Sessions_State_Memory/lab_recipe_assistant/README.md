<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Lab: recipe assistant (sessions, state, and memory)

## What this shows

A recipe assistant that uses all three layers from this module:

1. **Persistent sessions.** `adk web` stores sessions in SQLite
   (`SqliteSessionService`). On Google Cloud, swap in a managed session
   service with a different `--session_service_uri`; the agent does not change.
2. **User-scoped preference.** `set_dietary` writes `user:dietary`, which
   follows the user into every new session. The instruction reads it with
   `{user:dietary?}`, so every prompt respects it without a tool call.
3. **Session-scoped cart.** `add_recipe`, `view_cart`, and `clear_cart` use
   `cart` (no prefix), which belongs to one session.
4. **Memory.** After a session, `PATCH .../memory` copies it into the memory
   service. The built-in `load_memory` tool lets the agent search it for
   things that were said but never written to state, such as a favorite
   cuisine. The local memory service matches keywords, so the instruction
   asks the model for plain-word queries.

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)) and a `.env` with your Gemini
  settings (see `recipe_agent/.env.example`; on Agent Platform use
  `GOOGLE_CLOUD_LOCATION=global`).
- `curl`, for adding a session to memory.

## Run it

1. `cd Module_08_Sessions_State_Memory/lab_recipe_assistant`
2. `adk web --session_service_uri=sqlite:///./sessions.db --artifact_service_uri=memory:// --memory_service_uri=memory://`
3. Open http://localhost:8000 and select `recipe_agent` in the agent dropdown.
4. Send: "I am vegetarian. Remember that. I also love South Indian food."

## Try it

Session 1:

- "I am vegetarian. Remember that. I also love South Indian food."
- "Add Paneer Tikka to my cart."
- "What is in my cart?"

Copy session 1 into memory (replace `<session-id>`; the dev UI user is
`user`):

```bash
curl -X PATCH http://127.0.0.1:8000/apps/recipe_agent/users/user/memory \
  -H 'Content-Type: application/json' -d '{"session_id": "<session-id>"}'
```

Session 2 (**New Session**, same `adk web` run):

- Check the State tab first.
- "Suggest one recipe I would enjoy tonight."

## What to look for

- Session 2 starts with no events, `user:dietary: vegetarian` already in
  state, and no `cart`.
- The agent calls `load_memory`, the response contains "South Indian food"
  from session 1, and it suggests a vegetarian South Indian dish.
- Restart `adk web` and open a new session: `user:dietary` is still there
  (SQLite), but memory is empty (in process). A managed memory service such
  as Memory Bank (`--memory_service_uri=agentengine://...`) removes that gap.

## Clean up

```bash
rm sessions.db
```
