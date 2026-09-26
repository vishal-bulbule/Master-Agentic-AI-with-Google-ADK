<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Module 4: Custom Tools in ADK

Write tools the model uses correctly the first time. Every function tool is
described to the model by three things only: the function name, the
type-hinted parameters, and the docstring. Treat them as user-facing copy.

## Topics (in order)

| # | Folder | What it shows |
|---|---|---|
| 1 | `01_anatomy_of_a_tool/` | Five rules for a well-crafted tool; `bad_tool_agent` runs the same job with a badly written tool for comparison |
| 2 | `02_return_value_status/` | Returning `success` / `error` / `ambiguous` dicts |
| 3 | `03_required_vs_optional/` | Required type hints vs default-valued optional parameters |
| 4 | `04_long_running_tool/` | `LongRunningFunctionTool`: return pending now, deliver the result later |
| 5 | `05_agent_as_tool/` | Calling a specialist agent as a tool (`mode="single_turn"` sub-agent) |
| 6 | `06_tool_context_state/` | `tool_context.state` and the `user:` / `app:` / `temp:` prefixes |
| 7 | `07_tool_context_actions/` | `transfer_to_agent`, `skip_summarization`, `escalate` |
| 8 | `08_openapi_tool/` | `OpenAPIToolset` generated from a YAML spec |
| 9 | `09_tool_auth/` | Env-var API keys and a per-user OAuth credential request |
| 10 | `10_tool_confirmation/` | `require_confirmation=True` for risky writes |
| 11 | `lab_github_triage/` | Lab: GitHub triage agent with 4 tools, 2 gated by confirmation; `pytest tests` checks the tools against a fake GitHub |

## Before you start

- Repository setup from [SETUP.md](../SETUP.md): virtual environment,
  `pip install -r requirements.txt` (includes `PyGithub`), and a `.env` at
  the repository root.
- Gemini credentials: `GOOGLE_API_KEY`, or Agent Platform (formerly Vertex
  AI) with `GOOGLE_CLOUD_LOCATION=global` for `gemini-3.5-flash`.
- `08_openapi_tool`: outbound HTTPS to `httpbin.org`.
- `09_tool_auth`: `WEATHER_API_KEY` (any string); optionally a real OAuth
  client to complete the calendar consent flow.
- `lab_github_triage`: `GITHUB_PERSONAL_ACCESS_TOKEN` (fine-grained; Issues
  read and write on a repository you own for the write path).

Each topic keeps its agent in an `agent/` subfolder with a `.env.example`
listing the variables it reads.

## Run any topic

```bash
cd Module_04_Custom_Tools/01_anatomy_of_a_tool
adk web                      # open http://localhost:8000, pick "agent" in the app dropdown
adk run agent                # or chat in the terminal
```

`01_anatomy_of_a_tool` has a second agent, `bad_tool_agent`, in the same
app dropdown. Every other topic has one agent, `agent`.

In the dev UI, the Events view lists each tool call and result; click a row
to see its details in the side panel. For a model call, the **Request** icon
in the side panel shows the tool declarations ADK sent to the model, which
is the fastest way to check what the model knows about your tool.

By default `adk web` and `adk run` keep sessions in `<agent>/.adk/` (ignored
by git). Delete it to start from a clean slate.

## State-prefix cheat sheet (used in 06 and 07)

| Prefix | Lifetime | Use for |
|---|---|---|
| (no prefix) | This session | Conversation-scoped facts |
| `user:` | Across sessions for this user | Preferences, profile |
| `app:` | All users of this app | Shared catalogs, feature flags |
| `temp:` | This invocation only | Hand-off between tools within one turn |
