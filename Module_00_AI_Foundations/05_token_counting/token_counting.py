# Author: Vishal Bulbule
# Date: 2026-09-22

"""Count tokens and turn the counts into a cost estimate.

`count_tokens` is a separate, free API call: it tokenizes the input without
generating anything. Use it to build intuition for how text maps to tokens
and to size a workload before you run it.

The rates below are example values. Look up the current price for your model
on the pricing page of the API you use before trusting the projection:
https://ai.google.dev/gemini-api/docs/pricing or
https://cloud.google.com/vertex-ai/generative-ai/pricing
"""

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()

MODEL = "gemini-3.5-flash"

# Example rates in USD per 1M tokens. Replace with the current published rates.
# Thinking tokens are billed at the output rate.
INPUT_USD_PER_M = 0.30
OUTPUT_USD_PER_M = 2.50


def estimate_cost(in_tokens: int, out_tokens: int) -> float:
    return (in_tokens / 1_000_000) * INPUT_USD_PER_M + (out_tokens / 1_000_000) * OUTPUT_USD_PER_M


samples = [
    "hello",
    "hello world",
    "antidisestablishmentarianism",
    "Summarize this in one sentence: An AI agent is an LLM with autonomy, tools, memory, and a loop.",
]

for text in samples:
    n = client.models.count_tokens(model=MODEL, contents=text).total_tokens
    print(f"{n:>4} tokens  |  {text!r}")

print("\n--- Cost projection for 10,000 queries/day, 500 in + 500 out tokens each ---")
daily_calls = 10_000
in_tokens_per_call = 500
out_tokens_per_call = 500
daily_cost = estimate_cost(
    daily_calls * in_tokens_per_call,
    daily_calls * out_tokens_per_call,
)
print(f"Daily   : ${daily_cost:.2f}")
print(f"Monthly : ${daily_cost * 30:.2f}")
