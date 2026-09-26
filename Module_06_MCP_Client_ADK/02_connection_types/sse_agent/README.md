<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# SSE transport

## What this shows

HTTP+SSE is the original remote MCP transport: the client holds a long-lived
`GET /sse` stream for server messages and sends requests to a separate POST
endpoint. Streamable HTTP replaced it. Use SSE only for servers that do not
support Streamable HTTP yet; for new servers use `../streamable_http_agent/`.

```python
SseConnectionParams(
    url="https://your-mcp.example.com/sse",
    headers={"Authorization": "Bearer ..."},
)
```

| Pros | Cons |
|---|---|
| Works with older servers | Superseded in the MCP spec |
| Server lifetime independent of the agent | Long-lived streams complicate load balancing; cannot run stateless |
| Auth through HTTP headers | Some proxies buffer or cut `text/event-stream` responses |

## Prerequisites

- Repository setup ([SETUP.md](../../../SETUP.md)) and a `.env` with your
  Gemini settings (see `agent/.env.example`; on Agent Platform use
  `GOOGLE_CLOUD_LOCATION=global`).
- An SSE MCP server running first. Serve the Module 5 tools over SSE with the
  `fastmcp` CLI, from this folder, in its own terminal:

  ```bash
  fastmcp run ../../../Module_05_MCP_Fundamentals/05_stdio_vs_http/stdio_server.py --transport sse --port 8001
  ```

  The agent defaults to `http://127.0.0.1:8001/sse`. If port 8001 is taken,
  pick another port and set `MCP_SSE_URL=http://127.0.0.1:<port>/sse` in your
  `.env`.

## Run it

1. `cd Module_06_MCP_Client_ADK/02_connection_types/sse_agent`
2. `adk web`
3. Open http://localhost:8000 and select `agent` in the agent dropdown.
4. Send: "Ping the server."

Terminal alternative: `adk run agent`.

## What to look for

The Events view shows a `ping` call returning `pong`. The server log shows the
`GET /sse` stream opening and a `POST /messages/` for each request.
