<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 04: Long-Running Tools

## What this shows

`LongRunningFunctionTool` is for work that cannot or should not finish inside
one agent turn: human approvals, batch jobs, video processing, payment
confirmations. The tool function returns immediately with a pending status
and an id. The final result is delivered later as a function response for
the same call id.

```
turn 1  user:    "Please approve INR 12,000 for the team offsite dinner."
        agent:   calls ask_for_approval(purpose, amount)
        tool:    returns {"status": "pending", "ticket_id": "APPROVAL-..."}
        agent:   "Ticket APPROVAL-XYZ created, a manager has been notified."
        (the event lists the call id in long_running_tool_ids; the run ends)

later   the manager approves in some other system

turn 2  client:  sends a FunctionResponse for the same call id:
                 {"status": "approved", "ticket_id": "APPROVAL-XYZ"}
        agent:   tells the user the expense was approved
```

The tool function must return immediately. Do not `time.sleep` or poll
inside it.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`agent/.env.example`](agent/.env.example):
      `GOOGLE_API_KEY`, or Agent Platform (formerly Vertex AI) with
      `GOOGLE_CLOUD_LOCATION=global` (`gemini-3.5-flash` is served from
      `global`).

## Run it

1. `cd Module_04_Custom_Tools/04_long_running_tool`
2. `adk web`
3. Open http://localhost:8000 and pick `agent` in the app dropdown in the top bar.
4. Send: "Please approve INR 12,000 for the team offsite dinner."

Terminal alternative: `adk run agent`.

## Try it

1. Send the approval request. The agent reports a ticket id and the turn ends.
2. Deliver the decision for the pending call:
   - `adk web`: under the `ask_for_approval` call row in the Events view
     there is an **Enter your response...** box. Enter
     `{"status": "approved", "approver": "finance-manager@example.com"}`
     and press Enter.
   - `adk run`: after the ticket message it prints
     `[HITL] Waiting for input for ask_for_approval(...)`. Type the same JSON.

## What to look for

- Events view, turn 1: click the `ask_for_approval` call row; the raw JSON
  view in the side panel lists its id in `longRunningToolIds`. The run stops
  after the agent reports the ticket.
- Turn 2: the agent reports the approval without calling the tool again. ADK
  adds a note to the tool description telling the model not to re-call a
  long-running tool that already returned a pending status.

## Using this from Python

Your own client sends the final result as a `FunctionResponse` part with the
id of the original call (from the event whose `long_running_tool_ids`
contains it):

```python
from google.genai import types

final = types.Part(function_response=types.FunctionResponse(
    id=call_id,
    name="ask_for_approval",
    response={"status": "approved", "ticket_id": ticket_id},
))
async for event in runner.run_async(
    user_id=user_id,
    session_id=session_id,
    new_message=types.Content(role="user", parts=[final]),
):
    ...
```
