<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 04: Multiple MCP Servers, One Agent

## What this shows

Several `McpToolset` instances in one `tools` list. ADK merges their tools
into one list for the model.

```python
LlmAgent(
    tools=[
        McpToolset(connection_params=filesystem_params, tool_filter=[...]),
        McpToolset(connection_params=memory_params),
    ],
)
```

| Server | Used for |
|---|---|
| `@modelcontextprotocol/server-filesystem` (read-only filter) | Reading files in `/tmp/mcp-demo` |
| `@modelcontextprotocol/server-memory` | A knowledge graph stored in `/tmp/mcp-demo-memory.jsonl`, so facts persist across sessions |

Tool names must be unique across all toolsets, because the model calls tools
by name. When two servers both expose `search` or `read`:

1. `tool_name_prefix="fs"` on a McpToolset renames its tools (`fs_read_text_file`),
   which keeps every server's tools and removes the clash.
2. `tool_filter` on each toolset, so the exposed names do not overlap.
3. Keep one concern per server: do not load three servers that all "search".
4. Split overlapping servers into sub-agents and delegate with `AgentTool`
   (see `Module_04_Custom_Tools/05_agent_as_tool/`).

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)) and a `.env` with your Gemini
  settings (see `agent/.env.example`; on Agent Platform use
  `GOOGLE_CLOUD_LOCATION=global`).
- Node.js with `npx` on your PATH. ADK starts both servers itself.
- A sample file:

  ```bash
  mkdir -p /tmp/mcp-demo
  echo "Project: ADK MCP samples. Owner: platform team." > /tmp/mcp-demo/project.txt
  ```

## Run it

1. `cd Module_06_MCP_Client_ADK/04_multiple_servers`
2. `adk web`
3. Open http://localhost:8000 and select `agent` in the agent dropdown.
4. Send: "Read project.txt."

Terminal alternative: `adk run agent`. Each `adk run` is a new process, which
also shows that the stored facts survive a restart.

## Try it

1. "Read project.txt." Calls `read_text_file` on the filesystem server.
2. "Remember that I am a Python developer who prefers espresso." Calls
   `create_entities` or `add_observations` on the memory server.
3. Click **New Session**, then ask "What do you remember about me?" Calls
   `search_nodes` or `read_graph`. The facts come back from the file, not
   from the session history.

## What to look for

- Both servers start as separate child processes (two `npx` processes).
- The tool list the model receives (click a model row in the Events view,
  then the side panel's Request view) contains 2 filesystem tools plus all
  9 memory tools.
- `cat /tmp/mcp-demo-memory.jsonl` shows what the agent stored.

## Clean up

```bash
rm -f /tmp/mcp-demo-memory.jsonl   # resets the knowledge graph
rm -rf /tmp/mcp-demo
```
