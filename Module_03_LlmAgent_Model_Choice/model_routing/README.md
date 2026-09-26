<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Model Routing

## What this shows

A rule-based router that sends easy questions to Flash and long or
math-heavy ones to Pro, inside a single agent. `route_model` in `router.py`
is a `before_model_callback`: ADK calls it right before each model request,
and it replaces `llm_request.model` with the model `pick_model` chooses.
Routing is plain Python that runs before any model call, so it adds no
latency and is easy to debug.

- `router.py`: `pick_model(query)` heuristic and the `route_model` callback.
- `agent.py`: `root_agent`, declared with Flash and wired to `route_model`.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`.env.example`](.env.example): `GOOGLE_API_KEY`, or
      Agent Platform (formerly Vertex AI) with `GOOGLE_CLOUD_LOCATION=global`
      (`gemini-3.5-flash` is served from `global`).
- [ ] Access to the Pro model (`gemini-2.5-pro`) on your key or project. If
      an organization policy blocks it, set `ROUTER_PRO_MODEL` in `.env` to
      a model you can use, for example `ROUTER_PRO_MODEL=gemini-2.5-flash`.

## Run it

1. `cd Module_03_LlmAgent_Model_Choice`
2. `adk web`
3. Open http://localhost:8000 and select `model_routing` in the agent dropdown.
4. Send: "Hi! What's the capital of France?"

Terminal alternative: `adk run model_routing`.

## Try it

Send these in one session:

1. Hi! What's the capital of France?
2. Calculate the derivative of x^3 + 2x^2 - 5x + 7.
3. Tell me a joke about programmers.
4. Solve the equation 2x + 5 = 17 step by step.
5. I have a long-form analytical question. Please compare and contrast the
   architectural tradeoffs between rule-based model routing,
   classifier-based routing, and cost-aware retry escalation, with at least
   three concrete examples for each strategy.

## What to look for

- State tab: `routed_model` changes per turn. Queries 2, 4 and 5 go to the
  Pro model; 1 and 3 stay on Flash.
- Events view: click a model response row. The side panel (raw JSON view)
  shows `modelVersion`, the model that actually answered, and
  `usageMetadata` with its token counts. Pro replies are usually longer and
  slower (Traces view).
- The conversation history is shared across models: the agent is the same,
  only the model serving each turn changes.

## Common errors

| Symptom | Cause | Fix |
|---|---|---|
| `FAILED_PRECONDITION` naming `constraints/vertexai.allowedGenAIModels` on queries 2, 4, 5 | Your organization blocks the Pro model | Set `ROUTER_PRO_MODEL` to an allowed model and restart `adk web` |

## Trade-off

Keyword rules are free and predictable, but they misroute anything the
keyword list does not anticipate. A classifier (a small Flash call that emits
a difficulty label) routes better at the cost of one extra model call per
query. Try replacing `pick_model` with one.
