<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 01 - Anatomy of a Test File

## What this shows

A `*.test.json` file is the smallest unit of evaluation in ADK. It holds one or more
eval cases, each a short session that the evaluator replays against your agent. The
file is an `EvalSet` (see `google/adk/evaluation/eval_set.py` and `eval_case.py`), the
same schema used by the larger `*.evalset.json` files in topic 02.

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)). The root `requirements.txt` installs
  `google-adk[eval]` (ROUGE and the judge models) plus `pytest` and `pytest-asyncio`.
- Credentials: copy `weather_agent/.env.example` to `weather_agent/.env` and fill it in.
  Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`.

## Run it

1. `cd Module_14_Evaluation_Observability/01_test_file_anatomy`
2. `adk eval weather_agent tests/weather.test.json --print_detailed_results`

No `test_config.json` sits next to the test file, so `adk eval` uses the default
criteria: `tool_trajectory_avg_score` 1.0 and `response_match_score` 0.8.

To try the two cases by hand: `adk web` from this folder, select `weather_agent`, and
send "What's the weather in Paris?" and "Weather in Atlantis please.". The Events view
shows the `get_weather` call the test file expects.

## What to look for

- `tests/weather.test.json` has two cases: a happy path (Paris) and a not-found path
  (Atlantis) that exercises the tool's `not_found` status.
- The detailed results table shows, per invocation, the expected and actual tool calls
  and responses, and the score for each metric.
- The agent instruction pins the exact wording of the not-found reply. Without that,
  the Atlantis case fails `response_match_score` (the model phrases its apology
  differently each run, and ROUGE-1 only counts shared words). Remove the pinned
  wording and rerun to see it; topic 05 covers the semantic alternative
  (`final_response_match_v2`).
- Results are also written to `weather_agent/.adk/eval_history/`. That folder is
  local run history; do not commit it.

## The skeleton

```jsonc
{
  "eval_set_id": "weather_unit_tests",            // unique id for this file
  "eval_cases": [{                                 // one entry per scenario
    "eval_id": "case_1_paris_happy_path",          // case id, used to run one case
    "conversation": [{                             // ordered list of invocations (turns)
      "invocation_id": "inv-1",
      "user_content":   { "parts": [{"text": "What's the weather in Paris?"}], "role": "user" },
      "final_response": { "parts": [{"text": "Sunny, 22 C."}], "role": "model" },
      "intermediate_data": {                       // expected tool trajectory
        "tool_uses": [{ "name": "get_weather", "args": {"city": "Paris"} }],
        "intermediate_responses": []
      }
    }],
    "session_input": { "app_name": "weather_agent", "user_id": "test_user", "state": {} }
  }]
}
```

| Field | Purpose |
|---|---|
| `user_content` | The message the evaluator sends to the agent. |
| `final_response` | The reference answer. Used by `response_match_score` and `final_response_match_v2`. |
| `intermediate_data.tool_uses` | The expected tool calls, compared by `tool_trajectory_avg_score`. |
| `session_input` | App name, user id, and initial session state for the case. |

The models use `extra="forbid"`, so a misspelled key fails validation instead of being
ignored. Both `snake_case` and `camelCase` keys are accepted.

## Common errors

| Error | Cause |
|---|---|
| `ValidationError ... Extra inputs are not permitted` | A misspelled key in the JSON. |
| `Exactly one of conversation and conversation_scenario must be provided` | A case has neither (or both). |
| `ModuleNotFoundError: No module named 'rouge_score'` | Eval extras missing: `pip install "google-adk[eval]"`. |

## Clean up

`adk eval` writes run history to `weather_agent/.adk/eval_history/`. Delete it with
`rm -rf weather_agent/.adk`.
