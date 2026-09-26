<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 09 Output keys as glue

## What this shows

`output_key` saves an agent's final text into session state, and `{key}`
placeholders read it back into a later agent's instruction. After `researcher`
finishes, ADK writes its text to `state["research_findings"]`; before `writer`
calls the model, ADK replaces `{research_findings}` with that value (use
`{key?}` when the key may be missing). No tool and no custom code move the
data. The pipeline is a `Workflow` chain, migrated from the deprecated
`SequentialAgent`. In a Workflow the researcher's text also arrives at the
writer as its node input; `output_key` is what makes it visible in state and
usable by any later step, not only the next one.

```python
researcher = LlmAgent(
    name="researcher",
    instruction="Give exactly 3 concise factual bullets about the user's topic.",
    output_key="research_findings",       # saved to state["research_findings"]
)
writer = LlmAgent(
    name="writer",
    instruction="Write a 2-paragraph report using these findings: {research_findings}",
)
root_agent = Workflow(name="report_pipeline", edges=[("START", researcher, writer)])
```

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials
go in a `.env` at the repository root or in the agent folder; see
`report_pipeline/.env.example` (Gemini API key, or Agent Platform (formerly
Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_09_Workflow_MultiAgent/09_output_keys_glue`
2. `adk web`
3. Open http://localhost:8000 and select `report_pipeline`.
4. Send: `Black holes`

Terminal alternative: `adk run report_pipeline`.

## What to look for

- The researcher's three bullets, then the writer's two paragraphs built only
  from those bullets.
- State tab: `research_findings` appears before the writer runs, and
  `final_report` after.

## Clean up

Sessions are kept in `report_pipeline/.adk/session.db`. Delete it to start
clean: `rm -rf report_pipeline/.adk`
