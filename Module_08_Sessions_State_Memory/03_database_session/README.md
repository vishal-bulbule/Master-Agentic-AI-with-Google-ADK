<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 03 DatabaseSessionService (SQLite)

## What this shows

`DatabaseSessionService` stores sessions, events, and state through
SQLAlchemy, so the same code runs on SQLite, PostgreSQL, or MySQL; only the
URL changes. The service is async, so the URL must name an async driver:
`sqlite+aiosqlite` for SQLite, `postgresql+asyncpg` for PostgreSQL. `adk web`
passes any URL whose scheme it does not recognise to `DatabaseSessionService`.
A plain `sqlite:///path` URL selects a different, lighter class,
`SqliteSessionService`, which the other SQLite samples in this module use.

ADK creates these tables on first use: `sessions`, `events` (one row per
event, the event stored as JSON in `event_data`), `app_states`,
`user_states`, and `adk_internal_metadata`.

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)) and a `.env` with your Gemini
  settings (see `db_agent/.env.example`; on Agent Platform use
  `GOOGLE_CLOUD_LOCATION=global`). `sqlalchemy` and `aiosqlite` are in the
  root `requirements.txt`.
- Optional: the `sqlite3` command-line tool, to read the database.

## Run it

1. `cd Module_08_Sessions_State_Memory/03_database_session`
2. `adk web --session_service_uri=sqlite+aiosqlite:///./sessions.db --artifact_service_uri=memory:// --memory_service_uri=memory://`
3. Open http://localhost:8000 and select `db_agent` in the agent dropdown.
4. Send: "Remember to buy milk.", then "Also call mom."

The database is `sessions.db` in the folder you started `adk web` from.

## Try it

1. Stop `adk web` with Ctrl+C and start it again with the same command.
2. Pick the same session in the session dropdown and ask: "What is on my list?"
3. With the server stopped, read the database:

   ```bash
   sqlite3 sessions.db "SELECT id, user_id, create_time FROM sessions;"
   sqlite3 sessions.db "SELECT json_extract(event_data, '$.author'), invocation_id FROM events ORDER BY timestamp;"
   ```

## What to look for

- The startup log says `Using DatabaseSessionService for URI: sqlite+aiosqlite:...`.
- After the restart the session is still listed, and `list_notes` returns
  both notes.
- One `events` row per user message, tool call, tool result, and reply,
  grouped by `invocation_id` (one invocation per user turn).

## Common errors

| Symptom | Cause and fix |
|---|---|
| `ValueError: Database URL ... resolves to a synchronous driver` | The URL names no async driver, for example `sqlite:///` passed straight to `DatabaseSessionService(db_url=...)` in your own code. Use `sqlite+aiosqlite:///`. |
| `unable to open database file` | The path in the URL points to a folder that does not exist. |

For managed deployments on Google Cloud, `VertexAiSessionService`
(`agentengine://...`) and `google.adk.integrations.firestore.FirestoreSessionService`
remove the database from your operations list.

## Clean up

```bash
rm sessions.db
```
