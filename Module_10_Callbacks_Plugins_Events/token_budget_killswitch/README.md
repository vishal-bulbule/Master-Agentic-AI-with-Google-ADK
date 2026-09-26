<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Token budget kill switch

## What this shows

A `before_model_callback` that keeps a running token total in session state
and refuses with an `LlmResponse` once the next call would push the session
past 10,000 tokens. The model is never called after that point, so a runaway
conversation or loop cannot keep spending. Tokens are estimated as characters
divided by 4, which is close enough for a spending cap; for exact counts read
`llm_response.usage_metadata` in an `after_model_callback`.

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials go in a `.env` at the repository root or in the agent folder; `.env.example` in this folder lists the variables (a Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_10_Callbacks_Plugins_Events`
2. `adk web`
3. Open http://localhost:8000 and select `token_budget_killswitch` in the agent dropdown.
4. Send: `Explain what a token budget is in two sentences.`

The callbacks print to the terminal where `adk web` is running; keep it visible.
Terminal alternative: `adk run token_budget_killswitch` prints the same lines inline with the chat.

## Try it

A short chat uses a few hundred tokens. To see the refusal, set
`TOKEN_BUDGET = 300` in `token_budget_killswitch/agent.py`, restart `adk web`,
and send three or four messages in one session (or paste a few pages of text
with the default budget).

## What to look for

```
[killswitch] OK used=12/10000
[killswitch] OK used=108/10000
...
[killswitch] BUDGET EXCEEDED used=... +incoming=... > 10000
```

- The count grows faster than your messages do, because every request resends
  the full history.
- State tab: `tokens_used`. It is per session; a new session starts from zero.
  Sessions persist in `.adk/session.db`, so the total survives an `adk web`
  restart.

## Clean up

`adk web` and `adk run` keep sessions in `token_budget_killswitch/.adk/session.db`. Delete it to start clean: `rm -rf token_budget_killswitch/.adk`
