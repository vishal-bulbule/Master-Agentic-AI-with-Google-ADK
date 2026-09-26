<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Capital agent

## What this shows

The minimal ADK agent: an `LlmAgent` with one tool, in the folder layout ADK
expects (`__init__.py` with `from . import agent`, and `agent.py` defining
`root_agent`). ADK builds the tool declaration from `get_capital`'s
signature and docstring.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`.env.example`](.env.example): `GOOGLE_API_KEY`, or
      Agent Platform (formerly Vertex AI) with `GOOGLE_CLOUD_LOCATION=global`
      (`gemini-3.5-flash` is served from `global`).

## Run it

1. `cd Module_02_First_ADK_Agent`
2. `adk web`
3. Open http://localhost:8000 and select `capital_agent` in the agent dropdown.
4. Send: "What's the capital of Japan?"

Terminal alternative: `adk run capital_agent`.

## Try it

- "What's the capital of Japan?"
- "What's the capital of Peru?" (not in the tool's data)

## What to look for

- Events view: a `get_capital` call with `country: "Japan"`, the response
  `{"status": "success", "capital": "Tokyo"}`, then the answer. Click a row
  to see its details in the side panel.
- Peru: the tool returns `status: not_found` and the agent says it does
  not know instead of answering from memory, because the instruction tells it
  to rely on the tool.
