<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Lab: weather and jokes agent

## What this shows

The reference solution for this module's lab: an agent with two tools, where
the model picks the right one from the request.

| Tool | Signature | Triggered by |
|---|---|---|
| `get_weather` | `(city: str) -> dict` | "What's the weather in Pune?" |
| `tell_joke` | `() -> dict` | "Tell me a joke." or "Cheer me up." |

Both return a dict with a `status` key so the model can branch on success or
failure.

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
3. Open http://localhost:8000 and select `weather_jokes_agent` in the agent dropdown.
4. Send: "What's the weather in Tokyo?"

Terminal alternative: `adk run weather_jokes_agent`.

## Try it

1. "What's the weather in Tokyo?"
2. "Tell me a joke."
3. "Weather in Atlantis?"

## What to look for

- Prompt 1 calls `get_weather` and returns the Tokyo report; prompt 2 calls
  `tell_joke`. Check which function call appears in the Events view.
- Prompt 3 gets `status: not_found` and the agent says it has no data.

If a tool never gets called, check that every parameter has a type hint, the
function has a docstring, and the function is listed in `tools=[...]`.
