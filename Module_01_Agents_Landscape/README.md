<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Module 1: Agents and the ADK landscape

Module 0 used the raw SDK. Here the same function-calling primitive goes
inside an ADK `LlmAgent`, and you watch the agent loop run in `adk web` and in
the terminal. By the end you can say what makes something an agent, contrast
it with a chatbot and RAG, and read the Events view.

## Topics

Work through them in order.

| Folder | What it shows |
|---|---|
| `minimal_agent_inspect/` | The smallest `LlmAgent` with one tool, inspected event by event in `adk web` |
| `chatbot_vs_rag_vs_agent/` | One customer question sent to three sibling agents: a chatbot, a RAG agent and a tool-calling agent (run `adk web` from this folder) |
| `agent_loop_trace/` | The five steps of the agent loop printed by callbacks as they happen |
| `decision_heuristic_examples/` | Five worked "agent or no agent?" cases, each matched to its cheapest shape (reading, no code) |
| `lab_run_sample_agent/` | Lab: run a larger agent from `google/adk-samples` and read its events |

## Before you start

- Repository setup from [SETUP.md](../SETUP.md): virtual environment,
  `pip install -r requirements.txt`, and a `.env` at the repository root.
  Each agent folder has a `.env.example` listing the variables it reads.
- Gemini credentials: `GOOGLE_API_KEY`, or Agent Platform (formerly Vertex
  AI) with `GOOGLE_CLOUD_LOCATION=global` for `gemini-3.5-flash`.
- `lab_run_sample_agent`: `git`, and the tools the chosen `google/adk-samples`
  agent needs (usually `uv` or `poetry`).

`adk web` and `adk run` load the nearest `.env` walking up from the agent
folder.

## Run an agent in the web UI

```bash
cd Module_01_Agents_Landscape
adk web
```

Open http://localhost:8000 and pick an agent (for example
`minimal_agent_inspect`) from the list. Each agent folder has the standard
ADK layout:

```
minimal_agent_inspect/
    __init__.py     # from . import agent
    agent.py        # defines root_agent
    README.md
```

The folder name is the app name, and ADK requires app names to start with a
letter (letters, digits, `_` and `-` after that). That is why these folders
have no numeric prefix. For a terminal chat instead of the browser:
`adk run minimal_agent_inspect`.

`chatbot_vs_rag_vs_agent/` is a folder of three agents, not an agent itself.
Run `adk web` from inside it to get `support_chatbot`, `support_rag` and
`support_agent` in the dropdown.

By default `adk web` and `adk run` keep sessions in a `.adk/` folder inside
each agent folder (ignored by git). Delete it to start from a clean slate.
