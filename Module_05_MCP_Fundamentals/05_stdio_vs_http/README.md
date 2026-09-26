<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 05: stdio vs Streamable HTTP

## What this shows

The same two tools (`ping`, `add`) served over the two MCP transports. The
tool code is identical; only the `mcp.run()` call changes, and the JSON-RPC
messages are the same on both. Tools do not know which transport carried the
request.

```python
# stdio_server.py
mcp.run()

# http_server.py
mcp.run(transport="http", host="127.0.0.1", port=8000, path="/mcp")
```

| | stdio | Streamable HTTP |
|---|---|---|
| How it starts | The host spawns the server as a child process | The server runs on its own; clients connect to a URL |
| Where it runs | Same machine as the host | Local or remote (Cloud Run, GKE, any HTTP platform) |
| Auth | Inherits the OS user | Bearer tokens, OAuth, IAM in front of the service |
| Clients per process | One | Many |
| Setup | None: no port, no TLS | A host, a port, and eventually auth |
| Typical hosts | Claude Desktop, IDEs, local ADK agents | Deployed agents, shared team servers, hosted servers such as Google Maps Grounding Lite |

The older HTTP+SSE transport (two endpoints) is superseded by Streamable HTTP
and is only needed for servers that have not moved yet.

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)), virtual environment active.
- Node.js with `npx`, for MCP Inspector.
- Port 8000 free for the HTTP server.
- No API keys.

## Run it

stdio (Inspector launches the server for you):

1. `cd Module_05_MCP_Fundamentals/05_stdio_vs_http`
2. `npx @modelcontextprotocol/inspector python stdio_server.py`
3. Open the printed URL, click **Connect**, then **List Tools**.

Streamable HTTP (you start the server, then connect):

1. `cd Module_05_MCP_Fundamentals/05_stdio_vs_http`
2. `python http_server.py` (prints `Starting MCP server 'transport-demo-http' with transport 'http' on http://127.0.0.1:8000/mcp`)
3. In a second terminal: `npx @modelcontextprotocol/inspector`
4. Set **Transport Type** to **Streamable HTTP**, URL `http://127.0.0.1:8000/mcp`,
   click **Connect**, then **List Tools**, and run `add` with `a` = 19, `b` = 23.

Without a browser, while `http_server.py` runs:

```bash
npx @modelcontextprotocol/inspector --cli http://127.0.0.1:8000/mcp --transport http \
  --method tools/call --tool-name add --tool-arg a=19 --tool-arg b=23
```

## What to look for

- Both servers list the same two tools with the same schemas.
- With HTTP, the server log shows one `POST /mcp` per JSON-RPC request. With
  stdio there is nothing to see: traffic goes through pipes.
- Stop the HTTP server and Inspector loses the connection: the server
  lifetime is yours to manage. With stdio, closing Inspector stops the server.

Module 6 connects ADK agents over both transports; Module 7 deploys a
Streamable HTTP server to Cloud Run.

## Common errors

| Symptom | Cause and fix |
|---|---|
| `Address already in use` | Something else holds port 8000. Stop it or change `port=` in `http_server.py`. |
| Inspector gets 404 | The URL must include the `/mcp` path. |
