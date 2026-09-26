<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Structured Output (`output_schema`)

## What this shows

The agent's final reply is constrained to JSON matching a Pydantic model
(`CapitalOutput`). Because `output_key="found_capital"` is also set, ADK
stores the parsed result in session state as a dict, where later agents,
tools or your own code can read it without parsing prose.

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
3. Open http://localhost:8000 and select `structured_output` in the agent dropdown.
4. Send: "What is the capital of Japan?"

Terminal alternative: `adk run structured_output`.

## What to look for

- The reply is a bare JSON object:
  `{"country": "Japan", "capital": "Tokyo", "confidence": 0.95}`.
- State tab: `found_capital` holds the same data as a dict. In the Events
  view, click the final model row: the side panel shows it in
  `actions.stateDelta`.
- Try "Capital of Atlantis?". The reply still matches the schema; watch
  what the model does with `confidence`.

## Using this from Python

To check the contract in your own code, validate what landed in state:

```python
from structured_output.agent import CapitalOutput

# session: from session_service.get_session(...) after the run
typed = CapitalOutput.model_validate(session.state["found_capital"])
```

## Notes

This agent has no tools to keep the example small. Current ADK versions
support `output_schema` together with `tools`: tools run during the
reasoning loop and the schema applies only to the final answer. Older
samples split tool calling and formatting into two agents; that pattern
works but is no longer required.
