<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Lab: guardrail stack for a customer-service agent

## What this shows

A customer-service agent with four callbacks, each doing one job. The agent
can `lookup_order`, `issue_refund`, and `send_followup_email`, all backed by
in-memory fakes. `callbacks.py` holds the callbacks; `agent.py` wires them
with `before_model_callback=[pii_redaction, token_budget]`. A list of
`before_model` callbacks runs in order and stops at the first one that returns
a value, so redaction runs first and the budget check counts the redacted
text.

| Callback | Hook | What it does |
|---|---|---|
| `pii_redaction` | `before_model` | Replaces emails and phone numbers in the outgoing request with `[REDACTED_EMAIL]` / `[REDACTED_PHONE]` |
| `token_budget` | `before_model` | Keeps a running token estimate in state and refuses once the session would pass 10,000 |
| `profanity_filter` | `after_model` | Rewrites forbidden words in the reply to `[FILTERED]` |
| `cost_logger` | `after_tool` | Adds an estimated cost per tool call to a session total |

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials go in a `.env` at the repository root or in the agent folder; `.env.example` in this folder lists the variables (a Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_10_Callbacks_Plugins_Events`
2. `adk web`
3. Open http://localhost:8000 and select `lab_guardrail_stack` in the agent dropdown.
4. Send: `Hi, I'm Asha. Reach me at asha.kumar@example.com or +91 98765 43210. Can you check order A-100 for me?`

The callbacks print to the terminal where `adk web` is running; keep it visible.
Terminal alternative: `adk run lab_guardrail_stack` prints the same lines inline with the chat.

## Try it

Send these in one session, in order. Each one triggers a different callback.

| # | Send | Triggers |
|---|---|---|
| 1 | `Hi, I'm Asha. Reach me at asha.kumar@example.com or +91 98765 43210. Can you check order A-100 for me?` | PII redaction, cost logger |
| 2 | `Now please check order A-101 as well.` | Cost logger |
| 3 | `A-101 is late again. Write me a one-sentence apology in the voice of a fed-up support agent, and quote me saying 'this is a damn stupid delay' in it.` | Profanity filter |
| 4 | Any further message | Token budget, once lowered (below) |

Turns 1 to 3 use about 600 estimated tokens. To see the budget refuse, set
`TOKEN_BUDGET = 800` in `lab_guardrail_stack/callbacks.py`, restart
`adk web`, replay the turns in a new session, and send one or two more short
messages. With
the default budget, pasting a message of about 30,000 characters trips it.

## What to look for

In the terminal:

```
[pii_redaction] redacted 2 item(s) before send
[token_budget] OK used=24/10000
[cost_logger] tool=lookup_order cost=$0.0020 session_total=$0.0020
...
[profanity_filter] replaced 2 word(s) in model output
...
[token_budget] BUDGET EXCEEDED used=... +incoming=... > 10000, refusing
```

- `[pii_redaction]` fires on every model call, not just the first turn. The
  request is rebuilt from session history each time, and the session still
  holds the original text (see your first message, row #1 in the Events
  view).
  Redaction controls what the model sees, not what you store. If stored PII is
  a problem, redact before the message reaches the runner.
- State tab: `tokens_used` and `total_cost_usd`, per session.
- The model may call more tools than the prompt asks for (it sends follow-up
  emails because the instruction says to). The cost logger records each call.

## Clean up

`adk web` and `adk run` keep sessions in `lab_guardrail_stack/.adk/session.db`. Delete it to start clean: `rm -rf lab_guardrail_stack/.adk`
