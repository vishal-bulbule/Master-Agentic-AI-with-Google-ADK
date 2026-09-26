# Author: Vishal Bulbule
# Date: 2026-09-22

"""Agent that answers personal questions by searching long-term memory.

`tool_context.search_memory(query)` asks the app's memory service for entries
that match the query. Memory is filled separately, by calling
`add_session_to_memory` on a finished session (the `adk web` server exposes
that as `PATCH /apps/{app}/users/{user}/memory`). The tool code does not change
when you move from the in-memory service to a managed one.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext


async def recall_facts(query: str, tool_context: ToolContext) -> dict:
    """Search long-term memory for facts about the user.

    Args:
        query: A short natural-language query, for example "user's company".
        tool_context: Injected by ADK; gives the tool access to memory.

    Returns:
        A dict with status, the number of snippets, and the snippets.
    """
    response = await tool_context.search_memory(query=query)
    snippets = [
        part.text
        for memory in response.memories
        if memory.content and memory.content.parts
        for part in memory.content.parts
        if part.text
    ]
    return {"status": "ok", "count": len(snippets), "snippets": snippets}


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="memory_search_agent",
    description="Answers personal questions by searching long-term memory.",
    instruction=(
        "When the user asks anything about themselves (their company, name, "
        "preferences, history), call recall_facts(query) with a short query "
        "and answer using the snippets it returns. If no snippets come back, "
        "say you do not have that on record. If the user shares a fact, "
        "acknowledge it briefly without claiming to have saved it; memory is "
        "updated outside this conversation."
    ),
    tools=[recall_facts],
)
