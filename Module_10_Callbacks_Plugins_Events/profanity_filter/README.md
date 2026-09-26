<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Output filter

## What this shows

An `after_model_callback` that rewrites words from a block list to
`[FILTERED]`. Returning a new `LlmResponse` from an `after_*` callback replaces
what the model returned; returning `None` keeps the original. The check runs on
the model's output, so it catches problems no input guardrail can. The block
list is mild on purpose: `damn`, `hell`, `crap`, `stupid`, `idiot`.

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials go in a `.env` at the repository root or in the agent folder; `.env.example` in this folder lists the variables (a Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_10_Callbacks_Plugins_Events`
2. `adk web`
3. Open http://localhost:8000 and select `profanity_filter` in the agent dropdown.
4. Send: `Write a three-sentence frustrated rant about Mondays. Use the words damn and hell.`

The callbacks print to the terminal where `adk web` is running; keep it visible.
Terminal alternative: `adk run profanity_filter` prints the same lines inline with the chat.

## What to look for

- `[profanity_filter] replaced N word(s)` in the terminal and `[FILTERED]` in
  the reply.
- The session stores the filtered text, not the original, so later turns and
  the Events view only ever see the scrubbed version.
- Non-text parts pass through unchanged, so the filter is safe on agents that
  call tools.
- With streaming on, the filter runs on every chunk and again on the final
  response, so you may see several `replaced` lines for one reply.

## Clean up

`adk web` and `adk run` keep sessions in `profanity_filter/.adk/session.db`. Delete it to start clean: `rm -rf profanity_filter/.adk`
