<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 07: Tool Context: Actions

## What this shows

`tool_context.actions` lets a tool change what the runtime does after it
returns. Three flags:

| Flag | Effect |
|---|---|
| `actions.transfer_to_agent = "name"` | Hand the conversation to another agent. |
| `actions.skip_summarization = True` | End the turn with the tool result; the model does not rephrase it. |
| `actions.escalate = True` | Stop the enclosing `LoopAgent` (Module 9). |

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`agent/.env.example`](agent/.env.example):
      `GOOGLE_API_KEY`, or Agent Platform (formerly Vertex AI) with
      `GOOGLE_CLOUD_LOCATION=global` (`gemini-3.5-flash` is served from
      `global`).

## Run it

1. `cd Module_04_Custom_Tools/07_tool_context_actions`
2. `adk web`
3. Open http://localhost:8000 and pick `agent` in the app dropdown in the top bar.
4. Send: "I need a refund for invoice 1234."

Terminal alternative: `adk run agent`.

## Try it

Use a new session for each prompt:

- "I need a refund for invoice 1234." (`route_to_billing` sets `transfer_to_agent`)
- "What's the system status?" (`get_system_status` sets `skip_summarization`)
- "Check loop with value 7" (`check_loop_condition` sets `escalate`)

## What to look for

- Refund: the tool event carries `actions.transferToAgent`, the reply is
  authored by `billing_agent`, not `router_agent`, and your next message
  also goes to `billing_agent`.
- System status: the turn ends with the function response. There is no
  model-written sentence after it; the dev UI shows the raw dict.
- Check loop: the event carries `escalate: true`, but outside a `LoopAgent`
  nothing stops, and the model simply describes the result.
