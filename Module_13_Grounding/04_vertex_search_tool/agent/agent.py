# Author: Vishal Bulbule
# Date: 2026-09-22

"""Grounding on your own documents with `VertexAiSearchTool`.

For private content (internal docs, policy PDFs, knowledge base articles) the
source is a Vertex AI Search data store instead of the web. Like
`google_search`, `VertexAiSearchTool` is a built-in tool: Gemini queries the
data store inside the model call and returns `grounding_metadata` whose chunks
point at your documents (`retrieved_context`), not web pages.

The tool needs Agent Platform (formerly Vertex AI) mode,
`GOOGLE_GENAI_USE_ENTERPRISE=TRUE`; a Gemini API key does not work. Set
`VERTEX_AI_SEARCH_DATASTORE_ID` to the full resource name of your data store.
"""

import logging
import os

from google.adk.agents import LlmAgent
from google.adk.tools import VertexAiSearchTool

# Full resource name, for example:
# projects/<PROJECT_ID>/locations/global/collections/default_collection/dataStores/<DATASTORE_ID>
DATASTORE_ID = os.environ.get("VERTEX_AI_SEARCH_DATASTORE_ID", "")

if not DATASTORE_ID:
    # Keep the agent importable so `adk web` still lists it; the first model
    # call fails until the variable is set.
    logging.getLogger(__name__).warning(
        "VERTEX_AI_SEARCH_DATASTORE_ID is not set. See the README in "
        "04_vertex_search_tool."
    )
    DATASTORE_ID = (
        "projects/YOUR_PROJECT_ID/locations/global/collections/"
        "default_collection/dataStores/YOUR_DATASTORE_ID"
    )

root_agent = LlmAgent(
    name="docs_search_agent",
    model="gemini-3.5-flash",
    description=(
        "Answers questions about internal documentation by searching a "
        "Vertex AI Search data store."
    ),
    instruction=(
        "You are an internal documentation assistant.\n"
        "For every question, search the data store for supporting passages. "
        "Answer in 2-4 sentences and name the documents you used. If the data "
        "store returns nothing relevant, say so; do not answer from general "
        "knowledge."
    ),
    tools=[VertexAiSearchTool(data_store_id=DATASTORE_ID)],
)
