<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 07: Test with MCP Inspector

## What this shows

Two ways to test an MCP server before an agent depends on it: MCP Inspector
for interactive checks, and `smoke_test.py` for a scripted check that can run
in CI. Most server bugs (a tool that is not registered, a wrong argument
type, a result that does not serialize) show up here faster than through an
agent and a model.

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)), virtual environment active.
- Node.js with `npx`, for MCP Inspector. `smoke_test.py` needs only Python.
- No API keys.
- For the HTTP checks, the server from `../04_streamable_http_server/`
  running first, in its own terminal:
  `python ../04_streamable_http_server/server.py`

## Run it

1. `cd Module_07_Build_MCP_Server/07_test_with_inspector`
2. Scripted smoke test (starts `../01_fastmcp_hello/server.py` itself):
   `python smoke_test.py`
3. Inspector UI against a stdio server:
   `npx @modelcontextprotocol/inspector python ../01_fastmcp_hello/server.py`
4. Inspector UI against the HTTP server: `npx @modelcontextprotocol/inspector`,
   then **Streamable HTTP**, URL `http://localhost:8080/mcp`, **Connect**.

Inspector's CLI mode runs one method and prints JSON, with no browser:

```bash
npx @modelcontextprotocol/inspector --cli python ../01_fastmcp_hello/server.py --method tools/list
npx @modelcontextprotocol/inspector --cli http://localhost:8080/mcp \
  --method tools/call --tool-name get_weather --tool-arg city=Pune
```

`smoke_test.py` prints:

```
OK   initialize  -> my-server (protocol 2025-11-25)
OK   list_tools  -> ['get_weather']
OK   call_tool   -> {"status": "success", "city": "Pune", "temp_c": 22, "condition": "sunny"}

All smoke checks passed.
```

It exits with status 1 if a check fails, so a CI step fails with it.

## What to look for

1. **Connect**: Inspector starts the process (stdio) or opens the HTTP session.
2. **Tools**: every `@mcp.tool()` you registered, with its input schema.
   Fill the form and run one.
3. **Resources**: resource templates such as `invoice://{invoice_id}` are
   listed separately from concrete resources.
4. **Prompts**: select a prompt and fill its arguments; Inspector shows the
   messages the host would send to the model.
5. **History**: the raw JSON-RPC requests and responses. This is where
   schema and serialization problems show up.

Common findings:

- **A tool is missing:** the decorator is missing, or the module failed
  before registering it. Run `python server.py` directly to see the traceback.
- **Wrong argument type:** the schema shows what the type hints say. `city: list`
  instead of `city: str` is obvious here and confusing in an agent.
- **A result is not what you expected:** FastMCP returns dicts both as text
  `content` and as `structuredContent`. Low-level servers must build
  `CallToolResult` themselves.
- **A resource template is not listed:** a URI without a `{placeholder}`
  is a concrete resource and appears in the other list.

### Which to use

| Need | Use |
|---|---|
| First look: schemas, manual calls, raw JSON-RPC | Inspector UI |
| One-off check from a terminal or a script | Inspector `--cli` |
| CI gate or regression check | `smoke_test.py` (extend it with your own tool calls) |
| End-to-end check with a model | An ADK agent pointed at the server (Module 6) |
