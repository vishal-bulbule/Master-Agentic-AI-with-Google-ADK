<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 02: MCP Connection Types

## What this shows

Three sibling agents, one per MCP transport. The `McpToolset` call is the
same in all three; only the `connection_params` class changes, and the model
sees the same kind of function declarations whatever the transport.

| Folder | Class | Use when |
|---|---|---|
| `stdio_agent/` | `StdioConnectionParams` | The server is a local program (npm package, Python script, binary) that ADK starts as a child process |
| `streamable_http_agent/` | `StreamableHTTPConnectionParams` | The server runs on its own behind a URL: Cloud Run, GKE, a hosted server. The default for anything remote |
| `sse_agent/` | `SseConnectionParams` | The server only supports the older HTTP+SSE transport |

Each subfolder has its own README with the details and the pros and cons of
that transport.

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)) and a `.env` with your Gemini
  settings (see each `agent/.env.example`). On Agent Platform (formerly Vertex
  AI) the model `gemini-3.5-flash` needs `GOOGLE_CLOUD_LOCATION=global`.
- stdio agent: Node.js with `npx`, and `mkdir -p /tmp/mcp-demo`.
- The two HTTP agents need an MCP server running first. Both use the tools from
  `Module_05_MCP_Fundamentals/05_stdio_vs_http/` (`ping`, `add`). From this
  folder (`02_connection_types/`), in separate terminals:

  ```bash
  # Streamable HTTP on http://127.0.0.1:8000/mcp (for streamable_http_agent)
  python ../../Module_05_MCP_Fundamentals/05_stdio_vs_http/http_server.py

  # The same tools over SSE on http://127.0.0.1:8001/sse (for sse_agent)
  fastmcp run ../../Module_05_MCP_Fundamentals/05_stdio_vs_http/stdio_server.py --transport sse --port 8001
  ```

  The Streamable HTTP server takes port 8000, which is also the `adk web`
  default, so start `adk web` with `--port 8080` while it runs.

## Run it

Each agent folder is named `agent`, so run `adk` from the subfolder:

1. `cd Module_06_MCP_Client_ADK/02_connection_types/streamable_http_agent`
   (or `stdio_agent`, or `sse_agent`)
2. `adk web --port 8080`
3. Open http://localhost:8080 and select `agent` in the agent dropdown.
4. Send: "Add 19 and 23, then ping the server." (stdio agent: "List the files
   in the folder.")

Terminal alternative, from the same subfolder: `adk run agent`.

## What to look for

- The same agent code shape for all three transports.
- The HTTP servers log a `POST /mcp` (or `GET /sse` plus `POST /messages/`)
  line per call; the stdio agent has no network traffic at all.
- Stop the HTTP server and send another message: the tool call fails with a
  connection error, while the agent keeps running. Remote servers have their
  own lifetime; plan for them being unavailable.

Point the HTTP agents at another server with `MCP_SERVER_URL` or
`MCP_SSE_URL`, for example a Module 7 server deployed to Cloud Run.

## Common errors

| Symptom | Cause and fix |
|---|---|
| `adk web` fails with address already in use | The Module 5 HTTP server holds port 8000. Pass `--port 8080` to `adk web`. |
| Agent runs without tools, log says the toolset failed to load | The MCP server is not running, or the URL is wrong. Start the server first. |
| SSE server cannot bind port 8001 | Another process holds it. Use another port and set `MCP_SSE_URL=http://127.0.0.1:<port>/sse`. |
