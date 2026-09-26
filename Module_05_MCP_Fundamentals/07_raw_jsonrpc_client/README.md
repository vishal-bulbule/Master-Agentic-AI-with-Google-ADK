<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 07: Raw JSON-RPC Client (Low-Level `mcp` SDK)

## What this shows

A client written with the official `mcp` Python SDK, without FastMCP. It
starts the weather server from `../03_fastmcp_first_server/` as a stdio child
process and runs the three calls every MCP host makes: `initialize`,
`tools/list`, `tools/call`. ADK's `McpToolset` (Module 6) does the same thing
internally. `mcp` is the official SDK with both client and server APIs;
`fastmcp` is a higher-level framework built on top of it.

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). The script
starts the server itself with the same interpreter, so nothing needs to be
running first. No API keys.

## Run it

1. `cd Module_05_MCP_Fundamentals/07_raw_jsonrpc_client`
2. `python raw_client.py`

## What to look for

```
Launching MCP server: server.py

Server info : weather-demo 4.0.5
Protocol    : 2025-11-25

tools/list response:
  - get_weather: Return the current weather for a city.
    input_schema: { ... "required": ["city"] ... }

tools/call -> get_weather(city='Pune')
  content           : {"status":"success","city":"Pune","temp_c":31,"condition":"sunny"}
  structured_content: {"status": "success", "city": "Pune", "temp_c": 31, "condition": "sunny"}
  is_error          : False
```

(The version and protocol lines depend on the installed packages. FastMCP
also logs a banner to stderr when the server starts.)

What each step does:

1. `stdio_client(SERVER)` starts the child process and opens read and write
   streams on its stdout and stdin.
2. `ClientSession` adds JSON-RPC framing and request IDs on top of the streams.
3. `session.initialize()` performs the handshake: the `initialize` request
   and the `notifications/initialized` notification.
4. `session.list_tools()` sends `tools/list`.
5. `session.call_tool(name, args)` sends `tools/call`.

In `mcp` 2.x the Python attributes are snake_case (`server_info`,
`input_schema`, `structured_content`, `is_error`). The JSON on the wire keeps
the camelCase names from the MCP spec.

## Common errors

| Symptom | Cause and fix |
|---|---|
| `MCPError: Connection closed` | The server process exited. Run `python ../03_fastmcp_first_server/server.py` directly to see its traceback. |
