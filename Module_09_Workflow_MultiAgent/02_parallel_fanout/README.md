<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 02 Parallel fan-out and join

## What this shows

Three searcher agents look at the same topic from different angles and run
concurrently; a `JoinNode` waits for all three, then a combiner writes one
report. This replaces the deprecated `SequentialAgent([ParallelAgent([...]), combiner])`.
Without the `JoinNode` the combiner would run three times, once per branch.
Fan-out does not merge results: each searcher writes its own `output_key`, and
the combiner reads `{google_findings}`, `{arxiv_findings}`, and
`{news_findings}` from state. `mock_search` returns canned strings so the
sample needs no search API; swap in a real search tool and the graph stays the
same.

```python
searchers = (google_searcher, arxiv_searcher, news_searcher)
wait_for_all = JoinNode(name="wait_for_all")

root_agent = Workflow(
    name="research_team",
    edges=[
        ("START", searchers),         # fan-out: all three run concurrently
        (searchers, wait_for_all),    # fan-in: wait for every branch
        (wait_for_all, combiner),
    ],
)
```

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials
go in a `.env` at the repository root or in the agent folder; see
`research_team/.env.example` (Gemini API key, or Agent Platform (formerly
Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_09_Workflow_MultiAgent/02_parallel_fanout`
2. `adk web`
3. Open http://localhost:8000 and select `research_team`.
4. Send: `Research the impact of transformer architectures on robotics.`

Terminal alternative: `adk run research_team`.

## What to look for

- Events view: three `mock_search` calls (`angle` google, arxiv, news) and three
  summaries, interleaved in no fixed order.
- The combiner responds once, last.
- State tab: `google_findings`, `arxiv_findings`, `news_findings`, and
  `combined_report`.

## Clean up

Sessions are kept in `research_team/.adk/session.db`. Delete it to start
clean: `rm -rf research_team/.adk`
