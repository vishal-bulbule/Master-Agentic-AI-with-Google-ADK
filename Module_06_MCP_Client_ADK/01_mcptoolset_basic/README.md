<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 01: McpToolset Basics

## What this shows

The smallest MCP client agent: one `McpToolset` over stdio, pointed at the
reference filesystem MCP server (`@modelcontextprotocol/server-filesystem`).
The agent gets every tool the server advertises without any adapter code, and
the server enforces its own sandbox whatever the instruction says.

```python
McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp/mcp-demo"],
        ),
        timeout=30,
    ),
)
```

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)) and a `.env` with your Gemini
  settings (see `agent/.env.example`). On Agent Platform (formerly Vertex AI)
  the model `gemini-3.5-flash` needs `GOOGLE_CLOUD_LOCATION=global`.
- Node.js with `npx` on your PATH (`which npx` prints a path). ADK starts the
  MCP server itself; you do not start it.
- The sandbox folder and a sample file:

  ```bash
  mkdir -p /tmp/mcp-demo
  echo "hello from MCP" > /tmp/mcp-demo/sample.txt
  ```

## Run it

1. `cd Module_06_MCP_Client_ADK/01_mcptoolset_basic`
2. `adk web`
3. Open http://localhost:8000 and select `agent` in the agent dropdown.
4. Send: "List the files in the folder."

Terminal alternative: `adk run agent`.

## Try it

- "List the files in the folder."
- "Read sample.txt."
- "Create a file called notes.md with the text 'MCP works'."
- "What is in /etc/passwd?"

## What to look for

On the first turn, ADK:

1. Starts `npx -y @modelcontextprotocol/server-filesystem /tmp/mcp-demo` as a
   child process.
2. Opens an MCP session over stdio and calls `tools/list`.
3. Wraps each MCP tool (`list_directory`, `read_text_file`, `write_file`, and
   the rest) as an ADK tool whose schema comes from the MCP `inputSchema`.
4. Forwards each model function call to the server with `tools/call`.
5. Stops the child process when the runner closes (when you stop `adk web`).

In the Events view, `list_directory` and `read_text_file` appear as tool
call and tool result rows; click a row to see its arguments or response in
the side panel. For `/etc/passwd` the model either
refuses (instruction) or calls a tool and gets "Access denied - path outside
allowed directories" (the server's own sandbox).

## Common errors

| Symptom | Cause and fix |
|---|---|
| `Failed to create MCP session` or a timeout on the first turn | `npx` is not on the PATH that `adk` sees, or the package download took longer than the timeout. Run `npx -y @modelcontextprotocol/server-filesystem /tmp/mcp-demo` once by hand to warm the cache. |
| Access denied for every path | `/tmp/mcp-demo` does not exist. |

## Clean up

`rm -rf /tmp/mcp-demo` removes the sandbox folder and any files the agent
wrote. Delete the `agent/.adk/` folder that `adk web` or `adk run` creates for
its local session store.
