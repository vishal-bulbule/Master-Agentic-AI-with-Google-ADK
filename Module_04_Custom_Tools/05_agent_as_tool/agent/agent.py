# Author: Vishal Bulbule
# Date: 2026-09-22

"""Agent as a tool: the parent calls a specialist agent like a function.

`summarizer` is declared with `mode="single_turn"` and attached through
`sub_agents`. ADK then exposes it to `researcher` as a tool instead of a
transfer target: the researcher calls it with a request, the summarizer runs
once in an isolated branch and returns its text, and the researcher keeps
owning the conversation.

This replaces wrapping the agent in `AgentTool`, which ADK 2.x still ships
but discourages. The single-turn form also keeps the specialist's internal
events in the session history, so you can inspect them.
"""

from google.adk.agents import LlmAgent

summarizer = LlmAgent(
    name="summarizer",
    model="gemini-3.5-flash",
    mode="single_turn",
    description="Summarizes any chunk of text into a tight 2-3 sentence brief.",
    instruction=(
        "You are a summarizer. Given a passage of text, return a 2-3 sentence summary. "
        "Keep it factual, with no filler such as 'This text discusses...'."
    ),
)


root_agent = LlmAgent(
    name="researcher",
    model="gemini-3.5-flash",
    description="Researches a topic and uses the summarizer agent to condense findings.",
    instruction=(
        "You research topics for the user. Write detailed notes on the topic from "
        "what you know, then call the 'summarizer' tool with those notes to get a "
        "tight summary. Reply to the user with the summary, not the raw notes."
    ),
    sub_agents=[summarizer],
)
