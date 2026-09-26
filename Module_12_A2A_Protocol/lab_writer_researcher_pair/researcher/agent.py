# Author: Vishal Bulbule
# Date: 2026-09-22

"""Researcher agent, served over A2A by `adk api_server --a2a --port 8081`.

A plain LlmAgent with one mock search tool, so the lab runs without a search
API and gives the same results every time. `agent.json` next to this file is
the agent card; its presence is what makes `--a2a` serve this folder at
/a2a/researcher. The writer reaches it only through that card, so you can
replace the tool (or the whole agent) and redeploy without touching the writer.
"""

from google.adk.agents import LlmAgent

# Fictional search results. The sources and figures are made up for the lab;
# do not quote them.
_FIXTURES = {
    "ai agent adoption": [
        {
            "title": "Mock analyst report: agentic features in enterprise software",
            "url": "https://example.com/analyst-agentic",
            "snippet": (
                "A third of enterprise software applications are expected to "
                "embed agentic features by 2028, up from under 1% in 2024. "
                "Adoption is fastest in customer service, IT operations, and "
                "developer tooling."
            ),
        },
        {
            "title": "Mock survey: half of large firms run an agent in production",
            "url": "https://example.com/survey-2026",
            "snippet": (
                "51% of large firms surveyed run at least one agentic "
                "workflow in production. The most cited blockers are "
                "evaluation tooling and data access governance."
            ),
        },
        {
            "title": "Mock case study: open protocols and agent integration cost",
            "url": "https://example.com/a2a-mcp-2026",
            "snippet": (
                "Teams that standardized on A2A for agent-to-agent calls and "
                "MCP for tools report about 40% lower integration cost than "
                "with custom glue code."
            ),
        },
    ],
    "ai agent market size": [
        {
            "title": "Mock market sizing: AI agents to reach $47B by 2030",
            "url": "https://example.com/market-47b",
            "snippet": (
                "The AI agents market is projected at $47B by 2030, a 44% "
                "CAGR from 2024. Vertical agents (legal, finance, healthcare) "
                "grow about twice as fast as horizontal platforms."
            ),
        },
    ],
}


def mock_web_search(query: str) -> dict:
    """Search the web (mock). Returns a short list of result snippets.

    Args:
        query: Natural-language search query.

    Returns:
        A dict with `status` "ok", the `query`, and a `results` list of
        {title, url, snippet}.
    """
    q = query.lower()
    for key, hits in _FIXTURES.items():
        if key in q:
            return {"status": "ok", "query": query, "results": hits}

    # Generic fallback so the agent never gets an empty payload.
    return {
        "status": "ok",
        "query": query,
        "results": [
            {
                "title": f"No fixture for '{query}'; generic mock result",
                "url": "https://example.com/generic",
                "snippet": (
                    "In 2026, agentic AI moved from pilots to production in "
                    "most large enterprises. Standardizing on A2A and MCP is "
                    "reducing integration cost and letting each domain team "
                    "own a specialist agent."
                ),
            }
        ],
    }


root_agent = LlmAgent(
    name="researcher",
    model="gemini-3.5-flash",
    description=(
        "Research specialist. Searches for facts and returns compact, "
        "citation-ready findings."
    ),
    instruction=(
        "You are a research specialist.\n"
        "Given a topic:\n"
        "1. Call mock_web_search with a focused query (or a few, if needed).\n"
        "2. Summarize the snippets as 3-6 bullet points of facts only.\n"
        "3. End each bullet with the source URL in parentheses.\n"
        "4. Do not write narrative prose; that is the writer's job.\n"
        "5. If you cannot research the request, say so plainly."
    ),
    tools=[mock_web_search],
)
