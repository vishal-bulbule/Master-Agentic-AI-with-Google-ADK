<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# MCP without a framework

## What this shows

A client talking to an MCP server directly with the `mcp` Python SDK. The
script starts the reference filesystem server over stdio, lists the tools it
advertises, then calls `list_directory` and `read_text_file` against the
`sample_docs/` folder. This is the protocol exchange ADK's `McpToolset`
performs for you in later modules. No model is called.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and `pip install -r requirements.txt` (includes `mcp`).
- [ ] Node.js with `npx` on your path. The first run downloads
      `@modelcontextprotocol/server-filesystem`.
- [ ] No credentials: nothing here calls Gemini.

## Run it

1. `cd Module_00_AI_Foundations/09_mcp_grounding`
2. `python mcp_grounding.py`

## What to look for

- The server's own log lines ("Secure MCP Filesystem Server running on
  stdio") on stderr, then the list of tools it advertises, each with a
  description a model would read.
- The `read_text_file` result is the text you would put into a prompt to
  ground an answer.

## Common errors

| Symptom | Fix |
|---|---|
| `npx: command not found` or `FileNotFoundError: npx` | Install Node.js (see SETUP.md) |
| Long pause on first run | `npx` is downloading the server package; wait |
