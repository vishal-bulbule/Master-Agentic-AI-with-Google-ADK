# Author: Vishal Bulbule
# Date: 2026-09-22

"""Grounded agent that renders its own citations from grounding_metadata.

The agent is the same as in 02_google_search_grounding, except that the model
is told to keep URLs out of the answer. An `after_model_callback` then builds
the citations from the response's `grounding_metadata`: it inserts footnote
markers such as [1][3] after each supported span of the answer and appends a
numbered list of sources.

That is what a UI should do. The metadata records what the model actually
retrieved and which sources support which part of the answer, while URLs the
model types into the text are unverified.
"""

from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.adk.tools import google_search
from google.genai import types


def add_citations(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Adds footnote markers and a source list to a grounded answer.

    Returns the modified response, or None to keep the response unchanged
    when it carries no grounding sources.
    """
    metadata = llm_response.grounding_metadata
    # With streaming on, partial chunks arrive first and the metadata comes
    # with the final, complete response. Only that one is rewritten.
    if llm_response.partial or not metadata or not metadata.grounding_chunks:
        return None
    if not llm_response.content or not llm_response.content.parts:
        return None

    parts = llm_response.content.parts
    answer = "".join(p.text for p in parts if p.text and not p.thought)
    if not answer:
        return None

    # Segment offsets are byte offsets into the UTF-8 answer text. Insert the
    # markers from the end backwards so earlier offsets stay valid.
    text = answer.encode("utf-8")
    supports = [
        s
        for s in metadata.grounding_supports or []
        if s.segment and s.segment.end_index is not None and s.grounding_chunk_indices
    ]
    for support in sorted(supports, key=lambda s: s.segment.end_index, reverse=True):
        marker = "".join(f"[{i + 1}]" for i in support.grounding_chunk_indices)
        end = support.segment.end_index
        text = text[:end] + marker.encode("utf-8") + text[end:]

    lines = ["", "", "Sources:"]
    for number, chunk in enumerate(metadata.grounding_chunks, start=1):
        # Google Search fills `web`; data store grounding fills `retrieved_context`.
        source = chunk.web or chunk.retrieved_context
        title = (source.title if source else None) or "(no title)"
        uri = (source.uri if source else None) or ""
        lines.append(f"[{number}] [{title}]({uri})" if uri else f"[{number}] {title}")

    cited = text.decode("utf-8") + "\n".join(lines)
    thoughts = [p for p in parts if p.thought]
    llm_response.content.parts = thoughts + [types.Part(text=cited)]
    return llm_response


root_agent = LlmAgent(
    name="citation_demo_agent",
    model="gemini-3.5-flash",
    description="Grounded agent that renders citations from grounding_metadata.",
    instruction=(
        "Answer factual questions using google_search. Be concise (2-4 "
        "sentences). Do not include URLs or a source list in the answer; "
        "the sources are added from the grounding metadata afterwards."
    ),
    tools=[google_search],
    after_model_callback=add_citations,
)
