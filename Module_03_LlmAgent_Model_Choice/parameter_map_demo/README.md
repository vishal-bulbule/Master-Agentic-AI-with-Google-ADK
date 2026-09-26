<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# LlmAgent Parameter Map

## What this shows

One small agent that sets every commonly used `LlmAgent` field: `model`,
`name`, `description`, `instruction`, `tools`, `output_key`,
`include_contents` and `generate_content_config`. Each field in `agent.py`
has a comment explaining what it controls. Read the file as a reference card.

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
3. Open http://localhost:8000 and select `parameter_map_demo` in the agent dropdown.
4. Send: "Tell me a fact about Japan."

Terminal alternative: `adk run parameter_map_demo`.

## Try it

- "Tell me a fact about Japan."
- "What about France?" (works because `include_contents="default"` sends the previous turn)
- "Country: Mars" (the tool returns `status: error`)

## What to look for

- Events view: a `get_country_fact` function call and response before every answer.
- State tab: `last_country_fact` holds the latest reply. That is `output_key`.
- For Mars the agent apologizes instead of inventing a fact, because the
  instruction says how to handle an error status.
