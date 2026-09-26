<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 05: A2A task lifecycle

## What this shows

An A2A call is not a single request and response. Each interaction is a task
with a tracked state, so the remote agent can pause and ask for more
information before it finishes. The `billing_agent` here closes invoices.
When a customer has several open invoices it calls `ask_client`, a
`LongRunningFunctionTool`; ADK's A2A executor turns that pending call into
the task state `TASK_STATE_INPUT_REQUIRED`. The client answers on the same
task and it moves on to `TASK_STATE_COMPLETED`. You drive both turns with
`curl` against `adk api_server --a2a`, so every state you see comes from a
real A2A server.

```
05_task_lifecycle/
  billing_agent/
    __init__.py
    agent.py        root_agent; ask_client is a LongRunningFunctionTool
    agent.json      A2A agent card; its presence enables --a2a for this folder
    .env.example
```

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)). The root
      `requirements.txt` installs `google-adk[a2a]`, which pulls in `a2a-sdk`.
- [ ] Credentials in a `.env`: copy `billing_agent/.env.example` to
      `billing_agent/.env` (or use the root `.env`). Either a Gemini API key
      or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on
      location `global`.
- [ ] Port 8081 free (stop topic 02's server if it is still running). To use
      another port, change the `url` in `billing_agent/agent.json` too.

## Run it

1. `cd Module_12_A2A_Protocol/05_task_lifecycle`
2. `adk api_server --a2a --port 8081`
3. In another terminal, start a task:

   ```bash
   curl -s http://localhost:8081/a2a/billing_agent \
     -H 'Content-Type: application/json' \
     -H 'A2A-Version: 1.0' \
     -d '{"jsonrpc": "2.0", "id": "1", "method": "SendMessage",
          "params": {"message": {"messageId": "m1", "role": "ROLE_USER",
                     "parts": [{"text": "Close the open invoice for Acme."}]}}}'
   ```

4. The reply is a task in `TASK_STATE_INPUT_REQUIRED`. Copy three values from
   it into shell variables:

   ```bash
   TASK_ID=...      # result.task.id
   CONTEXT_ID=...   # result.task.contextId
   CALL_ID=...      # result.task.status.message.parts[0].data.id (the ask_client call)
   ```

5. Optional: read the task back. It is still paused:

   ```bash
   curl -s http://localhost:8081/a2a/billing_agent \
     -H 'Content-Type: application/json' -H 'A2A-Version: 1.0' \
     -d "{\"jsonrpc\": \"2.0\", \"id\": \"2\", \"method\": \"GetTask\",
          \"params\": {\"id\": \"$TASK_ID\", \"historyLength\": 0}}"
   ```

6. Answer the question on the same task. The answer is the `ask_client`
   function response:

   ```bash
   curl -s http://localhost:8081/a2a/billing_agent \
     -H 'Content-Type: application/json' -H 'A2A-Version: 1.0' \
     -d "{\"jsonrpc\": \"2.0\", \"id\": \"3\", \"method\": \"SendMessage\",
          \"params\": {\"message\": {\"messageId\": \"m2\", \"role\": \"ROLE_USER\",
            \"taskId\": \"$TASK_ID\", \"contextId\": \"$CONTEXT_ID\",
            \"parts\": [{\"data\": {\"id\": \"$CALL_ID\", \"name\": \"ask_client\",
                                    \"response\": {\"answer\": \"INV-22\"}},
                         \"metadata\": {\"adk_type\": \"function_response\"}}]}}}"
   ```

`adk web --a2a --port 8081` serves the same A2A endpoint and adds the dev UI
on that port.

## What to look for

- Step 3: `result.task.status.state` is `TASK_STATE_INPUT_REQUIRED`.
  `status.message.parts[0]` is a data part with `adk_type: function_call`,
  `adk_is_long_running: true`, `name: ask_client`, and the question in
  `args.question` ("Acme has multiple open invoices: INV-19, INV-22,
  INV-30..."). The `history` shows the `find_open_invoices` call and result
  that came before it.
- Step 5: `GetTask` returns the same task id, still `INPUT_REQUIRED`.
  `INPUT_REQUIRED` is not terminal.
- Step 6: the same task id, now `TASK_STATE_COMPLETED`. The `artifacts`
  carry the answer ("closed the invoice INV-22 for Acme ... 84,500 INR"), and
  the `history` shows the `close_invoice` call.
- "Close the open invoice for Globex." completes in one call: Globex has one
  open invoice, so the agent never pauses.

## Common errors

| Symptom | Cause |
|---|---|
| Step 6 returns `INPUT_REQUIRED` again with a new question | The reply was plain text, or the `id` did not match the pending call. ADK resumes a paused task only from a `function_response` data part for that call id. |
| `Task ... is in terminal state` (`-32602`) | You sent another message on a task that already completed. Start a new task (omit `taskId`). |
| `404` on `/a2a/billing_agent` | `--a2a` was not passed, or `agent.json` is missing or invalid (check the startup log for `Setting up A2A agent: billing_agent`). |
| `VERSION_NOT_SUPPORTED` | A malformed `A2A-Version` header. It must be exactly `1.0`. |

## Clean up

Stop the server with Ctrl+C. Sessions are stored under `billing_agent/.adk/`;
delete that folder to start fresh. Tasks live in memory and are gone after a
restart.

## States

```
SendMessage (client starts a task)
        |
    SUBMITTED        accepted, queued
        |
     WORKING         agent is processing, may stream updates
        |
   +----+-----------------+----------------+
   |                      |                |
INPUT_REQUIRED        COMPLETED          FAILED
   |
   client sends another message on the same task
   |
back to WORKING
```

In a2a-sdk 1.x the wire values carry a `TASK_STATE_` prefix.

| State | Meaning |
|---|---|
| `TASK_STATE_SUBMITTED` | The server accepted the task. |
| `TASK_STATE_WORKING` | The agent is processing. It may send status updates. |
| `TASK_STATE_INPUT_REQUIRED` | The agent needs more from the client. The task is paused, not finished. |
| `TASK_STATE_AUTH_REQUIRED` | The agent needs the client to authenticate before it continues. |
| `TASK_STATE_COMPLETED` | Final result delivered in the task's artifacts. |
| `TASK_STATE_FAILED` | Terminal, with an error. |
| `TASK_STATE_CANCELED` | The client or server ended the task early. |
| `TASK_STATE_REJECTED` | The agent declined the task. |

The client reads the state from the `SendMessage` reply, from `GetTask`,
from a stream (`SendStreamingMessage`, `SubscribeToTask`), or from push
notifications.

## Why it matters

A tool call over MCP sends arguments and gets a result. The agent behind A2A
has its own model, and it can discover partway through that it is missing
information. Ask a billing agent to "close the invoice for Acme" and it may
reply `INPUT_REQUIRED: Acme has 3 open invoices, which one?`. The client
answers, the task goes back to `WORKING`, and then `COMPLETED`.

When you use `RemoteA2aAgent` as the client, ADK tracks the task for you: it sends the
first message, surfaces an `INPUT_REQUIRED` question to the parent agent (which
asks the user or answers from context), and sends the next turn on the same
task.
