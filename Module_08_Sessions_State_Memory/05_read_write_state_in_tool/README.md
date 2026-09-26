<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 05 Read and write state inside a tool

## What this shows

A tool that declares a `tool_context: ToolContext` parameter gets the session
state as `tool_context.state`. Read and write it like a dict; ADK records each
write as a state delta on the tool's event and the session service persists
it. The key here uses the `user:` prefix, so the color belongs to the user,
not to one session, and sessions are stored in SQLite so it also survives a
restart.

```python
def remember_color(color: str, tool_context: ToolContext) -> dict:
    tool_context.state["user:favorite_color"] = color
    return {"status": "saved", "color": color}

def recall_color(tool_context: ToolContext) -> dict:
    return {"status": "ok", "color": tool_context.state.get("user:favorite_color", "unknown")}
```

## Prerequisites

Repository setup ([SETUP.md](../../SETUP.md)) and a `.env` with your Gemini
settings (see `color_agent/.env.example`; on Agent Platform use
`GOOGLE_CLOUD_LOCATION=global`).

## Run it

1. `cd Module_08_Sessions_State_Memory/05_read_write_state_in_tool`
2. `adk web --session_service_uri=sqlite:///./sessions.db --artifact_service_uri=memory:// --memory_service_uri=memory://`
3. Open http://localhost:8000 and select `color_agent` in the agent dropdown.
4. Send: "Remember my favorite color is turquoise."

## Try it

1. Click **New Session** (same user).
2. Ask: "What is my favorite color?"

## What to look for

- The new session has no events, but its State tab already shows
  `user:favorite_color: turquoise`.
- The agent calls `recall_color` and answers turquoise.

## Clean up

```bash
rm sessions.db
```
