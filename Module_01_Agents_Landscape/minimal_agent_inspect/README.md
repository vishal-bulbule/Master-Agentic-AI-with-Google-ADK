<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Minimal agent, inspected

## What this shows

The smallest `LlmAgent` in the repository: one model, one tool, one job
(tell the time in a known city). The agent is not the point. The point is
learning to read what `adk web` shows you for a single turn.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`.env.example`](.env.example): `GOOGLE_API_KEY`, or
      Agent Platform (formerly Vertex AI) with `GOOGLE_CLOUD_LOCATION=global`
      (`gemini-3.5-flash` is served from `global`).

## Run it

1. `cd Module_01_Agents_Landscape`
2. `adk web`
3. Open http://localhost:8000 and select `minimal_agent_inspect` in the agent dropdown.
4. Send: "What time is it in Tokyo?"

Terminal alternative: `adk run minimal_agent_inspect`.

## Try it

1. "What time is it in Tokyo?" (one tool call)
2. "What time is it in Berlin?" (the tool returns an error and the agent recovers)
3. "What time is it in Mumbai, and what time in New York?" (two tool calls in one turn)
4. "Bake me a cake." (no tool fits, so the model answers without calling one)

## What to look for

The Events view in the main panel lists one numbered row per event. For
prompt 1:

| # | Event | Meaning |
|---|---|---|
| 1 | user message | Your prompt as text |
| 2 | `functionCall` | The model chose `get_current_time(city="Tokyo")` |
| 3 | `functionResponse` | The tool returned `{"status": "success", "city": "Tokyo", "time": "10:30 AM JST"}` |
| 4 | model message | The final natural-language answer |

Click a row to see its details in the side panel; the raw JSON view shows
every field. This is the agent loop, one step per event.

- Prompt 3: two `functionCall` parts in one model event; the model can
  request several tools in parallel.
- Prompt 4: no `functionCall` at all. Not every request needs a tool, and
  the model decides.

State tab: empty, because nothing writes to session state. Later modules
write keys to state and you see them change event by event.

Traces view (the toggle next to Events): timing for each model call and
tool call. This is where you look first when an agent is slow.
