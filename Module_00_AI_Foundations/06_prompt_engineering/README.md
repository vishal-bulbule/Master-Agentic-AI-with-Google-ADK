<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Prompt engineering: the four pillars

## What this shows

The same refactoring request sent twice: once as a vague one-liner, once
with a role, a task, constraints and one example. The structured prompt
leaves the model far less to guess.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and `pip install -r requirements.txt`.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`.env.example`](.env.example): `GOOGLE_API_KEY`, or
      Agent Platform (formerly Vertex AI) with `GOOGLE_GENAI_USE_ENTERPRISE=TRUE`,
      `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION=global`
      (`gemini-3.5-flash` is served from `global`).

## Run it

1. `cd Module_00_AI_Foundations/06_prompt_engineering`
2. `python four_pillars.py`

## What to look for

- SLOPPY: a style lecture and extra variants, in markdown.
- STRUCTURED: usually only the refactored function with type hints and a
  docstring, because the constraints and example say so.

The same four pillars reappear as the structure of agent instructions in
Module 3.
