<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# PII guardrail

## What this shows

A `before_model_callback` that looks for an email address or phone number in
the latest user message. On a match it returns an `LlmResponse` with a
refusal, so the model is never called and never sees the data. Without a match
it returns `None`. Only the latest user turn is checked: scanning the whole
history would make every later turn fail once PII had appeared. The regexes
are deliberately simple; a production guardrail would use a proper detector
such as Sensitive Data Protection (Cloud DLP).

```python
def pii_block(callback_context, llm_request):
    if has_pii(latest_user_text(llm_request)):
        return LlmResponse(content=types.Content(role="model", parts=[...]))
    return None
```

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials go in a `.env` at the repository root or in the agent folder; `.env.example` in this folder lists the variables (a Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_10_Callbacks_Plugins_Events`
2. `adk web`
3. Open http://localhost:8000 and select `guardrail_pii` in the agent dropdown.
4. Send: `What's the capital of France?`

The callbacks print to the terminal where `adk web` is running; keep it visible.
Terminal alternative: `adk run guardrail_pii` prints the same lines inline with the chat.

## Try it

| Send | Outcome |
|---|---|
| `What's the capital of France?` | Normal model answer |
| `Email me at jane@example.com` | Refusal, model not called |
| `Call me on +91 98765 43210` | Refusal, model not called |

## What to look for

- `[pii_block] PII detected, refusing without calling the model` in the
  terminal on a match.
- In the Traces view, the refused turns have no model call span.

## Clean up

`adk web` and `adk run` keep sessions in `guardrail_pii/.adk/session.db`. Delete it to start clean: `rm -rf guardrail_pii/.adk`
