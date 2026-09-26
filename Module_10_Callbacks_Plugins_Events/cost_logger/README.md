<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Cost logger

## What this shows

An `after_tool_callback` that prices every tool call, keeps a running total in
session state, and prints a line per call. It returns `None`, so tool results
reach the model unchanged. The same hook is where you would emit a metering
event or enforce a per-session spend limit on paid APIs. The prices are made
up; load real ones from your billing config.

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials go in a `.env` at the repository root or in the agent folder; `.env.example` in this folder lists the variables (a Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_10_Callbacks_Plugins_Events`
2. `adk web`
3. Open http://localhost:8000 and select `cost_logger` in the agent dropdown.
4. Send: `Search the web for ADK callbacks, then look up the price of sku abc-1.`

The callbacks print to the terminal where `adk web` is running; keep it visible.
Terminal alternative: `adk run cost_logger` prints the same lines inline with the chat.

## What to look for

```
[cost] tool=search_web cost=$0.0050 session_total=$0.0050
[cost] tool=lookup_price cost=$0.0010 session_total=$0.0060
```

- One `[cost]` line per tool call, with the total carried across turns.
- Events view: the `search_web` and `lookup_price` calls and responses.
- State tab: `total_cost_usd`.

## Clean up

`adk web` and `adk run` keep sessions in `cost_logger/.adk/session.db`. Delete it to start clean: `rm -rf cost_logger/.adk`
