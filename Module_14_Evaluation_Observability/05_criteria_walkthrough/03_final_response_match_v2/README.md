<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# final_response_match_v2

## What this shows

An LLM judge sees the user prompt, the agent's answer, and the reference answer, and
labels the answer valid or invalid. `num_samples` is the number of judge calls per
invocation; the majority label wins. The threshold is the fraction of invocations that
must be valid.

Use it when you trust the reference answer but the wording may vary.

Cost: each invocation pays `num_samples` judge calls, on top of the agent run.

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
       --config_file_path=../05_criteria_walkthrough/03_final_response_match_v2/test_config.json \
       --print_detailed_results
   ```

## What to look for

- One valid or invalid label per invocation, the majority of 5 judge samples.
- Reword a reference answer in `tests/weather.test.json` without changing its meaning:
  this metric still passes where `response_match_score` would drop.

## Clean up

From `01_test_file_anatomy`, `rm -rf weather_agent/.adk` removes the eval history.
