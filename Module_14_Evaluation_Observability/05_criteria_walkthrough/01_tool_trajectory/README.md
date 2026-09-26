<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# tool_trajectory_avg_score

## What this shows

Compares the tool calls the agent made in each invocation with the expected
`tool_uses` in the test file. An invocation scores 1.0 on a match and 0.0 otherwise; the
case score is the average over invocations.

Match types (`match_type`):

- `EXACT` (default): same tool names, same arguments, same order, no extra calls.
- `IN_ORDER`: the expected calls appear in that order; extra calls in between are allowed.
- `ANY_ORDER`: the expected calls all appear, in any order; extra calls are allowed.

Arguments are compared exactly. Set `"ignore_args": true` to compare tool names only,
for tools whose arguments are free text.

Use it for CI and regression checks. It is cheap, deterministic, and needs no judge model.

## Prerequisites

- The repository setup ([SETUP.md](../../../SETUP.md)); `google-adk[eval]` is in the root
  `requirements.txt`.
- The topic 01 agent's credentials in `01_test_file_anatomy/weather_agent/.env` (copy its
  `.env.example`). The command below reuses that agent and test file.

## Run it

1. `cd Module_14_Evaluation_Observability/01_test_file_anatomy`
2. Run:

   ```bash
   adk eval weather_agent tests/weather.test.json \
       --config_file_path=../05_criteria_walkthrough/01_tool_trajectory/test_config.json \
       --print_detailed_results
   ```

## What to look for

- Per invocation, the expected and actual tool calls side by side, scored 1.0 or 0.0.
- Both weather cases pass: each makes exactly one `get_weather` call with the expected
  `city`. Change `"Paris"` to `"paris"` in the test file and the Paris case fails,
  because arguments are compared exactly.

## Clean up

From `01_test_file_anatomy`, `rm -rf weather_agent/.adk` removes the eval history.
