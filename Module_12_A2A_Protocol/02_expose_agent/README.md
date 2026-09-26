<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 02: Expose an agent over A2A

## What this shows

An ordinary ADK `LlmAgent` served over A2A so other agents can call it, with
no server code. The `product_catalog` agent has two function tools,
`lookup_product(sku)` and `list_categories()`, and knows nothing about A2A.
What makes it an A2A agent is the `agent.json` agent card next to `agent.py`:
`adk api_server --a2a` (or `adk web --a2a`) serves every agent folder that has
one. ADK 2.9.2 mounts each of them under `/a2a/<app_name>`:

| What | URL (port 8081 as used here) |
|---|---|
| JSON-RPC endpoint | `POST http://localhost:8081/a2a/product_catalog` |
| Agent card | `GET http://localhost:8081/a2a/product_catalog/.well-known/agent-card.json` |

The card is served exactly as written in `agent.json`. ADK does not fill in
the URL, so `supportedInterfaces[0].url` must match the host, port, and path
you serve on. Tasks live in an in-memory task store (`--task_store_uri` makes
them persistent); a restart loses them.

```
02_expose_agent/
  product_catalog/
    __init__.py
    agent.py        root_agent (LlmAgent)
    tools.py        lookup_product, list_categories
    agent.json      A2A agent card; its presence enables --a2a for this folder
    .env.example
```

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)). The root
  `requirements.txt` installs `google-adk[a2a]`, which pulls in `a2a-sdk`.
- Credentials in a `.env`: copy `product_catalog/.env.example` to
  `product_catalog/.env` (or use the root `.env`). Either a Gemini API key or
  Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location
  `global`.
- Port 8081 free. If it is not, pick another port and change the `url` in
  `product_catalog/agent.json` to match.

## Run it

1. `cd Module_12_A2A_Protocol/02_expose_agent`
2. `adk api_server --a2a --port 8081`
   (or `adk web --a2a --port 8081` to also get the dev UI on that port)
3. In another terminal, fetch the agent card:

   ```bash
   curl -s http://localhost:8081/a2a/product_catalog/.well-known/agent-card.json
   ```

4. Send a message with raw JSON-RPC (A2A protocol 1.0):

   ```bash
   curl -s http://localhost:8081/a2a/product_catalog \
     -H 'Content-Type: application/json' \
     -H 'A2A-Version: 1.0' \
     -d '{"jsonrpc": "2.0", "id": "1", "method": "SendMessage",
          "params": {"message": {"messageId": "m1", "role": "ROLE_USER",
                     "parts": [{"text": "How much is SKU-3001?"}]}}}'
   ```

To try the agent on its own first, without A2A: `adk web` in this folder, open
http://localhost:8000, select `product_catalog`, and send "How much is
SKU-3001?". `adk run product_catalog` works too.

## What to look for

- The `SendMessage` reply is a Task with `status.state`
  `TASK_STATE_COMPLETED`. Its `artifacts` carry the answer text ("SKU-3001
  (Noise-Cancelling Headphones) is priced at INR 8,999."). Its `history`
  carries the `lookup_product` call and result as data parts with
  `adk_type` `function_call` and `function_response`.
- The server log shows `Setting up A2A agent: product_catalog` at startup. A
  folder without `agent.json` is still served over the normal ADK REST API
  but not over A2A.
- `A2A-Version: 1.0` selects the 1.0 wire format (`SendMessage`, `ROLE_USER`,
  parts as `{"text": ...}`). Without it a2a-sdk servers assume 0.3.

## Using this from Python

To serve an agent over A2A from your own ASGI app instead of the ADK CLI,
`to_a2a()` builds the card from the agent's name, description, and tools, and
mounts the endpoint at `/` and the card at `/.well-known/agent-card.json`:

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

app = to_a2a(root_agent, host="localhost", port=8081)  # run with uvicorn
```

The `host` and `port` only set the URL advertised in the generated card; they
must match what uvicorn binds.

## Common errors

| Symptom | Cause |
|---|---|
| `404` on `/a2a/product_catalog/...` | `agent.json` is missing or invalid (check the startup log for `Failed to setup A2A agent`), or `--a2a` was not passed. |
| `404` on `/.well-known/agent.json` | That is the pre-1.0 path, and without the `/a2a/<app_name>` prefix. |
| Card loads but calls fail | The `url` in `agent.json` does not match the port or path the server runs on. |
| `address already in use` | Something else is on port 8081. Use another port and update `agent.json`. |

## Clean up

Stop the server with Ctrl+C. `adk api_server` stores sessions under
`product_catalog/.adk/`; delete that folder if you do not want to keep them.

Next: [03_agent_card](../03_agent_card/) explains the card, and
[04_consume_remote_agent](../04_consume_remote_agent/) calls this server from
another agent.
