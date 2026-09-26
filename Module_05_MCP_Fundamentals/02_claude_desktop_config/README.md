<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 02: Claude Desktop Config

## What this shows

Claude Desktop is an MCP host. It reads one JSON file that lists MCP servers,
launches each one as a child process over stdio when it starts, and offers
their tools to the model. `claude_desktop_config.sample.json` in this folder
is a working config for the reference filesystem MCP server.

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)).
- Claude Desktop, signed in: https://claude.ai/download
- Node.js with `npx` on your PATH (`npx --version` prints a version). The
  `@modelcontextprotocol/server-filesystem` package is downloaded by `npx -y`
  on first use.
- The folder the server may access: `mkdir -p /tmp/mcp-demo`, or run
  `bash ../lab_filesystem_mcp_inspector/setup_demo_folder.sh` for sample files.

Where the config file lives:

| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

If the file does not exist, create it (Claude Desktop creates the folder the
first time it starts). You can also open it from Claude Desktop under
Settings, Developer, Edit Config.

## Run it

1. Open the config file in an editor:
   - macOS: `open -a TextEdit "$HOME/Library/Application Support/Claude/claude_desktop_config.json"`
   - Windows (PowerShell): `notepad "$env:APPDATA\Claude\claude_desktop_config.json"`
   - Linux: `${EDITOR:-nano} ~/.config/Claude/claude_desktop_config.json`
2. Copy the contents of `claude_desktop_config.sample.json` into it. If you
   already have servers configured, add the `filesystem` entry under the
   existing `mcpServers` key instead of replacing the file. To use a different
   folder, change the last argument to an absolute path.
3. Quit Claude Desktop completely (Cmd+Q on macOS, not just closing the
   window) and start it again.
4. In a new chat, send: "List the files in /tmp/mcp-demo and summarize them."

To add a Python server, add another key under `mcpServers`. Use the absolute
path of the interpreter that has `fastmcp` installed (Claude Desktop does not
see your activated virtual environment) and the absolute path of the script:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp/mcp-demo"]
    },
    "weather": {
      "command": "/absolute/path/to/repo/.venv/bin/python",
      "args": ["/absolute/path/to/repo/Module_05_MCP_Fundamentals/03_fastmcp_first_server/server.py"]
    }
  }
}
```

## What to look for

- The tools menu in the chat input lists the filesystem server's tools
  (`read_text_file`, `list_directory`, `write_file`, and others).
- Claude asks for approval before each tool call. Expand a tool call to see
  the JSON arguments it sent and the result the server returned.
- Each entry under `mcpServers` is a separate child process.

## Common errors

| Symptom | Cause and fix |
|---|---|
| Tools do not appear | Claude Desktop was not fully quit, or the JSON is invalid. Check with `python -m json.tool claude_desktop_config.json`. |
| `spawn npx ENOENT` | Claude Desktop cannot find Node. Install Node.js and restart it. With nvm, set `command` to the absolute path of `npx`. |
| Server starts, then errors | Read `~/Library/Logs/Claude/mcp*.log` (macOS) or `%APPDATA%\Claude\logs` (Windows). Usually the folder path does not exist. |

## Clean up

Remove the `filesystem` (and `weather`) entries from the config file and
restart Claude Desktop. `rm -rf /tmp/mcp-demo` removes the demo folder.
