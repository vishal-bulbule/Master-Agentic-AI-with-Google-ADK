# Author: Vishal Bulbule
# Date: 2026-09-22

"""Chatbot variant: one model call per turn, no tools, no retrieval.

An `LlmAgent` with no tools is a chatbot. The answer can only come from what
the model learned in training, so it knows nothing about this customer's
order. `support_rag` and `support_agent` in the sibling folders get the same
question.
"""

from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    name="support_chatbot",
    model="gemini-3.5-flash",
    description="Support chatbot with no tools and no retrieval.",
    instruction=(
        "You are a customer support assistant. Answer the user's question "
        "clearly and concisely."
    ),
)
