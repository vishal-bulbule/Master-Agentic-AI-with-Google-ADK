<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Module 14: Evaluation and Observability

Agents are non-deterministic: the same input gives different outputs from run to run,
so one green test run does not prove the agent works. This module covers how to measure
agent quality with ADK's eval framework, and how to see what an agent did with
OpenTelemetry traces.

## Topics

Follow them in order.

| Folder | What it shows |
|---|---|
| [`01_test_file_anatomy/`](01_test_file_anatomy/) | The `*.test.json` shape: user turn, reference answer, expected tool calls; run with `adk eval` |
| [`02_eval_set/`](02_eval_set/) | A multi-session `*.evalset.json` with `IN_ORDER` trajectories and a semantic judge |
| [`03_run_pytest/`](03_run_pytest/) | Evals inside pytest with `AgentEvaluator.evaluate` and `evaluate_eval_set` |
| [`04_run_cli/`](04_run_cli/) | `adk eval` flags, running single cases, and gating a script on the result |
| [`05_criteria_walkthrough/`](05_criteria_walkthrough/) | One `test_config.json` per built-in metric, and how to choose between them |
| [`06_rubric_metric/`](06_rubric_metric/) | A custom rubric ("the response cites a source URL") with no reference answer |
| [`07_user_simulation/`](07_user_simulation/) | Built-in user simulation: `conversation_scenario` eval cases, an LLM playing the user, rubric judge over the whole conversation (`adk eval`) |
| [`08_opentelemetry_traces/`](08_opentelemetry_traces/) | ADK's built-in spans in the `adk web` Traces view, and in Cloud Trace with `--trace_to_cloud` |
| [`09_safety_patterns/`](09_safety_patterns/) | Three safety layers as callbacks: input, tool permission, output |
| [`lab_eval_harness/`](lab_eval_harness/) | Lab: 15-case eval suite, CI workflow, and traces for one agent |

## Before you start

- Repository setup: [SETUP.md](../SETUP.md). The root `requirements.txt` already has
  `google-adk[eval]`, `pytest`, `pytest-asyncio`, and `opentelemetry-exporter-gcp-trace`;
  nothing extra to install.
- Credentials: a Gemini API key, or Agent Platform (formerly Vertex AI) with
  `gemini-3.5-flash` on location `global`. Each agent folder has a `.env.example`; copy
  it to `.env` in the same folder. `adk eval`, `adk web`, and `adk run` load it; the
  pytest topics load it in `conftest.py`.
- Google Cloud, only where noted:
  - `safety_v1` and `multi_turn_task_success_v1` (topic 05) call the Agent Platform Gen
    AI Eval service: a project with `aiplatform.googleapis.com` enabled, application
    default credentials, and `roles/aiplatform.user`.
  - Cloud Trace export (topic 08 and the lab, optional): `cloudtrace.googleapis.com`
    enabled, `roles/cloudtrace.agent`, and `GOOGLE_CLOUD_PROJECT` exported in the shell.
- For the lab's CI workflow: a GitHub repository and a `GOOGLE_API_KEY` Actions secret.

## Logs, metrics, traces

| Signal | Question it answers | Best for |
|---|---|---|
| Logs | What happened? | Errors, audit trails, ad-hoc search |
| Metrics | How much, how often, how long? | Dashboards, alerts, SLOs |
| Traces | Where did the time go, step by step? | Slow agents, tool-call waterfalls |

For agents, traces matter most: each model call, tool call, and sub-agent run is a span,
so a trace shows which step took 8 seconds or 5,000 tokens.

## Notes

- `adk eval` writes run history to `<agent folder>/.adk/eval_history/`. Do not commit it.
- The eval APIs are marked experimental in ADK 2.x and print `UserWarning`s; that is
  expected.
