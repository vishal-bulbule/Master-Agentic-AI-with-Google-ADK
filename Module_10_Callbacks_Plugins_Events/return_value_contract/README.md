<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# The return-value contract

## What this shows

What a callback returns decides what ADK does next. Returning `None` lets the
step run; returning a value skips the step and uses your value in its place.
Guardrails, caches, mocks, and kill switches are all built on this rule, with
no change to the agent's instruction or tools. Each subfolder is a separate
agent that exercises one row of the table.

| Return | From | Effect |
|---|---|---|
| `None` | any callback | Proceed normally |
| `LlmResponse` | `before_model_callback` | Model call is skipped; your response is used |
| `dict` | `before_tool_callback` | Tool body is skipped; your dict is the tool result |
| `types.Content` | `before_agent_callback` | Agent does not run; your content is its response |
| Same types | `after_*` callbacks | Replace the result that was just produced |

| Agent folder | Callback | Result |
|---|---|---|
| `return_none/` | `before_model` returns `None` | Model answers as usual |
| `return_llmresponse/` | `before_model` returns `LlmResponse` | Fixed reply, no model call |
| `return_dict_from_tool_cb/` | `before_tool` returns `dict` | Model reports the mock 22 C reading |
| `return_content_from_agent_cb/` | `before_agent` returns `Content` | Fixed "offline" reply, no model call |

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials go
in a `.env` at the repository root or in an agent folder; each agent folder
has a `.env.example` (a Gemini API key, or Agent Platform (formerly Vertex AI)
with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_10_Callbacks_Plugins_Events/return_value_contract`
2. `adk web`
3. Open http://localhost:8000 and select `return_none` in the agent dropdown.
4. Send: `What is the weather in Pune?`
5. Repeat with `return_llmresponse`, `return_dict_from_tool_cb`, and
   `return_content_from_agent_cb`.

The callbacks print to the terminal where `adk web` is running. Terminal
alternative: `adk run return_none` (and the other three folder names).

## What to look for

- Each callback prints one `[before_...]` line saying which path it took.
- `return_dict_from_tool_cb`: the Events view shows a `get_weather` call.
  Click its result row: the response is `temp_c: 22` with the note "mock
  reading returned by before_tool callback". The real tool body would
  return 99 C.
- `return_llmresponse` and `return_content_from_agent_cb` answer instantly;
  the Traces view shows no model call.
- `return_none` may say it has no live weather data: it has no tools, and the
  model answers as usual.

## Clean up

Sessions are kept in `.adk/session.db` inside each agent folder:
`rm -rf */.adk`
