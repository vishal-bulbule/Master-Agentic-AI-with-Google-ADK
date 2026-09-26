<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Smart Router Lab: Results

Fill these tables from one `adk web` session with the ten queries in the
README: the model and latency per query from the Events and Traces views, and
the totals from the `token_usage` state key. Token counts vary a little
between runs even at temperature 0, and tool calls add a second model call
(with the tool schema and tool response) to every math query.

## Per-query results

| # | Query | Model | Prompt tokens | Output tokens | Latency (s) |
|---|---|---|---|---|---|
| | | | | | |

## Totals per model

| Model | Queries | Prompt tokens | Output tokens |
|---|---|---|---|
| | | | |

## Questions to answer from your run

1. Did every math query go to the Pro model and every general query to Flash?
   Which query, if any, was misrouted, and which rule caused it?
2. How do prompt and output tokens per query compare between the two models?
3. How much slower is the Pro route per query? Would that latency be
   acceptable on a user-facing endpoint?
4. Multiply your token totals by current per-token prices for each model.
   What would the run have cost if every query had gone to Pro?
