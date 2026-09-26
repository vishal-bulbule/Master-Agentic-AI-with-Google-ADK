# Author: Vishal Bulbule
# Date: 2026-09-22

"""FastAPI app that serves every agent under `agents/` from a custom image.

`get_fast_api_app` does the routing: it discovers each agent package under
`agents_dir` and serves the standard ADK API (`/list-apps`, `/run`,
`/run_sse`, `/apps/<app>/users/<user>/sessions`, `/health`). Add a folder
under `agents/` and it is served by the same container.

Sessions go to SQLite on the container's local disk. That disk is per
instance and is wiped when a revision is replaced, so set `SESSION_DB_URL` to
a managed database (for example Cloud SQL for PostgreSQL) before relying on
sessions in production.
"""

import os
from pathlib import Path

from google.adk.cli.fast_api import get_fast_api_app

AGENTS_DIR = str(Path(__file__).resolve().parent / "agents")

SESSION_DB_URL = os.environ.get(
    "SESSION_DB_URL",
    "sqlite+aiosqlite:///./sessions.db",
)

app = get_fast_api_app(
    agents_dir=AGENTS_DIR,
    session_service_uri=SESSION_DB_URL,
    # Without an explicit URI, ADK 2.x writes artifacts under the agent folder.
    artifact_service_uri="memory://",
    web=False,
)
