<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Basic Gemini calls

## What this shows

The primitive every agent is built on: one `generate_content` call with the
`google-genai` SDK, and what comes back. Four scripts:

| Script | What it shows |
|---|---|
| `basic_call.py` | One call, then every field of the response object, including `usage_metadata` |
| `basic_call_with_config.py` | `GenerateContentConfig` one setting at a time: temperature, output cap, system instruction, stop sequences, candidates, JSON mode, response schema, thinking, safety, a combined config |
| `compare_response_time.py` | The same call timed on Flash and Pro |
| `google_grounding.py` | Google Search grounding, with the queries and sources the model used |

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and `pip install -r requirements.txt`.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`.env.example`](.env.example): `GOOGLE_API_KEY`, or
      Agent Platform (formerly Vertex AI) with `GOOGLE_GENAI_USE_ENTERPRISE=TRUE`,
      `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION=global`
      (`gemini-3.5-flash` is served from `global`).
- [ ] For the Pro side of `compare_response_time.py`: access to
      `gemini-2.5-pro`. If your project blocks it, the script prints the
      error for that model and continues.

## Run it

1. `cd Module_00_AI_Foundations/01_genai_basic_call`
2. `python basic_call.py`
3. `python basic_call_with_config.py` (all ten examples) or
   `python basic_call_with_config.py 7` (one example, numbered as in the script)
4. `python compare_response_time.py`
5. `python google_grounding.py`

## What to look for

- `basic_call.py`: `usage_metadata.thoughts_token_count` is the reasoning
  the model did before answering. It is billed as output.
- `basic_call_with_config.py 2`: `finish_reason` is `MAX_TOKENS` and the
  text is cut off. Thinking tokens count against the cap.
- `basic_call_with_config.py 7`: `response.parsed` is a list of Pydantic
  objects, not text.
- `compare_response_time.py`: the latency gap between Flash and Pro.
- `google_grounding.py`: an answer about a current release, followed by the
  search queries and source URLs from `grounding_metadata`. Remove the
  `tools` line from the config and run again to compare with an
  ungrounded answer.
