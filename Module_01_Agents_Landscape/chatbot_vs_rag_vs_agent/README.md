<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Chatbot vs RAG vs agent

## What this shows

One customer question, three ADK agents side by side:

> "I ordered headphones 3 days ago, order #A-1042. Where are they?"

| Folder | Shape | How it is built |
|---|---|---|
| `support_chatbot/` | Chatbot | `LlmAgent` with no tools. One model call per turn. |
| `support_rag/` | RAG | `LlmAgent` with a `before_model_callback` that always retrieves policy documents and appends them to the system instruction. Fixed retrieve-then-generate flow; the model decides nothing about retrieval. |
| `support_agent/` | Agent | `LlmAgent` with two tools, `get_order_status` and `lookup_shipping_policy`. The model decides per turn which to call. |

Only the agent can answer, because only the agent can look the order up.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in an agent folder,
      with the variables from `support_agent/.env.example` (all three folders
      need the same ones): `GOOGLE_API_KEY`, or Agent Platform (formerly
      Vertex AI) with `GOOGLE_CLOUD_LOCATION=global` (`gemini-3.5-flash` is
      served from `global`).

## Run it

1. `cd Module_01_Agents_Landscape/chatbot_vs_rag_vs_agent`
2. `adk web`
3. Open http://localhost:8000. The agent dropdown lists `support_agent`,
   `support_chatbot` and `support_rag`.
4. Select each one in turn from the app dropdown (each gets its own session) and send:
   "I ordered headphones 3 days ago, order #A-1042. Where are they?"

Terminal alternative, from the same folder: `adk run support_chatbot`,
`adk run support_rag`, `adk run support_agent`.

## What to look for

| Agent | Expected behavior |
|---|---|
| `support_chatbot` | A generic "please contact support" answer or a confident, invented status. It has no order data, so anything specific it says is made up. Events view: the user message and one answer row, no tool call chips. |
| `support_rag` | Quotes the shipping policies ("3-5 business days") but cannot see this order. State tab: `retrieved_docs` holds the documents the callback injected. Events view: no tool call chips; retrieval happened in code before the model ran. |
| `support_agent` | Events view: a `get_order_status` tool call chip with `order_id: "A-1042"`, the tool result chip with the ETA, and an answer that quotes it. Click a row to see its details in the side panel. |

- Chatbot: no tools, no grounding. Cheapest and fastest.
- RAG: one retrieval step, fixed flow. Right for "answer from our docs".
- Agent: several tools, the model picks the flow. Needed when the task
  requires action or per-user lookups, not only retrieval.

Also try "What is your returns policy?" on all three. The chatbot guesses,
RAG answers from the injected documents, and the agent calls
`lookup_shipping_policy`. In `support_agent/agent.py` the order data sits
under `order_status` rather than `status`, because `status` is reserved for
the tool's own success or error flag.

## Clean up

`adk web` and `adk run` keep sessions in a `.adk/` folder inside each agent
folder. Delete them to start fresh:

```bash
rm -rf support_chatbot/.adk support_rag/.adk support_agent/.adk
```
