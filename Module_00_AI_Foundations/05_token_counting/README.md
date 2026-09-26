<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Token counting

## What this shows

`count_tokens` is a separate, free API call that tokenizes input without
generating anything. The script counts a few strings, then projects daily
and monthly cost for a workload from example per-token rates.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and `pip install -r requirements.txt`.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`.env.example`](.env.example): `GOOGLE_API_KEY`, or
      Agent Platform (formerly Vertex AI) with `GOOGLE_GENAI_USE_ENTERPRISE=TRUE`,
      `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION=global`
      (`gemini-3.5-flash` is served from `global`).

## Run it

1. `cd Module_00_AI_Foundations/05_token_counting`
2. `python token_counting.py`

## What to look for

- A long rare word costs several tokens; common words cost one.
- The projection is only as good as the rates at the top of the script.
  Replace `INPUT_USD_PER_M` and `OUTPUT_USD_PER_M` with the current prices
  for your model and API before you rely on it. Thinking tokens are billed at
  the output rate.
