<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 05: Agentic RAG

## What this shows

Naive RAG embeds the user's words and returns the nearest chunks. In agentic
RAG the model drives retrieval: it builds the query, picks metadata filters,
and searches again when the first attempt misses. Here that is two function
tools over a mock vector store of 8 chunks: `construct_query(user_intent)`
returns a query string and suggested filters (`category`, `level`), and
`vector_search(query, filters)` returns the top 3 chunks that match the
filters, or `no_results`. The instruction makes the model call
`construct_query` first and retry with empty filters on `no_results`. It costs
at least two model round trips per answer instead of one; it pays off when
queries need metadata filters, when user wording differs from the corpus, or
when a second retrieval is needed after reading the first results. Replace the
body of `vector_search` with a call to your vector database and the agent does
not change.

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials go in a `.env` at the repository root or in the `agent/` folder; `agent/.env.example` lists the variables (a Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_13_Grounding/05_agentic_rag`
2. `adk web`
3. Open http://localhost:8000 and select `agent` in the agent dropdown (the agent folder is named `agent`).
4. Send: `How do I deploy an agent to production?`

Terminal alternative: `adk run agent`.

## Try it

Each in a new session:

```
How do I deploy an agent to production?
Where do I learn about MCP basics?
What is hybrid search good for?
```

## What to look for

- Events view: `construct_query`, then one or more `vector_search` calls, then
  an answer ending with a `Sources:` list of chunk IDs.
- "How do I deploy an agent to production?" shows the retry: the keyword
  rules guess `category=adk, level=advanced` (because of "agent" and
  "production"), the filtered search returns `no_results`, and the model
  searches again with `{}` and finds chunk `c07`. A bad filter guess costs one
  extra tool call instead of a wrong answer.
- The model sometimes adds a search of its own with a rewritten query. That
  is the agentic part: the retrieval plan is the model's, not fixed code.

## Clean up

`adk web` and `adk run` keep sessions in `agent/.adk/session.db`. Delete it to start clean: `rm -rf agent/.adk`
