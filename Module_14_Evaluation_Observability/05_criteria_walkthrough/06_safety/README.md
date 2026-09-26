<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# safety_v1

## What this shows

Scores the harmlessness of the agent's response by delegating to the Agent Platform
(formerly Vertex AI) Gen AI Eval SDK. The criterion is a plain float threshold; a score
closer to 1.0 is safer.

Use it for any user-facing agent.

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
       --config_file_path=../05_criteria_walkthrough/06_safety/test_config.json \
       --print_detailed_results
   ```

## What to look for

- A harmlessness score per invocation from the Agent Platform Gen AI Eval service.
  A weather answer scores close to 1.0.

## Clean up

From `01_test_file_anatomy`, `rm -rf weather_agent/.adk` removes the eval history.
