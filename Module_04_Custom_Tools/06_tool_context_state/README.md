<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 06: Tool Context: State

## What this shows

Add a `tool_context: ToolContext` parameter to a tool and ADK injects the
context object when it calls the tool; the parameter is left out of the
schema the model sees. `tool_context.state` is a dict-like store whose key
prefix controls lifetime:

| Prefix | Lifetime | Example key |
|---|---|---|
| (none) | this session only | `last_topic` |
| `user:` | this user, across sessions | `user:theme` |
| `app:` | all users of the app | `app:feature_flag` |
| `temp:` | this invocation only | `temp:scratchpad` |

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`agent/.env.example`](agent/.env.example):
      `GOOGLE_API_KEY`, or Agent Platform (formerly Vertex AI) with
      `GOOGLE_CLOUD_LOCATION=global` (`gemini-3.5-flash` is served from
      `global`).

## Run it

1. `cd Module_04_Custom_Tools/06_tool_context_state`
2. `adk web`
3. Open http://localhost:8000 and pick `agent` in the app dropdown in the top bar.
4. Send: "Set my theme to dark."

Terminal alternative: `adk run agent`.

## Try it

1. Session 1: "Set my theme to dark.", then "Remember that we were talking
   about ADK custom tools."
2. Start a new session (same user) and send: "What theme do I have saved?"

## What to look for

- State tab after session 1: `user:theme = dark` and `last_topic`.
- State tab in session 2: `user:theme` is there, `last_topic` is not, and
  the agent reads the saved theme with `get_theme`.
- Events view: click a tool result row; each write appears in its
  `actions.stateDelta` in the side panel.

By default `adk web` stores sessions in `agent/.adk/session.db`, so
`user:` state also survives a restart. Start it with
`adk web --session_service_uri=memory://` to keep everything in memory and
lose it on exit. Module 8 covers session services in depth.

## Clean up

```bash
rm -rf Module_04_Custom_Tools/06_tool_context_state/agent/.adk
```
