<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 04: Consume a remote agent with `RemoteA2aAgent`

## What this shows

The other side of topic 02. `customer_service` is a local `LlmAgent` with one
sub-agent, a `RemoteA2aAgent` pointing at the product catalog that topic 02
serves over A2A on port 8081. Product questions are transferred to the remote
agent over A2A; returns and order questions stay local. Two `adk` processes
run side by side: one serves the catalog over A2A, the other runs the dev UI
with the consumer.

```
adk web (:8000)                             adk api_server --a2a (:8081)
customer_service                            product_catalog
  sub_agents=[catalog]   --- A2A over HTTP ->   POST /a2a/product_catalog
  catalog = RemoteA2aAgent(
    agent_card=".../a2a/product_catalog/.well-known/agent-card.json")
```

```python
remote_catalog = RemoteA2aAgent(
    name="catalog",
    description="Remote product catalog agent: SKU lookups and category listings.",
    agent_card=f"http://localhost:8081/a2a/product_catalog{AGENT_CARD_WELL_KNOWN_PATH}",
    use_legacy=False,
)
root_agent = LlmAgent(name="customer_service", ..., sub_agents=[remote_catalog])
```

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)).
- Credentials for both agents: copy `customer_service/.env.example` to
  `customer_service/.env` and `../02_expose_agent/product_catalog/.env.example`
  to `../02_expose_agent/product_catalog/.env` (or use the root `.env`). Gemini
  API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on
  location `global`.
- The catalog running over A2A on port 8081. In its own terminal:

  ```bash
  cd Module_12_A2A_Protocol/02_expose_agent
  adk api_server --a2a --port 8081
  ```

## Run it

1. `cd Module_12_A2A_Protocol/04_consume_remote_agent`
2. `adk web`
3. Open http://localhost:8000 and select `customer_service` in the agent dropdown.
4. Send: "How much is SKU-1001 and is it in stock?"

Terminal alternative: `adk run customer_service` from the same folder.

## Try it

| Prompt | Expected |
|---|---|
| How much is SKU-1001 and is it in stock? | Transferred to `catalog`: INR 5,499, in stock |
| What categories of products do you sell? | Transferred to `catalog`: audio, office, peripherals |
| I want to return an order I placed last week. | Answered by `customer_service`, no transfer |

## What to look for

- Events view: for product questions, `customer_service` calls
  `transfer_to_agent` with `agent_name="catalog"`, and the reply is authored
  by `catalog`. The remote `lookup_product` or `list_categories` call and its
  result also appear as events, forwarded from the A2A server.
- The return request is answered by `customer_service` itself.
- The catalog terminal logs `GET /a2a/product_catalog/.well-known/agent-card.json`
  before the first `POST /a2a/product_catalog`. The card is fetched on first
  use, not at import time, so `adk web` starts even when the catalog is down.
- A transfer hands the conversation to the sub-agent: its reply is the final
  answer. When the parent must post-process the remote result, wrap the
  remote agent in `AgentTool` instead, as the lab does.

## Common errors

| Symptom | Cause |
|---|---|
| `AgentCardResolutionError` or connection refused | The catalog is not running with `--a2a` on port 8081. |
| 404 on the card URL | Missing `/a2a/product_catalog` in the URL, or a hard-coded `/.well-known/agent.json`. Use `AGENT_CARD_WELL_KNOWN_PATH`. |
| The same product answer printed twice in `adk run` | Streaming prints a partial and a final event. Only one reaches the session. |

## Clean up

Stop both processes with Ctrl+C. Delete `customer_service/.adk/` and
`../02_expose_agent/product_catalog/.adk/` to drop the local sessions.
