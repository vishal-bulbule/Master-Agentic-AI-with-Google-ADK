<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 06 - A Custom Rubric

## What this shows

Some questions have no single right answer, but a good answer still has attributes you
can check. Rubrics express those attributes in words, and an LLM judge assesses each one.

This topic evaluates a small research agent on one rubric: does the response include the
source URL? The test cases have no `final_response` at all; the rubric metric does not
need a reference.

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)). The root `requirements.txt` installs
  `google-adk[eval]` (ROUGE and the judge models) plus `pytest` and `pytest-asyncio`.
- Credentials: copy `research_agent/.env.example` to `research_agent/.env` and fill it in
  (`conftest.py` loads it). Gemini API key, or Agent Platform (formerly Vertex AI) with
  `gemini-3.5-flash` on location `global`; the judge uses the same model.

## Run it

1. `cd Module_14_Evaluation_Observability/06_rubric_metric`
2. `pytest -v -s`

To try the agent by hand: `adk web` from this folder, select `research_agent`, and send
"Who is Ada Lovelace?". The reply should end with
`Source: https://en.wikipedia.org/wiki/Ada_Lovelace`.

## What to look for

- For each invocation the judge gets the user prompt, the agent's final response, and
  the rubric text, and answers yes or no with a rationale. The rationale is in the
  printed results table; read it when a case fails.
- With `num_samples: 3` the judge is called three times per invocation and the votes
  are aggregated. Three cases cost 3 agent runs plus 9 judge calls.
- Break the agent on purpose: remove the "Always include the URL" sentence from the
  instruction and rerun. The rubric score drops and the test fails.

## Files

- `research_agent/` - answers "who is X?" from a lookup tool that returns a fact and a URL.
- `tests/rubric.test.json` - three cases, one query each, plus the expected tool call.
- `tests/test_config.json` - `rubric_based_final_response_quality_v1` with one rubric,
  `cites_a_source_url`, judged by `gemini-3.5-flash` with 3 samples per invocation.
- `tests/test_rubric.py` - runs the eval through `AgentEvaluator.evaluate`.
- `conftest.py` - puts this folder on `sys.path` and loads `research_agent/.env`.

## Writing rubrics

If the judge is too lenient, make the rubric more specific. The rubric used here already
rules out a vague answer:

> The response includes an http(s):// URL pointing to the source the agent used. A
> hand-wave like 'see Wikipedia' without an actual link does not count.

Treat rubric wording like prompt wording: test it against answers that should pass and
answers that should fail before you rely on it in CI.

## Clean up

Nothing to clean up. Delete `research_agent/.adk/` if you used `adk web`.
