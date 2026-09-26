<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 06: A Catalog of MCP Servers

## What this shows

Eight MCP servers worth knowing, with how each one authenticates and a
`McpToolset` block you can paste into an agent. This folder has no code to
run; the blocks use the same shape as the runnable agents in this module.

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)).
- Each server has its own requirements, listed with its block below: Node.js
  and `npx` for the npm servers, `uv` (for `uvx`) for the Python fetch server,
  a GitHub personal access token, database credentials, or a Maps API key.

## Run it

There is nothing to run in this folder. To try a block, from
`Module_06_MCP_Client_ADK/06_mcp_server_survey`:

1. Copy an agent folder that has a runnable agent, for example
   `cp -r ../01_mcptoolset_basic/agent ../01_mcptoolset_basic/survey_agent`.
2. Replace the `McpToolset(...)` in `survey_agent/agent.py` with the block,
   and add the imports shown below.
3. `cd ../01_mcptoolset_basic && adk web`, then select `survey_agent`.

## What to look for

All blocks assume:

```python
import os

from google.adk.tools.mcp_tool import (
    McpToolset,
    StdioConnectionParams,
    StreamableHTTPConnectionParams,
)
from mcp import StdioServerParameters
```

Package names and tool names were checked on 2026-09-22. Several of the early
reference servers (`server-github`, `server-postgres`, `server-slack`,
`server-puppeteer`) are deprecated on npm; the entries below use their
maintained replacements.

### 1. Filesystem: `@modelcontextprotocol/server-filesystem`

Sandboxed read and write access to local folders.
Auth: none. The allowed folders are the command-line arguments.

```python
McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp/mcp-demo"],
        ),
        timeout=30,
    ),
    tool_filter=["read_text_file", "list_directory"],
)
```

Runnable: `../01_mcptoolset_basic/`, `../03_tool_filter/`.

### 2. GitHub: GitHub's official MCP server (remote)

Issues, pull requests, repository contents, Actions, code security.
Auth: a GitHub personal access token in the `Authorization` header.
Hosted by GitHub at `https://api.githubcopilot.com/mcp/`; also available as a
local binary or container (`ghcr.io/github/github-mcp-server`). This replaces
the deprecated `@modelcontextprotocol/server-github` npm package, whose tool
names (`get_issue`, `create_comment`) no longer exist in the official server.

```python
McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://api.githubcopilot.com/mcp/",
        headers={
            "Authorization": f"Bearer {os.environ['GITHUB_PERSONAL_ACCESS_TOKEN']}",
            "X-MCP-Toolsets": "issues",   # only the issues toolset
            "X-MCP-Readonly": "true",     # server drops every write tool
        },
        timeout=30,
    ),
    tool_filter=["list_issues", "search_issues", "issue_read"],
)
```

Runnable: `../lab_github_triage_mcp/`.

### 3. Databases: MCP Toolbox for Databases

Google's open-source MCP server for PostgreSQL, AlloyDB, Cloud SQL, BigQuery,
Spanner, MySQL, SQLite, and others. Replaces the deprecated
`@modelcontextprotocol/server-postgres`.
Auth: database credentials in environment variables.

```python
McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@toolbox-sdk/server", "--prebuilt", "postgres", "--stdio"],
            env={
                "POSTGRES_HOST": "127.0.0.1",
                "POSTGRES_PORT": "5432",
                "POSTGRES_DATABASE": os.environ["POSTGRES_DATABASE"],
                "POSTGRES_USER": os.environ["POSTGRES_USER"],
                "POSTGRES_PASSWORD": os.environ["POSTGRES_PASSWORD"],
            },
        ),
        timeout=30,
    ),
)
```

The prebuilt configurations include tools that run arbitrary SQL, and the
server warns that they are meant for trusted developers. For agents that talk
to end users, define your own tools in a `tools.yaml` with fixed, parameterized
queries and pass `--config tools.yaml` instead of `--prebuilt`.

### 4. Browser automation: `@playwright/mcp`

Microsoft's Playwright MCP server: navigate, click, fill forms, and read pages
through the accessibility tree. Replaces the deprecated
`@modelcontextprotocol/server-puppeteer`.
Auth: none. The first run may need `npx playwright install chromium`.

```python
McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@playwright/mcp@latest", "--headless"],
        ),
        timeout=60,
    ),
)
```

A browser tool can reach any site the host can. Restrict it with
`tool_filter` and run it in a sandboxed container before exposing it to
untrusted input.

### 5. Knowledge-graph memory: `@modelcontextprotocol/server-memory`

Entities, relations, and observations persisted to a JSONL file.
Auth: none.

```python
McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-memory"],
            env={"MEMORY_FILE_PATH": "/tmp/mcp-demo-memory.jsonl"},
        ),
        timeout=30,
    ),
)
```

Without `MEMORY_FILE_PATH` the file is written inside the npm package
directory in the npx cache. Runnable: `../04_multiple_servers/`.

### 6. Web fetch: `mcp-server-fetch` (Python)

Fetches a URL and returns the page as markdown. A reference server written in
Python, launched with `uvx` instead of `npx`.
Auth: none.

```python
McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uvx",
            args=["mcp-server-fetch"],
        ),
        timeout=60,
    ),
)
```

The server can fetch internal addresses reachable from the host. Do not run
it where the agent's input is untrusted and the network holds private
services.

### 7. Google Maps Grounding Lite (remote)

Place search, weather, routes, grounded in Google Maps data.
Auth: Maps Platform API key in the `X-Goog-Api-Key` header.
Hosted by Google; nothing to install.

```python
McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://mapstools.googleapis.com/mcp",
        headers={"X-Goog-Api-Key": os.environ["GOOGLE_MAPS_API_KEY"]},
        timeout=30,
    ),
)
```

Runnable: `../05_google_maps_remote/`.

### 8. Your own server

Any FastMCP server from Module 5 or Module 7, locally over stdio or deployed
to Cloud Run over Streamable HTTP:

```python
McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://your-service-xxxx.run.app/mcp",
    ),
)
```

Runnable: `../02_connection_types/`, `../../Module_07_Build_MCP_Server/lab_techtrapture_mcp/`.

### Evaluating a new MCP server

Before adding one to an agent, check:

1. **Auth model.** Token, connection string, OAuth? Where does the secret live?
2. **Write tools.** Does it expose mutations you do not want? Use `tool_filter`
   or a server-side read-only mode.
3. **Transport.** Local stdio or remote HTTP? It decides how you deploy.
4. **Maintenance.** Is the package maintained, or deprecated like several of
   the early reference servers? Pin a version in production instead of `@latest`.
5. **Tool names.** Will they collide with another server you already load?

Directories: https://github.com/modelcontextprotocol/servers and the MCP
Registry at https://registry.modelcontextprotocol.io.

## Clean up

If you copied an agent folder to try a block: `rm -rf ../01_mcptoolset_basic/survey_agent`.
