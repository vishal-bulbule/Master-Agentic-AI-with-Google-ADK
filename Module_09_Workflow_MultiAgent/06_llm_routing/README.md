<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 06 LLM-driven routing

## What this shows

The root agent lists two specialists in `sub_agents`. The model reads their
`description` fields and calls `transfer_to_agent(agent_name=...)` to hand
over; no code decides the route. It handles messy phrasing, but the same input
can route differently across runs, and routing is only as good as the
descriptions (`researcher` "finds facts", `writer` "writes prose"). If routing
misbehaves: keep each description to one sentence that says how it differs
from its peers, tell the root explicitly to delegate and not answer, list the
specialists by name in the root instruction, and sharpen the descriptions
before adding examples.

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials
go in a `.env` at the repository root or in the agent folder; see
`routing_root/.env.example` (Gemini API key, or Agent Platform (formerly
Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_09_Workflow_MultiAgent/06_llm_routing`
2. `adk web`
3. Open http://localhost:8000 and select `routing_root`.
4. Send: `Find me three facts about Saturn's rings.`

Terminal alternative: `adk run routing_root`.

## Try it

Each prompt in a new session:

- `Find me three facts about Saturn's rings.` goes to `researcher`.
- `Write a short poem about the ocean.` goes to `writer`.

## What to look for

Events view: a `transfer_to_agent` call from `routing_root`, then the
specialist's answer authored by `researcher` or `writer` (click a row to see
its author in the side panel).

## Clean up

Sessions are kept in `routing_root/.adk/session.db`. Delete it to start
clean: `rm -rf routing_root/.adk`
