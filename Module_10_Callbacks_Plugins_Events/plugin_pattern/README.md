<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Plugin pattern

## What this shows

When the same callbacks need to run on many agents, package them as a plugin:
a `BasePlugin` subclass registered once on the `App`. Plugin callbacks run for
every agent, model call, and tool call in the App. `GuardrailPlugin`
(`guardrail_plugin.py`) bundles a PII block and a per-session token budget
(`before_model_callback`) and a forbidden-word filter
(`after_model_callback`). `agent.py` defines a plain agent with no callbacks
plus `app = App(..., plugins=[GuardrailPlugin()])`. `adk web` and `adk run`
load a module-level `app` before `root_agent`, so the plugin is active in
both. The App name (`plugin_pattern`) matches the folder name, and App names
must start with a letter.

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials go in a `.env` at the repository root or in the agent folder; `.env.example` in this folder lists the variables (a Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_10_Callbacks_Plugins_Events`
2. `adk web`
3. Open http://localhost:8000 and select `plugin_pattern` in the agent dropdown.
4. Send: `Email me at user@example.com`

The callbacks print to the terminal where `adk web` is running; keep it visible.
Terminal alternative: `adk run plugin_pattern` prints the same lines inline with the chat.

## Try it

| Send | Outcome |
|---|---|
| `Email me at user@example.com` | Blocked by the PII check |
| `Repeat exactly this sentence: That was a damn stupid idea.` | `That was a [FILTERED] [FILTERED] idea.` |
| Many long messages in one session | The session budget eventually refuses |

## What to look for

- `[GuardrailPlugin] ...` lines in the terminal, even though `root_agent` has
  no callbacks.
- Plugin callbacks run before agent callbacks. If a plugin callback returns a
  value, the remaining plugins and the agent's own callbacks for that step are
  skipped.
- State tab: `guardrail_tokens_used`. The counter lives in session state, not
  on the plugin instance: one instance serves every session, so an instance
  attribute would make all users share one budget.

## Using this from Python

Pass the same App to a runner. The older `Runner(plugins=[...])` argument
still works but is deprecated.

```python
from google.adk.runners import InMemoryRunner

from plugin_pattern.agent import app

runner = InMemoryRunner(app=app)
```

## Clean up

`adk web` and `adk run` keep sessions in `plugin_pattern/.adk/session.db`. Delete it to start clean: `rm -rf plugin_pattern/.adk`
