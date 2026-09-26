<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 07 - User Simulation

## What this shows

A fixed test file does not work for multi-turn chats: the agent may ask for two things
at once or one at a time, and the user may answer in any order. ADK's built-in user
simulation replaces the fixed user turns. An eval case carries a
`conversation_scenario` (a `starting_prompt`, a `conversation_plan` and a
`user_persona`) instead of a `conversation`, an LLM plays the user, and `adk eval`
judges the whole conversation.

The agent under test, `subscription_agent`, handles cancellations with one retention
offer (50% off for three months). The eval set has two scenarios:

| Eval case | Persona | Plan | Rubric the conversation must meet |
|---|---|---|---|
| `determined_to_cancel` | Custom `FRUSTRATED_CUSTOMER`: blunt, refuses every offer | Give the email, refuse the discount, get cancelled | Cancelled with the access end date; at most one offer |
| `accepts_discount` | Pre-built `NOVICE` | Mention the price, accept the discount | Discount applied, not cancelled |

Two metrics in `tests/test_config.json` score each case:

- `rubric_based_multi_turn_trajectory_quality_v1`: an LLM judge reads the full
  conversation, tool calls included, and answers each rubric yes or no. The rubrics sit
  on each eval case with `type: TRAJECTORY_QUALITY`.
- `per_turn_user_simulator_quality_v1`: checks the simulated user itself stayed on the
  plan and in persona, so a failing case is not just a badly behaved simulator.

```
07_user_simulation/
  subscription_agent/
    __init__.py
    agent.py                       root_agent with three tools
    .env.example
  tests/
    user_simulation.evalset.json   two conversation_scenario eval cases
    test_config.json               metrics, rubric judge and user simulator settings
```

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)). The root `requirements.txt`
      installs `google-adk[eval]`; nothing extra.
- [ ] Credentials: copy `subscription_agent/.env.example` to `subscription_agent/.env`
      (or use the root `.env`). A Gemini API key, or Agent Platform (formerly Vertex
      AI) with `gemini-3.5-flash` on location `global`. The agent, the simulated user
      and the judge all use `gemini-3.5-flash`.

## Run it

1. `cd Module_14_Evaluation_Observability/07_user_simulation`
2. Run both scenarios:

   ```bash
   adk eval subscription_agent tests/user_simulation.evalset.json \
       --config_file_path tests/test_config.json \
       --print_detailed_results
   ```

3. One scenario only: append `:determined_to_cancel` to the eval set path.

A run takes one to two minutes and makes roughly 20 model calls (agent turns, simulated
user turns, and judge samples).

To talk to the agent yourself: run `adk web` in this folder, open
http://localhost:8000, pick `subscription_agent` in the app dropdown, and send "I want
to cancel my subscription. My email is sam@example.com." The Events view shows the
`get_subscription` tool call chip, the offer, and after you refuse, the
`cancel_subscription` call. Terminal alternative: `adk run subscription_agent`.

## What to look for

- `Eval Run Summary` with `Tests passed: 2`.
- The `Invocation Details` table for each case: the `prompt` column holds the user
  turns. Only turn 0 is the fixed `starting_prompt`; every later turn was written by the
  simulator from the plan and persona, and the wording changes on every run.
- `determined_to_cancel` usually takes three turns: the agent asks for the email, calls
  `get_subscription` and makes the offer, the user refuses, the agent calls
  `cancel_subscription`. The simulator then ends the conversation.
- The rubric metric shows `NOT_EVALUATED` on every turn but the last; the last turn
  carries the verdict and a `Reasoning:` column per rubric.
- Make the agent fail: remove `cancel_subscription` from `tools` in
  `subscription_agent/agent.py` and rerun `determined_to_cancel`. The rubric metric
  drops to 0.5 (the offer rubric still passes) and the case fails, while
  `per_turn_user_simulator_quality_v1` stays at 1.0: the user did its job, the agent did
  not.
- Run the eval several times. The pass rate, not a single run, answers "can a
  determined customer get out of the retention flow?"

## How the scenario and simulator are configured

A custom persona must tell the simulator when to stop. The pre-built personas
(`NOVICE`, `EXPERT`, `EVALUATOR`) include that behavior; `FRUSTRATED_CUSTOMER` adds it
as its own behavior with `{{ stop_signal }}` in the instructions. Without it the
simulator keeps chatting ("Bye.", "Stop replying.") until `max_allowed_invocations`.

`user_simulator_config` in `tests/test_config.json` sets the simulator model and
`max_allowed_invocations` (6 here; the initial prompt counts as one). The default model
is `gemini-flash-latest`.

To add scenarios without editing JSON by hand, write them to a scenarios file
(`{"scenarios": [...]}`) and a session input file
(`{"app_name": "subscription_agent", "user_id": "user"}`), then let the CLI create the
eval cases:

```bash
adk eval_set create subscription_agent my_scenarios
adk eval_set add_eval_case subscription_agent my_scenarios \
    --scenarios_file scenarios.json \
    --session_input_file session_input.json
```

The CLI writes `subscription_agent/my_scenarios.evalset.json` (inside the agent
folder, not `tests/`) with a generated id for each case.

With Agent Platform you can also score the goal with `multi_turn_task_success_v1`
(`"criteria": {"multi_turn_task_success_v1": {"threshold": 0.8}}`). It calls the Gen AI
Eval service, whose autorater is a Pro model (`gemini-3.1-pro-preview` when this was
written), so your project must be allowed to use it; see the module README for the
project setup.

## Common errors

| Symptom | Cause |
|---|---|
| Conversation runs to `max_allowed_invocations` with "Bye." turns | A custom persona without a stop behavior. |
| `ValueError` about empty rubrics | No rubrics in the config and none on the eval case with `type: TRAJECTORY_QUALITY`. |
| No output for minutes after `Stopping user message generation` | A judge request stalled (the eval has no per-request timeout). Stop it with Ctrl+C and rerun. |
| `FAILED_PRECONDITION` for an autorater model | `multi_turn_task_success_v1` needs the Gen AI Eval service and access to its Pro autorater model. |

## Clean up

`adk eval` writes run history to `subscription_agent/.adk/eval_history/`. Delete
`subscription_agent/.adk/` to remove it.
