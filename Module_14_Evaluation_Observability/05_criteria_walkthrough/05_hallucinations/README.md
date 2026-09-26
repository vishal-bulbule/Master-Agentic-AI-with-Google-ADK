<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# hallucinations_v1

## What this shows

A two-step LLM judge:

1. It splits the agent's response into sentences.
2. It labels each sentence against the available context (instructions, user prompt,
   tool definitions, tool outputs) as `supported`, `unsupported`, `contradictory`,
   `disputed`, or `not_applicable`.

The score is the fraction of sentences labeled `supported` or `not_applicable`. Higher
is better. No reference answer is needed.

Use it for grounded answers (RAG, tool-driven Q&A). It catches the agent stating facts
the tools did not return.

Set `evaluate_intermediate_nl_responses` to `true` to also check text that sub-agents
emit before the final answer.

## Prerequisites

- The repository setup ([SETUP.md](../../../SETUP.md)); `google-adk[eval]` is in the root
  `requirements.txt`.
- The topic 01 agent's credentials in `01_test_file_anatomy/weather_agent/.env` (copy its
  `.env.example`). The command below reuses that agent and test file.
- The judge model is `gemini-3.5-flash`; on Agent Platform it needs location `global`.

## Run it

1. `cd Module_14_Evaluation_Observability/01_test_file_anatomy`
2. Run:

   ```bash
   adk eval weather_agent tests/weather.test.json \
       --config_file_path=../05_criteria_walkthrough/05_hallucinations/test_config.json \
       --print_detailed_results
   ```

## What to look for

- The per-sentence labels (`supported`, `unsupported`, ...) and the fraction supported.
- The weather answers repeat the tool's `report` field, so they score high. An answer
  that adds a forecast the tool never returned would not.

## Clean up

From `01_test_file_anatomy`, `rm -rf weather_agent/.adk` removes the eval history.
