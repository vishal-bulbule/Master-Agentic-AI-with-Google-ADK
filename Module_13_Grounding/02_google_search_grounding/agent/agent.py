# Author: Vishal Bulbule
# Date: 2026-09-22

"""Google Search grounding: the `google_search` built-in tool.

`google_search` is not a Python function. It tells Gemini to run Google Search
itself, inside the model call, and the response comes back with
`grounding_metadata` listing the pages used. There is no tool call event in
the session; the search happens on the model side.

It works only with Gemini models, and the Gemini API does not accept it in
the same request as function tools or sub-agent transfer. To combine them,
use `GoogleSearchTool(bypass_multi_tools_limit=True)`, which makes ADK run
the search in a separate agent call.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import google_search

root_agent = LlmAgent(
    name="grounded_search_agent",
    model="gemini-3.5-flash",
    description="Answers questions using live Google Search results with citations.",
    instruction=(
        "Use google_search for current information and always cite sources.\n"
        "When you answer:\n"
        "  1. Search for any time-sensitive or factual claim.\n"
        "  2. Write a concise answer (2-4 sentences).\n"
        "  3. End with a 'Sources:' list of the URLs you actually used.\n"
        "If the search returns nothing useful, say so. Do not invent facts."
    ),
    tools=[google_search],
)
