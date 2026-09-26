<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 07: When not to ground

## What this shows

Grounding adds latency, adds cost, and constrains the model. That is the right
trade for most factual agents and the wrong one for pure reasoning (math,
code, logic, where a search adds a round trip and can pull in an irrelevant
snippet the model anchors on), creative writing (grounding anchors the model to
what exists: ask a search-grounded model for "five unusual names for a cat
cafe" and you tend to get names of existing cat cafes), and stable,
high-volume questions ("What is the refund policy?" asked 100,000 times a day
has one answer; serve it from a cache such as Memorystore or an in-process LRU
and fall back to grounded retrieval on a miss or when the source changes).
The table below puts numbers on the trade-off. Rule of thumb: ground when the answer
depends on something the model cannot know and the user will rely on it;
otherwise cache the answer or let the model reason.

## Prerequisites

None. This topic is a worked cost comparison, with no agent to run.

## The numbers

Assumptions per query: an ungrounded call sends 200 input tokens and returns
150; a grounded call sends 1,200 (the retrieved context is added to the
prompt) and returns 200.

| Approach | Cost per query | Cost for 100,000 queries |
|---|---|---|
| Ungrounded model call | $0.00044 | $43.50 |
| Google Search grounded | $0.03586 | $3,586.00 |
| Vertex AI Search grounded | $0.00286 | $286.00 |
| Cached answer (no model call) | $0.00001 | $1.00 |

Prices used (USD, placeholders for a Flash-class model): $0.30 per 1M input
tokens, $2.50 per 1M output tokens, $35 per 1,000 Google Search grounded
requests after the free tier, $0.002 per Vertex AI Search query, and $0.00001
per cache hit. Replace them with current list prices
(https://cloud.google.com/vertex-ai/generative-ai/pricing) or your contract
rates before you quote a number. Search grounding is billed differently across
model generations (per grounded prompt or per search query) and has a free
tier.

## What to look for

- With these prices, Google Search grounding costs about 80 times an
  ungrounded call and about 3,600 times a cached answer. The ratios, not the
  dollar amounts, are the point: they tell you where a cache or skipping
  grounding pays off.
- To try your own numbers: cost per query = input tokens / 1,000,000 x input
  price + output tokens / 1,000,000 x output price + any per-request search or
  retrieval fee.
