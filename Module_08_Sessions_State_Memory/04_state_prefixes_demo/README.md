<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 04 State prefixes

## What this shows

A prefix on a state key sets its scope and whether it is persisted. The agent
has one tool per scope; each tool returns a snapshot of the state it can see,
so you can compare that with what the session service stores.
`SqliteSessionService` (`sqlite:///./sessions.db`) keeps `app:` and `user:`
keys in their own tables, which is what makes them appear in every session of
the app or the user.

| Prefix | Scope | Persisted by a database service | Persisted by InMemory |
|---|---|---|---|
| (none) | this session | yes | until the process stops |
| `user:` | every session of this `user_id` in this app | yes | until the process stops |
| `app:` | every user and session of this app | yes | until the process stops |
| `temp:` | the current invocation (one turn) | never | never |

```python
state["cart"] = [...]           # this session
state["user:name"] = "Vishal"   # follows the user across sessions
state["app:flag"] = True        # shared by the whole app
state["temp:token"] = "xyz"     # dropped when the turn ends
```

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)) and a `.env` with your Gemini
  settings (see `prefix_agent/.env.example`; on Agent Platform use
  `GOOGLE_CLOUD_LOCATION=global`).
- `curl`, for creating sessions as other users.

## Run it

1. `cd Module_08_Sessions_State_Memory/04_state_prefixes_demo`
2. `adk web --session_service_uri=sqlite:///./sessions.db --artifact_service_uri=memory:// --memory_service_uri=memory://`
3. Open http://localhost:8000 and select `prefix_agent` in the agent dropdown.
4. Send, one at a time:
   1. "Set the app feature flag to true."
   2. "Set my user name to Vishal."
   3. "Add book to my cart."
   4. "Set a temporary token to abc123."

## Try it

Compare sessions (the dev UI user is `user`):

```bash
# a new session, same user
curl -X POST http://127.0.0.1:8000/apps/prefix_agent/users/user/sessions
# a new session, different user
curl -X POST http://127.0.0.1:8000/apps/prefix_agent/users/someone-else/sessions
```

Or click **New Session** in the dev UI and open the State tab.

## What to look for

- The tool response in step 4 (click its row in the Events view) includes
  `temp:token`; the State tab after the turn does not.
- The new session for the same user already has `app:flag` and `user:name`,
  but no `cart`.
- The session for a different user has only `app:flag`.

## Clean up

```bash
rm sessions.db
```
