<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# BuiltInPlanner (Gemini Thinking)

## What this shows

`BuiltInPlanner` with a `ThinkingConfig` turns on Gemini's native thinking
for every request the agent makes. With `include_thoughts=True`, thought
summaries come back as event parts marked `thought: true`, so you can read
the reasoning next to the tool calls.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`.env.example`](.env.example): `GOOGLE_API_KEY`, or
      Agent Platform (formerly Vertex AI) with `GOOGLE_CLOUD_LOCATION=global`
      (`gemini-3.5-flash` is served from `global`).

## Run it

1. `cd Module_03_LlmAgent_Model_Choice`
2. `adk web`
3. Open http://localhost:8000 and select `planner_builtin` in the agent dropdown.
4. Send: "A delivery has 3 boxes. Each box has 4 packets. Each packet weighs 2.5 kg. What is the total weight? Use the tools."

Terminal alternative: `adk run planner_builtin`.

## What to look for

- Events view: thought parts before each tool call, then `multiply(3, 4)` and
  `multiply(12, 2.5)`, and a reply ending with `Answer: 30`.
- `usageMetadata.thoughtsTokenCount` on each model event (click the row and
  read it in the side panel): thinking is billed as output tokens.

## Notes

- Gemini 3.x models take `thinking_level` (`MINIMAL`, `LOW`, `MEDIUM`,
  `HIGH`). Gemini 2.5 models take `thinking_budget` (a token count).
- Thinking costs output tokens and latency. Use it where the task needs
  multi-step reasoning, not for simple lookups.
- For models without native thinking, see `planner_react`.
