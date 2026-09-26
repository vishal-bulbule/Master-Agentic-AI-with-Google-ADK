<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 04 - Running Evals from the Shell

## What this shows

`adk eval` runs an eval set against an agent from the command line. It is the form you
use for one-off "did my prompt change break anything?" checks and for scripts.

```bash
adk eval \
    <AGENT_MODULE_FILE_PATH> \
    <EVAL_SET_FILE_PATH>[:eval_id1,eval_id2] ... \
    [--config_file_path=<PATH_TO_CONFIG>] \
    [--print_detailed_results]
```

| Argument / flag | Purpose |
|---|---|
| `AGENT_MODULE_FILE_PATH` | Agent folder containing `__init__.py` and `agent.py` with `root_agent`. |
| `EVAL_SET_FILE_PATH` | One or more `.test.json` / `.evalset.json` files. Append `:id1,id2` to run only those cases. |
| `--config_file_path` | Criteria file. If omitted and you pass a single eval file, `adk eval` uses `test_config.json` in the same folder, or the defaults. |
| `--print_detailed_results` | Per-invocation table with expected vs actual responses and tool calls. |
| `--eval_storage_uri` | `gs://<bucket>` to read eval sets from and write results to Cloud Storage. |

`adk eval` loads the `.env` nearest to the agent folder, and writes each run to
`<agent folder>/.adk/eval_history/*.evalset_result.json`.

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)). The root `requirements.txt` installs
  `google-adk[eval]` (ROUGE and the judge models) plus `pytest` and `pytest-asyncio`.
- Credentials for the topic 01 agent, which this topic reuses: copy
  `../01_test_file_anatomy/weather_agent/.env.example` to
  `../01_test_file_anatomy/weather_agent/.env` and fill it in.

## Run it

1. `cd Module_14_Evaluation_Observability/04_run_cli`
2. `bash run_eval.sh`

Run one case only:

1. `cd Module_14_Evaluation_Observability/01_test_file_anatomy`
2. `adk eval weather_agent tests/weather.test.json:case_1_paris_happy_path`

## What to look for

- The `Eval Run Summary` block with passed and failed counts, then one table per case.
- `adk eval` exits with status 0 even when cases fail. `run_eval.sh` greps the summary
  and exits 1 on failure; use that pattern, or the pytest form from topic 03, when the
  result must gate a pipeline.

## Clean up

Delete the eval history `adk eval` wrote:
`rm -rf ../01_test_file_anatomy/weather_agent/.adk`.
