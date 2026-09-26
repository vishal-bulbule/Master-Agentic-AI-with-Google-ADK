<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 03 - Running Evals with pytest

## What this shows

The same kind of `.test.json` file from topic 01, driven by `pytest` so it runs in your
CI suite next to your unit tests.

`AgentEvaluator.evaluate(...)`:

1. Imports the agent module by name (`weather_agent`) and takes its `root_agent`.
2. Replays every case in the test file against the agent, `num_runs` times (default 2).
3. Scores each case with the criteria in `test_config.json` next to the test file, or
   the defaults (`tool_trajectory_avg_score` 1.0, `response_match_score` 0.8) if there
   is no config file.
4. Raises `AssertionError` listing every failed case, so pytest reports a normal
   failure.

`tests/test_weather.py` has two tests:

- `test_weather_agent_with_config_file` - criteria from `tests/test_config.json`
  (trajectory 1.0, response match 0.7).
- `test_weather_agent_trajectory_only` - loads the `EvalSet` and passes an `EvalConfig`
  built in code to `AgentEvaluator.evaluate_eval_set`.

`conftest.py` puts this folder on `sys.path` and loads `weather_agent/.env`. pytest does
not load `.env` files on its own; `adk eval` does.

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)). The root `requirements.txt` installs
  `google-adk[eval]` (ROUGE and the judge models) plus `pytest` and `pytest-asyncio`.
- Credentials: copy `weather_agent/.env.example` to `weather_agent/.env` and fill it in.
  Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on
  location `global`. `conftest.py` loads that file; pytest does not
  load `.env` files on its own.

## Run it

1. `cd Module_14_Evaluation_Observability/03_run_pytest`
2. `pytest -v` (add `-s` to see the per-case results tables as they print)

To chat with the same agent: `adk web` from this folder, select `weather_agent`, and
send "What's the weather in Paris?".

## What to look for

- Each test prints a results table per case before the pass/fail line. Run with
  `pytest -v -s` to see it live.
- `num_runs=1` keeps model calls low. In CI, raise it to 2 or 3: a flaky case that passes
  once and fails once is a real signal about your agent.
- Experimental-feature `UserWarning`s from `google.adk.evaluation` are expected; the
  eval APIs are marked experimental in ADK 2.x.

## Run one case

`AgentEvaluator.evaluate` runs every case in the file. To run one case, split the file,
or use the CLI: `adk eval weather_agent tests/weather.test.json:case_1_paris_happy_path`.

## Common errors

| Error | Cause |
|---|---|
| `ModuleNotFoundError: No module named 'weather_agent'` | `conftest.py` is missing, or `agent_module` does not match the agent folder name. |
| `ValueError: No API key was provided` | `weather_agent/.env` missing or empty. |
| `async def functions are not natively supported` | `pytest-asyncio` is not installed. |

## Clean up

Nothing to clean up. `adk web` creates `weather_agent/.adk/` for local sessions;
delete it if you used the dev UI.
