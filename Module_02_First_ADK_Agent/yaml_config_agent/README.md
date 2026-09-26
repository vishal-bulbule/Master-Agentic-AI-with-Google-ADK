<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# YAML agent config

## What this shows

The same agent as `../capital_agent/`, declared in `root_agent.yaml` instead of
Python. The Python file holds only the tool; the agent definition (model,
name, instruction, tools) is data.

```
yaml_config_agent/
    __init__.py       # package marker, so the YAML can import tools.py
    root_agent.yaml   # the agent definition
    tools.py          # get_capital
```

When a folder has no `agent.py` with a `root_agent`, the ADK loader looks for
`root_agent.yaml` in it and builds the agent from that file.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`.env.example`](.env.example): `GOOGLE_API_KEY`, or
      Agent Platform (formerly Vertex AI) with `GOOGLE_CLOUD_LOCATION=global`
      (`gemini-3.5-flash` is served from `global`).

## Run it

1. `cd Module_02_First_ADK_Agent`
2. `adk web`
3. Open http://localhost:8000 and select `yaml_config_agent` in the agent dropdown.
4. Send: "What's the capital of Japan?"

Terminal alternative: `adk run yaml_config_agent`.

## What to look for

- Events view: the answer comes from a `get_capital` call, the same as in the
  Python version. Click an event row: the author in the side panel is
  `capital_agent_yaml`, from the YAML `name` field.
- ADK prints `[EXPERIMENTAL]` warnings when it loads this agent. Agent Config
  is still an experimental feature in ADK 2.9.
- The first line of `root_agent.yaml` points editors that use
  yaml-language-server at the published JSON schema, so you get completion
  and validation while editing.

## When to pick YAML over code

| Use YAML when | Use code when |
|---|---|
| People who do not write Python own the prompt | You need control flow (branching, retries, loops) |
| You want instruction changes to be small, reviewable diffs | Your tools or callbacks are non-trivial |
| You deploy many similar agents that differ only in text | You need plugins or before/after hooks |
| You want to edit the agent without touching Python | The agent composes other agents in non-trivial ways |

YAML suits prompts and wiring; Python suits behavior.

## Known limits

- Only Gemini models are supported by Agent Config.
- Tools are referenced by Python import path, so `tools.py` must be
  importable from the folder you start `adk` in.
- `LangGraphAgent` and `A2aAgent` are not supported in YAML.

See the [ADK Agent Config docs](https://adk.dev/agents/config/) for the full
schema.
