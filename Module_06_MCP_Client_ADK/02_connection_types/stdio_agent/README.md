<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Stdio transport

## What this shows

ADK starts the MCP server as a child process and speaks JSON-RPC over its
stdin and stdout. `timeout` is how long ADK waits for the session to start;
the default is 5 seconds, which a first `npx` download can exceed.

```python
StdioConnectionParams(
    server_params=StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp/mcp-demo"],
    ),
    timeout=30,
)
```

| Pros | Cons |
|---|---|
| No networking, no port, no TLS | One server process per agent process |
| The server runs with the agent's OS permissions and nothing more | Server lifetime is tied to the agent |
| Works in any container that has the command (`npx`, `python`) installed | Not shareable between users or services |

## Prerequisites

- Repository setup ([SETUP.md](../../../SETUP.md)) and a `.env` with your
  Gemini settings (see `agent/.env.example`; on Agent Platform use
  `GOOGLE_CLOUD_LOCATION=global`).
- Node.js with `npx` on your PATH (`which npx` prints a path).
- `mkdir -p /tmp/mcp-demo`

## Run it

1. `cd Module_06_MCP_Client_ADK/02_connection_types/stdio_agent`
2. `adk web`
3. Open http://localhost:8000 and select `agent` in the agent dropdown.
4. Send: "List the files in the folder."

Terminal alternative: `adk run agent`.

## What to look for

A `list_directory` call with `path` set to `/tmp/mcp-demo` in the Events view,
and no network traffic: the server is a child process of `adk web`.
