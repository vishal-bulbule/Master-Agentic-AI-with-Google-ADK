<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 04 - Required Project Structure

## What this shows

`adk run`, `adk web`, `adk deploy cloud_run`, and `adk deploy agent_engine` all expect the
same folder shape. Get it wrong and you see "module not found" or "no root_agent" errors;
get it right and deploying is one command.

```
sample_agent/
|-- __init__.py        one line: from . import agent
|-- agent.py           defines root_agent at module scope
|-- requirements.txt   extra packages the deployed image installs
|-- .env.example       committed template; copy to .env locally
`-- .gcloudignore      keeps .env and .adk/ out of the deployed image
```

No `setup.py`, `pyproject.toml`, or Dockerfile is needed.

| File | Role | If it is wrong |
|---|---|---|
| `__init__.py` | Makes the folder a package so ADK can import `sample_agent.agent` | The agent is not found |
| `agent.py` | Exports `root_agent` (or an `App` named `app`) | "No root_agent found" |
| `requirements.txt` | Installed into the image by `adk deploy` | `ImportError` at startup in the cloud |
| Folder name | Becomes the app name | Must start with a letter and use only letters, digits, `_`, `-` |

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)).
- Credentials: copy `sample_agent/.env.example` to `sample_agent/.env` and fill it in.
  Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on
  location `global`. Nothing in Google Cloud is created in this topic.

## Run it

Check the structure locally before spending Cloud Build minutes:

1. `cd Module_15_Deployment/04_required_project_structure`
2. `adk web`
3. Open http://localhost:8000 and select `sample_agent` in the agent dropdown.
4. Send: "Hello from the deploy module"

The agent calls `echo` and repeats the message. Terminal alternative:
`adk run sample_agent`.

## What to look for

- `adk web` and `adk run` must be started from the parent folder; the dropdown entry
  (and the `adk run` argument) is the folder name. The same path is what you pass to
  `adk deploy`.
- In the Events view, click the `echo` tool call row: it carries your message as `text`.
- `adk web` and `adk run` create `sample_agent/.adk/` for local session storage. It is excluded from
  deploys by `.gcloudignore`; do not commit it.

## Keep `.env` out of the image

`.env` holds your API key. `adk deploy cloud_run` copies the whole agent folder into the
image, `.env` included, unless the folder has a `.gitignore`, `.gcloudignore`, or
`.ae_ignore` that excludes it. The repository's root `.gitignore` does not count: ADK
reads ignore files from the agent folder only. The `.gcloudignore` here handles it.

Also:

1. Keep `.env` in `.gitignore` so it is never committed.
2. With a custom Dockerfile, add `.env` to `.dockerignore` (topic 08).
3. In production, pass secrets through Secret Manager (topic 06), not files.

Commit `.env.example` instead: the variable names with placeholder values.

## Clean up

`rm -rf sample_agent/.adk` removes the local session store. Keep `sample_agent/.env`
out of git.
