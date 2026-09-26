<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Lab: Filesystem MCP Server in Claude Desktop and Inspector

## What this shows

Raw MCP with no ADK and no Python code: the reference filesystem MCP server
(`@modelcontextprotocol/server-filesystem`) used from two hosts. Claude
Desktop lets a model call its tools; MCP Inspector lets you call the same
tools by hand and read the JSON-RPC. Same server, same tools, two clients.

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)).
- Node.js with `npx` on your PATH.
- Claude Desktop, signed in: https://claude.ai/download
- A browser, for MCP Inspector.
- No API keys and no Python code.

## Run it

All commands run from `Module_05_MCP_Fundamentals/lab_filesystem_mcp_inspector`.

### Step 1: Create the demo folder

From this folder:

```bash
bash setup_demo_folder.sh
```

This creates `/tmp/mcp-demo/` with `readme.txt`, `pricing.txt`, and
`meeting_notes.txt`. Set `MCP_DEMO_DIR` to use another folder. On Windows,
create a folder such as `C:\Users\you\mcp-demo` and add three text files.

### Step 2: Configure Claude Desktop

Edit (or create) the Claude Desktop config file. Its location per OS is in
`../02_claude_desktop_config/README.md`. Add:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/tmp/mcp-demo"
      ]
    }
  }
}
```

On Windows use a path like `C:\\Users\\you\\mcp-demo` (backslashes escaped).

Quit Claude Desktop completely (Cmd+Q on macOS, right-click the tray icon and
Quit on Windows) and start it again.

### Step 3: Ask Claude to use the tools

In a new chat, open the tools menu in the input area. The filesystem tools
are listed (`read_text_file`, `read_multiple_files`, `list_directory`,
`write_file`, and others). Send:

> List the files in /tmp/mcp-demo, then read all three and give me a one-paragraph summary.

Claude asks for approval, then calls `list_directory` and a read tool. Expand
each tool call to see its JSON arguments and result.

### Step 4: Open the same server in MCP Inspector

Warm the npm cache once, so Inspector does not have to install the package
while it waits for the server to start. Stop it with Ctrl+C after it prints
`Secure MCP Filesystem Server running on stdio`:

```bash
npx -y @modelcontextprotocol/server-filesystem /tmp/mcp-demo
```

Then start Inspector. Do not pass `-y` here: Inspector would treat it as its
own option.

```bash
npx @modelcontextprotocol/inspector npx @modelcontextprotocol/server-filesystem /tmp/mcp-demo
```

This starts a second, separate copy of the server and prints a URL with an
`MCP_INSPECTOR_API_TOKEN` parameter. Open that URL.

### Step 5: Call tools/list and read_text_file by hand

1. Click **Connect**.
2. Open **Tools** and click **List Tools**. This is the same `tools/list`
   response Claude Desktop received.
3. Select `read_text_file`, set `path` to `/tmp/mcp-demo/readme.txt`, and run it.
4. Open the **History** pane to see the raw requests and responses.

The same two calls from the terminal, without the browser:

```bash
npx @modelcontextprotocol/inspector --cli npx @modelcontextprotocol/server-filesystem /tmp/mcp-demo --method tools/list
npx @modelcontextprotocol/inspector --cli npx @modelcontextprotocol/server-filesystem /tmp/mcp-demo \
  --method tools/call --tool-name read_text_file --tool-arg path=/tmp/mcp-demo/readme.txt
```

## What to look for

- The tool list in Claude Desktop and in Inspector is identical: both came
  from the same `tools/list` call.
- `read_file` is still listed but its description says it is deprecated in
  favor of `read_text_file`. Servers evolve; always check `tools/list`
  rather than hardcoding names from old examples.
- The server only allows paths under the folder passed on its command line.
  Ask Claude to read `/etc/hosts` and the tool returns an access-denied error.

### Going further

- Add a second server under `mcpServers` (for example
  `@modelcontextprotocol/server-memory`) and use both in one chat.
- Point the filesystem server at a folder you cannot write to, then ask
  Claude to create a file and read the error it gets back.
- Compare the `inputSchema` of `read_text_file` with the one FastMCP generated
  for `get_weather` in `../03_fastmcp_first_server/`.

## Common errors

| Symptom | Cause and fix |
|---|---|
| No tools in Claude Desktop | It was not fully quit before reopening, or the config JSON is invalid. |
| `spawn npx ENOENT` | Install Node.js and restart Claude Desktop. |
| Inspector: connection timed out | The server package was still being downloaded. Run the warm-up command in Step 4, then retry. |
| Access denied on a path | The path is outside the allowed folder. On macOS `/tmp` is a link to `/private/tmp`; the server accepts both. |

## Clean up

```bash
rm -rf /tmp/mcp-demo
```

Remove the `filesystem` entry from `claude_desktop_config.json` and restart
Claude Desktop.
