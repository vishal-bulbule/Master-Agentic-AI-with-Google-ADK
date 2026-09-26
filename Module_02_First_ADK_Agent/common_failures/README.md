<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Common first-run failures

## What this shows

Each folder here is broken on purpose and reproduces one failure you are
likely to hit with your first agents. Run it, read the error (or the
suspiciously normal output), then read its `FIX.md`.

| Folder | What you see on ADK 2.9 | Lesson |
|---|---|---|
| `broken_no_init/` | `adk run` and `adk web` work; `adk eval` fails with `FileNotFoundError: ... broken_no_init/__init__.py` | Every agent folder needs `__init__.py` with `from . import agent` |
| `broken_wrong_name/` | `ValueError: No root_agent found for 'broken_wrong_name'` | The variable must be named `root_agent` |
| `broken_no_type_hint/` | Usually works, but the tool schema has no parameter type | Type hints are the only source of parameter types in the tool schema |
| `broken_no_docstring/` | Usually works, but the tool has no description | The docstring is the tool description the model reads |
| `broken_no_env/` | With `ADK_DISABLE_LOAD_DOTENV=1`: `No API key was provided` | Credentials must reach the process environment |

Two of these no longer fail loudly: current Gemini models often guess right
from a clear function name. They are kept because the missing schema
information is still a real bug; it just shows up later, on tools with vaguer
names or more parameters. Each `FIX.md` shows how to see the problem directly.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials in a `.env` at the repository root (each folder has a
      `.env.example`). For Agent Platform (formerly Vertex AI) set
      `GOOGLE_CLOUD_LOCATION=global`.
- [ ] For `broken_no_env`: a shell with no Google credentials exported.
      Exported variables would make it work.

## Run it

Each failure is easiest to read in the terminal:

1. `cd Module_02_First_ADK_Agent/common_failures`
2. Run the command for a folder, then read its `FIX.md`:

```bash
adk run broken_wrong_name                                  # fails at load time
adk eval broken_no_init                                    # fails at load time
adk run broken_no_type_hint "What's the capital of France?"
adk run broken_no_docstring "What's the capital of France?"
ADK_DISABLE_LOAD_DOTENV=1 adk run broken_no_env "Are you up?"
```

In the browser: run `adk web` from `Module_02_First_ADK_Agent/` and select
`common_failures.broken_wrong_name` and so on in the agent dropdown. The
load-time failures show up when you send the first message.

## What to look for

- `broken_wrong_name`: `ValueError: No root_agent found for 'broken_wrong_name'`.
- `broken_no_init`: `FileNotFoundError: ... broken_no_init/__init__.py` from
  `adk eval`, while `adk run broken_no_init` works.
- `broken_no_type_hint` and `broken_no_docstring`: a normal answer. The
  `FIX.md` shows how to print the declaration and see what is missing.
- `broken_no_env`: `No API key was provided` on the first model call.

Leave the folders broken; copy one elsewhere if you want to practice the fix.

## When you hit a new failure

Check in this order:

1. Is the virtual environment active? `which adk` should point inside `.venv/`.
2. Did you start `adk` in the folder that contains the agent folder?
3. Does the agent folder have `__init__.py` with `from . import agent`?
4. Is the variable in `agent.py` named exactly `root_agent`?
5. Does every tool have type hints and a docstring?
6. Are credentials loaded? Test them outside ADK with
   `Module_00_AI_Foundations/01_genai_basic_call/basic_call.py`.
