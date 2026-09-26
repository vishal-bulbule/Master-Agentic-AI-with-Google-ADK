<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Observability callback

## What this shows

A `before_model_callback` that logs each model call and returns `None`, so it
never changes the run. This is the base pattern for audit trails, metrics, and
debugging: swap the logger for Cloud Logging, BigQuery, or OpenTelemetry and
you have per-call observability without touching the agent.

```python
def log_calls(callback_context, llm_request):
    logger.info("model_call agent=%s ...", callback_context.agent_name)
    return None
```

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials go in a `.env` at the repository root or in the agent folder; `.env.example` in this folder lists the variables (a Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_10_Callbacks_Plugins_Events`
2. `adk web`
3. Open http://localhost:8000 and select `observability_callback` in the agent dropdown.
4. Send: `What is ADK?`

The callbacks print to the terminal where `adk web` is running; keep it visible.
Terminal alternative: `adk run observability_callback` prints the same lines inline with the chat.

## Try it

Send two messages in the same session: `What is ADK?`, then
`Name one callback type.`

## What to look for

```
INFO: model_call agent=observability_agent input_chars=12 preview='What is ADK?'
INFO: model_call agent=observability_agent input_chars=585 preview='What is ADK? | ...'
```

- One `INFO: model_call` line per model call.
- `input_chars` grows on the second turn because `llm_request.contents` holds
  the full conversation history. This is why long sessions cost more per call.
- The dev UI Traces view shows the same calls as spans, with no code at all.

## Clean up

`adk web` and `adk run` keep sessions in `observability_callback/.adk/session.db`. Delete it to start clean: `rm -rf observability_callback/.adk`
