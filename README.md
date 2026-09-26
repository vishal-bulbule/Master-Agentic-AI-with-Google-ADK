<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Master Agentic AI with Google ADK

**Build, test and deploy AI agents with the Google Agent Development Kit (ADK):
117 runnable Python agents covering tools, MCP, A2A, multi-agent workflows,
sessions and memory, RAG and grounding, the Live API, evaluation, observability
and deployment to Cloud Run and Agent Runtime.**

[![ADK](https://img.shields.io/badge/Google%20ADK-2.9.2-4285F4?logo=google&logoColor=white)](https://adk.dev)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Gemini](https://img.shields.io/badge/Gemini-3.5%20Flash-8E75B2?logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![License](https://img.shields.io/github/license/vishal-bulbule/Master-Agentic-AI-with-Google-ADK?color=0C56DC)](LICENSE)
[![Stars](https://img.shields.io/github/stars/vishal-bulbule/Master-Agentic-AI-with-Google-ADK?style=flat&color=0C56DC)](https://github.com/vishal-bulbule/Master-Agentic-AI-with-Google-ADK/stargazers)
[![YouTube](https://img.shields.io/badge/YouTube-Master%20Agentic%20AI%20with%20ADK-FF0000?logo=youtube&logoColor=white)](https://www.youtube.com/playlist?list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi)

> **About me** - I am **Vishal Bulbule**, founder of [TechTrapture](https://www.techtrapture.com),
> a Google Developer Expert for Google Cloud and AI, and an enterprise architect.
> I contribute to the open-source [Google ADK](https://github.com/google/adk-python)
> project, teach Agentic AI and MCP through [TechTrapture Academy](https://academy.techtrapture.com),
> and have been publishing Google Cloud content on [YouTube](https://youtube.com/@techtrapture) for 5 years.
>
> This repository is the code behind the **Master Agentic AI with Google ADK**
> playlist, rebuilt and tested on current ADK.

Sixteen modules take you from a raw Gemini API call to a deployed, evaluated
multi-agent system. Each topic folder holds one ADK feature as a standalone
agent you run in the dev UI with `adk web`, with a README that lists its
prerequisites, the exact command, and what to look for.

Every sample runs on **ADK 2.9.2**, verified on 2026-09-22 with google-genai
2.24, mcp 2.2, fastmcp 4.0 and a2a-sdk 1.1 on Python 3.12, using
`gemini-3.5-flash`.

**Topics:** Google ADK tutorial, AI agents in Python, LlmAgent, function
tools, OpenAPI tools, Model Context Protocol (MCP) clients and servers,
FastMCP, Agent2Agent (A2A) protocol, sequential, parallel and loop workflows,
`Workflow` graphs, callbacks and plugins, guardrails, sessions, state and
long-term memory, artifacts, Google Search grounding, Vertex AI Search, agentic
RAG, streaming and the Live API for voice agents, `adk eval`, rubric metrics,
OpenTelemetry tracing, Cloud Run and Agent Runtime deployment, Secret Manager,
CI/CD with GitHub Actions.

## Want to learn Agentic AI with guidance?

This repository is free and self-paced. If you would rather learn it in a
cohort, with live sessions, real deployments and feedback on your own agents,
join the next **[TechTrapture Academy](https://academy.techtrapture.com)**
cohort on Agentic AI and Google Cloud.

**[Join the next cohort](https://academy.techtrapture.com)**

## What is covered

- The ADK 2.x `Workflow` graph API for pipelines, fan-out, joins and loops,
  alongside the `SequentialAgent`, `ParallelAgent` and `LoopAgent` classes it
  replaces
- MCP in both directions: consuming servers with `McpToolset`, and building
  servers with FastMCP and the low-level `mcp` server API
- A2A 1.0: exposing an agent with `to_a2a` and calling it with `RemoteA2aAgent`
- Callbacks at all six hook points, plugins, skills, and guardrails
- Sessions, state prefixes, memory, artifacts, and session rewind
- The Live API for voice agents, and token streaming
- Evaluation with `adk eval`, pytest, rubric and custom metrics, plus
  OpenTelemetry tracing
- Deployment to Cloud Run and Agent Runtime, with Secret Manager and CI/CD

## Quick start

```bash
git clone https://github.com/vishal-bulbule/Master-Agentic-AI-with-Google-ADK.git
cd Master-Agentic-AI-with-Google-ADK

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env    # add a Gemini API key, or Agent Platform settings
```

[SETUP.md](SETUP.md) covers accounts, keys, Google Cloud APIs, and the extra
setup a few modules need.

## Running a sample

Every agent sample is a plain ADK agent folder (`agent.py` with a
`root_agent`, `__init__.py`, `.env.example`) with no runner code. Run it from
the folder that contains it:

```bash
cd Module_02_First_ADK_Agent
adk web                 # dev UI at http://localhost:8000
```

Open http://localhost:8000, pick the agent in the dropdown, and send a
prompt. The main panel's Events view lists what the agent did as numbered
rows (click one to see its details in the side panel), and the Traces view
next to it shows the timing of each model and tool call. The side panel's
State and Artifacts tabs show session state (read-only) and saved files.
`adk run <agent_folder>` runs the same agent in the terminal.

Each topic README follows the same layout: **Prerequisites** (extra packages,
keys, cloud resources to create first, servers that must be running), **Run
it** (the exact `adk web` command and flags), **Try it** (prompts to send and
what to look for), and **Clean up**. A few samples need flags such as
`--session_service_uri` or `--a2a`; their README gives the full command.

Every agent here has been run against a live model. The few that cannot be
verified end to end without extra setup, such as a microphone, a deployed
service or a third-party key, say so in their README.

The only things you run with `python` or `pytest` are the ones that are not
agents: the raw SDK scripts in Module 0, the MCP-without-ADK samples and MCP
servers in Modules 5 and 7, pytest suites, and the custom container app in
`Module_15_Deployment/08_custom_dockerfile`.

## Modules

Work through them in order. Each module README lists its topics and the order
to follow.

| # | Module | Agents | What it covers |
|---|---|---|---|
| 0 | [AI Foundations](Module_00_AI_Foundations/) | 1 | The raw `google-genai` SDK underneath every agent: config, streaming, multimodal, function calling, tokens, MCP without ADK, then the same task as an ADK agent |
| 1 | [Agents Landscape](Module_01_Agents_Landscape/) | 5 | The same task as a chatbot, a RAG pipeline and an agent; the agent loop traced |
| 2 | [First ADK Agent](Module_02_First_ADK_Agent/) | 9 | One agent in all three runtimes (`adk web`, `adk run`, `adk api_server`), YAML config, and five broken agents to debug |
| 3 | [LlmAgent and Model Choice](Module_03_LlmAgent_Model_Choice/) | 11 | Instructions, structured output, model routing, generation config, planners, LiteLLM |
| 4 | [Custom Tools](Module_04_Custom_Tools/) | 12 | Function tools, long-running tools, agents as tools, OpenAPI, auth, tool confirmation |
| 5 | [MCP Fundamentals](Module_05_MCP_Fundamentals/) | 1 | MCP on its own: FastMCP servers, the JSON-RPC exchange, MCP Inspector, Claude Desktop, then an ADK agent as the host |
| 6 | [MCP Client in ADK](Module_06_MCP_Client_ADK/) | 9 | `McpToolset` over stdio, SSE and Streamable HTTP; tool filters; GitHub and Google Maps servers |
| 7 | [Build an MCP Server](Module_07_Build_MCP_Server/) | 1 | FastMCP and low-level servers, exposing ADK tools over MCP, security, Cloud Run |
| 8 | [Sessions, State and Memory](Module_08_Sessions_State_Memory/) | 10 | Session services, state prefixes, memory, artifacts, rewind |
| 9 | [Workflows and Multi-Agent](Module_09_Workflow_MultiAgent/) | 12 | `Workflow` graphs, parallel fan-out and join, loops, routing, custom agents, hierarchies |
| 10 | [Callbacks, Plugins and Events](Module_10_Callbacks_Plugins_Events/) | 15 | All six callback hooks, guardrails, caching, cost control, plugins, skills |
| 11 | [Streaming and Live API](Module_11_Streaming_Live_API/) | 4 | Token streaming, Live API voice agents in the dev UI, streaming tools |
| 12 | [A2A Protocol](Module_12_A2A_Protocol/) | 6 | Exposing and consuming agents over A2A, agent cards, extensions |
| 13 | [Grounding](Module_13_Grounding/) | 7 | Google Search grounding, citations, Vertex AI Search, agentic and hybrid RAG |
| 14 | [Evaluation and Observability](Module_14_Evaluation_Observability/) | 8 | Eval sets, criteria, pytest, rubrics, user simulation, tracing, safety layers |
| 15 | [Deployment](Module_15_Deployment/) | 6 | Agent Runtime, Cloud Run, secrets, IAM, custom containers, scaling, CI/CD |

## Video walkthroughs

Every topic below has videos in the
[Master Agentic AI with Google ADK playlist](https://www.youtube.com/playlist?list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi)
on YouTube. Earlier videos were recorded on older ADK releases, so some APIs
and model names on screen have changed; the linked modules have the current,
tested code, and the code from the first videos is in
[archived_samples/](archived_samples/).

### Getting started

Code: [Module 1](Module_01_Agents_Landscape/), [Module 2](Module_02_First_ADK_Agent/)

<div align="center">

<table><tr><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=xXQKoYaoZwA&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/xXQKoYaoZwA/mqdefault.jpg" width="250" alt="Google Cloud Agent Development Kit Tutorial | Build Your First ADK Agent"/><br/><b>Google Cloud Agent Development Kit Tutorial | Build Your First ADK Agent</b></a><br/><sub>Sep 17, 2025</sub></td></tr></table>

</div>

### Tools

Code: [Module 4](Module_04_Custom_Tools/)

<div align="center">

<table><tr><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=idgTB7IZGOk&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/idgTB7IZGOk/mqdefault.jpg" width="250" alt="Google Cloud ADK Agent Tools Explained | In-Built Tools, Function Tools &amp; Third-Party Tools"/><br/><b>Google Cloud ADK Agent Tools Explained | In-Built Tools, Function Tools &amp; Third-Party Tools</b></a><br/><sub>Sep 18, 2025</sub></td><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=Q9OC2e6yGgk&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/Q9OC2e6yGgk/mqdefault.jpg" width="250" alt="Build a BigQuery Agent using Google Cloud ADK | Built-In Tool Demo"/><br/><b>Build a BigQuery Agent using Google Cloud ADK | Built-In Tool Demo</b></a><br/><sub>Sep 19, 2025</sub></td><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=jsXHoTAc2A8&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/jsXHoTAc2A8/mqdefault.jpg" width="250" alt="Google Cloud ADK Third-Party Tools | Build AI Agents with LangChain &amp; CrewAI"/><br/><b>Google Cloud ADK Third-Party Tools | Build AI Agents with LangChain &amp; CrewAI</b></a><br/><sub>Sep 23, 2025</sub></td></tr><tr><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=zTwuzJWQIiI&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/zTwuzJWQIiI/mqdefault.jpg" width="250" alt="Build GitHub Agent with Google Cloud ADK | Function Tools Demo"/><br/><b>Build GitHub Agent with Google Cloud ADK | Function Tools Demo</b></a><br/><sub>Sep 23, 2025</sub></td></tr></table>

</div>

### Agent types and workflows

Code: [Module 9](Module_09_Workflow_MultiAgent/)

<div align="center">

<table><tr><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=xOzKm3U2Y-E&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/xOzKm3U2Y-E/mqdefault.jpg" width="250" alt="Google Cloud ADK Agents Explained | LLM, Workflow &amp; Custom Agents"/><br/><b>Google Cloud ADK Agents Explained | LLM, Workflow &amp; Custom Agents</b></a><br/><sub>Sep 24, 2025</sub></td><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=XT2grQenzsg&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/XT2grQenzsg/mqdefault.jpg" width="250" alt="Build a Job Search AI Agent with Google Cloud ADK | Sequential Agent Demo"/><br/><b>Build a Job Search AI Agent with Google Cloud ADK | Sequential Agent Demo</b></a><br/><sub>Sep 25, 2025</sub></td><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=F6cBBbyBJTw&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/F6cBBbyBJTw/mqdefault.jpg" width="250" alt="Build a Content Creation AI Agent with Google Cloud ADK | Parallel Agent Demo"/><br/><b>Build a Content Creation AI Agent with Google Cloud ADK | Parallel Agent Demo</b></a><br/><sub>Sep 26, 2025</sub></td></tr><tr><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=CUQm-2zckn4&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/CUQm-2zckn4/mqdefault.jpg" width="250" alt="Cloud Architect Agent with Google Cloud ADK | Loop Agent Tutorial"/><br/><b>Cloud Architect Agent with Google Cloud ADK | Loop Agent Tutorial</b></a><br/><sub>Sep 29, 2025</sub></td></tr></table>

</div>

### Model Context Protocol (MCP)

Code: [Module 5](Module_05_MCP_Fundamentals/), [Module 6](Module_06_MCP_Client_ADK/), [Module 7](Module_07_Build_MCP_Server/)

<div align="center">

<table><tr><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=kFf37B8UsFE&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/kFf37B8UsFE/mqdefault.jpg" width="250" alt="Model Context Protocol (MCP) Explained with Real Examples"/><br/><b>Model Context Protocol (MCP) Explained with Real Examples</b></a><br/><sub>Oct 08, 2025</sub></td><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=EF6LLGR9k0I&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/EF6LLGR9k0I/mqdefault.jpg" width="250" alt="Build Your First MCP Server with Google Maps &amp; VS Code | MCP Beginner Tutorial"/><br/><b>Build Your First MCP Server with Google Maps &amp; VS Code | MCP Beginner Tutorial</b></a><br/><sub>Oct 10, 2025</sub></td><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=9jRBRNRDRh4&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/9jRBRNRDRh4/mqdefault.jpg" width="250" alt="Build Your First MCP Server with Google Maps &amp; Claude Desktop"/><br/><b>Build Your First MCP Server with Google Maps &amp; Claude Desktop</b></a><br/><sub>Oct 13, 2025</sub></td></tr><tr><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=4qwgR9XxBQg&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/4qwgR9XxBQg/mqdefault.jpg" width="250" alt="I Built a Google Maps AI Agent in 10 Minutes with Google ADK"/><br/><b>I Built a Google Maps AI Agent in 10 Minutes with Google ADK</b></a><br/><sub>Oct 14, 2025</sub></td><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=Z_wOZwMfoxI&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/Z_wOZwMfoxI/mqdefault.jpg" width="250" alt="Connect Your Database to Google ADK AI Agents Using MCP | BigQuery Tutorial"/><br/><b>Connect Your Database to Google ADK AI Agents Using MCP | BigQuery Tutorial</b></a><br/><sub>Oct 15, 2025</sub></td><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=f8ttt3WfjeM&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/f8ttt3WfjeM/mqdefault.jpg" width="250" alt="BigQuery MCP Server Explained with HR Agents"/><br/><b>BigQuery MCP Server Explained with HR Agents</b></a><br/><sub>Oct 16, 2025</sub></td></tr></table>

</div>

### Callbacks

Code: [Module 10](Module_10_Callbacks_Plugins_Events/)

<div align="center">

<table><tr><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=aUoqSzOARSg&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/aUoqSzOARSg/mqdefault.jpg" width="250" alt="Google ADK Callbacks Explained | Build Production AI Agents"/><br/><b>Google ADK Callbacks Explained | Build Production AI Agents</b></a><br/><sub>Oct 27, 2025</sub></td><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=6o-gEahLSYo&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/6o-gEahLSYo/mqdefault.jpg" width="250" alt="Implementing Agent Callbacks with Google Cloud ADK | Step-by-Step Tutorial"/><br/><b>Implementing Agent Callbacks with Google Cloud ADK | Step-by-Step Tutorial</b></a><br/><sub>Nov 05, 2025</sub></td><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=DyeW_0mcqI4&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/DyeW_0mcqI4/mqdefault.jpg" width="250" alt="Unlock Model Callbacks in ADK | Before &amp; After LLM Hooks Explained"/><br/><b>Unlock Model Callbacks in ADK | Before &amp; After LLM Hooks Explained</b></a><br/><sub>Nov 06, 2025</sub></td></tr><tr><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=Ee1Y7gwvhy8&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/Ee1Y7gwvhy8/mqdefault.jpg" width="250" alt="Master Tool Execution Callbacks in Google Cloud ADK | Before &amp; After Tool Hooks"/><br/><b>Master Tool Execution Callbacks in Google Cloud ADK | Before &amp; After Tool Hooks</b></a><br/><sub>Nov 11, 2025</sub></td></tr></table>

</div>

### Sessions, state and memory

Code: [Module 8](Module_08_Sessions_State_Memory/)

<div align="center">

<table><tr><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=F1a9lLySxLI&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/F1a9lLySxLI/mqdefault.jpg" width="250" alt="Google ADK Session &amp; State Management Explained | Session, State &amp; Memory"/><br/><b>Google ADK Session &amp; State Management Explained | Session, State &amp; Memory</b></a><br/><sub>Feb 12, 2026</sub></td><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=E9BcLtuuI7U&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/E9BcLtuuI7U/mqdefault.jpg" width="250" alt="Google ADK Session Management Hands-On (InMemory, Cloud SQL, Vertex AI)"/><br/><b>Google ADK Session Management Hands-On (InMemory, Cloud SQL, Vertex AI)</b></a><br/><sub>Feb 13, 2026</sub></td><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=JNO9xb1p1mQ&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/JNO9xb1p1mQ/mqdefault.jpg" width="250" alt="ADK State Management Explained with Demo"/><br/><b>ADK State Management Explained with Demo</b></a><br/><sub>Feb 17, 2026</sub></td></tr><tr><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=5onUg-YJBZA&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/5onUg-YJBZA/mqdefault.jpg" width="250" alt="Build Agents with Long-Term Memory | InMemory vs Agent Platform Memory Bank"/><br/><b>Build Agents with Long-Term Memory | InMemory vs Agent Platform Memory Bank</b></a><br/><sub>Feb 18, 2026</sub></td><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=5BT8i57cYIk&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/5BT8i57cYIk/mqdefault.jpg" width="250" alt="Agent Platform Memory Bank Demo | Long-Term Memory for AI Agents"/><br/><b>Agent Platform Memory Bank Demo | Long-Term Memory for AI Agents</b></a><br/><sub>Feb 19, 2026</sub></td></tr></table>

</div>

### Deployment

Code: [Module 15](Module_15_Deployment/)

<div align="center">

<table><tr><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=adtykJjkF_0&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/adtykJjkF_0/mqdefault.jpg" width="250" alt="Deploy ADK Agent to Vertex AI Agent Engine | Google Cloud ADK Tutorial"/><br/><b>Deploy ADK Agent to Vertex AI Agent Engine | Google Cloud ADK Tutorial</b></a><br/><sub>Sep 30, 2025</sub></td><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=zA0Y3smlavA&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/zA0Y3smlavA/mqdefault.jpg" width="250" alt="Deploy ADK Agent to Cloud Run | Google Cloud ADK Tutorial"/><br/><b>Deploy ADK Agent to Cloud Run | Google Cloud ADK Tutorial</b></a><br/><sub>Oct 01, 2025</sub></td><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=vj97RE5sjYQ&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/vj97RE5sjYQ/mqdefault.jpg" width="250" alt="Deploy Google ADK Agent on Cloud Run | Live Demo"/><br/><b>Deploy Google ADK Agent on Cloud Run | Live Demo</b></a><br/><sub>Jun 25, 2026</sub></td></tr><tr><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=kndv61pGjS8&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/kndv61pGjS8/mqdefault.jpg" width="250" alt="Deploy ADK Agent on Agent Runtime (Agent Engine) | Live Demo"/><br/><b>Deploy ADK Agent on Agent Runtime (Agent Engine) | Live Demo</b></a><br/><sub>Jun 30, 2026</sub></td><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=j68Q5wvwaao&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/j68Q5wvwaao/mqdefault.jpg" width="250" alt="Deploy AI Agents on GKE with Google ADK | Live Demo"/><br/><b>Deploy AI Agents on GKE with Google ADK | Live Demo</b></a><br/><sub>Jul 01, 2026</sub></td></tr></table>

</div>

### Real-world builds

<div align="center">

<table><tr><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=ZlcJFnVaXD4&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/ZlcJFnVaXD4/mqdefault.jpg" width="250" alt="Building an AI SRE Agent with ADK + MCP | Auto RCA, Log Analysis &amp; Send Emails"/><br/><b>Building an AI SRE Agent with ADK + MCP | Auto RCA, Log Analysis &amp; Send Emails</b></a><br/><sub>Feb 26, 2026</sub></td><td align="center" valign="top" width="33%"><a href="https://www.youtube.com/watch?v=uYN8Y4lDk80&list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi"><img src="https://i.ytimg.com/vi/uYN8Y4lDk80/mqdefault.jpg" width="250" alt="I Built a CloudOps Agent with Google ADK | Real-World Demo"/><br/><b>I Built a CloudOps Agent with Google ADK | Real-World Demo</b></a><br/><sub>Jun 05, 2026</sub></td></tr></table>

</div>

## Archived samples

The code from the original
[YouTube playlist](https://www.youtube.com/playlist?list=PLLrA_pU9-Gz2HwepRUVpq1TEPuYWo_fSi)
is in [archived_samples/](archived_samples/). It is kept as recorded so it
matches the videos, and it is not maintained.

## Author

**Vishal Bulbule** - Google Developer Expert for Google Cloud and AI, founder of
[TechTrapture](https://www.techtrapture.com).

[YouTube](https://youtube.com/@techtrapture) |
[LinkedIn](https://www.linkedin.com/in/vishal-bulbule/) |
[Medium](https://vishalbulbule.medium.com/) |
[X](https://x.com/vishal__bulbule) |
[TechTrapture Academy](https://academy.techtrapture.com)

Issues and pull requests are welcome. If a sample breaks on a newer ADK
release, open an issue with the module path and the error.

## License

Apache License 2.0. See [LICENSE](LICENSE).

<img src="https://komarev.com/ghpvc/?username=vishal-bulbule-master-agentic-ai-adk&label=Repo%20Views&color=1E3A8A&style=for-the-badge" alt="repo views"/>
