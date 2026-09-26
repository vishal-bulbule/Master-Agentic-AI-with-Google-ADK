<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 01: No-grounding baseline

## What this shows

A plain `LlmAgent` with no tools and no retrieval. Its instruction tells it to
answer instead of declining, so time-sensitive questions get confident answers
from training data, with no sources and no indication of how current they
are. Run this first, then ask topic 02 the same questions.

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials go in a `.env` at the repository root or in the `agent/` folder; `agent/.env.example` lists the variables (a Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_13_Grounding/01_no_grounding_baseline`
2. `adk web`
3. Open http://localhost:8000 and select `agent` in the agent dropdown (the agent folder is named `agent`).
4. Send: `Who is the current US president?`

Terminal alternative: `adk run agent`.

## Try it

Each in a new session:

```
Who is the current US president?
What is the current Cloud Run price per vCPU-second?
What is the newest Gemini model?
```

## What to look for

- The model does not refuse. It answers with full confidence.
- Events view: one model response, no tool call. Click the response row: the
  raw JSON view in the side panel has no `groundingMetadata`.
- Anything that changed after the training cutoff is likely wrong. Asked for
  the newest Gemini model, it names one that is already old.
  Check prices against [cloud.google.com/run/pricing](https://cloud.google.com/run/pricing).

## Clean up

`adk web` and `adk run` keep sessions in `agent/.adk/session.db`. Delete it to start clean: `rm -rf agent/.adk`
