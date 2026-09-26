<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 03: Filtering MCP Tools

## What this shows

By default `McpToolset` exposes every tool the server advertises.
`tool_filter` limits the agent to the names you list. The filesystem server
has 14 tools, including `write_file`, `edit_file`, and `move_file`; this agent
sees two, so it is read-only by construction, not only by instruction.

```python
McpToolset(
    connection_params=...,
    tool_filter=["read_text_file", "list_directory"],
)
```

| Reason to filter | Detail |
|---|---|
| Least privilege | A read-only agent should not have write tools at all, whatever its instruction says. |
| Fewer wrong calls | Every extra tool is another option the model can pick by mistake. |
| Smaller requests | Every tool's schema is sent with every model request. Fewer tools cost fewer tokens. |

`tool_filter` also accepts a function `(tool, readonly_context) -> bool`, for
rules such as "only tools whose name starts with `read_`".

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)) and a `.env` with your Gemini
  settings (see `agent/.env.example`; on Agent Platform use
  `GOOGLE_CLOUD_LOCATION=global`).
- Node.js with `npx` on your PATH. ADK starts the filesystem server itself.
- A sample file:

  ```bash
  mkdir -p /tmp/mcp-demo
  echo "quarterly numbers: draft" > /tmp/mcp-demo/notes.txt
  ```

## Run it

1. `cd Module_06_MCP_Client_ADK/03_tool_filter`
2. `adk web`
3. Open http://localhost:8000 and select `agent` in the agent dropdown.
4. Send: "Read notes.txt."

Terminal alternative: `adk run agent`.

## Try it

- "Read notes.txt." Works.
- "List the files here." Works.
- "Write a file called hack.txt." The agent has no write tool and says so.

## What to look for

- In the Events view, click a model row and open the side panel's Request
  view: the function declarations contain only `read_text_file` and
  `list_directory`.
- The refusal for the write request does not depend on the model obeying the
  instruction. Even a prompt injection cannot call a tool the agent was never
  given.

Filter tool names against what the server advertises today. The filesystem
server renamed `read_file` to `read_text_file` (the old name is kept but
marked deprecated); a filter that names a tool the server no longer has
silently exposes nothing for it.
