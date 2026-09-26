<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Six hook points

## What this shows

One agent with all six callbacks attached. Each callback prints a line and
returns `None`, so it observes the run without changing it, and the printed
lines show the order in which ADK calls the hooks.

| Hook | Fires |
|---|---|
| `before_agent_callback` | Before the agent handles the request |
| `after_agent_callback` | After the agent produces its final response |
| `before_model_callback` | Before each model call |
| `after_model_callback` | After each model response |
| `before_tool_callback` | Before each tool call |
| `after_tool_callback` | After each tool call |

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials go in a `.env` at the repository root or in the agent folder; `.env.example` in this folder lists the variables (a Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_10_Callbacks_Plugins_Events`
2. `adk web`
3. Open http://localhost:8000 and select `six_hook_points` in the agent dropdown.
4. Send: `What time is it in UTC?`

The callbacks print to the terminal where `adk web` is running; keep it visible.
Terminal alternative: `adk run six_hook_points` prints the same lines inline with the chat.

## What to look for

In the terminal:

```
hook: before_agent (agent=six_hooks_agent)
hook: before_model
hook: after_model
hook: before_tool (tool=get_time, args={'timezone': 'UTC'})
hook: after_tool (tool=get_time)
hook: before_model
hook: after_model
hook: after_agent (agent=six_hooks_agent)
```

- The model is called twice: the first call returns the tool call, the second
  writes the answer from the tool result. Model hooks fire once per call. The
  Events view shows the matching `get_time` call and response.
- Send `hi`: the tool hooks and the second model call do not happen.
- With `adk run`, `after_agent` prints after the answer, because the final
  event is shown as soon as it arrives and the agent finishes after that.

## Clean up

`adk web` and `adk run` keep sessions in `six_hook_points/.adk/session.db`. Delete it to start clean: `rm -rf six_hook_points/.adk`
