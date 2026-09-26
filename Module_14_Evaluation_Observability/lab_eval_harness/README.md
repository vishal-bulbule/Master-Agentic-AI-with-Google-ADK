<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Lab 14 - Eval Harness and Traces

## What this shows

A repo-ready eval setup for one agent: 15 eval cases run by pytest, a CI workflow that
runs them on every push, and traces for any run from the `adk web` Traces view or Cloud
Trace. It combines topics 01 to 08 in the shape you would ship.

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)), or `pip install -r requirements.txt`
  from this folder (the same packages CI installs: `google-adk[eval]`, `pytest`,
  `pytest-asyncio`, `python-dotenv`, `opentelemetry-exporter-gcp-trace`).
- Credentials: copy `weather_agent/.env.example` to `weather_agent/.env` and fill it in.
  `conftest.py` loads it for pytest. Gemini API key, or Agent Platform (formerly Vertex
  AI) with `gemini-3.5-flash` on location `global`; the rubric judge also uses
  `gemini-3.5-flash`.
- For Cloud Trace (optional): the Cloud Trace API enabled, `roles/cloudtrace.agent` for
  your credentials, and `GOOGLE_CLOUD_PROJECT` exported in the shell (topic 08).
- For CI: a GitHub repository and a `GOOGLE_API_KEY` Actions secret (see CI setup).

```
lab_eval_harness/
|-- weather_agent/                 the agent under eval
|   |-- __init__.py
|   |-- agent.py
|   `-- .env.example
|-- tests/
|   |-- reference/
|   |   |-- weather_reference.test.json   10 cases with reference answers
|   |   `-- test_config.json              trajectory + ROUGE-1
|   |-- rubric/
|   |   |-- weather_rubric.test.json      5 cases, no reference, one rubric each
|   |   `-- test_config.json              trajectory + rubric judge
|   `-- test_weather.py                   pytest entry point
|-- conftest.py                    sys.path + .env loading for pytest
|-- requirements.txt
`-- .github/workflows/eval.yml     runs pytest on push and pull request
```

## The 15 cases

Reference-based (`tests/reference/`):

| eval_id | Checks |
|---|---|
| `happy_paris`, `happy_london`, `happy_tokyo`, `happy_mumbai`, `happy_new_york`, `happy_sydney` | Standard lookup. |
| `edge_unknown_city` | `not_found` path. |
| `edge_empty_city` | No city given: the agent must ask, and call no tool. |
| `edge_typo_pariis` | Typo: the agent must pass the name as written, not silently correct it. |
| `edge_multi_city_in_one_query` | Two cities: two `get_weather` calls, in order. |

Rubric-judged (`tests/rubric/`), each with its own case-level rubric plus the shared
`grounded_in_tool_output` rubric from `test_config.json`:

| eval_id | Case rubric |
|---|---|
| `rubric_concise_paris` | `concise` |
| `rubric_temp_included` | `includes_temperature` |
| `rubric_no_speculation` | `no_forecast` (asked about tomorrow) |
| `rubric_acknowledge_query` | `names_the_city` |
| `rubric_edge_polite_refusal` | `polite_refusal` |

The cases are split into two folders because criteria apply to every case in a file.
`response_match_score` against an empty reference scores 0, so rubric-only cases cannot
share a config with reference cases. `AgentEvaluator.evaluate` on the `tests/` folder
walks both subfolders and uses the `test_config.json` next to each file.

## Run it

Run the eval suite:

1. `cd Module_14_Evaluation_Observability/lab_eval_harness`
2. `pytest -v`

Look at the traces of the same questions:

1. `cd Module_14_Evaluation_Observability/lab_eval_harness`
2. `adk web` (or `adk web --trace_to_cloud` to also export to Cloud Trace)
3. Open http://localhost:8000 and select `weather_agent` in the agent dropdown.
4. Send, in one session: "What's the weather in Paris?", "How about London and Tokyo?",
   "What's it like in Atlantis?"
5. Click **Traces** (next to **Events**, top of the main panel).

## What to look for

- One suite run is 15 agent runs plus 15 judge calls (5 rubric cases, 3 samples each).
  `num_runs=1` in `test_weather.py` keeps it at that; raise it in CI for more stable
  results at a proportional cost.
- `response_match_score` is set to 0.4. The reference answers are phrased differently
  from the agent's answers, and ROUGE-1 scores in a test run ranged from about 0.48 to
  0.89. A threshold that is too tight makes CI flaky; one that is too loose passes wrong
  answers. Look at the scores in your own runs before picking it.
- In the Traces view, the two-city question produces two `execute_tool get_weather` spans
  from one model call, plus an `execute_tool (merged)` span: the model requested both
  calls in parallel and ADK ran them together. The Atlantis question
  shows the `not_found` result in the tool response and no invented weather.

## CI setup

1. Copy `.github/workflows/eval.yml` to `.github/workflows/` at the root of your
   repository and set `LAB_DIR` to this folder's path.
2. In the repository settings, under Secrets and variables, Actions, add a secret
   `GOOGLE_API_KEY` with a Gemini API key. The workflow uses the API key path; for
   Agent Platform, authenticate with `google-github-actions/auth` (Workload Identity
   Federation) and set `GOOGLE_GENAI_USE_ENTERPRISE`, `GOOGLE_CLOUD_PROJECT`, and
   `GOOGLE_CLOUD_LOCATION` instead. Module 15 topic 11 shows that setup.
3. Push. A failing case fails the `Run eval suite` step.
4. For a status badge, use the Actions page of the workflow: the "..." menu has
   "Create status badge".

## Clean up

`pytest` and `adk web` write nothing you need to keep; delete `weather_agent/.adk/` to
drop local sessions. If you added the workflow to a repository, delete the
`GOOGLE_API_KEY` secret there when you no longer need it.
