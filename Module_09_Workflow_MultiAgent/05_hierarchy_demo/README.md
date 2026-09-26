<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 05 Multi-agent hierarchy

## What this shows

A coordinator `LlmAgent` hands each request to one of three sub-agents, and one
of them is itself a three-step pipeline. Sub-agents are passed in
`sub_agents=[...]`; ADK sets `parent_agent` on each child and gives the
coordinator a `transfer_to_agent` tool. The coordinator chooses from the
sub-agents' `name` and `description` and does not care what kind of agent is
underneath. `code_pipeline` is still a `SequentialAgent`: that class is
deprecated in ADK 2.x, but a `Workflow` cannot yet be an `LlmAgent` sub-agent
(constructing one fails validation), so ADK logs a deprecation warning for it.

```text
assistant_team_root (LlmAgent, coordinator)
|-- researcher      (LlmAgent)
|-- code_pipeline   (SequentialAgent)
|   |-- code_writer
|   |-- code_reviewer
|   |-- code_refactorer
|-- critic          (LlmAgent)
```

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials
go in a `.env` at the repository root or in the agent folder; see
`assistant_team/.env.example` (Gemini API key, or Agent Platform (formerly
Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_09_Workflow_MultiAgent/05_hierarchy_demo`
2. `adk web`
3. Open http://localhost:8000 and select `assistant_team`.
4. Send: `Who was the first person to walk on the moon?`

Terminal alternative: `adk run assistant_team`.

## Try it

Send each prompt in a new session (the New Session button):

| Prompt | Goes to |
|---|---|
| `Who was the first person to walk on the moon?` | `researcher` |
| `Write a Python factorial function.` | `code_pipeline` |
| `Critique this haiku: An old silent pond, a frog jumps into the pond, splash! Silence again.` | `critic` |

## What to look for

- Events view: a `transfer_to_agent` call from `assistant_team_root`; click
  it to see the chosen agent name in the side panel.
- For the code prompt, three responses (writer, reviewer, refactorer) after the
  transfer.
- After a transfer, the next message in the same session goes to the
  sub-agent that took over, not to the coordinator.

## Common errors

| Symptom | Cause |
|---|---|
| Log line: app "can transfer between agents but has no context_cache_config" | A cost hint, not an error. Each transfer changes the system instruction, so the prompt prefix is not cached. |

## Clean up

Sessions are kept in `assistant_team/.adk/session.db`. Delete it to start
clean: `rm -rf assistant_team/.adk`
