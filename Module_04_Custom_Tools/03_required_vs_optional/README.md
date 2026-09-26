<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 03: Required vs Optional Parameters

## What this shows

How the function signature decides what the model must supply:

| Behavior | How to declare |
|---|---|
| Required | Type hint, no default (`city: str`) |
| Optional | Default value (`unit: str = "celsius"`) |
| Nullable | `Optional[str]` or `str \| None` |

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`agent/.env.example`](agent/.env.example):
      `GOOGLE_API_KEY`, or Agent Platform (formerly Vertex AI) with
      `GOOGLE_CLOUD_LOCATION=global` (`gemini-3.5-flash` is served from
      `global`).

## Run it

1. `cd Module_04_Custom_Tools/03_required_vs_optional`
2. `adk web`
3. Open http://localhost:8000 and pick `agent` in the app dropdown in the top bar.
4. Send: "What's the weather?"

Terminal alternative: `adk run agent`.

## Try it

- "What's the weather?" (asks which city)
- "Weather in Mumbai?" (uses Celsius, the default)
- "Weather in New York in fahrenheit" (overrides the default)

## What to look for

- No function call for the first prompt: `city` is required, so the agent asks.
- The Mumbai call in the Events view has no `unit` argument at all (click
  the tool call row to see its arguments in the side panel); the default
  applies inside the function.

## Anti-pattern to avoid

```python
def book_flight(destination: str = "Paris"):  # BAD
    ...
```

The model will skip asking the user and book everyone to Paris. Defaults are
for genuine settings (units, page size, locale), not for missing user input.
