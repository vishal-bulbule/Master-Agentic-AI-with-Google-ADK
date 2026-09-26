# Author: Vishal Bulbule
# Date: 2026-09-22

"""Baseline agent with no grounding: answers from model memory only.

This agent has no tools and no retrieval, and its instruction tells it to
answer rather than decline. Ask it about something time-sensitive and it
answers from training data, confidently and without sources. Run the same
questions against 02_google_search_grounding to see the difference.

Questions to try:
    - Who is the current US president?
    - What is the current Cloud Run price per vCPU-second?
    - What is the newest Gemini model?
"""

from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    name="ungrounded_agent",
    model="gemini-3.5-flash",
    description="Plain LLM with no grounding. Used to show unsupported answers.",
    instruction=(
        "Answer the user's question concisely. Do not say you don't know or "
        "that you cannot access the web; give your best answer from what you "
        "remember. This agent is deliberately ungrounded, for comparison with "
        "a grounded one."
    ),
)
