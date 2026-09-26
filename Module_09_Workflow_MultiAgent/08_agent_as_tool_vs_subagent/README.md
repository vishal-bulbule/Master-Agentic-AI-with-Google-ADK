<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 08 Agent as a tool vs sub-agent

## What this shows

Two ways for one agent to use another, which look similar and behave
differently. In `translator_demo/` a hotel concierge calls a translator agent
as a tool when the guest writes in another language, then writes the reply
itself; the translator never talks to the user. In `support_team/` a support
coordinator answers general questions and transfers billing conversations to
`billing_specialist`, which then replies directly and keeps the conversation.
Translation, conversion, and formatting fit a tool; billing, returns, and
scheduling fit a sub-agent.

|  | Agent as a tool | Sub-agent |
|---|---|---|
| Wiring | `AgentTool(agent=...)` in `tools=[...]` | the agent in `sub_agents=[...]` |
| After the call | control returns to the parent | the sub-agent keeps the conversation |
| Who replies to the user | the parent | the sub-agent |
| Use for | one-shot help inside a larger reply | handing off a whole domain |

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials
go in a `.env` at the repository root or in the agent folder; see
`translator_demo/.env.example` (Gemini API key, or Agent Platform (formerly
Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_09_Workflow_MultiAgent/08_agent_as_tool_vs_subagent`
2. `adk web`
3. Open http://localhost:8000 and select `translator_demo`.
4. Send: `Bonjour, pouvez-vous me recommander un restaurant ?`
5. Select `support_team` and send: `I was charged twice for my subscription this month.`

Terminal alternative: `adk run translator_demo` and `adk run support_team`.

## What to look for

- `translator_demo`: a `translator` function call and response in the Events
  view, then a reply authored by `concierge`.
- `support_team`: a `transfer_to_agent` call, then a reply authored by
  `billing_specialist`. Send another message (for example
  `It was on my Visa card ending 4242.`) and billing answers again, without
  going back through the coordinator.

## Clean up

Sessions are kept in `.adk/session.db` inside each agent folder:
`rm -rf translator_demo/.adk support_team/.adk`
