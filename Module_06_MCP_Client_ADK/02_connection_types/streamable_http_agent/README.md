<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Streamable HTTP transport

## What this shows

Streamable HTTP is the current MCP transport for remote servers: one HTTP
endpoint that answers JSON-RPC requests with either JSON or an SSE stream.
Servers can run stateless, which lets any instance behind a load balancer
serve any request.

```python
StreamableHTTPConnectionParams(
    url="https://your-mcp-server.run.app/mcp",
    headers={"Authorization": "Bearer ..."},
)
```

- `headers=` on the connection params is sent on every request. Use it for a
  static API key or token.
- `header_provider=` on `McpToolset` is a function that receives the
  `ReadonlyContext` and returns headers for each request. Use it when the
  value depends on the user or session, for example a per-user token kept in
  session state.

| Pros | Cons |
|---|---|
| Designed for cloud deployment and horizontal scale | The server must implement Streamable HTTP |
| Plain HTTPS: works with proxies, load balancers, and standard auth | You own auth, uptime, and rate limits |

## Prerequisites

- Repository setup ([SETUP.md](../../../SETUP.md)) and a `.env` with your
  Gemini settings (see `agent/.env.example`; on Agent Platform use
  `GOOGLE_CLOUD_LOCATION=global`).
- The MCP server running first. From this folder, in its own terminal:

  ```bash
  python ../../../Module_05_MCP_Fundamentals/05_stdio_vs_http/http_server.py
  ```

  It listens on `http://127.0.0.1:8000/mcp`, the agent's default. To use
  another server, set `MCP_SERVER_URL` in your `.env`.

## Run it

1. `cd Module_06_MCP_Client_ADK/02_connection_types/streamable_http_agent`
2. `adk web --port 8080` (port 8000 is taken by the MCP server)
3. Open http://localhost:8080 and select `agent` in the agent dropdown.
4. Send: "Add 19 and 23."

Terminal alternative: `adk run agent`.

## What to look for

The Events view shows an `add` call returning `{"status": "success", "result": 42}`,
and the MCP server logs a `POST /mcp` for each JSON-RPC message.
`../../05_google_maps_remote/` connects to a hosted Google server over the
same transport.
