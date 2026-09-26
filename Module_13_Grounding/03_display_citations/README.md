<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 03: Display citations

## What this shows

A grounded agent that renders its own citations from `grounding_metadata`
instead of trusting URLs the model types. The model is told to keep URLs out
of the answer. An `after_model_callback`, `add_citations`, then inserts
footnote markers such as `[1][3]` after each supported span of the answer and
appends a numbered `Sources:` list. With streaming on, partial chunks pass
through unchanged and only the final response, which carries the metadata, is
rewritten.

| Field | What it is |
|---|---|
| `web_search_queries` | The queries the model ran |
| `grounding_chunks[i].web.uri`, `.title` | Source `i`: a redirect URL and the site's domain (Google Search) |
| `grounding_chunks[i].retrieved_context` | Source `i` when grounding on a data store (topic 04) |
| `grounding_supports[j].segment` | A span of the answer text, with `start_index` and `end_index` (UTF-8 byte offsets) |
| `grounding_supports[j].grounding_chunk_indices` | Which sources support that span |

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials go in a `.env` at the repository root or in the `agent/` folder; `agent/.env.example` lists the variables (a Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_13_Grounding/03_display_citations`
2. `adk web`
3. Open http://localhost:8000 and select `agent` in the agent dropdown (the agent folder is named `agent`).
4. Send: `What were the most significant announcements at Google Cloud Next 2026?`

Terminal alternative: `adk run agent`.

## What to look for

- The answer ends each supported sentence with markers like `[1][2]`, followed
  by `Sources:` and a numbered list of links. The link text is the site's
  domain; the URL is a `vertexaisearch.cloud.google.com/grounding-api-redirect/...`
  link that resolves to the real page.
- Events view: click the final response row; the raw JSON view in the side
  panel still shows the original `groundingMetadata`. Compare its `groundingSupports` segments with where the
  markers landed.
- Turn on streaming in the dev UI (More options > Streaming) and ask again: the text streams without
  markers, then the final message shows them.
- The same callback works for data store grounding (topic 04), where the
  sources come from `retrieved_context` instead of `web`.

## Common errors

| Symptom | Cause |
|---|---|
| No markers or `Sources:` list | The model answered without searching, so there is no `grounding_metadata`. Ask a question that needs current information. |

## Clean up

`adk web` and `adk run` keep sessions in `agent/.adk/session.db`. Delete it to start clean: `rm -rf agent/.adk`
