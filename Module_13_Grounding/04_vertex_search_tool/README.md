<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 04: Grounding on your documents with `VertexAiSearchTool`

## What this shows

For internal documents, swap `google_search` for `VertexAiSearchTool` pointed
at a Vertex AI Search data store (AI Applications in the Google Cloud
console). Like `google_search` it is a built-in tool: Gemini queries the data
store inside the model call, and the grounding chunks come back as
`retrieved_context` entries naming your documents. The agent is told to
answer only from the data store and to say so when it finds nothing.

```python
from google.adk.tools import VertexAiSearchTool

root_agent = LlmAgent(
    ...,
    tools=[VertexAiSearchTool(data_store_id=os.environ["VERTEX_AI_SEARCH_DATASTORE_ID"])],
)
```

## Prerequisites

This topic needs cloud resources you create yourself. Complete these before
running it.

1. **Agent Platform (formerly Vertex AI) credentials.** A Gemini API key does
   not work with this tool. Install the Google Cloud CLI and run
   `gcloud auth application-default login`.
2. **APIs enabled** in your project:
   `gcloud services enable aiplatform.googleapis.com discoveryengine.googleapis.com`
3. **IAM.** Your account needs Discovery Engine Admin
   (`roles/discoveryengine.admin`) to create the data store, and at least
   Discovery Engine Viewer (`roles/discoveryengine.viewer`) plus Vertex AI User
   (`roles/aiplatform.user`) to run the agent.
4. **Documents in Cloud Storage.** Any PDFs, HTML, or text files work:
   ```bash
   gcloud storage buckets create gs://YOUR_BUCKET --location=US
   gcloud storage cp ./my-docs/*.pdf gs://YOUR_BUCKET/docs/
   ```
5. **A data store**, in the console:
   1. Open **AI Applications**, then **Data Stores**, then **Create data store**.
   2. Pick **Cloud Storage**, choose **Unstructured documents**, and select
      `gs://YOUR_BUCKET/docs/*`.
   3. Set the location to **global**, give it a name, and click **Create**.
   4. Wait for the import to finish (the **Documents** tab shows the count; a
      few minutes for a small corpus).
6. **The data store ID.** Copy it from the data store list, or list the data
   stores from the command line:
   ```bash
   curl -s -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
     -H "x-goog-user-project: YOUR_PROJECT_ID" \
     "https://discoveryengine.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/global/collections/default_collection/dataStores"
   ```
7. **Environment variables**, from `agent/.env.example`, in your `.env`:
   ```env
   GOOGLE_GENAI_USE_ENTERPRISE=TRUE
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=global
   VERTEX_AI_SEARCH_DATASTORE_ID=projects/your-project-id/locations/global/collections/default_collection/dataStores/your-datastore-id
   ```
   `VERTEX_AI_SEARCH_DATASTORE_ID` is the full resource name, not the short
   ID. The model is `gemini-3.5-flash` on location `global`.

The data store has storage and query costs. See Clean up.

## Run it

1. `cd Module_13_Grounding/04_vertex_search_tool`
2. `adk web`
3. Open http://localhost:8000 and select `agent` in the agent dropdown (the agent folder is named `agent`).
4. Send: `<a question about something in your documents>`

Terminal alternative: `adk run agent`.

## What to look for

- The answer names the documents it used. In the Events view, click the
  final response row: the raw JSON view in the side panel shows
  `groundingMetadata.groundingChunks`, whose `retrievedContext` entries have
  your document titles and `gs://` URIs. There is no tool call row, as with
  `google_search`.
- Ask about something that is not in the documents (for example
  `What is the capital of Australia?`): the agent says the data store has
  nothing relevant, and the event has no grounding chunks.
- `03_display_citations/agent/agent.py` has an `add_citations` callback that
  renders these chunks as footnotes; it handles `retrieved_context` too.

## Common errors

| Symptom | Cause |
|---|---|
| Warning `VERTEX_AI_SEARCH_DATASTORE_ID is not set` at startup | Set the variable; the placeholder ID fails on the first question. |
| `NOT_FOUND` for the data store | Wrong ID, a short ID instead of the full resource name, or the data store is in a different project or location. |
| `PERMISSION_DENIED` | Your ADC account lacks the roles in step 3. |
| Error that Vertex AI Search is not supported | `GOOGLE_GENAI_USE_ENTERPRISE` is not `TRUE`. |
| Answers say nothing was found for every question | The import has not finished, or the documents did not import. Check the data store's **Documents** tab. |

## Google Search or Vertex AI Search

| | Google Search grounding | Vertex AI Search |
|---|---|---|
| Source | The public web | Your indexed documents |
| Freshness | Real time | As of your last import |
| Access control | Public only | Your IAM |
| Cost | Search fee per grounded request | Storage plus per-query fee, lower at volume |

Many agents need both: Google Search for "what is the latest CVE", Vertex AI
Search for "what is our patch policy".

## Clean up

- Delete the data store: console, **AI Applications**, **Data Stores**, select
  it, **Delete**.
- Delete the bucket: `gcloud storage rm -r gs://YOUR_BUCKET`
- Local sessions: `rm -rf agent/.adk`
