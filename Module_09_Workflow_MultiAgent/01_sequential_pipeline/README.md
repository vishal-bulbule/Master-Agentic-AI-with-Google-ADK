<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 01 Sequential pipeline

## What this shows

Three LlmAgents (`code_writer`, `code_reviewer`, `code_refactorer`) run in a
fixed order inside a `Workflow`; code, not a model, decides the order. In ADK
2.x `SequentialAgent` is deprecated in favor of `Workflow`, and the chain is a
single edge tuple. Each agent's answer is passed to the next node as its input,
and `output_key` also writes it to session state, where later instructions read
it with `{generated_code}` and `{review_comments}`. The refactorer needs both
values, which is why state is used rather than node input alone.

```python
root_agent = Workflow(
    name="code_pipeline",
    edges=[("START", code_writer, code_reviewer, code_refactorer)],
)
```

```text
code_writer      -> state["generated_code"]
code_reviewer    reads {generated_code}                      -> state["review_comments"]
code_refactorer  reads {generated_code} and {review_comments} -> state["final_code"]
```

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Put your
credentials in a `.env` at the repository root or in the agent folder;
`code_pipeline/.env.example` lists the variables (a Gemini API key, or Agent
Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_09_Workflow_MultiAgent/01_sequential_pipeline`
2. `adk web`
3. Open http://localhost:8000 and select `code_pipeline` in the agent dropdown.
4. Send: `Write a Python function that returns the n-th Fibonacci number.`

Terminal alternative: `adk run code_pipeline`.

## What to look for

- Three responses in order, authored by `code_writer`, `code_reviewer`, and
  `code_refactorer`.
- State tab: `generated_code`, `review_comments`, and `final_code` appear one
  after another. Each event that wrote one shows it as a `state_delta` when
  you click its row in the Events view.

## Common errors

| Symptom | Cause |
|---|---|
| `KeyError` for `generated_code` in an instruction | A placeholder without `?` references a key that is not in state yet. Check the agent order and the `output_key` spelling. |

## Clean up

`adk web` and `adk run` keep sessions in `code_pipeline/.adk/session.db`.
Delete it to start clean: `rm -rf code_pipeline/.adk`
