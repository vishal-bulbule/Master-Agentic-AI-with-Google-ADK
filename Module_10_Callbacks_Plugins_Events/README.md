<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Module 10: Callbacks, Plugins, Skills, and Events

Every ADK run passes through fixed hook points. A callback installed at a hook
can observe the step, change its input, or skip it and supply its own result.
That one mechanism covers guardrails, caches, cost meters, and audit logs
without changing the agent's instruction or tools. Plugins package callbacks
for a whole App, skills load task instructions on demand, and the event stream
shows everything that happened.

## Before you start

- The repository setup in [SETUP.md](../SETUP.md): the Python environment from
  `requirements.txt` and credentials in a `.env` (a Gemini API key, or Agent
  Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`).
- Nothing else: no extra packages, tools, keys, or cloud resources. All tools
  in this module return canned data.

## Topics

Work through them in this order:

| # | Folder | What it shows |
|---|---|---|
| 1 | `six_hook_points/` | All six callbacks on one agent and the order they fire in |
| 2 | `return_value_contract/` | Four small agents, one per return path (None, LlmResponse, dict, Content) |
| 3 | `observability_callback/` | `before_model` that logs each call and returns None |
| 4 | `guardrail_pii/` | `before_model` that refuses requests containing an email or phone number |
| 5 | `cache_lookup/` | `before_model` and `after_model` pair that serves repeated questions from a cache |
| 6 | `token_budget_killswitch/` | Per-session token cap enforced in `before_model` |
| 7 | `profanity_filter/` | `after_model` that rewrites forbidden words in the reply |
| 8 | `cost_logger/` | `after_tool` that meters each tool call |
| 9 | `plugin_pattern/` | `GuardrailPlugin` registered on an `App`, covering every agent in it |
| 10 | `skills_agent/` | `SkillToolset` with one skill from disk and one defined in code |
| 11 | `event_subscribe/` | The event stream in the dev UI's Events view, plus a short `run_async` loop in the README |
| Lab | `lab_guardrail_stack/` | Customer-service agent with four callbacks, driven by four prompts |

## The six hook points

| Hook | Fires |
|---|---|
| `before_agent_callback` | Before the agent handles the request |
| `after_agent_callback` | After the agent produces its final response |
| `before_model_callback` | Before each model call |
| `after_model_callback` | After each model response |
| `before_tool_callback` | Before each tool call |
| `after_tool_callback` | After each tool call |

## The return-value contract

| Return | From | Effect |
|---|---|---|
| `None` | any callback | Proceed normally |
| `LlmResponse` | `before_model_callback` | Skip the model call and use this response |
| `dict` | `before_tool_callback` | Skip the tool and use this as its result |
| `types.Content` | `before_agent_callback` | Skip the agent and use this as its response |
| Same types | `after_*` callbacks | Replace what was just produced |

## Run it

Every agent in this module is a folder directly under
`Module_10_Callbacks_Plugins_Events/`, except the four agents in
`return_value_contract/`, which run from that subfolder.

```bash
cd Module_10_Callbacks_Plugins_Events
adk web                      # dev UI at http://localhost:8000, pick any agent
adk run six_hook_points      # terminal chat with one agent
```

Callbacks in these samples `print` what they did. The lines appear in the
terminal running `adk web` (or inline with `adk run`), so keep it visible. The
dev UI shows the rest: the Events and Traces views in the main panel, and
the State tab in the side panel. Sessions are kept in
`<agent>/.adk/session.db`; delete that folder to start clean.

## Common errors

- `Invalid app name '01_...': must start with a letter`: ADK 2.x uses the
  agent folder name as the app name, and app names must start with a letter.
  That is why the folders here have no numeric prefix.
- A callback never fires: check the parameter names. ADK calls callbacks with
  keyword arguments (`callback_context`, `llm_request`, `llm_response`,
  `tool`, `args`, `tool_context`, `tool_response`), so a renamed parameter
  raises a `TypeError`.
