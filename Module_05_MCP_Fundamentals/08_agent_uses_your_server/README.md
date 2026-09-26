<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 08: An agent as the MCP host

## What this shows

The rest of this module drives MCP servers from Inspector, Claude Desktop, or
a raw JSON-RPC client. Here an ADK agent is the host. `McpToolset` starts
`../03_fastmcp_first_server/server.py` over stdio, reads `tools/list`, and
turns `get_weather` into a tool the model can call.

The server file does not change. That is the payoff of the protocol: write a
server once and every MCP host can use it. Module 6 takes this further with
remote servers, tool filters, and several servers behind one agent.

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)): the virtual environment and
  credentials in a `.env` at the repository root, or in this agent folder
  using the variables from [`agent/.env.example`](agent/.env.example).
- `fastmcp` from `requirements.txt`, which the server needs. The agent starts
  the server with the same Python interpreter it runs on, so an active
  virtual environment is enough.
- Nothing to start by hand. ADK launches the server as a child process and
  stops it with the session.

## Run it

1. `cd Module_05_MCP_Fundamentals/08_agent_uses_your_server`
2. `adk web`
3. Open http://localhost:8000 and pick `agent` in the app dropdown in the top
   bar.
4. Send: "What's the weather in Pune?"

Terminal alternative: `adk run agent`.

## Try it

| Prompt | What happens |
|---|---|
| "What's the weather in Pune?" | One `get_weather` call over MCP, then the answer |
| "Compare Delhi and Bengaluru" | Two calls to the same server in one turn |
| "What's the weather in Oslo?" | The server returns `status: error`, and the agent lists the cities it does have |

## What to look for

- In the Events view, the tool call row shows `get_weather`. It looks like any
  other ADK tool: the model never learns that the tool lives in another
  process.
- The tool description and input schema in the side panel's Request view come
  from the server's docstring and type hints, sent by `tools/list`.
- The same server answers Inspector in topic 06 and Claude Desktop in topic
  02. One server, three hosts.

## Common errors

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: fastmcp` in the terminal | The server started on a Python without the dependencies | Activate the repository virtual environment before `adk web` |
| The agent reports no tools | The server failed to start | Run `python ../03_fastmcp_first_server/server.py` and check the error |
| The first call times out | The server was slow to start | The toolset allows 30 seconds; try again |

## Clean up

`adk web` and `adk run` store sessions in `agent/.adk/`. Remove it with
`rm -rf agent/.adk`.
