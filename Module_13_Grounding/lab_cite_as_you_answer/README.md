<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Lab: cite as you answer

## What this shows

A research agent that follows every factual claim with an inline
`[source: URL]` citation, and an `adk eval` test that checks it does. The agent
uses Google Search grounding (`tools=[google_search]`), and its instruction
makes inline citations mandatory and shows an example. `tests/` holds five
time-sensitive questions (current news, demographics, release notes, sports
results, a published service commitment), each unreliable when answered from
training data. `rubric_based_final_response_quality_v1` has an LLM judge read
each answer against one rubric: factual claims are followed by
`[source: <URL>]` tags with an http(s) link. There is no reference answer.

| File | Purpose |
|---|---|
| `agent/agent.py` | `root_agent` with the cite-as-you-answer instruction |
| `tests/cite_as_you_answer.test.json` | The five questions, one eval case each |
| `tests/test_config.json` | The rubric, judged by `gemini-3.5-flash`, pass threshold 0.8 |

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials go in a `.env` at the repository root or in the `agent/` folder; `agent/.env.example` lists the variables (a Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`). The eval needs the `eval` extra, which the root `requirements.txt` already installs (`google-adk[a2a,eval]`).

## Run it

1. `cd Module_13_Grounding/lab_cite_as_you_answer`
2. `adk web`
3. Open http://localhost:8000 and select `agent` in the agent dropdown.
4. Send: `What is the current estimated population of Bengaluru, India?`

Terminal alternative: `adk run agent`.

To check all five questions at once:

```bash
adk eval agent tests/cite_as_you_answer.test.json --config_file_path tests/test_config.json
```

It runs the agent on each question (a fresh session per case), asks the judge
once per answer, and prints `Tests passed: 5` / `Tests failed: 0`. Add
`--print_detailed_results` to see each answer and the judge's verdict.

## Try it

Send each in a new session:

```
What were the most significant AI announcements at Google I/O 2026?
What is the current estimated population of Bengaluru, India?
What new features did Cloud Run release in the last six months?
Who won the most recent FIFA World Cup final, and against whom?
What is the monthly uptime SLA for Gemini models on Google Cloud?
```

## What to look for

- Every sentence with a fact ends with `[source: https://...]`. The URLs are
  grounding redirect links (`vertexaisearch.cloud.google.com/grounding-api-redirect/...`)
  that resolve to the real pages.
- Events view: click the final response row; the raw JSON view in the side
  panel shows `groundingMetadata` with `groundingChunks`, which proves the
  model searched. The judge sees only the
  answer text, so the eval checks the formatting the instruction asks for,
  not the metadata.
- The rubric discriminates: run the same eval against the ungrounded agent
  from topic 01 (`adk eval ../01_no_grounding_baseline/agent tests/cite_as_you_answer.test.json --config_file_path tests/test_config.json`)
  and all five cases fail.
- For a stricter check, tighten the rubric text (for example, require every
  sentence to end with a tag) and raise `num_samples` in `tests/test_config.json`
  so the judge votes several times per answer.

## Clean up

`adk web` and `adk run` keep sessions in `agent/.adk/session.db`, and
`adk eval` writes results to `agent/.adk/eval_history/`. Delete them with
`rm -rf agent/.adk`
