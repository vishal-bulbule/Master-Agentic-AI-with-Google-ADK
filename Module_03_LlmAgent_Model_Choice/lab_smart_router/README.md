<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Lab: Smart Router (reference solution)

## What this shows

One agent that answers simple questions on Flash and sends math to Pro. A
`before_model_callback` (`route_model`) reads the user message, calls
`pick_model`, and replaces `llm_request.model` before every model request,
so the tool round trip in a math turn stays on the same model. An
`after_model_callback` (`record_usage`) adds each call's token counts to the
`token_usage` state key per model, so you can compare the cost of each route
in the dev UI.

| File | Role |
|---|---|
| `tools.py` | Shared `compute(expression)` tool (safe arithmetic, no `eval`) |
| `agent.py` | `pick_model`, the two callbacks, and `root_agent` |
| `results.md` | Template for your results and the questions to answer |

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`.env.example`](.env.example): `GOOGLE_API_KEY`, or
      Agent Platform (formerly Vertex AI) with `GOOGLE_CLOUD_LOCATION=global`
      (`gemini-3.5-flash` is served from `global`).
- [ ] Access to the Pro model (`gemini-2.5-pro`) on your key or project. If
      an organization policy blocks it, set `ROUTER_PRO_MODEL` in `.env` to a
      model you can use, for example `ROUTER_PRO_MODEL=gemini-2.5-flash`.
      Routing still works; only the cost comparison loses meaning.

## Run it

1. `cd Module_03_LlmAgent_Model_Choice`
2. `adk web`
3. Open http://localhost:8000 and select `lab_smart_router` in the agent dropdown.
4. Send: "Compute 12 * (3 + 4) - 5."

Terminal alternative: `adk run lab_smart_router`.

## Try it

Send these ten queries in one session:

1. What's the capital of France?
2. Who wrote the play Hamlet?
3. Compute 12 * (3 + 4) - 5.
4. Solve 2x + 5 = 17 step by step.
5. Give me a fun fact about octopuses.
6. Calculate the compound interest on 50000 at 8% per year for 3 years.
7. What does TCP stand for?
8. Evaluate (45 ** 2) / 9 + 100.
9. Recommend three sci-fi books about AI.
10. Find the result of 7! (7 factorial).

## What to look for

- State tab: `routed_model` shows the model chosen for the last turn, and
  `token_usage` holds `model_calls`, `prompt_tokens` and `output_tokens`
  (thinking included) per model.
- Events view: click a model response row; the side panel (raw JSON view)
  shows its `modelVersion`. Math queries
  (3, 4, 6, 8, 10) show the Pro model and a `compute` call and response;
  general queries (1, 2, 5, 7, 9) show Flash and no tool call.
- A math turn costs two model calls: the tool round trip resends the
  conversation plus the tool result.
- Traces view: latency per model call, for the latency side of the comparison.

Copy the numbers into `results.md` and answer the questions there.

## Common errors

| Symptom | Cause | Fix |
|---|---|---|
| `FAILED_PRECONDITION` naming `constraints/vertexai.allowedGenAIModels` on math queries | Your organization blocks the Pro model | Set `ROUTER_PRO_MODEL` to an allowed model and restart `adk web` |
| `404 NOT_FOUND` for `gemini-3.5-flash` on Agent Platform | `GOOGLE_CLOUD_LOCATION` is a region | Set `GOOGLE_CLOUD_LOCATION=global` |

## Extending

- Replace the keyword and regex `pick_model` with a small Flash classifier
  that emits a difficulty label. It routes better but adds one model call.
- Cost-aware retry: send the query to Flash first; if the answer fails a cheap
  validator, retry on Pro.
- Add a third tier with a Claude model through `LiteLlm` (see
  `litellm_model`). That needs a second agent: `llm_request.model` switches
  between models of the same provider class, not from Gemini to LiteLLM.
