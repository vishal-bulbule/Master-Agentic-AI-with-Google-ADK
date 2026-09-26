<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Streaming

## What this shows

`generate_content_stream` returns an iterator of partial responses. Printing
each chunk as it arrives is what makes chat UIs feel responsive: the first
words show up long before the full answer is finished. ADK streams the same
way in `adk web`.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and `pip install -r requirements.txt`.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`.env.example`](.env.example): `GOOGLE_API_KEY`, or
      Agent Platform (formerly Vertex AI) with `GOOGLE_GENAI_USE_ENTERPRISE=TRUE`,
      `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION=global`
      (`gemini-3.5-flash` is served from `global`).

## Run it

1. `cd Module_00_AI_Foundations/02_streaming`
2. `python streaming_call.py`

## What to look for

The haiku appears in pieces rather than all at once. Some chunks carry only
metadata and no text, which is why the script prints `chunk.text or ""`.
