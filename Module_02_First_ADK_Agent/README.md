<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Module 2: Your first ADK agent

A working agent on localhost, run through all three ADK runtimes: `adk web`,
`adk run` and `adk api_server`. Module 0 used the raw `google-genai` SDK to
show the LLM primitive; from here on everything is ADK.

## Topics

Work through them in order.

| Folder | What it shows |
|---|---|
| `capital_agent/` | The smallest `LlmAgent`: one tool, the standard folder layout |
| `three_runtimes_demo/` | The same agent served by `adk web`, `adk run` and `adk api_server` |
| `api_server_curl/` | The REST flow: create a session, call `/run_sse`, read the event stream |
| `yaml_config_agent/` | The capital agent declared in YAML instead of Python |
| `common_failures/` | First-run failures reproduced on purpose, each with a `FIX.md` |
| `weather_jokes_agent/` | Lab reference solution: `get_weather` and `tell_joke` tools |

## Before you start

- Repository setup from [SETUP.md](../SETUP.md): virtual environment,
  `pip install -r requirements.txt`, and a `.env` at the repository root.
  `adk web`, `adk run` and `adk api_server` load the nearest `.env` walking
  up from the agent folder; each agent folder also has a `.env.example`.
- Gemini credentials: `GOOGLE_API_KEY`, or Agent Platform (formerly Vertex
  AI) with `GOOGLE_CLOUD_LOCATION=global` for `gemini-3.5-flash`.
- `curl` (and optionally `jq`) for `three_runtimes_demo` and `api_server_curl`.

## How to run any topic

ADK discovers agents by folder, and the folder name is the app name.

```bash
cd Module_02_First_ADK_Agent

adk web                    # browser UI at http://localhost:8000, pick the agent from the list
adk run capital_agent      # terminal chat with one agent
adk api_server             # REST API at http://localhost:8000
```

`adk web` also lists the agents inside `common_failures/` (as
`common_failures.broken_no_env` and so on). `adk api_server` only serves the
agent folders directly under the directory it starts in.

By default all three keep sessions in a `.adk/` folder inside each agent
folder (ignored by git). Delete it to start from a clean slate.

## First-run troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `adk: command not found` | Virtual environment not active | `source .venv/bin/activate` from the repository root |
| `No root_agent found for '...'` | The variable in `agent.py` is not named `root_agent`, or you started `adk` in the wrong folder | Name it `root_agent`; start `adk` in the folder that contains the agent folder |
| `Invalid app name '...': must start with a letter` | Agent folder name starts with a digit or has other characters | Rename the folder: letters, digits, `_` and `-`, starting with a letter |
| `No API key was provided` or `Missing key inputs argument` | No `.env` found and no credentials in the environment | Create the root `.env` (see SETUP.md) |
| `404 NOT_FOUND` for the model on Agent Platform | `GOOGLE_CLOUD_LOCATION` is a region | Set `GOOGLE_CLOUD_LOCATION=global` |
| Port 8000 in use | Another `adk` server is running | `adk web --port 8001` |
| Tool never gets called, or gets odd arguments | Tool is missing type hints or a docstring | Add type hints on every parameter and a docstring with an `Args:` section |
| `ModuleNotFoundError: No module named 'google.adk'` | Wrong virtual environment | Activate the repository's `.venv`, or `pip install google-adk` in yours |

Warnings you can ignore while learning: `[EXPERIMENTAL] ...` user warnings.
If you see `GOOGLE_GENAI_USE_VERTEXAI is deprecated, please use
GOOGLE_GENAI_USE_ENTERPRISE instead`, your `.env` uses the old variable name;
rename it (both names still work in ADK 2.9).

For each failure mode, `common_failures/` has a broken folder you can run and
a `FIX.md`.

## What done looks like

1. In the web UI, pick `capital_agent`, ask "What's the capital of Japan?" and get Tokyo.
2. Run `adk run weather_jokes_agent` and trigger both tools in one conversation.
3. Run `adk api_server` and complete the flow in `api_server_curl/run_demo.sh`.
4. Read `yaml_config_agent/root_agent.yaml` and explain when you would choose YAML over Python.
