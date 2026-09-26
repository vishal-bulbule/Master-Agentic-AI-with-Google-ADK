<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Module 9: Workflows and multi-agent systems

Compose several agents, and plain code, into one application: fixed
pipelines, parallel branches, loops, routing, and delegation.

## ADK 2.x changes in this module

`SequentialAgent`, `ParallelAgent`, and `LoopAgent` are deprecated in
ADK 2.x in favor of `Workflow`, a graph of nodes (agents, functions, tools)
and edges. The samples were migrated:

| ADK 1.x | ADK 2.x (these samples) |
|---|---|
| `SequentialAgent(sub_agents=[a, b, c])` | `Workflow(edges=[("START", a, b, c)])` |
| `ParallelAgent(sub_agents=[a, b, c])` then a combiner | `("START", (a, b, c))`, `((a, b, c), JoinNode(...))`, `(join, combiner)` |
| `LoopAgent(max_iterations=N)` plus `escalate=True` | a function node that returns `Event(route="revise")` or `Event(route="done")`, with an edge back to an earlier node |

Two exceptions, on purpose:

- `05_hierarchy_demo` keeps a `SequentialAgent` as the sub-agent of an
  `LlmAgent`. A `Workflow` cannot yet be an `LlmAgent` sub-agent.
- `04_custom_base_agent` subclasses `BaseAgent`. That is still supported;
  the README there lists the `Workflow` alternatives.

## LLM agents vs workflows

| | LLM agent routing | Workflow |
|---|---|---|
| Who picks the next step | the model | code (edges and routes) |
| Determinism | no | yes |
| Cost of orchestration | tokens per decision | none |
| Use for | open-ended requests, delegation | pipelines, fan-out, retries, loops |

A workflow does not reason; its nodes can still be LLM agents.

## Before you start

- The repository setup in [SETUP.md](../SETUP.md): the Python environment from
  `requirements.txt` and credentials in a `.env` (a Gemini API key, or Agent
  Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`).
- Nothing else: no extra packages, tools, keys, or cloud resources. The
  search tools in `02_parallel_fanout` and `lab_research_team` are mocks.

## Topics, in order

| Folder | What it shows |
|---|---|
| `01_sequential_pipeline/` | `Workflow` chain: code_writer, code_reviewer, code_refactorer |
| `02_parallel_fanout/` | fan-out to three searchers, `JoinNode`, then a combiner |
| `03_loop_refinement/` | writer and critic loop with a routed exit |
| `04_custom_base_agent/` | `BaseAgent` subclass that retries a flaky sub-agent |
| `05_hierarchy_demo/` | `LlmAgent` coordinator over mixed sub-agents |
| `06_llm_routing/` | the model routes with `transfer_to_agent` |
| `07_programmatic_routing/` | a Python function routes: as a tool (`routing_demo`) and as a Workflow node (`code_router`) |
| `08_agent_as_tool_vs_subagent/` | `AgentTool` vs `sub_agents` |
| `09_output_keys_glue/` | `output_key` and `{key}` placeholders between agents |
| `lab_research_team/` | lab: planner, parallel researchers, join, writer/critic loop in one graph |

## Workflow cheat sheet

```python
from google.adk import Event, Workflow
from google.adk.workflow import JoinNode

Workflow(name="pipeline", edges=[("START", a, b, c)])            # in order

join = JoinNode(name="join")
Workflow(name="fanout", edges=[("START", (a, b, c)),             # concurrently
                               ((a, b, c), join), (join, d)])    # then once

def decide(ctx) -> Event:                                         # loop exit
    return Event(route="done" if ctx.state.get("ok") else "again")

Workflow(name="loop", edges=[("START", worker, decide),
                             (decide, {"again": worker, "done": finish})])
```

Data moves between nodes as node output and input, and through session
state: `output_key` on an `LlmAgent` writes its answer to state, and
`{key}` in a later instruction reads it.

## Running a topic

From a topic folder:

```bash
adk web                # dev UI at http://localhost:8000, pick the agent
adk run <agent_name>   # terminal chat
```

`adk web` and `adk run` keep sessions in `<agent>/.adk/session.db`; delete
that folder to start clean.

## Reference

- [Graph-based workflows](https://adk.dev/graphs/),
  [routes](https://adk.dev/graphs/routes/),
  [data handling](https://adk.dev/graphs/data-handling/),
  [dynamic workflows](https://adk.dev/graphs/dynamic/)
- [Collaborative workflows](https://adk.dev/workflows/collaboration/)
- [Custom agents](https://adk.dev/agents/custom-agents/)
- [Template workflow agents](https://adk.dev/agents/workflow-agents/) (the deprecated 1.x classes)
- Module 8 covers state and `{key?}` placeholders in depth.
