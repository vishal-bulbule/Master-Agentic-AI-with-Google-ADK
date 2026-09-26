# Author: Vishal Bulbule
# Date: 2026-09-22

"""Research agent that puts a [source: URL] citation after every factual claim.

It uses Google Search grounding, and its instruction makes inline citations
mandatory. `tests/` in the lab folder has an `adk eval` rubric test that
asks five time-sensitive questions and has an LLM judge check that each answer
carries inline [source: URL] tags.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import google_search

root_agent = LlmAgent(
    name="cite_as_you_answer_agent",
    model="gemini-3.5-flash",
    description=(
        "Research agent that grounds every factual claim with an inline "
        "[source: URL] citation."
    ),
    instruction=(
        "You are a research assistant. For every factual claim you must:\n"
        "  1. Use google_search to find a supporting source.\n"
        "  2. Follow the claim immediately with an inline citation in the form "
        "[source: <URL>], using the URL you found.\n"
        "  3. Never state a fact without a [source: ...] tag right after it.\n"
        "\n"
        "Style:\n"
        "  - Be concise: 2-5 short sentences.\n"
        "  - Every sentence with a fact ends with [source: URL]. Several facts "
        "in one sentence get several tags.\n"
        "  - If you cannot find a source, say so. Do not invent one.\n"
        "\n"
        "Example:\n"
        "  Q: When was the Eiffel Tower built?\n"
        "  A: The Eiffel Tower was completed in 1889 "
        "[source: https://en.wikipedia.org/wiki/Eiffel_Tower]. It stands 330 "
        "metres tall including antennas "
        "[source: https://www.toureiffel.paris/en/the-monument/key-figures]."
    ),
    tools=[google_search],
)
