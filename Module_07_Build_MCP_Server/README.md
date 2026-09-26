<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Module 7: Building MCP Servers with FastMCP

Module 5 covered the protocol and Module 6 connected ADK agents to existing
servers. This module builds servers: with FastMCP (decorators on typed
functions, the same style as ADK function tools) and with the low-level `mcp`
SDK where it helps to see the parts. It ends with a server packaged for
Cloud Run and an ADK agent that uses it locally and remotely.

## Before you start

- Repository setup from [SETUP.md](../SETUP.md), virtual environment active
  (`fastmcp`, `mcp`, `starlette`, `uvicorn`, `google-adk` are all in
  `requirements.txt`).
- Node.js with `npx`, for MCP Inspector.
- The lab agent calls a model: a `.env` with your Gemini settings (Gemini API
  key, or Agent Platform (formerly Vertex AI) with
  `GOOGLE_CLOUD_LOCATION=global` for `gemini-3.5-flash`). Nothing else in this
  module needs a key.
- For the deploy steps (topic 05 and the lab): the `gcloud` CLI,
  authenticated, and a project with billing and the Cloud Run, Cloud Build,
  and Artifact Registry APIs enabled. Docker is optional;
  `gcloud run deploy --source .` builds the image in Cloud Build.

The servers are not ADK agents: they run with `python`, and you inspect them
with MCP Inspector. The one agent, `lab_techtrapture_mcp/course_advisor/`,
runs with `adk web`.

## Topics

Follow them in this order.

| Order | Folder | What it shows |
|---|---|---|
| 1 | `01_fastmcp_hello/` | The smallest FastMCP server: one tool over stdio |
| 2 | `02_three_primitives/` | Tools, resources, and prompts in one server |
| 3 | `03_adk_to_mcp_bridge/` | Publish an existing ADK `FunctionTool` as an MCP server |
| 4 | `04_streamable_http_server/` | Stateless Streamable HTTP with the low-level `mcp` SDK |
| 5 | `05_dockerfile/` | Container image and `gcloud run deploy --source .` |
| 6 | `06_security_checklist/` | Auth, input validation, rate limiting, audit logging, read-only defaults |
| 7 | `07_test_with_inspector/` | MCP Inspector (UI and CLI) and a scripted smoke test |
| 8 | `lab_techtrapture_mcp/` | Lab: a full server, stdio to Cloud Run, used by an ADK agent in `adk web` |

## Library versions

The samples target `mcp` 2.x and `fastmcp` 4.x. Two changes matter if you
compare with older examples online:

- `mcp` 2.x low-level servers register handlers in the constructor,
  `Server(name, on_list_tools=..., on_call_tool=...)`, and its Python types
  use snake_case attributes (`input_schema`, `structured_content`).
- FastMCP 4.x builds the HTTP app with `mcp.http_app(path=..., stateless_http=...)`;
  `streamable_http_app()` and HTTP settings on the `FastMCP(...)` constructor
  are gone.

## Key idea

Publish one MCP server and every MCP-capable host (ADK, Claude Desktop, IDEs,
other agent frameworks) can use your tools without a client library.
