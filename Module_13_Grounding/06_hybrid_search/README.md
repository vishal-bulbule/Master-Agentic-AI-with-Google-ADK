<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 06: Hybrid search

## What this shows

Dense (vector) and sparse (keyword) retrieval fail on different queries, so
production retrieval often runs both and fuses the rankings. Vector search
handles paraphrases and synonyms but misses exact IDs and rare tokens; keyword
search (BM25) is the reverse. Reciprocal rank fusion (RRF) merges ranked lists
using ranks only, because raw vector and keyword scores are on different
scales: `rrf_score(doc) = sum over lists of 1 / (k + rank)`, with `k = 60`.
`agent/agent.py` defines `vector_search`, `keyword_search`, and
`hybrid_search`; the agent gets only `hybrid_search`, whose result includes
the fused top 5 plus `vector_ranking` and `keyword_ranking`, so you can see
how the lanes disagreed. Both scorers are token-overlap stand-ins, not real
embeddings or BM25, so the sample runs offline. Production systems often add
a cross-encoder reranker over the top fused candidates: better ordering, at
the cost of one extra model call per candidate.

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials go in a `.env` at the repository root or in the `agent/` folder; `agent/.env.example` lists the variables (a Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_13_Grounding/06_hybrid_search`
2. `adk web`
3. Open http://localhost:8000 and select `agent` in the agent dropdown (the agent folder is named `agent`).
4. Send: `how do I ship my agent`

Terminal alternative: `adk run agent`.

## Try it

Each in a new session, then click the `hybrid_search` tool result row in the
Events view and read the response in the side panel:

| Send | `vector_ranking` | `keyword_ranking` | Fused |
|---|---|---|---|
| `how do I ship my agent` | d02, d03 | d03, d01, d02 | d03, d02, d01 |
| `BM25` | d06 | d06 | d06 |
| `reciprocal rank fusion for grounding` | d07, d05, d04 | d07, d04, d05, d09 | d07, d05, d04, d09 |

## What to look for

- `how do I ship my agent`: the lanes disagree. Vector ranks d02 ("Deploy an
  agent...") first; keyword ranks d03 ("Ship to production...") first and also
  pulls in d01 on the word "agent". RRF puts d03 and d02, which both lanes
  rank, above d01, which only one lane ranks.
- `BM25`: both lanes find d06, and RRF keeps it on top.
- One `hybrid_search` call per question, and an answer that ends with the doc
  IDs it used.

## Clean up

`adk web` and `adk run` keep sessions in `agent/.adk/session.db`. Delete it to start clean: `rm -rf agent/.adk`
