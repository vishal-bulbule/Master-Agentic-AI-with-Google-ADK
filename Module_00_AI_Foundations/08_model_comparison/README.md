<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Model comparison

## What this shows

One reasoning prompt on Flash and on Pro, with wall-clock latency, input
tokens, output tokens and thinking tokens for each. Pick the smallest model
that answers correctly.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and `pip install -r requirements.txt`.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`.env.example`](.env.example): `GOOGLE_API_KEY`, or
      Agent Platform (formerly Vertex AI) with `GOOGLE_GENAI_USE_ENTERPRISE=TRUE`,
      `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION=global`
      (`gemini-3.5-flash` is served from `global`).
- [ ] Access to `gemini-2.5-pro` for the Pro side. If your project blocks
      it, the script prints the error for that model and continues.

## Run it

1. `cd Module_00_AI_Foundations/08_model_comparison`
2. `python compare_models.py`

## What to look for

Both models should answer "2 hours". Compare `thinking=` and the latency:
the thinking tokens are billed as output, so they drive most of the cost
difference on a question this small.
