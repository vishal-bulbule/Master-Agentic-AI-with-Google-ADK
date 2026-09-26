<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Module 6: Consuming MCP Servers in ADK

`McpToolset` connects an ADK agent to any MCP server. Put it in the agent's
`tools` list and ADK opens the session, discovers the tools, converts their
schemas, proxies the calls, and closes the connection when the runner shuts
down. You write no adapter code.

## Before you start

- Repository setup from [SETUP.md](../SETUP.md) and a `.env` with your Gemini
  settings: a Gemini API key, or Agent Platform (formerly Vertex AI) with
  `GOOGLE_CLOUD_LOCATION=global` (the default model, `gemini-3.5-flash`, is
  served from `global`). Each agent folder has a `.env.example` listing
  exactly what it needs.
- Node.js with `npx` on your PATH, for every stdio agent (topics 01 to 04, 07).
- `/tmp/mcp-demo` for the filesystem agents: `mkdir -p /tmp/mcp-demo`.
- For topic 02's HTTP agents: an MCP server from Module 5 running first (the
  topic README has the commands).
- For topic 05: `GOOGLE_MAPS_API_KEY`, a Maps Platform key with the Maps
  Grounding Lite API (`mapstools.googleapis.com`) enabled.
- For the lab: `GITHUB_PERSONAL_ACCESS_TOKEN`, a fine-grained token with
  read-only access to public repositories (or Issues: Read-only on a private
  one).

## Topics

Follow them in this order.

| Order | Folder | What it shows |
|---|---|---|
| 1 | `01_mcptoolset_basic/` | `McpToolset` over stdio against the filesystem MCP server |
| 2 | `02_connection_types/` | stdio, Streamable HTTP, and SSE: three sibling agents |
| 3 | `03_tool_filter/` | `tool_filter` to expose only read tools |
| 4 | `04_multiple_servers/` | One agent, two MCP servers (filesystem and memory), and tool name collisions |
| 5 | `05_google_maps_remote/` | A hosted remote MCP server: Google Maps Grounding Lite |
| 6 | `06_mcp_server_survey/` | Catalog of MCP servers with ready-to-paste `McpToolset` blocks |
| 7 | `07_sync_vs_async/` | Why `root_agent` is defined at module scope, and the async pattern for your own Runner |
| 8 | `lab_github_triage_mcp/` | Lab: a read-only GitHub issue-triage agent on GitHub's official MCP server |

## Run any topic

Every topic keeps its agent in a folder named `agent`, which is the app name
`adk` shows. From the topic folder:

```bash
cd 01_mcptoolset_basic
adk web          # open http://localhost:8000 and select "agent"
# or
adk run agent
```

`02_connection_types/` holds three agents, each in its own subfolder
(`stdio_agent/agent`, `streamable_http_agent/agent`, `sse_agent/agent`); run
`adk` from the subfolder.

`adk web` and `adk run` keep sessions in `agent/.adk/` by default. Delete that
folder to start over.

## Key takeaway

Whatever the transport, the agent code has the same shape:

```python
LlmAgent(
    tools=[McpToolset(connection_params=<Stdio|StreamableHTTP|Sse>ConnectionParams(...))],
)
```

The transport is a deployment detail. Tool selection (`tool_filter`), auth
headers, and server-side read-only modes are where the design decisions are.
