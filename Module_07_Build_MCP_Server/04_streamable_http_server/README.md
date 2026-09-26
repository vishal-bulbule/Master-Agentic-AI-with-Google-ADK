<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 04: Streamable HTTP Server

## What this shows

The transport you deploy. One ASGI app with one route (`/mcp`), stateless so
it runs on Cloud Run without sticky sessions. The server uses the low-level
`mcp` SDK so each part is visible; FastMCP does the same wiring in one call
(`mcp.http_app(stateless_http=True)`, used in `../lab_techtrapture_mcp/`).

| Transport | Shape | Use for |
|---|---|---|
| stdio | Pipes to a child process | Local development, desktop hosts, one user |
| HTTP+SSE (legacy) | A `GET /sse` stream plus a separate POST endpoint | Older servers only |
| Streamable HTTP | One endpoint; each POST gets a JSON or SSE response | Anything deployed |

Why `stateless=True` on Cloud Run: a stateful Streamable HTTP server keeps
each MCP session in process memory and gives the client a session ID. On
Cloud Run, consecutive requests from the same client can reach different
instances, and an instance that never saw the session rejects it. With
`stateless=True` every request is handled with a fresh transport and no
session lookup, so any instance can serve any request. The trade-off: no
server-initiated messages between requests (notifications, sampling,
elicitation), which a tool server rarely needs.

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)), virtual environment active.
- Node.js with `npx`, for MCP Inspector.
- Port 8080 free (or set `PORT`).
- No API keys.

## Run it

1. `cd Module_07_Build_MCP_Server/04_streamable_http_server`
2. `python server.py` (prints `Uvicorn running on http://0.0.0.0:8080`)
3. In another terminal:

   ```bash
   npx @modelcontextprotocol/inspector --cli http://localhost:8080/mcp --method tools/list
   npx @modelcontextprotocol/inspector --cli http://localhost:8080/mcp \
     --method tools/call --tool-name get_weather --tool-arg city=Pune
   ```

   Or with the Inspector UI: `npx @modelcontextprotocol/inspector`, choose
   **Streamable HTTP**, URL `http://localhost:8080/mcp`, **Connect**.

To use it from an ADK agent, set the URL in an agent's `McpToolset`, as in
Module 6 `02_connection_types/streamable_http_agent/` (its `MCP_SERVER_URL`
setting takes `http://localhost:8080/mcp`):

```python
McpToolset(connection_params=StreamableHTTPConnectionParams(url="http://localhost:8080/mcp"))
```

## What to look for

The server code, top to bottom:

1. Handler functions `list_tools(ctx, params)` and `call_tool(ctx, params)`
   return `ListToolsResult` and `CallToolResult` objects.
2. `Server(name, on_list_tools=..., on_call_tool=...)` registers them. (The
   `mcp` 1.x decorator style was removed in 2.x.)
3. `StreamableHTTPSessionManager(app=server, stateless=True)` implements
   the transport.
4. A Starlette `Route("/mcp", ...)` hands requests to the manager.
5. The Starlette `lifespan` runs `session_manager.run()`. Without it the
   manager refuses to handle requests.

In the uvicorn log, each JSON-RPC message is one `POST /mcp`; the
`notifications/initialized` message gets `202 Accepted`.

Next: package it in `../05_dockerfile/`.

## Common errors

| Symptom | Cause and fix |
|---|---|
| `Address already in use` | Another process holds 8080. Stop it or run `PORT=8090 python server.py`. |
| 404 Not Found | The client URL is missing the `/mcp` path. |
