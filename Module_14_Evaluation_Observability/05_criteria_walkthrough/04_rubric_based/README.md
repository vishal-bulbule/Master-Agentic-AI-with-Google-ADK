<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# rubric_based_final_response_quality_v1

## What this shows

You describe quality in words instead of giving a reference answer. The judge assesses
each rubric as yes or no for every invocation; the invocation score is the fraction of
rubrics met, and the case score is the average over invocations.

Rubrics can be set on the criterion (apply to every case, as here), on an eval case
(`"rubrics"` inside the case), or on a single invocation. The effective list must not be
empty, and rubric ids must be unique across those levels.

Use it for open-ended responses with no single right answer: chat, summaries,
tone-sensitive copy. Topic `06_rubric_metric/` has a runnable example.

## Prerequisites

- The repository setup ([SETUP.md](../../../SETUP.md)); `google-adk[eval]` is in the root
  `requirements.txt`.
- The topic 01 agent's credentials in `01_test_file_anatomy/weather_agent/.env` (copy its
  `.env.example`). The command below reuses that agent and test file.
- The judge model is `gemini-3.5-flash`; on Agent Platform it needs location `global`.

## Run it

1. `cd Module_14_Evaluation_Observability/01_test_file_anatomy`
2. Run:

   ```bash
   adk eval weather_agent tests/weather.test.json \
       --config_file_path=../05_criteria_walkthrough/04_rubric_based/test_config.json \
       --print_detailed_results
   ```

## What to look for

- A yes or no verdict per rubric per invocation, with the judge's rationale.
- The score is the fraction of rubrics met; read the rationale of any rubric that fails
  before changing the rubric text.

## Clean up

From `01_test_file_anatomy`, `rm -rf weather_agent/.adk` removes the eval history.
