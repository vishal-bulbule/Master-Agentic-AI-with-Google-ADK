# Author: Vishal Bulbule
# Date: 2026-09-22

"""RAG variant: retrieve documents, then generate. Fixed flow, no decisions.

`inject_retrieved_docs` is a `before_model_callback`: before every model
request it retrieves policy documents and appends them to the system
instruction. Retrieval always runs, and the model never chooses whether or
what to look up. That fixed retrieve-then-generate flow is what separates RAG
from the tool-calling agent in `support_agent`.

The answer is grounded in shipping policy, but the policy documents know
nothing about order A-1042. The retrieved documents are also written to the
`retrieved_docs` state key so you can see them in the State tab of the dev UI.
"""

from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse

# Stand-in for a vector store such as Vector Search, pgvector or Pinecone.
KNOWLEDGE_BASE = [
    "Our standard shipping takes 3-5 business days.",
    "Express shipping arrives within 1-2 business days.",
    "All orders include free returns within 30 days.",
    "If your order is delayed beyond the estimated date, contact support.",
]


def retrieve(query: str) -> list[str]:
    """Returns the documents relevant to the query.

    Args:
        query: The user's question.

    Returns:
        Every document in the knowledge base. A real retriever ranks
        documents by similarity to the query and returns the top k.
    """
    return KNOWLEDGE_BASE


def inject_retrieved_docs(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Retrieves policy documents and adds them to the model request.

    Args:
        callback_context: Context for the current invocation.
        llm_request: The request about to be sent to the model.

    Returns:
        None, so the (modified) request goes to the model.
    """
    user_content = callback_context.user_content
    query = ""
    if user_content and user_content.parts:
        query = " ".join(p.text for p in user_content.parts if p.text)
    docs = retrieve(query)
    callback_context.state["retrieved_docs"] = docs
    context = "\n".join(f"- {d}" for d in docs)
    llm_request.append_instructions([f"Policies:\n{context}"])
    return None


root_agent = LlmAgent(
    name="support_rag",
    model="gemini-3.5-flash",
    description="Support assistant that answers only from retrieved policies.",
    instruction=(
        "You are a customer support assistant. Answer using ONLY the policies "
        "provided below. If they do not contain the answer, say so."
    ),
    before_model_callback=inject_retrieved_docs,
)
