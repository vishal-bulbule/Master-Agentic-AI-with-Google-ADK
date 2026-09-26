<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# response_match_score

## What this shows

ROUGE-1 (unigram overlap) between the agent's final response and the reference
`final_response` in the test file. The score is between 0 and 1, higher is better. The
criterion is a plain float threshold.

Use it for CI and regression checks with a hand-written reference answer. It is cheap
and deterministic.

Do not use it where many phrasings are valid. "Paris is in France." and "France
contains Paris." share few words, so ROUGE-1 scores them low even though they mean the
same. Use `final_response_match_v2` for that. An empty reference always scores 0.

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
       --config_file_path=../05_criteria_walkthrough/02_response_match/test_config.json \
       --print_detailed_results
   ```

## What to look for

- The ROUGE-1 score per invocation next to the 0.8 threshold.
- The Atlantis case passes only because the agent instruction pins the exact reply
  wording; that is the price of a word-overlap metric.

## Clean up

From `01_test_file_anatomy`, `rm -rf weather_agent/.adk` removes the eval history.
