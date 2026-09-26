<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 06: MCP Inspector Walkthrough

## What this shows

MCP Inspector is a browser UI for MCP servers. It launches or connects to a
server, lists what it exposes, lets you call tools, read resources, and render
prompts by hand, and shows the JSON-RPC messages. Use it to debug a server
before you connect an agent to it, and to see exactly what a host such as
Claude Desktop or ADK receives.

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)), virtual environment active.
- Node.js with `npx`; `npx` downloads Inspector on first use.
- A browser.
- No API keys. The walkthrough uses the server in `../03_fastmcp_first_server/`.

## Run it

1. `cd Module_05_MCP_Fundamentals/06_inspector_walkthrough`
2. `npx @modelcontextprotocol/inspector python ../03_fastmcp_first_server/server.py`
3. Open the full URL Inspector prints, for example
   `http://localhost:6274/?MCP_INSPECTOR_API_TOKEN=...`.
4. Click **Connect**. Inspector sends `initialize`; the status turns to
   connected and shows the server name `weather-demo`.
5. Open **Tools** and click **List Tools**. `get_weather` appears with its
   input schema.
6. Select `get_weather`, enter `Pune` for `city`, click **Run Tool**.
7. Open the **History** pane to see each request and response.

Inspector also has a CLI mode that runs one method and prints the JSON:

```bash
npx @modelcontextprotocol/inspector --cli python ../03_fastmcp_first_server/server.py --method tools/list
npx @modelcontextprotocol/inspector --cli python ../03_fastmcp_first_server/server.py \
  --method tools/call --tool-name get_weather --tool-arg city=Pune
```

For an HTTP server, run `npx @modelcontextprotocol/inspector` with no
arguments, choose **Streamable HTTP**, and enter the server URL (for example
`http://127.0.0.1:8000/mcp` for `../05_stdio_vs_http/http_server.py`).

## What to look for

These are the messages for the steps above, captured from the server in
`03_fastmcp_first_server/` (FastMCP 4.0.5, protocol version `2025-11-25`).

`tools/list` request and response:

```json
{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
```

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "get_weather",
        "title": "Get Weather",
        "description": "Return the current weather for a city.",
        "inputSchema": {
          "type": "object",
          "properties": {
            "city": {"type": "string", "description": "City name, for example \"Pune\"."}
          },
          "required": ["city"],
          "additionalProperties": false
        },
        "outputSchema": {"type": "object", "additionalProperties": true},
        "_meta": {"fastmcp": {"tags": []}}
      }
    ]
  }
}
```

The argument description came from the `Args:` section of the docstring.

`tools/call` request and response:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {"name": "get_weather", "arguments": {"city": "Pune"}}
}
```

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {"type": "text", "text": "{\"status\":\"success\",\"city\":\"Pune\",\"temp_c\":31,\"condition\":\"sunny\"}"}
    ],
    "structuredContent": {"status": "success", "city": "Pune", "temp_c": 31, "condition": "sunny"},
    "isError": false
  }
}
```

`content` is what a model reads; `structuredContent` is the same result as a
JSON object for programmatic clients. That is the whole protocol: JSON-RPC
over a pipe or an HTTP endpoint.

## Common errors

| Symptom | Cause and fix |
|---|---|
| Connection closed right after Connect | The `python` Inspector launched has no `fastmcp`. Activate the virtual environment or pass the full interpreter path. |
| Browser says the request is unauthorized | Open the full URL Inspector prints, including the `MCP_INSPECTOR_API_TOKEN` query parameter. |
