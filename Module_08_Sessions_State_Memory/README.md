<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Module 8: Sessions, state, memory, and artifacts

How an ADK agent remembers: within a conversation, across conversations, and
across restarts, and where files go.

| Concept | Scope | Lifetime | Use for |
|---|---|---|---|
| Session | one conversation | until deleted | the event log of a chat |
| State | key-value data on a session (or user, or app) | set by the prefix and the session service | current cart, current step, user preferences |
| Memory | searchable knowledge across sessions | long-term | "the user prefers South Indian food" |
| Artifact | named, versioned files | per session or per user | PDFs, images, audio |

## Before you start

- Repository setup from [SETUP.md](../SETUP.md) and a `.env` with your Gemini
  settings: a Gemini API key, or Agent Platform (formerly Vertex AI) with
  `GOOGLE_CLOUD_LOCATION=global` for `gemini-3.5-flash`. Each agent folder
  has a `.env.example` if you prefer a per-agent `.env`.
- `sqlalchemy` and `aiosqlite` (in the root `requirements.txt`) for the SQLite
  samples.
- `curl`, for the REST calls the dev UI has no button for (adding a session
  to memory, creating a session with initial state, listing versions).
- Optional: the `sqlite3` command-line tool, to read `sessions.db`.
- No cloud resources. Memory Bank, RAG corpora, and Cloud Storage are
  mentioned as drop-in URIs but not required.

## Topics

Follow them in this order.

| Order | Folder | What it shows |
|---|---|---|
| 1 | `01_session_anatomy/` | A session is `id`, `user_id`, `events`, `state`; inspect one over REST |
| 2 | `02_inmemory_session/` | `InMemorySessionService`; sessions vanish on restart |
| 3 | `03_database_session/` | `DatabaseSessionService` on SQLite (`sqlite+aiosqlite`); sessions survive restart |
| 4 | `04_state_prefixes_demo/` | `app:`, `user:`, no prefix, and `temp:` scopes |
| 5 | `05_read_write_state_in_tool/` | `tool_context.state` read and write; `user:` state crosses sessions |
| 6 | `06_state_in_instruction/` | `{user_name?}` placeholders filled from state |
| 7 | `07_memory_search/` | `add_session_to_memory` and `tool_context.search_memory` |
| 8 | `08_artifacts/` | `save_artifact` / `load_artifact` with versioned PDFs |
| 9 | `09_rewind_session/` | `Runner.rewind_async` to undo turns (Python snippet) |
| 10 | `lab_recipe_assistant/` | Lab: user-scoped preference, session cart, and `load_memory` together |

## State prefixes

| Prefix | Scope | Persisted |
|---|---|---|
| (none) | this session | if the session service persists |
| `user:` | all sessions of this `user_id` in this app | if the session service persists |
| `app:` | all users and sessions of this app | if the session service persists |
| `temp:` | the current invocation (one turn) | never |

## Running the samples

Every sample runs with `adk web` from its topic folder. The session, artifact,
and memory services each topic is about are chosen with `adk web` flags, not
code:

| Flags | Service | Topics |
|---|---|---|
| `--session_service_uri=memory://` | `InMemorySessionService` | 01, 02, 06, 07, 08, 09 |
| `--session_service_uri=sqlite+aiosqlite:///./sessions.db` | `DatabaseSessionService` (SQLAlchemy) | 03 |
| `--session_service_uri=sqlite:///./sessions.db` | `SqliteSessionService` | 04, 05, lab |
| `--artifact_service_uri=memory://` | `InMemoryArtifactService` (`file:///dir` and `gs://bucket` also work) | all |
| `--memory_service_uri=memory://` | `InMemoryMemoryService` (`agentengine://` and `rag://` also work) | all |

For example:

```bash
cd 03_database_session
adk web --session_service_uri=sqlite+aiosqlite:///./sessions.db --artifact_service_uri=memory:// --memory_service_uri=memory://
```

`./sessions.db` is relative to the folder you start `adk web` from; delete it
to start over. With no URIs, ADK 2.x stores sessions in
`<agent>/.adk/session.db` and artifacts in `<agent>/.adk/artifacts`; delete
those `.adk/` folders when you are done. `adk run <agent>` accepts the same
flags. `adk api_server` serves the same REST API without the UI.

REST endpoints used in this module, served by `adk web` at http://127.0.0.1:8000:

```text
GET    /list-apps
POST   /apps/{app}/users/{user}/sessions            body: {"session_id": "...", "state": {...}}
GET    /apps/{app}/users/{user}/sessions
GET    /apps/{app}/users/{user}/sessions/{id}
DELETE /apps/{app}/users/{user}/sessions/{id}
POST   /run                                         body: app_name, user_id, session_id, new_message
PATCH  /apps/{app}/users/{user}/memory              body: {"session_id": "..."}
GET    /apps/{app}/users/{user}/sessions/{id}/artifacts
```

`POST /apps/{app}/users/{user}/sessions/{id}` still exists but is deprecated;
send the id in the body instead.

## Reference

- [Sessions](https://adk.dev/sessions/), [State](https://adk.dev/sessions/state/),
  [Memory](https://adk.dev/sessions/memory/)
- [Artifacts](https://adk.dev/artifacts/)
- [Events](https://adk.dev/events/)
