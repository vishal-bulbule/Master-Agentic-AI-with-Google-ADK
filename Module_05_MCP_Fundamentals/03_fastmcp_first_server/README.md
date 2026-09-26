<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 03: Your First FastMCP Server

## What this shows

A complete MCP server with one tool, `get_weather(city)`, in about 20 lines
of FastMCP. The decorator generates the tool schema from the function
signature and docstring; the default transport is stdio. The weather data is
a stub so the server runs offline.

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)), with the virtual environment
  active so `python` has `fastmcp`.
- Node.js with `npx`, for MCP Inspector (downloaded on first use).
- No API keys.

## Run it

1. `cd Module_05_MCP_Fundamentals/03_fastmcp_first_server`
2. `npx @modelcontextprotocol/inspector python server.py`
3. Open the URL Inspector prints (it includes an `MCP_INSPECTOR_API_TOKEN`
   parameter), click **Connect**, open **Tools**, click **List Tools**.
4. Select `get_weather`, set `city` to `Pune`, click **Run Tool**.

Without a browser:

```bash
npx @modelcontextprotocol/inspector --cli python server.py \
  --method tools/call --tool-name get_weather --tool-arg city=Pune
```

`python server.py` on its own prints the FastMCP banner to stderr and waits.
That is expected: a stdio server does nothing until a host writes JSON-RPC to
its stdin. Press Ctrl+C to stop it.

## What to look for

- The tool result:

  ```json
  {"status": "success", "city": "Pune", "temp_c": 31, "condition": "sunny"}
  ```

- The input schema Inspector shows was generated from `city: str`, and the
  description came from the docstring.
- `mcp.run()` with no arguments means stdio. The same server runs over HTTP
  by changing only that call (see `../05_stdio_vs_http/`).
- To use it from Claude Desktop, add it under `mcpServers` with absolute paths
  (see `../02_claude_desktop_config/`).

## Common errors

| Symptom | Cause and fix |
|---|---|
| Inspector shows "Connection closed" or the server exits at once | The `python` Inspector launched has no `fastmcp`. Activate the virtual environment, or pass the full path: `npx @modelcontextprotocol/inspector /path/to/repo/.venv/bin/python server.py`. |
