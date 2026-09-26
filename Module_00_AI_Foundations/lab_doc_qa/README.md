<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Lab: doc-grounded Q&A (no framework)

## What this shows

A small CLI that retrieves documentation snippets, injects them into the
prompt, streams Gemini's answer and reports token usage and estimated cost.
It combines streaming (02), token counting (05) and MCP (09) without any
agent framework, so you can see what ADK later takes off your hands.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and `pip install -r requirements.txt`.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`.env.example`](.env.example): `GOOGLE_API_KEY`, or
      Agent Platform (formerly Vertex AI) with `GOOGLE_GENAI_USE_ENTERPRISE=TRUE`,
      `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION=global`
      (`gemini-3.5-flash` is served from `global`).

## Run it

1. `cd Module_00_AI_Foundations/lab_doc_qa`
2. Ask the four questions:

```bash
python doc_qa.py "How do I install ADK?"
python doc_qa.py "What's a Cloud Run cold start?"
python doc_qa.py "How do I deploy a Cloud Function with Secret Manager?"
python doc_qa.py "How do I configure Pub/Sub dead-letter topics?"
```

## What to look for

- The first three questions are answered from the matching `<doc>` and the
  answer cites it.
- The last question is not covered by the stub docs; the model should say so
  instead of answering from memory.
- The `out=` count includes thinking tokens, because they are billed as output.

## Extend it

`search_docs()` is a stub with three hardcoded snippets. Replace its body with
a call to a documentation MCP server, using the client code in
`../09_mcp_grounding/mcp_grounding.py`.
