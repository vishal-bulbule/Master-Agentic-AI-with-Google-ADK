<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 10: Tool Confirmation

## What this shows

For risky actions (destructive, billable, irreversible) the model should not
run the tool on its own. Wrap the tool in `FunctionTool(...,
require_confirmation=True)` and ADK pauses before executing it:

```python
from google.adk.tools import FunctionTool

delete_tool = FunctionTool(func=delete_user, require_confirmation=True)
```

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`agent/.env.example`](agent/.env.example):
      `GOOGLE_API_KEY`, or Agent Platform (formerly Vertex AI) with
      `GOOGLE_CLOUD_LOCATION=global` (`gemini-3.5-flash` is served from
      `global`).

## Run it

1. `cd Module_04_Custom_Tools/10_tool_confirmation`
2. `adk web`
3. Open http://localhost:8000 and pick `agent` in the app dropdown in the top bar.
4. Send: "Delete user u-1."

Terminal alternative: `adk run agent`.

## Try it

1. "Read user u-1" runs immediately with no prompt.
2. "Delete user u-1." pauses for approval:
   - `adk web`: a confirmation card appears under the
     `adk_request_confirmation` row in the Events view. Tick **Confirmed**
     and click **Submit** to approve; click **Submit** with the box unticked
     to reject.
   - `adk run`: it prints
     `[HITL confirm] Please approve or reject the tool call delete_user() ...`.
     Type `yes` to confirm, anything else to reject.

## What to look for

- Events view: the model's `delete_user` call is followed by an
  `adk_request_confirmation` call, and `delete_user` does not run until you
  submit the card.
- Approve: ADK resumes, `delete_user` runs, and the agent confirms the deletion.
- Reject: the tool body never runs and the agent reports that nothing was deleted.

Your own client answers the `adk_request_confirmation` call with a function
response whose payload is `{"confirmed": true}` (or `false`), using the id
of that `adk_request_confirmation` call.

## When to require confirmation

- Deletions and destructive writes.
- Anything billable (charging cards, sending SMS, paid API calls).
- Anything a human should sanity-check ("send this email to 300 customers").

Not for reads (friction with no safety gain), and not for high-volume calls
in a loop: use a different gate, or pass a callable to
`require_confirmation` that only asks above a threshold.
