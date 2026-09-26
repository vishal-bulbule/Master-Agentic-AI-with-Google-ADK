# Author: Vishal Bulbule
# Date: 2026-09-22

"""Agentic RAG: the model builds its own query and filters, then retrieves.

Naive RAG embeds the user's words and returns the top chunks. Here the model
drives retrieval with two function tools: `construct_query` turns the question
into a query plus metadata filters, and `vector_search` runs it against a mock
vector store. The instruction tells the model to retry without filters when
the first search finds nothing, so a bad filter guess does not end the turn.

Watch the events: every answer should show `construct_query`, then one or two
`vector_search` calls, before the final text.
"""

from google.adk.agents import LlmAgent

# Mock vector store: 8 chunks with metadata. Scoring is keyword overlap, so the
# sample runs offline and deterministically; a real store would compare
# embeddings, and only the body of vector_search would change.
_CHUNKS: list[dict] = [
    {
        "id": "c01",
        "text": (
            "ADK agents are built around the LlmAgent class. Tools are plain "
            "Python functions registered via the tools= parameter."
        ),
        "category": "adk",
        "level": "beginner",
        "source": "Module 02: First ADK Agent",
    },
    {
        "id": "c02",
        "text": (
            "MCP (Model Context Protocol) lets external servers expose tools "
            "to any compatible LLM client over JSON-RPC."
        ),
        "category": "mcp",
        "level": "beginner",
        "source": "Module 05: MCP Fundamentals",
    },
    {
        "id": "c03",
        "text": (
            "Vertex AI Search indexes your documents and returns the top-K "
            "chunks by semantic similarity. At high volume it costs less "
            "than Google Search grounding."
        ),
        "category": "grounding",
        "level": "intermediate",
        "source": "Module 13: Grounding",
    },
    {
        "id": "c04",
        "text": (
            "Hybrid search combines vector and keyword (BM25) results, then "
            "reranks. Reciprocal Rank Fusion is the simplest fusion formula."
        ),
        "category": "grounding",
        "level": "advanced",
        "source": "Module 13: Grounding",
    },
    {
        "id": "c05",
        "text": (
            "The Live API streams audio and text in both directions over a "
            "WebSocket. adk api_server streams run output to HTTP clients "
            "as server-sent events."
        ),
        "category": "streaming",
        "level": "intermediate",
        "source": "Module 11: Streaming and Live API",
    },
    {
        "id": "c06",
        "text": (
            "The A2A (Agent2Agent) protocol lets one agent call another agent "
            "over HTTP. The remote agent publishes an agent card that "
            "describes its skills and endpoint."
        ),
        "category": "a2a",
        "level": "advanced",
        "source": "Module 12: A2A Protocol",
    },
    {
        "id": "c07",
        "text": (
            "To deploy an ADK agent to Cloud Run: build a container, set "
            "GOOGLE_GENAI_USE_ENTERPRISE=TRUE, run it as a service account "
            "with the Vertex AI User role, and listen on port 8080."
        ),
        "category": "deployment",
        "level": "intermediate",
        "source": "Module 15: Deployment",
    },
    {
        "id": "c08",
        "text": (
            "ADK evaluation scores an agent against a set of prompts with "
            "expected tool calls and responses. Built-in criteria include "
            "tool trajectory match and response match."
        ),
        "category": "evals",
        "level": "intermediate",
        "source": "Module 14: Evaluation and Observability",
    },
]


def _score(text: str, query: str) -> float:
    """Fraction of query tokens (longer than 2 characters) found in the text."""
    q_tokens = {t for t in query.lower().split() if len(t) > 2}
    if not q_tokens:
        return 0.0
    t_tokens = {t for t in text.lower().split() if len(t) > 2}
    return len(q_tokens & t_tokens) / max(len(q_tokens), 1)


def construct_query(user_intent: str) -> dict:
    """Turn a user question into a search query plus suggested filters.

    Call this first. The suggested filters are a best guess at the category
    and level the user means; adjust them before calling vector_search.

    Args:
        user_intent: The user's question, as asked.

    Returns:
        A dict with `status` ("success" or "error"), `query` (the search
        string), and `suggested_filters` (metadata filters such as
        {"category": "grounding"}).
    """
    if not user_intent or not user_intent.strip():
        return {"status": "error", "error_message": "Empty user_intent."}

    text = user_intent.lower()

    # Keyword rules keep the sample deterministic; a real system would
    # classify with the model or an embedding.
    category = None
    for cat, keywords in {
        "adk": ["adk", "llmagent", "agent"],
        "mcp": ["mcp", "model context protocol"],
        "grounding": ["ground", "rag", "citation", "vector", "retriev"],
        "streaming": ["stream", "live api", "sse", "token"],
        "a2a": ["a2a", "agent-to-agent"],
        "deployment": ["deploy", "cloud run", "container"],
        "evals": ["eval", "metric", "benchmark"],
    }.items():
        if any(k in text for k in keywords):
            category = cat
            break

    level = None
    if any(w in text for w in ["beginner", "intro", "basic"]):
        level = "beginner"
    elif any(w in text for w in ["advanced", "deep", "production"]):
        level = "advanced"

    filters = {}
    if category:
        filters["category"] = category
    if level:
        filters["level"] = level

    return {
        "status": "success",
        "query": user_intent.strip(),
        "suggested_filters": filters,
    }


def vector_search(query: str, filters: dict) -> dict:
    """Search the mock vector store.

    Args:
        query: The search string from construct_query.
        filters: Metadata filters, for example {"category": "grounding"} or
            {"category": "adk", "level": "beginner"}. Pass {} to search
            everything.

    Returns:
        A dict with `status` ("success" or "no_results") and `results`, the
        top 3 chunks by score, each with id, text, score, source, category,
        and level.
    """
    filters = filters or {}

    candidates = _CHUNKS
    for key, value in filters.items():
        candidates = [c for c in candidates if c.get(key) == value]

    scored = [(c, _score(c["text"], query)) for c in candidates]
    scored = [(c, s) for c, s in scored if s > 0]
    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:3]

    if not top:
        return {
            "status": "no_results",
            "results": [],
            "message": (
                f"No chunks matched query={query!r} with filters={filters}. "
                "Try relaxing filters."
            ),
        }

    return {
        "status": "success",
        "results": [
            {
                "id": c["id"],
                "text": c["text"],
                "score": round(s, 3),
                "source": c["source"],
                "category": c["category"],
                "level": c["level"],
            }
            for c, s in top
        ],
    }


root_agent = LlmAgent(
    name="agentic_rag_agent",
    model="gemini-3.5-flash",
    description=(
        "Agentic RAG over a mock vector store of notes about this ADK "
        "sample library."
    ),
    instruction=(
        "You answer questions about this ADK sample library using two tools:\n"
        "  1. construct_query(user_intent): always call this first to get a "
        "query and suggested filters.\n"
        "  2. vector_search(query, filters): call this with the output of "
        "construct_query. If it returns no_results, retry once with an empty "
        "filters dict before giving up.\n"
        "\n"
        "After retrieval, answer in 2-4 sentences and end with a 'Sources:' "
        "list of the chunk IDs and source names you used. Answer only from "
        "retrieved chunks, never from general knowledge."
    ),
    tools=[construct_query, vector_search],
)
