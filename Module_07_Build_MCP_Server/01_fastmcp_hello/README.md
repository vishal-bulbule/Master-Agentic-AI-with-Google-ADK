<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 01: FastMCP Hello

## What this shows

A working MCP server in about 10 lines of code. The function-tool style is
the same as ADK's: a typed Python function with a docstring. `@mcp.tool()`
turns it into an MCP tool and `mcp.run()` serves it over stdio.

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)), virtual environment active.
- Node.js with `npx`, for MCP Inspector.
- No API keys.

## Run it

1. `cd Module_07_Build_MCP_Server/01_fastmcp_hello`
2. `npx @modelcontextprotocol/inspector python server.py`
3. Open the URL it prints, click **Connect**, open **Tools**, **List Tools**.
4. Run `get_weather` with `city` = `Mumbai`.

Without a browser:

```bash
npx @modelcontextprotocol/inspector --cli python server.py \
  --method tools/call --tool-name get_weather --tool-arg city=Mumbai
```

`python server.py` on its own prints the FastMCP banner to stderr and waits
for JSON-RPC on stdin. That is expected: a stdio server does not listen on a
port. Press Ctrl+C to stop it.

## What to look for

- The result: `{"status": "success", "city": "Mumbai", "temp_c": 22, "condition": "sunny"}`,
  returned both as text `content` and as `structuredContent`.
- What `@mcp.tool()` generated from the function:
  - an input schema: `{"type": "object", "properties": {"city": {"type": "string", ...}}, "required": ["city"]}`,
    with the `Args:` line as the property description;
  - a `tools/list` entry with the docstring summary as the description;
  - a `tools/call` handler that validates arguments, calls the function, and
    serializes the return value.

Next: resources and prompts in `../02_three_primitives/`.
