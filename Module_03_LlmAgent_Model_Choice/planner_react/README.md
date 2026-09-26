<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# PlanReActPlanner

## What this shows

`PlanReActPlanner` makes the model follow an explicit plan, act, reason,
answer loop by prompting. It needs no native thinking support, so it works
on any model. Three canned tools (`get_weather`, `get_local_time`,
`suggest_clothing`) give the planner something to schedule.

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
3. Open http://localhost:8000 and select `planner_react` in the agent dropdown.
4. Send: "What should I wear for a day in Tokyo?"

Terminal alternative: `adk run planner_react`.

## What to look for

- A planning part (marked as a thought) listing the steps, then tool calls:
  `get_weather` and `get_local_time` (often in parallel), then
  `suggest_clothing` with the temperature and summary from the weather result.
- The final answer combines all three results in one paragraph.
- The planner marks text under its `/*PLANNING*/` and `/*REASONING*/` tags
  as thought parts. When the model writes interim text without a tag, it
  shows up as a normal model message between tool calls.

## Trade-off

Compared with `planner_builtin`, the plan is visible and portable across
providers, but the planning text costs output tokens on every turn and the
model can drift from the tag format. Native thinking is cheaper to set up
when your model supports it.
