<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Agent or no agent? Five worked examples

The rule: use an agent only when the tools to call are decided at runtime,
the number of steps is not known in advance, and the system must recover
from intermediate failures. This file applies it five times. Each case states the task, the
verdict, and the cheapest shape that gets the job done.

The cost rule: **agents make 2 to 10 times more LLM calls than a chatbot.**
Don't reach for an agent when a simpler shape works.

---

## Case 1: "Summarize this email"

**Task:** Paste an email body, get a 2-line summary.

**Verdict:** No agent. **Single LLM call.**

**Why:** Input is fixed shape (text). No external lookup. No branching.
A chatbot endpoint is the right shape. Anything more is overkill.

---

## Case 2: "Search our policy docs and answer the user's question"

**Task:** Q&A over internal HR / engineering docs.

**Verdict:** No agent. **RAG.**

**Why:** One tool (vector search). Fixed flow: retrieve, then generate. No
runtime decisions about *which* tool to use. RAG is built for exactly
this.

*Caveat:* if the user can also book leave, edit their profile, or
trigger a workflow, you're now in agent territory.

---

## Case 3: "Triage this incoming GitHub issue"

**Task:** Read the issue, decide a label, post a comment, optionally
assign someone.

**Verdict:** **Agent.**

**Why:**
- Multiple tools: `set_label`, `post_comment`, `assign_user`,
  `search_similar_issues`.
- The model picks which to call based on issue content (bug? feature
  request? duplicate?).
- Needs to recover from intermediate failures ("user doesn't exist").
- Conversation can extend if a maintainer replies.

This is the canonical agent shape.

---

## Case 4: "Convert this CSV row to JSON in our schema"

**Task:** Deterministic data transformation.

**Verdict:** No agent. **No LLM at all.**

**Why:** This is a `for` loop. Spending tokens on it is the most
expensive way to do a free operation. Write the function.

*If* the schema mapping is fuzzy ("look at this row and figure out
which of these 30 fields it belongs in"), upgrade to a single LLM call
with structured output. Still not an agent.

---

## Case 5: "Plan and book a 3-city business trip within budget"

**Task:** Find flights, hotels, calendar slots, optimize for cost,
re-plan if a hotel is full.

**Verdict:** **Agent.**

**Why:**
- Many tools: `search_flights`, `search_hotels`, `read_calendar`,
  `compute_cost`, `book_flight`, `book_hotel`.
- Number of tool calls is unknowable in advance.
- Plan must adapt to intermediate observations ("Hotel A booked, try
  Hotel B").
- Multi-turn conversation with the user is likely.

This is also the case where you'll spend the most tokens, so put a
**budget cap** on it: in ADK, `RunConfig(max_llm_calls=...)` limits the
number of model calls per run.

---

## Cheat sheet

| Signals | Shape |
|---|---|
| Pure transform / deterministic | Function, no LLM |
| One LLM call, no lookup | Chatbot |
| One tool (search), fixed flow | RAG |
| Many tools, runtime decisions | Agent |
| Many tools + multi-turn + recovery | Agent (with eval + budget cap) |
