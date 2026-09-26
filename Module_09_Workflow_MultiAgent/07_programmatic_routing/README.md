<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 07 Programmatic routing

## What this shows

A Python function, not the model, picks the specialist from keywords in the
query. Compared with `06_llm_routing` it is predictable (the same input
reaches the same agent) and cheaper, but every case has to be enumerated in
code. Two agents in this folder show two ways to wire it:

| Agent | How the route is applied | Router model |
|---|---|---|
| `routing_demo/` | An LlmAgent coordinator has `route(query)` as a tool and the two specialists wrapped in `AgentTool`. It calls `route`, then the specialist it names, and relays the answer. | Yes: the decision is code, but a model relays it and could ignore it |
| `code_router/` | A `Workflow` whose first node, `classify`, is a plain function that returns `Event(route="researcher")` or `Event(route="writer")`. The routed edge runs only that specialist. | None: no tokens are spent on routing |

```python
def classify(node_input: str) -> Event:
    q = node_input.lower()
    choice = "researcher" if any(k in q for k in RESEARCHER_KEYWORDS) else ...
    return Event(output=node_input, route=choice, state={"routed_to": choice})

root_agent = Workflow(
    name="code_router",
    edges=[("START", classify),
           (classify, {"researcher": researcher, "writer": writer})],
)
```

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials
go in a `.env` at the repository root or in the agent folder; see
`routing_demo/.env.example` or `code_router/.env.example` (Gemini API key,
or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location
`global`).

## Run it

1. `cd Module_09_Workflow_MultiAgent/07_programmatic_routing`
2. `adk web`
3. Open http://localhost:8000 and select `code_router` (or `routing_demo`).
4. Send: `Who painted the Mona Lisa?`

Terminal alternative: `adk run code_router` or `adk run routing_demo`.

## Try it

Send each prompt in a new session, first to `code_router`, then to
`routing_demo`:

| Prompt | Specialist |
|---|---|
| `Who painted the Mona Lisa?` | `researcher` |
| `Write a two-line poem about rain.` | `writer` |
| `Define recursion in one sentence.` | `researcher` |

## What to look for

- `code_router`, Events view: an event from `code_router` with route
  `researcher` or `writer` and no model call before it, then the answer
  authored by that specialist. State tab: `routed_to`.
- `routing_demo`, Events view: a `route` function call and response, then a
  `researcher` or `writer` tool call, then the answer authored by
  `routing_demo`. That is two extra model turns compared with `code_router`.

## Clean up

Sessions are kept in `.adk/session.db` inside each agent folder:
`rm -rf code_router/.adk routing_demo/.adk`
