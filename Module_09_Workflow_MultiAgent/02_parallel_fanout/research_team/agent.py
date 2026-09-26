# Author: Vishal Bulbule
# Date: 2026-09-22

"""Parallel research fan-out with a join and a combiner.

Three LlmAgents look at the same topic from different angles. In a `Workflow`,
an edge from one node to a tuple of nodes runs those nodes concurrently
(fan-out). A `JoinNode` waits until every branch has finished, then the
combiner runs once. This replaces the deprecated `ParallelAgent` wrapped in a
`SequentialAgent`.

The fan-out does not merge anything by itself. Each searcher writes its own
state key through `output_key`, and the combiner reads all three keys through
`{key}` placeholders in its instruction.
"""

from google.adk import Workflow
from google.adk.agents import LlmAgent
from google.adk.workflow import JoinNode

MODEL = "gemini-3.5-flash"


def mock_search(angle: str, topic: str) -> dict:
    """Return canned search results so the sample runs without a search API.

    Args:
        angle: Which source to search: "google", "arxiv", or "news".
        topic: The research topic.

    Returns:
        A dict with status, the source searched, and a list of result strings.
    """
    angle = (angle or "").lower().strip()
    canned = {
        "google": [
            f"Top result: overview article on {topic}.",
            f"Wikipedia summary describing {topic}.",
            f"Official documentation page for {topic}.",
        ],
        "arxiv": [
            f"Paper: 'A Survey of {topic}' (2025).",
            f"Paper: 'Scaling Laws for {topic}' (2024).",
            f"Paper: 'Open Problems in {topic}' (2026).",
        ],
        "news": [
            f"News: Major release in {topic} announced this quarter.",
            f"News: Industry analysts call {topic} the trend of 2026.",
            f"News: Regulatory body issues guidance on {topic}.",
        ],
    }
    results = canned.get(angle, [f"No results from {angle} for {topic}."])
    return {"status": "ok", "source": angle, "results": results}


google_searcher = LlmAgent(
    model=MODEL,
    name="google_searcher",
    description="Searches the web (mock) for overview material on the topic.",
    instruction=(
        "You research from web sources. Call mock_search(angle='google', "
        "topic=<the user's topic>) once. Then summarize the results in "
        "2-3 bullets focused on general overview material. "
        "Use only what the results say; do not add facts from your own "
        "knowledge."
    ),
    tools=[mock_search],
    output_key="google_findings",
)


arxiv_searcher = LlmAgent(
    model=MODEL,
    name="arxiv_searcher",
    description="Searches arXiv (mock) for academic papers on the topic.",
    instruction=(
        "You research academic papers. Call mock_search(angle='arxiv', "
        "topic=<the user's topic>) once. Summarize in 2-3 bullets with a "
        "research-paper tone. "
        "Use only what the results say; do not add facts from your own "
        "knowledge."
    ),
    tools=[mock_search],
    output_key="arxiv_findings",
)


news_searcher = LlmAgent(
    model=MODEL,
    name="news_searcher",
    description="Searches recent news (mock) for the topic.",
    instruction=(
        "You research recent news. Call mock_search(angle='news', "
        "topic=<the user's topic>) once. Summarize in 2-3 bullets with a "
        "journalistic, current-events tone. "
        "Use only what the results say; do not add facts from your own "
        "knowledge."
    ),
    tools=[mock_search],
    output_key="news_findings",
)


combiner = LlmAgent(
    model=MODEL,
    name="combiner",
    description="Combines the three parallel findings into a single report.",
    instruction=(
        "Combine the findings below into a single, well-structured report.\n\n"
        "Web findings:\n{google_findings}\n\n"
        "Academic findings:\n{arxiv_findings}\n\n"
        "News findings:\n{news_findings}\n\n"
        "Produce a short report with these sections: Overview, Research, News, "
        "and a one-line 'Bottom line'."
    ),
    output_key="combined_report",
)

searchers = (google_searcher, arxiv_searcher, news_searcher)
wait_for_all = JoinNode(name="wait_for_all")

root_agent = Workflow(
    name="research_team",
    description="Parallel multi-source research with a final combiner agent.",
    edges=[
        ("START", searchers),
        (searchers, wait_for_all),
        (wait_for_all, combiner),
    ],
)
