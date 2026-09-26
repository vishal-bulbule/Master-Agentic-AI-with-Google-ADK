<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 05: Agent as a Tool

## What this shows

Two agents:

- `summarizer`: a small specialist that turns text into a 2-3 sentence
  summary. It is declared with `mode="single_turn"`.
- `researcher` (the root): writes notes on a topic, then calls `summarizer`
  as a tool to compress them before answering.

A `single_turn` agent in `sub_agents` is exposed to the parent as a function
tool, not as a transfer target. This is the ADK 2.x replacement for wrapping
an agent in `AgentTool` (which still works, but is discouraged).

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`agent/.env.example`](agent/.env.example):
      `GOOGLE_API_KEY`, or Agent Platform (formerly Vertex AI) with
      `GOOGLE_CLOUD_LOCATION=global` (`gemini-3.5-flash` is served from
      `global`).

## Run it

1. `cd Module_04_Custom_Tools/05_agent_as_tool`
2. `adk web`
3. Open http://localhost:8000 and pick `agent` in the app dropdown in the top bar.
4. Send: "Give me a quick summary of the history of the printing press."

Terminal alternative: `adk run agent`.

## What to look for

- Events view: a function call named `summarizer`; click the row to see the
  `request` argument holding the researcher's notes.
- The summarizer's own events run under its name, then the researcher gives
  the final reply. Your next message goes back to the researcher.

## Agent as tool vs sub-agent transfer

| Pattern | Who answers the next user message? |
|---|---|
| `single_turn` sub-agent (this folder) | The parent. The specialist returns its text and is done. |
| `chat` sub-agent with transfer (Module 9) | The sub-agent takes over the conversation until it transfers back. |

Use an agent as a tool for a specialist function call (translate this,
summarize that, classify this). Use transfer when you want to route the user
to a different agent entirely.
