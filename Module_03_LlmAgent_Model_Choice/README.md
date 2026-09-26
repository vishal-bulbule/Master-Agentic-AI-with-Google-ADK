<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Module 3: LlmAgent and Model Choice

Configure an `LlmAgent` beyond the defaults and pick the right model for the
job: every common constructor field, instruction patterns, structured output,
model routing, generation config, planners, and non-Gemini models through
LiteLLM.

## Topics

Work through them in order.

| # | Folder | What it shows |
|---|---|---|
| 1 | `parameter_map_demo/` | One agent that sets every common `LlmAgent` field |
| 2 | `instruction_patterns/` | Vague vs structured vs templated instructions (three agents) |
| 3 | `structured_output/` | `output_schema` with a Pydantic model, plus `output_key` |
| 4 | `model_routing/` | A `before_model_callback` that picks Flash or Pro per query |
| 5 | `generation_config/` | Temperature and `max_output_tokens` through `generate_content_config` |
| 6 | `planner_builtin/` | `BuiltInPlanner` with Gemini native thinking |
| 7 | `planner_react/` | `PlanReActPlanner`, which works on any model |
| 8 | `litellm_model/` | Claude through the `LiteLlm` wrapper |
| 9 | `lab_smart_router/` | Lab: Flash and Pro router with per-model token totals in state |

Folder names carry no number prefix because ADK app names must start with a
letter (`adk run 01_x` fails); follow the order in this table.

## Before you start

- Repository setup from [SETUP.md](../SETUP.md): virtual environment,
  `pip install -r requirements.txt` (includes `litellm`), and a `.env` at the
  repository root. Each agent folder has a `.env.example` listing the
  variables it reads.
- Gemini credentials: `GOOGLE_API_KEY`, or Agent Platform (formerly Vertex
  AI) with `GOOGLE_CLOUD_LOCATION=global` for `gemini-3.5-flash`.
- `model_routing` and `lab_smart_router`: access to `gemini-2.5-pro`, or set
  `ROUTER_PRO_MODEL` to a model your project allows.
- `litellm_model`: `ANTHROPIC_API_KEY` from https://console.anthropic.com/.

## Run

Every topic is an ADK agent and runs in the dev UI. From this folder:

```bash
cd Module_03_LlmAgent_Model_Choice
adk web                          # pick a topic in the agent dropdown
adk run parameter_map_demo       # or one agent in the terminal
```

`instruction_patterns` holds three agents; run `adk web` from inside that
folder to see them.

By default `adk web` and `adk run` keep sessions in a `.adk/` folder inside
each agent folder (ignored by git). Delete it to start from a clean slate.

## Models

The default model is `gemini-3.5-flash`. On Agent Platform it requires
`GOOGLE_CLOUD_LOCATION=global`. The routing samples use `gemini-2.5-pro` for
the Pro route; set `ROUTER_PRO_MODEL` if your project cannot use it.
