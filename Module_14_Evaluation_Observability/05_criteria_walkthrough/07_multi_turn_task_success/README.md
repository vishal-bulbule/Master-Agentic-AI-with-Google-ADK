<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# multi_turn_task_success_v1

## What this shows

Looks at the whole multi-turn conversation and decides whether the agent achieved the
user's goal. It delegates to the Agent Platform Gen AI Eval SDK.

Use it for chat agents where success is an outcome ("the user got their refund"), not a
particular phrasing or tool trajectory.

Pairs well with user simulation (topic 07): an eval case with a `conversation_scenario`
lets ADK's user simulator drive the conversation, and this metric scores the result.

## Prerequisites

- The repository setup ([SETUP.md](../../../SETUP.md)); `google-adk[eval]` is in the root
  `requirements.txt`.
- The topic 01 agent's credentials in `01_test_file_anatomy/weather_agent/.env` (copy its
  `.env.example`). The command below reuses that agent and test file.
- A Google Cloud project with the Agent Platform API enabled
  (`gcloud services enable aiplatform.googleapis.com --project=your-project-id`),
  application default credentials (`gcloud auth application-default login`), and
  `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` set in
  `01_test_file_anatomy/weather_agent/.env`. Your identity needs `roles/aiplatform.user`.

## Run it

1. `cd Module_14_Evaluation_Observability/01_test_file_anatomy`
2. Run:

   ```bash
   adk eval weather_agent tests/weather.test.json \
       --config_file_path=../05_criteria_walkthrough/07_multi_turn_task_success/test_config.json \
       --print_detailed_results
   ```

## What to look for

- One verdict per conversation: did the agent achieve the user's goal.
- The topic 01 cases are single-turn, and the metric reports them as `NOT_EVALUATED`
  with no score. That is expected: point it at a multi-turn eval set (topic 02's
  two-turn session, or a case with a `conversation_scenario`) for a real verdict.

## Clean up

From `01_test_file_anatomy`, `rm -rf weather_agent/.adk` removes the eval history.
