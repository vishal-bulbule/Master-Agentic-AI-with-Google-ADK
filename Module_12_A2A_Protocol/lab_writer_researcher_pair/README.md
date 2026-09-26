<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Lab: writer and researcher over A2A

## What this shows

Two agents in two processes, as they would be if two teams owned them. The
writer turns a request into a short brief; the researcher, served over A2A,
gathers the facts. The writer calls the researcher through
`AgentTool(RemoteA2aAgent(...))`, so the research comes back as a tool result
and the writer keeps control to draft the prose.

```
adk web (:8000)                           adk api_server --a2a (:8081)
writer                                    researcher
  LlmAgent                  -- A2A -->      LlmAgent
  tools=[AgentTool(                         tools=[mock_web_search]
    RemoteA2aAgent(researcher))]            card: researcher/agent.json
```

The researcher's `mock_web_search` returns fixed, fictional results, so the
lab needs no search API and gives the same facts on every run. Only
`researcher/` has an `agent.json` card, so `--a2a` serves only the researcher
over A2A.

```
lab_writer_researcher_pair/
  researcher/agent.py     LlmAgent with mock_web_search
  researcher/agent.json   A2A agent card, url http://localhost:8081/a2a/researcher
  writer/agent.py         LlmAgent with AgentTool(RemoteA2aAgent), calls :8081
```

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)).
- Credentials: copy `researcher/.env.example` and `writer/.env.example` to
  `.env` in the same folders (or use the root `.env`). Gemini API key, or Agent
  Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`.
- Port 8081 free for the researcher. To use another port, change the `url` in
  `researcher/agent.json` and set `RESEARCHER_URL` for the writer (see
  `writer/.env.example`).

## Run it

1. Terminal 1, the researcher:

   ```bash
   cd Module_12_A2A_Protocol/lab_writer_researcher_pair
   adk api_server --a2a --port 8081
   ```

2. Terminal 2, the writer, from the same folder:

   ```bash
   cd Module_12_A2A_Protocol/lab_writer_researcher_pair
   adk web
   ```

3. Open http://localhost:8000 and select `writer` in the agent dropdown.
4. Send: "Write a brief on AI agent adoption in 2026."

Terminal alternative for step 2: `adk run writer`.

## What to look for

- Events view: the writer calls the `researcher` tool once (sometimes twice).
  Click the tool result row: the response is the researcher's bullet points with `example.com`
  URLs; the final event is the writer's prose built from them.
- The final text cites sources inline as `(source: https://example.com/...)`
  and ends with a Sources list. Every URL comes from the mock results; any
  other URL was invented by the writer.
- Terminal 1 logs `GET /a2a/researcher/.well-known/agent-card.json`, then one
  `POST /a2a/researcher` per research call.
- The dropdown also lists `researcher`. Selecting it runs the researcher
  locally, in the dev UI process, without A2A.

To see the raw A2A wire format, call the researcher directly while terminal 1
is running:

```bash
curl -s http://localhost:8081/a2a/researcher \
  -H 'Content-Type: application/json' -H 'A2A-Version: 1.0' \
  -H 'A2A-Extensions: https://google.github.io/adk-docs/a2a/a2a-extension/' \
  -d '{"jsonrpc": "2.0", "id": "1", "method": "SendMessage",
       "params": {"message": {"messageId": "m1", "role": "ROLE_USER",
                  "parts": [{"text": "Research AI agent adoption."}]}}}'
```

The `A2A-Extensions` header opts in to ADK's newer executor, the same thing
`RemoteA2aAgent(use_legacy=False)` does in the writer (topic 06).

## Why `AgentTool` and not a sub-agent

Topic 04 puts the remote agent in `sub_agents`. That transfers the
conversation: the sub-agent's reply is the final answer. Here that would
return the researcher's bullet points to the user and the writer would never
write. Wrapping the remote agent in `AgentTool` makes it a call that returns,
which is what a pipeline step needs.

## Common errors

| Symptom | Cause |
|---|---|
| Writer says the researcher is unavailable, or `AgentCardResolutionError` | Terminal 1 is not running, or `RESEARCHER_URL` points elsewhere. |
| `404` on `/a2a/researcher` | `adk api_server` was started without `--a2a`, or from a folder other than this one. |
| `address already in use` | Port 8081 is taken. See Prerequisites for changing it. |

## Extensions to try

- Replace `mock_web_search` with the built-in `google_search` tool (Module 13).
- Add an editor agent with its own `agent.json` that the writer calls after
  drafting. One `adk api_server --a2a` serves both researcher and editor.
- Have the researcher ask "enterprise or consumer adoption?" before searching,
  so the task passes through `TASK_STATE_INPUT_REQUIRED`.

## Clean up

Stop both processes with Ctrl+C. Delete `researcher/.adk/` and `writer/.adk/`
to drop the local sessions.
