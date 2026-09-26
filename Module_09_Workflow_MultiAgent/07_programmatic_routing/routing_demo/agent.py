# Author: Vishal Bulbule
# Date: 2026-09-22

"""Programmatic routing: a Python function, not the model, picks the specialist.

`route` is a keyword classifier. In this variant it is exposed as a tool, and
the coordinator is told to call it first and then call whichever specialist
it names. The specialists are wrapped in `AgentTool`, so the coordinator keeps
control and returns their answer.

The coordinator is still an LLM, so the model could in principle ignore the
verdict. `code_router` in the same topic folder is the fully deterministic
version: a Workflow function node routes and no model makes the decision.
"""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

MODEL = "gemini-3.5-flash"

researcher = LlmAgent(
    model=MODEL,
    name="researcher",
    description="Finds facts: names, dates, numbers, definitions.",
    instruction="Answer the factual question in 2-4 sentences.",
)

writer = LlmAgent(
    model=MODEL,
    name="writer",
    description="Writes prose: poems, short stories, marketing copy.",
    instruction="Produce the piece the user asked for. Keep it tight.",
)

RESEARCHER_KEYWORDS = ("find", "fact", "who", "when", "where", "how many", "define")
WRITER_KEYWORDS = ("write", "poem", "story", "draft", "copy", "compose")


def route(query: str) -> dict:
    """Pick a specialist based on keywords in the user's query.

    Args:
        query: The full user message.

    Returns:
        A dict with status, the chosen specialist ("researcher" or "writer"),
        and the reason for the choice.
    """
    q = (query or "").lower()
    if any(k in q for k in RESEARCHER_KEYWORDS):
        return {
            "status": "ok",
            "specialist": "researcher",
            "reason": "matched researcher keywords",
        }
    if any(k in q for k in WRITER_KEYWORDS):
        return {
            "status": "ok",
            "specialist": "writer",
            "reason": "matched writer keywords",
        }
    return {
        "status": "ok",
        "specialist": "researcher",
        "reason": "no keyword match, defaulted to researcher",
    }


root_agent = LlmAgent(
    model=MODEL,
    name="routing_demo",
    description="Coordinator that uses a route() function to pick a specialist.",
    instruction=(
        "For every user message:\n"
        "  1. Call route(query=<the user's message>) to decide which "
        "specialist to use.\n"
        "  2. Call that specialist as a tool (researcher or writer), passing "
        "the user's original request.\n"
        "  3. Return the specialist's answer verbatim.\n"
        "Do not answer the question yourself."
    ),
    tools=[route, AgentTool(agent=researcher), AgentTool(agent=writer)],
)
