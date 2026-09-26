<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Module 13: Grounding

Grounding ties an agent's factual claims to a source it retrieved: Google
Search, your own indexed documents, or a retrieval pipeline you build. The
source travels back with the answer in `grounding_metadata` (or in your tool
results), so the answer can be checked.

## Topics

Follow them in order.

| Folder | What it shows |
|---|---|
| [`01_no_grounding_baseline/`](01_no_grounding_baseline/) | A tool-less agent answering time-sensitive questions from memory |
| [`02_google_search_grounding/`](02_google_search_grounding/) | The `google_search` built-in tool, and the same questions answered with sources |
| [`03_display_citations/`](03_display_citations/) | An `after_model_callback` that renders footnotes and a source list from `grounding_metadata` |
| [`04_vertex_search_tool/`](04_vertex_search_tool/) | `VertexAiSearchTool` over your own Vertex AI Search data store (needs cloud setup) |
| [`05_agentic_rag/`](05_agentic_rag/) | The model builds its own query and filters, and retries on a miss |
| [`06_hybrid_search/`](06_hybrid_search/) | Vector plus keyword retrieval fused with reciprocal rank fusion |
| [`07_when_not_to_use/`](07_when_not_to_use/) | Workloads where grounding costs more than it returns, with a cost table (no agent) |
| [`lab_cite_as_you_answer/`](lab_cite_as_you_answer/) | Lab: inline `[source: URL]` after every claim, checked by a 5-question `adk eval` rubric test |

## Before you start

- The repository setup in [SETUP.md](../SETUP.md): the Python environment from
  `requirements.txt` and credentials in a `.env` (a Gemini API key, or Agent
  Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`).
- Topics 02, 03, and the lab use Google Search grounding, billed per grounded
  request on top of tokens.
- Topic 04 only: Agent Platform credentials (a Gemini API key does not work),
  the Google Cloud CLI, the Discovery Engine and Vertex AI APIs enabled, a
  Cloud Storage bucket with your documents, a Vertex AI Search data store
  built from it, and `VERTEX_AI_SEARCH_DATASTORE_ID` set to its full resource
  name. The steps are in [04_vertex_search_tool/README.md](04_vertex_search_tool/README.md).
- No extra packages. The lab's eval uses `google-adk[eval]`, already in the
  root `requirements.txt`.

## Running a topic

Each agent lives in a folder named `agent`, so the ADK app name is `agent`.
From the topic folder:

```bash
cd Module_13_Grounding/02_google_search_grounding
adk web              # dev UI at http://localhost:8000, select "agent"
adk run agent        # terminal chat
```

Grounding metadata is on the model response event: click that numbered row
in the dev UI's Events view and read it in the side panel (the raw JSON view
shows every field). Topic 07 is a worked cost table with nothing to run, and the
lab adds an `adk eval` command.

## Choosing an approach

| Need | Use |
|---|---|
| Current events, public web facts | Google Search grounding (topics 02, 03) |
| Internal documents, enterprise knowledge | Vertex AI Search (topic 04) |
| Metadata filters, query rewriting, multi-step retrieval | Agentic RAG (topic 05) |
| Best recall on a fixed corpus with exact IDs and paraphrases | Hybrid search (topic 06) |
| Pure reasoning, code, creative writing, stable FAQ answers | No grounding, or a cache (topic 07) |

Google Search and Vertex AI Search are built-in tools: the search runs inside
the Gemini call and there is no tool call event. Topics 05 and 06 use ordinary
function tools, so every retrieval step is visible as a tool call and you
control the ranking.
