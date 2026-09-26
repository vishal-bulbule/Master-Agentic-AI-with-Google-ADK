# Author: Vishal Bulbule
# Date: 2026-09-22

"""Research-style agent that must cite a source URL in every answer.

There is no single right answer to "who is X?", so the eval in `tests/` checks an
attribute of the answer instead of comparing it with a reference: a custom rubric
asks the judge model whether the response contains the source URL.
"""

from google.adk.agents import LlmAgent

_FACTS = {
    "ada lovelace": {
        "fact": "First computer programmer; wrote an algorithm for the Analytical Engine.",
        "url": "https://en.wikipedia.org/wiki/Ada_Lovelace",
    },
    "alan turing": {
        "fact": "Founded theoretical computer science with the Turing machine model.",
        "url": "https://en.wikipedia.org/wiki/Alan_Turing",
    },
    "grace hopper": {
        "fact": "Created the first compiler (A-0) and popularized machine-independent code.",
        "url": "https://en.wikipedia.org/wiki/Grace_Hopper",
    },
}


def lookup_person(name: str) -> dict:
    """Returns a one-sentence fact about a person and the source URL.

    Args:
        name: Full name of the person, for example "Ada Lovelace".

    Returns:
        Dict with `status` (`success` or `not_found`) and either `fact` and
        `url`, or `error_message`.
    """
    info = _FACTS.get(name.lower())
    if info is None:
        return {"status": "not_found", "error_message": f"No entry for {name}."}
    return {"status": "success", "fact": info["fact"], "url": info["url"]}


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="research_agent",
    description="Answers 'who is X?' questions and cites a source URL.",
    instruction=(
        "When asked about a person, call lookup_person(name). Always include the "
        "URL returned by the tool in plain text, as 'Source: <url>'. If the lookup "
        "returns not_found, say so politely; no URL is needed then."
    ),
    tools=[lookup_person],
)
