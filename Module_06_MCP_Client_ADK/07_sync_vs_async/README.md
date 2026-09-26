<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 07: Sync vs Async Agent Definition

## What this shows

Two ways to create an agent that uses MCP tools, and which ADK tools can load
each one. ADK's agent loader imports your module and reads a module-level
`root_agent` (or `app`) that must already be an agent object. The `agent/`
folder here uses that shape. It works with MCP because `McpToolset(...)` is a
plain constructor: it does not connect at import time, and the MCP session
opens the first time the agent needs its tools. Older ADK versions had an
async `MCPToolset.from_server()` helper that forced an async shape; current
ADK does not need it.

| Pattern | Loadable by `adk web`, `adk run`, `adk deploy`, API server |
|---|---|
| `root_agent = LlmAgent(...)` at module scope (`agent/agent.py`) | Yes |
| Agent built inside `async def build_agent()` | No: only your own Runner can use it |

A coroutine function is not an agent, so the loader reports that it found no
`root_agent`.

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)) and a `.env` with your Gemini
  settings (see `agent/.env.example`). On Agent Platform (formerly Vertex AI)
  the model `gemini-3.5-flash` needs `GOOGLE_CLOUD_LOCATION=global`.
- Node.js with `npx` on your PATH: ADK starts the filesystem MCP server with
  `npx -y @modelcontextprotocol/server-filesystem`.
- The sandbox folder: `mkdir -p /tmp/mcp-demo && echo "hello from MCP" > /tmp/mcp-demo/sample.txt`

## Run it

1. `cd Module_06_MCP_Client_ADK/07_sync_vs_async`
2. `adk web`
3. Open http://localhost:8000 and select `agent` in the agent dropdown.
4. Send: "List the files in the folder."

Terminal alternative: `adk run agent`.

## What to look for

- Nothing about MCP happens when `adk web` starts: no `npx` process exists
  until your first message. The Events view then shows a `list_directory`
  call and its response.
- The model gets only `read_text_file` and `list_directory` (`tool_filter`).
- When you stop `adk web` (Ctrl+C), it closes the runner, which closes every
  toolset and stops the MCP child process.

## Using this from Python

If you write your own runtime around ADK and want the MCP server to start
before the first turn, so a broken server fails at startup instead of in the
middle of a conversation, build the agent in a coroutine and connect eagerly.
You then own the cleanup: `runner.close()` in a `finally` block, or the MCP
child process outlives your program.

```python
async def build_agent() -> LlmAgent:
    toolset = McpToolset(connection_params=..., tool_filter=[...])
    await toolset.get_tools()  # connects now; raises if the server is broken
    return LlmAgent(name="async_file_agent", model="gemini-3.5-flash", tools=[toolset])


async def main() -> None:
    runner = InMemoryRunner(agent=await build_agent(), app_name="async_demo")
    try:
        ...  # runner.run_async(...)
    finally:
        await runner.close()  # closes the toolsets and stops the MCP process
```

Rule: define `root_agent` synchronously in `agent.py` unless you are writing
your own runtime. For eager connection checks in a deployed agent, use a
startup hook or health check, not an async agent definition.

## Common errors

| Symptom | Cause and fix |
|---|---|
| `No root_agent found for 'agent'` | The agent is built inside a function. Define `root_agent` at module scope. |
| Timeout on the first turn | `npx` is still downloading the package. Run `npx -y @modelcontextprotocol/server-filesystem /tmp/mcp-demo` once by hand, then retry. |
