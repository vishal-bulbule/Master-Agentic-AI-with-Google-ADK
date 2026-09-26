<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Lab: research team

## What this shows

One `Workflow` graph that uses every pattern from this module. The planner
calls `save_sub_questions`, which writes `subq_1..3` to state. Three
researchers run concurrently, each reading its `{subq_N}` placeholder, calling
`mock_search`, and writing `findings_N`. `wait_for_findings` (a `JoinNode`)
holds the writer until all three finish. Writer and critic loop until the
critic calls `approve_report` or three rounds pass; loop keys use the `temp:`
prefix. `publish` writes `final_report` and `review_rounds`. In a graph the same `writer` node is
reached from two edges; with the older `SequentialAgent` and `ParallelAgent`
classes each agent instance can have only one parent, which forces two
identical writers. `mock_search` returns placeholder strings and the researchers are told
not to add facts of their own, so replace it with a real search tool before
trusting the report.

```text
START -> planner -> (researcher_1, researcher_2, researcher_3)   fan-out
      -> wait_for_findings                                       JoinNode
      -> writer -> critic -> decide_next_step
decide_next_step --"revise"--> writer                            loop
decide_next_step --"done"----> publish
```

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials
go in a `.env` at the repository root or in the agent folder; see
`research_team/.env.example` (Gemini API key, or Agent Platform (formerly
Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_09_Workflow_MultiAgent/lab_research_team`
2. `adk web`
3. Open http://localhost:8000 and select `research_team`.
4. Send: `What changed in Cloud Run pricing in 2026?`

Terminal alternative: `adk run research_team`.

## What to look for

1. Events view: the planner calls `save_sub_questions` and lists three
   sub-questions.
2. The three researchers' `mock_search` calls and summaries interleave.
3. The writer produces a draft, then the critic either critiques it (another
   writer/critic round, with a `revise` route) or calls `approve_report`
   (a `done` route).
4. The last message is the report from `publish`.
5. State tab: `sub_questions`, `subq_1..3`, `findings_1..3`, `planner_notes`,
   `final_report`, and `review_rounds`. The `temp:` loop keys are gone.

## Clean up

Sessions are kept in `research_team/.adk/session.db`. Delete it to start
clean: `rm -rf research_team/.adk`
