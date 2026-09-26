# Author: Vishal Bulbule
# Date: 2026-09-22

"""LLM-driven routing: the model picks which specialist handles the request.

The root LlmAgent lists two sub-agents in `sub_agents`. ADK gives it a
`transfer_to_agent` tool, and the model calls it with the name of the
specialist whose `description` best matches the request. No code decides the
route, so the sharper each `description` is, the better the routing.
"""

from google.adk.agents import LlmAgent

MODEL = "gemini-3.5-flash"

researcher = LlmAgent(
    model=MODEL,
    name="researcher",
    description="Finds facts: names, dates, numbers, definitions.",
    instruction=(
        "You are a researcher. Answer the user's factual question in 2-4 "
        "precise sentences."
    ),
)

writer = LlmAgent(
    model=MODEL,
    name="writer",
    description="Writes prose: poems, short stories, marketing copy, intros.",
    instruction=(
        "You are a writer. Produce the piece the user asked for in the tone "
        "they requested. Keep it tight."
    ),
)

root_agent = LlmAgent(
    model=MODEL,
    name="routing_root",
    description="Routes user requests to either the researcher or the writer.",
    instruction=(
        "You manage two specialists:\n"
        "  - researcher: factual lookups (who, what, when, how many).\n"
        "  - writer: creative writing (poems, stories, copy).\n"
        "Always delegate with transfer_to_agent. Never answer yourself."
    ),
    sub_agents=[researcher, writer],
)
