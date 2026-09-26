<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 02 - Test File vs Eval Set

## What this shows

`*.test.json` and `*.evalset.json` files use the same `EvalSet` schema. The difference
is what you put inside and how you run them.

|                   | Test file `*.test.json`   | Eval set `*.evalset.json` |
|-------------------|---------------------------|---------------------------|
| Sessions per file | one or a few short ones   | many full sessions        |
| Turns per session | 1 to 2                    | 5 to 20+                  |
| Use               | unit tests during dev     | regression / integration  |
| Runs on           | `pytest` and `adk eval`   | `adk eval` and the `adk web` Evals tab |
| Frequency         | every commit              | nightly / pre-release     |
| Authored via      | hand-written JSON         | usually recorded in `adk web`, then edited |

`AgentEvaluator.evaluate` in pytest only picks up files ending in `.test.json` when you
pass it a directory; `adk eval` takes any file name.

Start with test files. Move to eval sets when the agent is stable and you want to catch
regressions across realistic user journeys, not one hand-picked happy path.

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)). The root `requirements.txt` installs
  `google-adk[eval]` (ROUGE and the judge models) plus `pytest` and `pytest-asyncio`.
- Credentials: copy `customer_service/.env.example` to `customer_service/.env` and fill it in.
  Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`.

## Run it

1. `cd Module_14_Evaluation_Observability/02_eval_set`
2. `adk eval customer_service tests/customer_service.evalset.json --print_detailed_results`

`adk eval` picks up `tests/test_config.json` automatically because it sits next to the
single eval set file. Pass `--config_file_path` to use a different one.

To try the sessions by hand: `adk web` from this folder, select `customer_service`, and
send the eval set's opening lines: "Where is my order A100?", "I need to refund order
A102 for $49.", and "Refund order Z999 please.". The Events view shows `lookup_order`,
`issue_refund`, and `escalate_to_human` with the arguments the eval set expects.

## What to look for

- The two-turn session is scored per invocation; the case score is the average.
- `escalate_to_human` takes a `category` from a fixed list, not a free-text reason.
  Trajectory metrics compare arguments exactly, so a free-text argument can never match
  a reference. Design tool arguments you want to assert on as structured values, or set
  `"ignore_args": true` in the `tool_trajectory_avg_score` criterion.
- The reference answers are worded differently from what the model says. They still
  pass because `final_response_match_v2` judges meaning, not word overlap. Swap it for
  `"response_match_score": 0.8` and rerun to see the difference.

## What is in this folder

- `customer_service/` - an agent with `lookup_order`, `issue_refund`, and
  `escalate_to_human` tools.
- `tests/customer_service.evalset.json` - four sessions: shipping status, refund,
  unknown-order escalation, and a two-turn status-then-refund conversation. Each session
  has its own `eval_id` and `session_input`.
- `tests/test_config.json` - the criteria. `tool_trajectory_avg_score` with
  `IN_ORDER` matching (the expected calls must happen in that order, extra calls are
  allowed) and `final_response_match_v2` (an LLM judge decides whether the answer means
  the same as the reference).

## Clean up

Delete `customer_service/.adk/` (eval history and local sessions):
`rm -rf customer_service/.adk`.
