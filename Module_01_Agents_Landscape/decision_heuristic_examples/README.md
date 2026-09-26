<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Decision heuristic: agent or no agent?

## What this shows

Five common tasks, each matched to the cheapest shape that works: plain
code, a single LLM call, RAG, or an agent. [`cases.md`](cases.md) gives the
verdict and the reasoning for each. This topic is reading material; the
runnable versions of the chatbot, RAG and agent shapes are the three agents
in [`../chatbot_vs_rag_vs_agent`](../chatbot_vs_rag_vs_agent).

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)).

## Run it

Nothing to run here.

1. Read [`cases.md`](cases.md).
2. Run the three agents in [`../chatbot_vs_rag_vs_agent`](../chatbot_vs_rag_vs_agent)
   (`cd Module_01_Agents_Landscape/chatbot_vs_rag_vs_agent && adk web`) to
   see the chatbot, RAG and agent shapes from cases 1 to 3 as working code.

## What to look for

| Case | Verdict | Shape in ADK terms |
|---|---|---|
| 1. Summarize an email | Single LLM call | `LlmAgent` with no tools (same shape as `support_chatbot`), or one `generate_content` call |
| 2. Answer from policy docs | RAG | Fixed retrieve-then-generate (same shape as `support_rag`) |
| 3. Triage a GitHub issue | Agent | `LlmAgent` with tools the model picks at runtime (same shape as `support_agent`) |
| 4. CSV row to JSON | No LLM | A plain function |
| 5. Plan and book a trip | Agent | Many tools, unknown step count, a budget cap (`RunConfig(max_llm_calls=...)`) |

Case 4 is a function. Spending tokens on it is the most expensive way to do
a free operation:

```python
def csv_row_to_json(row: dict) -> dict:
    return {"id": row["id"], "amount_paise": int(row["amount"]) * 100}
```

Case 5 written as fixed code shows what an agent would have to decide at
runtime. Every `if` below is a decision someone hardcoded in advance:

```python
def book_trip(city: str, budget: int) -> dict:
    search = search_hotels(city, budget)
    if search["status"] != "success":      # no hotel fits: give up? raise budget? ask the user?
        return {"status": "no_match", "tried": city}
    chosen = search["options"][0]["name"]  # always the first match
    return book_hotel(chosen)
```

When those decisions depend on the input and cannot be written down in
advance, you need an agent. Agents earn their cost when all three are true:

1. The set of tools to call is decided at runtime.
2. The number of steps is not known in advance.
3. The system must recover from intermediate failures.

If none of them hold, a simpler shape is cheaper, faster and easier to debug.
