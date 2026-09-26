<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Module 5: MCP Fundamentals

MCP (Model Context Protocol) on its own, without ADK. The samples use the
`fastmcp` and `mcp` Python packages directly to build servers, look at the
JSON-RPC they exchange, and connect them to real hosts (Claude Desktop and MCP
Inspector). Module 6 plugs these servers into ADK agents; Module 7 goes deeper
on building and deploying servers.

Topics 1 to 8 are MCP servers and plain Python scripts, run with `python` or
through MCP Inspector; none of them is an ADK agent. Topic 9 closes the
module with an ADK agent that uses the server from topic 3, so you see the
same server answering a third kind of host.

## Before you start

- Repository setup from [SETUP.md](../SETUP.md), with the virtual environment
  active so `python` resolves to it (`fastmcp` and `mcp` are in
  `requirements.txt`).
- Node.js (current LTS) with `npx` on your PATH, for MCP Inspector and the
  reference servers (`node --version`, `npx --version`).
- Claude Desktop (https://claude.ai/download) for `02_claude_desktop_config/`
  and the lab.
- A browser for the Inspector UI.
- No API keys and no cloud resources for topics 1 to 8: nothing there calls a
  model. Topic 9 is an agent, so it needs the credentials from
  [SETUP.md](../SETUP.md).

## Topics

Follow them in this order.

| Order | Folder | What it shows |
|---|---|---|
| 1 | `01_mn_problem_diagram/` | Why MCP exists: M x N integrations become M + N |
| 2 | `02_claude_desktop_config/` | The host config file that tells Claude Desktop which servers to launch |
| 3 | `03_fastmcp_first_server/` | The smallest FastMCP server: one tool over stdio |
| 4 | `04_tools_resources_prompts/` | Tools, resources, and prompts in one server |
| 5 | `05_stdio_vs_http/` | The same server over stdio and over Streamable HTTP |
| 6 | `06_inspector_walkthrough/` | MCP Inspector: call tools by hand and read the JSON-RPC |
| 7 | `07_raw_jsonrpc_client/` | A client written with the low-level `mcp` SDK |
| 8 | `lab_filesystem_mcp_inspector/` | Lab: the filesystem MCP server in Claude Desktop and Inspector |
| 9 | `08_agent_uses_your_server/` | An ADK agent as the host for the topic 3 server, run with `adk web` |

## Key idea

A service writes one MCP server. An application writes one MCP client. Any
client can then use any server, whatever language either side is written in.
