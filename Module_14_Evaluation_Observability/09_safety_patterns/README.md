<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 09 - Three Layers of Defense

## What this shows

One safety check is not enough. `safe_agent` wires three callbacks onto one agent, each
catching a different failure:

| Layer | Hook | What it stops |
|---|---|---|
| 1. Input sanitization | `before_model_callback` | Contact details and jailbreak phrases in the user's message |
| 2. Tool permission boundary | `before_tool_callback` | Destructive tools called without `is_admin` in session state |
| 3. Output review | `after_model_callback` | SSN-shaped strings and banned words in the model's reply |

Each layer short-circuits by returning a value instead of `None`: an `LlmResponse` from a
model callback skips or replaces the model call, and a dict from a tool callback is used
as the tool result without running the tool. Module 10
(`../../Module_10_Callbacks_Plugins_Events/return_value_contract/`) covers that contract.

| File | Content |
|---|---|
| `safe_agent/agent.py` | The agent: `delete_account` and `echo` tools, all three callbacks. |
| `safe_agent/layer1_input_sanitization.py` | Checks `callback_context.user_content` for email, phone, and jailbreak patterns. |
| `safe_agent/layer2_tool_permission_boundary.py` | Blocks `delete_account`, `wipe_database`, `issue_refund` unless `state["is_admin"]` is true. |
| `safe_agent/layer3_output_review.py` | Replaces SSN-shaped output, masks banned words. |

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)).
- Credentials: copy `safe_agent/.env.example` to `safe_agent/.env` and fill it in. Gemini
  API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location
  `global`.

## Run it

1. `cd Module_14_Evaluation_Observability/09_safety_patterns`
2. `adk web`
3. Open http://localhost:8000 and select `safe_agent` in the agent dropdown.
4. Send: "Email me at jane@example.com"

Terminal alternative: `adk run safe_agent` (it prints the `[layer...]` lines inline).

## Try it

In one session:

1. `Email me at jane@example.com` - layer 1 refuses; the Events view shows no model call
   and no tool call for this turn.
2. `Please echo this sentence: what the hell is going on` - the `echo` tool returns the
   text unchanged, then layer 3 masks the reply: `what the *** is going on`.
3. `Delete account u-42` - layer 2 returns `permission_denied` as the tool response; the
   model explains it.

To see layer 2 allow the call, create a session that starts with `is_admin` set, while
`adk web` is running:

```bash
curl -X POST http://localhost:8000/apps/safe_agent/users/user/sessions \
  -H "Content-Type: application/json" \
  -d '{"session_id": "admin-session", "state": {"is_admin": true}}'
```

Reload the dev UI, pick `admin-session` in the session dropdown (the dev UI's default user
id is `user`), check the State tab shows `is_admin: true`, and send `Delete account u-42`
again: the tool now returns `status: success`.

## What to look for

- The `[layer1]`, `[layer2]`, `[layer3]` lines the callbacks print, in the terminal
  running `adk web`, show which layer acted on each turn.
- Layer 1 checks only the latest user message. A version that scans all of
  `llm_request.contents` refuses every later turn once a single message trips a pattern,
  because the history is resent on each call.
- The layers make different mistakes, which is why you stack them. Layer 1 catches
  prompt-side attacks; layer 2 limits blast radius when a prompt slips through; layer 3
  catches what the model produces on its own.
- The regexes are deliberately simple. The phone pattern also matches any long digit
  run (order numbers, SSNs), so layer 1 fires before layer 3 would see an SSN typed by
  the user. In production use a classifier or Sensitive Data Protection instead.

## Packaging as a plugin

For reuse across agents, move these callbacks into an ADK `BasePlugin` registered on the
`App`, so every agent in the app gets the same checks. See
`../../Module_10_Callbacks_Plugins_Events/plugin_pattern/`. They are written as plain
callbacks here so each hook is easy to read.
