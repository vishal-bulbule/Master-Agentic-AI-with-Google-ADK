# Author: Vishal Bulbule
# Date: 2026-09-22

"""Pure programmatic dispatch: a function node picks the agent, no router model.

`classify` is a plain Python node in a `Workflow`. It reads the user's message,
matches keywords, and emits `Event(route="researcher")` or
`Event(route="writer")`. The routed edge then runs only that specialist. The
same input always reaches the same agent, and no tokens are spent on the
routing decision.

Compare with `routing_demo`, where the same keyword rules are a tool that an
LLM coordinator calls and could, in principle, ignore.
"""

from google.adk import Event, Workflow
from google.adk.agents import LlmAgent

MODEL = "gemini-3.5-flash"

RESEARCHER_KEYWORDS = ("find", "fact", "who", "when", "where", "how many", "define")
WRITER_KEYWORDS = ("write", "poem", "story", "draft", "copy", "compose")

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


def classify(node_input: str) -> Event:
    """Route the user's message to a specialist by keyword, without a model."""
    q = (node_input or "").lower()
    if any(k in q for k in RESEARCHER_KEYWORDS):
        choice = "researcher"
    elif any(k in q for k in WRITER_KEYWORDS):
        choice = "writer"
    else:
        choice = "researcher"
    # `output` is what the chosen specialist receives as its input.
    return Event(output=node_input, route=choice, state={"routed_to": choice})


root_agent = Workflow(
    name="code_router",
    description="Routes each message to a researcher or writer with plain code.",
    edges=[
        ("START", classify),
        (classify, {"researcher": researcher, "writer": writer}),
    ],
)
