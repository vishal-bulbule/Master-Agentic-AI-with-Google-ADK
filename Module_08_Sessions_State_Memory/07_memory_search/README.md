<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 07 Memory search

## What this shows

Memory is long-term knowledge that outlives a session. It is filled by
copying finished sessions into a memory service, and queried from a tool with
`tool_context.search_memory(query)`.

```python
async def recall_facts(query: str, tool_context: ToolContext) -> dict:
    response = await tool_context.search_memory(query=query)
    snippets = [p.text for m in response.memories if m.content
                for p in m.content.parts if p.text]
    return {"status": "ok", "count": len(snippets), "snippets": snippets}
```

The `adk web` server exposes `add_session_to_memory` as
`PATCH /apps/{app}/users/{user}/memory`; the dev UI has no button for it.
ADK also ships built-in tools for this: `load_memory` (the model decides when
to search, used in the lab) and `preload_memory` (searches before every turn).

| Service | `--memory_service_uri` | Use |
|---|---|---|
| `InMemoryMemoryService` | `memory://` (the default) | Local development; keyword match; lost on restart |
| `VertexAiMemoryBankService` | `agentengine://<agent_engine_id>` | Agent Platform (formerly Vertex AI) Memory Bank: extracts facts with a model, semantic search |
| `VertexAiRagMemoryService` | `rag://<rag_corpus>` | Vector search over stored transcripts |

Swapping services changes only the URI; the tool code stays the same.

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)) and a `.env` with your Gemini
  settings (see `memory_agent/.env.example`; on Agent Platform use
  `GOOGLE_CLOUD_LOCATION=global`).
- `curl`, for adding a session to memory.
- Only for Memory Bank: an Agent Engine resource in your project; see the
  [Memory Bank overview](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview).
  This sample is tested with `memory://`.

## Run it

1. `cd Module_08_Sessions_State_Memory/07_memory_search`
2. `adk web --session_service_uri=memory:// --artifact_service_uri=memory:// --memory_service_uri=memory://`
3. Open http://localhost:8000 and select `memory_agent` in the agent dropdown.
4. Send: "My company is Acme Analytics and I am the founder."

## Try it

1. Copy the session id from the session dropdown (top bar) and add that
   session to memory (the dev UI user is `user`):

   ```bash
   curl -X PATCH http://127.0.0.1:8000/apps/memory_agent/users/user/memory \
     -H 'Content-Type: application/json' -d '{"session_id": "<session-id>"}'
   ```

2. Click **New Session** and ask: "What is my company?"

## What to look for

- In the new session, a `recall_facts` call whose response contains the
  sentence from the first session, and the answer "Acme Analytics".
- Ask the same question as a different user (over REST, `users/someone-else`):
  zero snippets. Memory is scoped per app and user.
- Skip step 1 and the new session cannot answer: memory holds only sessions
  that were added to it.
