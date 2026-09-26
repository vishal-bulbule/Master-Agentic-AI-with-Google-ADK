<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 05 - Built-in Eval Criteria, One Config Each

## What this shows

ADK ships a set of built-in metrics. Each subfolder here holds one `test_config.json`
with the exact JSON shape for one metric. Deterministic metrics are cheap and stable;
LLM-as-judge metrics catch semantic regressions but cost a judge call per invocation
per sample. Pick per metric, not by habit.

| Metric | Reference needed? | LLM judge? | When to use |
|---|---|---|---|
| `tool_trajectory_avg_score` | Yes (tool calls) | No | CI / regression. Fast and deterministic. |
| `response_match_score` | Yes (text) | No | CI / regression. ROUGE-1 word overlap. |
| `final_response_match_v2` | Yes (text) | Yes | Trusted reference answer, wording may vary. |
| `rubric_based_final_response_quality_v1` | No | Yes | No reference; judge against your own rubrics. |
| `hallucinations_v1` | No (uses tool outputs and instructions) | Yes | Answers must be grounded in tool output. |
| `safety_v1` | No | Yes (Agent Platform Eval SDK) | Harmlessness checks. Needs a Google Cloud project. |
| `multi_turn_task_success_v1` | No | Yes (Agent Platform Eval SDK) | Did the whole conversation reach the goal? Needs a Google Cloud project. |

The full list, including `rubric_based_tool_use_quality_v1` and the other multi-turn
metrics, is in the ADK docs under Evaluate, Evaluation Criteria, and in
`google/adk/evaluation/eval_metrics.py` (`PrebuiltMetrics`).

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)). The root `requirements.txt` installs
  `google-adk[eval]` (ROUGE and the judge models) plus `pytest` and `pytest-asyncio`.
- The topic 01 agent's credentials in `01_test_file_anatomy/weather_agent/.env`; the
  commands here reuse that agent and test file.
- For `safety_v1` and `multi_turn_task_success_v1` only: a Google Cloud project with the
  Agent Platform API enabled (`gcloud services enable aiplatform.googleapis.com`),
  `gcloud auth application-default login`, and `GOOGLE_CLOUD_PROJECT` and
  `GOOGLE_CLOUD_LOCATION` in that `.env`.

## Run it

Pass any config with `--config_file_path`. For example, the topic 01 test file with
the hallucinations config:

1. `cd Module_14_Evaluation_Observability/01_test_file_anatomy`
2. Run:

   ```bash
   adk eval weather_agent tests/weather.test.json \
       --config_file_path=../05_criteria_walkthrough/05_hallucinations/test_config.json \
       --print_detailed_results
   ```

`AgentEvaluator.evaluate` in pytest reads `test_config.json` from the folder of the test
file; `adk eval` does the same when you pass a single eval file and no
`--config_file_path`.

## What to look for

- Plain-float criteria (`"response_match_score": 0.8`) set only a threshold. Object
  criteria add options: `match_type` for trajectories, `judge_model_options` for LLM
  judges, `rubrics` for rubric metrics.
- `judge_model_options.num_samples` multiplies judge cost. 5 is the ADK default; 1 to 3
  is enough while iterating.
- The judge model defaults to `gemini-2.5-flash`. These configs set `gemini-3.5-flash`.
  On Agent Platform it is served from the `global` location, so set
  `GOOGLE_CLOUD_LOCATION=global`.

## Choosing a metric

```
Do you have a reference answer?
  yes: does the exact wording matter?
         yes -> response_match_score      (cheap, ROUGE-1)
         no  -> final_response_match_v2   (semantic, LLM-judged)
  no:  what do you want to check?
         tool calls        -> tool_trajectory_avg_score (needs the expected calls)
         quality rules     -> rubric_based_final_response_quality_v1
         groundedness      -> hallucinations_v1
         harmlessness      -> safety_v1
         multi-turn goal   -> multi_turn_task_success_v1
```

## Folder layout

| Folder | Metric |
|---|---|
| `01_tool_trajectory/` | `tool_trajectory_avg_score` |
| `02_response_match/` | `response_match_score` |
| `03_final_response_match_v2/` | `final_response_match_v2` |
| `04_rubric_based/` | `rubric_based_final_response_quality_v1` |
| `05_hallucinations/` | `hallucinations_v1` |
| `06_safety/` | `safety_v1` |
| `07_multi_turn_task_success/` | `multi_turn_task_success_v1` |

## Common errors

| Error | Cause |
|---|---|
| `ValueError` about an empty rubric list | A rubric metric with no rubrics in the criterion or the eval case. |
| `safety_v1` / `multi_turn_task_success_v1` fail with auth or project errors | They call the Agent Platform Eval SDK; set `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` and run `gcloud auth application-default login`. |

## Clean up

From `01_test_file_anatomy`, `rm -rf weather_agent/.adk` removes the eval history.
