# Author: Vishal Bulbule
# Date: 2026-09-22

"""Hybrid search: vector and keyword retrieval fused with reciprocal rank fusion.

Three retrievers over the same 10-document corpus. `vector_search` stands in
for dense retrieval and catches paraphrases; `keyword_search` stands in for
BM25 and catches exact terms and rare tokens; `hybrid_search` runs both and
merges the rankings with RRF. The agent gets only `hybrid_search`, so each
turn is one tool call.

Both scorers are token-overlap stand-ins so the sample runs offline. The
`hybrid_search` result also returns `vector_ranking` and `keyword_ranking`, so
the tool response in the dev UI shows how the two lanes disagreed.
"""

from google.adk.agents import LlmAgent

_CORPUS: list[dict] = [
    {"id": "d01", "text": "ADK LlmAgent wraps Gemini models with tool calling and sessions."},
    {"id": "d02", "text": "Deploy an agent by building a container, pushing to Artifact Registry, and starting a Cloud Run service."},
    {"id": "d03", "text": "Ship to production with Cloud Build, Cloud Run, and a service account with Vertex AI User role."},
    {"id": "d04", "text": "Vertex AI Search indexes private documents and returns ranked chunks for grounding."},
    {"id": "d05", "text": "Google Search grounding gives the LLM real-time web facts and returns grounding_metadata."},
    {"id": "d06", "text": "BM25 is a sparse retrieval algorithm that scores documents by term frequency and inverse document frequency."},
    {"id": "d07", "text": "Reciprocal Rank Fusion merges multiple ranked lists: score = sum over lists of 1/(k + rank)."},
    {"id": "d08", "text": "Vector search uses cosine similarity on dense embeddings. Strong on paraphrases, weak on rare tokens."},
    {"id": "d09", "text": "Reranking with a cross-encoder scores (query, doc) pairs jointly and reorders the top candidates."},
    {"id": "d10", "text": "MCP servers expose tools over JSON-RPC so any compatible LLM client can invoke them."},
]


def _vector_score(text: str, query: str) -> float:
    """Stand-in for cosine similarity: overlap of tokens longer than 3 chars.

    Dropping short tokens and normalizing by set size favors documents that
    share several conceptual words, and ignores short exact identifiers.
    """
    q = {t.strip(".,") for t in query.lower().split() if len(t) > 3}
    t = {tok.strip(".,") for tok in text.lower().split() if len(tok) > 3}
    if not q or not t:
        return 0.0
    return len(q & t) / (len(q | t) ** 0.5)


def _keyword_score(text: str, query: str) -> float:
    """Stand-in for BM25: substring matches of each query token, weighted by rarity.

    Catches IDs and uncommon names that the vector stand-in ignores.
    """
    text_l = text.lower()
    score = 0.0
    for tok in query.lower().split():
        tok = tok.strip(".,")
        if len(tok) < 3:
            continue
        if tok in text_l:
            # Rare-token bonus: 1 / (1 + corpus_freq).
            cf = sum(1 for d in _CORPUS if tok in d["text"].lower())
            score += 1.0 / (1 + cf)
    return score


def _rrf(ranked_lists: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    """Reciprocal rank fusion: score(doc) = sum over lists of 1 / (k + rank).

    Uses ranks only, never raw scores, because vector and keyword scores are
    on different scales. k=60 is the value from the original RRF paper.
    """
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, doc_id in enumerate(ranked):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def _doc(doc_id: str) -> dict:
    return next(d for d in _CORPUS if d["id"] == doc_id)


def vector_search(query: str) -> dict:
    """Mock semantic vector search over the corpus.

    Args:
        query: The search string.

    Returns:
        A dict with `status` ("success" or "no_results") and `results`, the
        top 5 documents with id, text, and score.
    """
    scored = [(d, _vector_score(d["text"], query)) for d in _CORPUS]
    scored = [(d, s) for d, s in scored if s > 0]
    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:5]
    if not top:
        return {"status": "no_results", "results": []}
    return {
        "status": "success",
        "results": [{"id": d["id"], "text": d["text"], "score": round(s, 3)} for d, s in top],
    }


def keyword_search(query: str) -> dict:
    """Mock keyword (BM25-style) search over the corpus.

    Args:
        query: The search string.

    Returns:
        A dict with `status` ("success" or "no_results") and `results`, the
        top 5 documents with id, text, and score.
    """
    scored = [(d, _keyword_score(d["text"], query)) for d in _CORPUS]
    scored = [(d, s) for d, s in scored if s > 0]
    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:5]
    if not top:
        return {"status": "no_results", "results": []}
    return {
        "status": "success",
        "results": [{"id": d["id"], "text": d["text"], "score": round(s, 3)} for d, s in top],
    }


def hybrid_search(query: str) -> dict:
    """Run vector and keyword search and fuse the rankings with RRF.

    Args:
        query: The search string, usually the user's question.

    Returns:
        A dict with `status` ("success" or "no_results"), `results` (the top 5
        fused documents with id, text, and rrf_score), and `vector_ranking`
        and `keyword_ranking` (document ids from each retriever, best first).
    """
    vec = vector_search(query)
    kw = keyword_search(query)

    vec_ids = [r["id"] for r in vec.get("results", [])]
    kw_ids = [r["id"] for r in kw.get("results", [])]

    fused = _rrf([vec_ids, kw_ids])
    top = fused[:5]

    if not top:
        return {
            "status": "no_results",
            "results": [],
            "vector_ranking": vec_ids,
            "keyword_ranking": kw_ids,
        }

    return {
        "status": "success",
        "results": [
            {
                "id": doc_id,
                "text": _doc(doc_id)["text"],
                "rrf_score": round(score, 4),
            }
            for doc_id, score in top
        ],
        "vector_ranking": vec_ids,
        "keyword_ranking": kw_ids,
    }


root_agent = LlmAgent(
    name="hybrid_search_agent",
    model="gemini-3.5-flash",
    description=(
        "Answers questions over a small mock corpus using hybrid (vector + "
        "keyword) retrieval with reciprocal rank fusion."
    ),
    instruction=(
        "Answer questions using only the hybrid_search tool.\n"
        "Workflow:\n"
        "  1. Call hybrid_search(query=<the user's question>).\n"
        "  2. Read the fused top results and answer in 2-3 sentences.\n"
        "  3. End with a 'Sources:' line listing the doc IDs you used.\n"
        "If the tool returns no_results, say you don't know. Do not guess."
    ),
    tools=[hybrid_search],
)
