<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Generation Config

## What this shows

`generate_content_config` passes a `google.genai.types.GenerateContentConfig`
to every model call the agent makes. This agent sets `temperature=1.0`, the
value Gemini 3.x models are tuned for, and a `max_output_tokens` cap. You
compare it against `temperature=0` by sending the same prompt in several
fresh sessions.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`.env.example`](.env.example): `GOOGLE_API_KEY`, or
      Agent Platform (formerly Vertex AI) with `GOOGLE_CLOUD_LOCATION=global`
      (`gemini-3.5-flash` is served from `global`).

## Run it

1. `cd Module_03_LlmAgent_Model_Choice`
2. `adk web`
3. Open http://localhost:8000 and select `generation_config` in the agent dropdown.
4. Send: "Give me a creative 3-word product tagline for an AI coding assistant."

Terminal alternative: `adk run generation_config`.

## Try it

1. Send the tagline prompt, click **New Session**, and send it again. Do
   this three times and note the answers.
2. In `agent.py`, change `temperature=1.0` to `temperature=0.0`, restart
   `adk web` (Ctrl+C, then `adk web`), and repeat step 1.

## What to look for

- At 1.0 the answers usually differ from session to session.
- At 0 they are more alike, but not identical: two fresh sessions at
  temperature 0 can still return two different taglines, and setting `seed` in
  the config does not make `gemini-3.5-flash` repeatable either. Do not build
  anything that depends on identical output.
- Three samples per setting are noisy; send more for a clearer signal.
- Events view: click the model response row. In the side panel,
  `usageMetadata` shows `thoughtsTokenCount`. Those thinking tokens count against
  `max_output_tokens` on Gemini 3.x.

| temperature | use for |
|---|---|
| 1.0 | the Gemini 3.x default; start here for every agent |
| 0.0 | narrow tasks such as classification, where you have measured that it helps |

Gemini 3.x models are tuned for 1.0, and Google recommends against lowering
it for reasoning-heavy work (see `Module_00_AI_Foundations/07_temperature_demo`).
Measure before you move away from 1.0.

## Common errors

| Symptom | Cause | Fix |
|---|---|---|
| Empty reply with a small `max_output_tokens` | Thinking used the whole budget | Raise the cap, or add `thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.MINIMAL)` to the config |
| `404 NOT_FOUND` for the model on Agent Platform | `GOOGLE_CLOUD_LOCATION` is a region | Set `GOOGLE_CLOUD_LOCATION=global` |
