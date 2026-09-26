<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Module 12: A2A Protocol

How ADK agents call other agents over HTTP with the Agent2Agent (A2A)
protocol: agents that run in another process, are owned by another team, or
are written in another language. MCP connects an agent to a tool; A2A connects
an agent to another agent that has its own model and its own judgment.

Tested with google-adk 2.9.2 and a2a-sdk 1.1.5 (A2A protocol 1.0).

## Topics

Follow them in order.

| Folder | What it shows |
|---|---|
| [`01_mcp_vs_a2a_table/`](01_mcp_vs_a2a_table/) | When to use MCP and when to use A2A, with a worked example |
| [`02_expose_agent/`](02_expose_agent/) | Serve an ADK agent over A2A with `adk api_server --a2a` and an `agent.json` card |
| [`03_agent_card/`](03_agent_card/) | The agent card: fields, well-known path, a validated sample |
| [`04_consume_remote_agent/`](04_consume_remote_agent/) | Use a remote agent as a sub-agent with `RemoteA2aAgent` |
| [`05_task_lifecycle/`](05_task_lifecycle/) | Task states on a real A2A server: `billing_agent` pauses in `INPUT_REQUIRED` and resumes on the same task |
| [`06_a2a_extensions/`](06_a2a_extensions/) | Extension URIs: `ticket_desk` advertises the ADK extension; a custom tenant-id extension as a snippet |
| [`lab_writer_researcher_pair/`](lab_writer_researcher_pair/) | Lab: a writer agent that calls a researcher agent in another process |

## Before you start

- Repository setup: [SETUP.md](../SETUP.md). The root `requirements.txt`
  installs `google-adk[a2a]`, which pulls in `a2a-sdk`. No extra packages.
- Credentials: a Gemini API key, or Agent Platform (formerly Vertex AI) with
  `gemini-3.5-flash` on location `global`. Each agent folder has a
  `.env.example`; copy it to `.env` in the same folder, or keep one `.env` at
  the repository root (`adk` loads the nearest one walking up).
- Topics 05 and 06 run one agent with `adk api_server --a2a --port 8081`
  and call it with `curl` from a second terminal. Run one topic at a time.
- Two terminals for topics 02 to 04 and the lab: one runs the remote agent
  with `adk api_server --a2a --port 8081`, the other runs the consumer with
  `adk web` on port 8000. Port 8081 must be free, or change the `url` in the
  `agent.json` cards to match the port you use.
- No cloud resources are created. Topics 01 and 03 need no
  credentials.

## How the pieces fit

```
consumer agent (adk web)                    provider agent (adk api_server --a2a)
LlmAgent                                    LlmAgent + agent.json card
  sub-agent or tool:          A2A over
  RemoteA2aAgent  ---------- HTTP ------->    POST /a2a/<app_name>  (JSON-RPC)
        |                                          |
        +-- GET /a2a/<app_name>/.well-known/agent-card.json
            (fetched once, before the first call)
```

Both sides are ordinary ADK agents. The provider adds an `agent.json` card
next to `agent.py`; the consumer adds `RemoteA2aAgent`. ADK handles the HTTP
calls, the message conversion, and the task lifecycle.

## Notes for ADK 2.x and a2a-sdk 1.x

- The agent card is served at `/.well-known/agent-card.json`. The old
  `/.well-known/agent.json` path returns 404. Use the
  `AGENT_CARD_WELL_KNOWN_PATH` constant rather than a literal.
- `adk api_server --a2a` and `adk web --a2a` serve only agent folders that
  contain an `agent.json` card, under `/a2a/<app_name>`, and serve the card as
  written. There is no `A2AServer` class; to serve from your own ASGI app, use
  `to_a2a()` from `google.adk.a2a.utils.agent_to_a2a` (topic 02).
- ADK prints `[EXPERIMENTAL]` warnings for its A2A classes. They are expected.
  Set `ADK_SUPPRESS_A2A_EXPERIMENTAL_FEATURE_WARNINGS=true` to hide them.
