<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# The agent loop, traced

## What this shows

An agent loop has five steps: reasoning, selection, invocation, observation
and finalization. This agent prints each step to the terminal that runs
`adk web` as it happens: three callbacks (`before_agent_callback`,
`after_model_callback`, `after_tool_callback`) plus a print inside each
tool. You match the terminal lines to the loop and to the events in the dev UI.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`.env.example`](.env.example): `GOOGLE_API_KEY`, or
      Agent Platform (formerly Vertex AI) with `GOOGLE_CLOUD_LOCATION=global`
      (`gemini-3.5-flash` is served from `global`).

## Run it

1. `cd Module_01_Agents_Landscape`
2. `adk web`
3. Open http://localhost:8000 and select `agent_loop_trace` in the agent dropdown.
4. Send: "Plan a 1-day trip to Tokyo."

Terminal alternative: `adk run agent_loop_trace` prints the same trace
lines followed by the agent's reply.

## What to look for

In the terminal running `adk web` (timestamps and wording will differ; the
model may request both tools in one step, as here):

```
[USER ] Plan a 1-day trip to Tokyo.

[MODEL] selected -> get_attractions({'city': 'Tokyo'})
[MODEL] selected -> get_food_recommendation({'city': 'Tokyo'})
[13:27:17] TOOL  >> get_attractions(city='Tokyo')
[OBS  ] get_attractions returned {'status': 'success', ...}
[13:27:17] TOOL  >> get_food_recommendation(city='Tokyo')
[OBS  ] get_food_recommendation returned {'status': 'success', ...}

[FINAL] Start your one-day trip to Tokyo at Tsukiji Outer Market ...
```

| Loop step | Terminal line | Dev UI Events view |
|---|---|---|
| 1. Reasoning | none: the model reads the prompt and history | click a model row: the side panel's Request view shows what the model read |
| 2. Selection | `[MODEL] selected -> ...` | model event with `functionCall` parts |
| 3. Invocation | `TOOL  >> ...`, printed inside the tool | (runs between the two events) |
| 4. Observation | `[OBS  ] ...` | event with `functionResponse` parts |
| 5. Finalization | `[FINAL] ...` | the final model text event |

Steps 2 to 4 repeat until the model decides it has enough. The instruction
says to call both tools, so there are two tool calls.

## Try it

Change the instruction in `agent.py` to call only `get_attractions`,
restart `adk web`, and send the prompt again. The loop now has one tool
call. The number of iterations is the model's decision; the instruction only
steers it.
