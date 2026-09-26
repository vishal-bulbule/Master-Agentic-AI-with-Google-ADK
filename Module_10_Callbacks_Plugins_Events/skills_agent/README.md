<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Agent Skills

## What this shows

A skill packages the instructions and reference material for one task so an
agent loads it only when a request needs it. Skills follow the
[Agent Skills specification](https://agentskills.io/specification): a folder
with a `SKILL.md` file (frontmatter with `name` and `description`, then the
instructions) and optional `references/`, `assets/`, and `scripts/` folders.
`SkillToolset` exposes them as three tools: `list_skills` (name and
description of each skill), `load_skill` (one skill's instructions), and
`load_skill_resource` (one file from the skill folder). Until a skill is
loaded, only its name and description take up context. This sample has
`translate-to-french`, loaded from disk with `load_skill_from_dir`, and
`meeting-summary`, defined in `agent.py` with
`Skill(frontmatter=..., instructions=...)`. Skills are experimental in ADK
2.x, so expect a warning on startup.

```
skills_agent/
|-- agent.py
`-- skills/
    `-- translate-to-french/
        |-- SKILL.md
        `-- references/
            `-- glossary.md
```

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials go in a `.env` at the repository root or in the agent folder; `.env.example` in this folder lists the variables (a Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_10_Callbacks_Plugins_Events`
2. `adk web`
3. Open http://localhost:8000 and select `skills_agent` in the agent dropdown.
4. Send: `Translate to French: The ADK callback runs on Cloud Run.`

`adk run skills_agent` works too, but shows only the final text.

## Try it

- `Translate to French: The ADK callback runs on Cloud Run.`
- In a new session: `Summarize these notes: Asha and Ravi met. Agreed to ship v2 on Friday. Ravi will update the docs by Thursday.`

## What to look for

- Events view: `list_skills`, then `load_skill` for the matching skill, then
  `load_skill_resource` for the glossary. The model picks the skill from its
  description alone.
- The French reply keeps "ADK", "callback", and "Cloud Run" in English
  because the glossary says so.
- State tab: an `_adk_activated_skill_skills_demo_agent` entry listing the
  skills loaded so far.

## Common errors

| Symptom | Cause |
|---|---|
| `AttributeError: load` from `Skill.load(...)` | There is no remote skill registry call in ADK. Load skills from a folder (`load_skill_from_dir`), a GCS bucket (`load_skill_from_gcs_dir`), or define them in code. |
| Validation error on load | `name` in `SKILL.md` must be lowercase kebab-case, 64 characters or fewer, and equal to the folder name; `description` must not be empty. |

## Clean up

`adk web` and `adk run` keep sessions in `skills_agent/.adk/session.db`. Delete it to start clean: `rm -rf skills_agent/.adk`
