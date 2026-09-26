<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 03 Loop refinement (writer and critic)

## What this shows

A writer drafts a paragraph, a critic reviews it, and the pair repeats until
the critic approves or a round limit is reached. `LoopAgent` is deprecated in
ADK 2.x; the loop is now an edge that points back to the writer.
`decide_next_step` is a plain Python function node that returns an `Event`
with `route="revise"` or `route="done"`, so `max_iterations` and `escalate`
become an `if` statement. A `Workflow` rejects a cycle with no routed edge, so
a loop always has an explicit exit. The critic approves by calling
`approve_draft`, which sets `temp:review_status`. The loop's working keys use
the `temp:` prefix, so each new request starts clean, and `publish` writes the
approved text to `final_draft`. The critic's criteria (under 90 words, one
concrete example, no hype words) usually fail the first draft, so you see at
least one revision.

```python
root_agent = Workflow(
    name="quality_loop",
    edges=[
        ("START", writer, critic, decide_next_step),
        (decide_next_step, {"revise": writer, "done": publish}),
    ],
)
```

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials
go in a `.env` at the repository root or in the agent folder; see
`quality_loop/.env.example` (Gemini API key, or Agent Platform (formerly
Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_09_Workflow_MultiAgent/03_loop_refinement`
2. `adk web`
3. Open http://localhost:8000 and select `quality_loop`.
4. Send: `Write a one-paragraph intro to retrieval-augmented generation.`

Terminal alternative: `adk run quality_loop`.

## What to look for

- Events view: `writer`, `critic` (bulleted critique), a `revise` route,
  `writer`, `critic` with an `approve_draft` call, a `done` route, then
  `Final draft after 2 round(s)`. The round count varies between runs.
- Send a second prompt in the same session: it starts again at round 1,
  because the loop's keys are `temp:`.
- State tab after the run holds only `final_draft`.

## Common errors

| Symptom | Cause |
|---|---|
| The loop runs to `MAX_ROUNDS` every time | The critic never calls `approve_draft`. Loosen its criteria or raise `MAX_ROUNDS`. |

## Clean up

Sessions are kept in `quality_loop/.adk/session.db`. Delete it to start
clean: `rm -rf quality_loop/.adk`
