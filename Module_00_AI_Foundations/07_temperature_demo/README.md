<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Temperature and variance

## What this shows

One prompt, three runs each at temperature 0.0, 0.3 and 1.0. Low temperature
makes repeated runs look alike; higher temperature spreads them out. Gemini
3.x models are tuned for the default of 1.0, and Google recommends not
lowering it for these models: values below 1.0 can cause looping or weaker
reasoning. For consistent agent behavior, use a precise system instruction
and structured output instead.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and `pip install -r requirements.txt`.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`.env.example`](.env.example): `GOOGLE_API_KEY`, or
      Agent Platform (formerly Vertex AI) with `GOOGLE_GENAI_USE_ENTERPRISE=TRUE`,
      `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION=global`
      (`gemini-3.5-flash` is served from `global`).

## Run it

1. `cd Module_00_AI_Foundations/07_temperature_demo`
2. `python temperature_demo.py` (nine small model calls)

## What to look for

Three identical taglines at 0.0 and more variety at 1.0. With three runs per
setting the counts are noisy; run the script twice to see how much.
