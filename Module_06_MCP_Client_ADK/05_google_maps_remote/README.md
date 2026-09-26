<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 05: Remote MCP Server: Google Maps Grounding Lite

## What this shows

An agent that uses a hosted MCP server. There is no `npx` and no child
process: `McpToolset` connects to `https://mapstools.googleapis.com/mcp` over
Streamable HTTP and sends the API key in a header. The server advertises
`search_places`, `lookup_weather`, `compute_routes`, `resolve_names`, and
`resolve_maps_urls`, all backed by Google Maps data.

```python
McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://mapstools.googleapis.com/mcp",
        headers={"X-Goog-Api-Key": os.environ["GOOGLE_MAPS_API_KEY"]},
    )
)
```

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)) and a `.env` with your Gemini
  settings (see `agent/.env.example`; on Agent Platform use
  `GOOGLE_CLOUD_LOCATION=global`).
- A Google Maps Platform API key for the Maps Grounding Lite API. Without it
  the agent still lists the Maps tools, but every tool call fails.
  1. In a Google Cloud project with billing enabled, enable the API:
     `gcloud services enable mapstools.googleapis.com`
     (or https://console.cloud.google.com/apis/library/mapstools.googleapis.com).
  2. Create an API key under APIs and Services, Credentials, and restrict it
     to the Maps Grounding Lite API.
  3. Add it to your `.env`: `GOOGLE_MAPS_API_KEY=your-maps-api-key`.

  Setup guide: https://developers.google.com/maps/ai/grounding-lite
- No Node.js: the server is hosted by Google.

## Run it

1. `cd Module_06_MCP_Client_ADK/05_google_maps_remote`
2. `adk web`
3. Open http://localhost:8000 and select `agent` in the agent dropdown.
4. Send: "Find coffee shops near Golden Gate Park."

Terminal alternative: `adk run agent`.

## Try it

- "I will be in San Francisco tomorrow. What is the weather?"
- "Find coffee shops near Golden Gate Park."
- "How long is the drive from the Googleplex to SFO?"

## What to look for

- The tool names and descriptions come from the server. The agent code only
  has a URL and a header.
- In the Events view, `search_places` is called with a `text_query` argument
  whose format is described in the server's tool description, not in the
  agent's instruction.
- Swapping providers means changing the URL. The agent code does not change.

## Common errors

| Symptom | Cause and fix |
|---|---|
| Tool results say the request is unauthenticated or the API is not enabled | The key is missing, restricted to other APIs, or the Grounding Lite API is not enabled in the key's project. |
| `GOOGLE_MAPS_API_KEY is not set` warning in the log | The `.env` was not found. `adk` loads the nearest `.env` walking up from the agent folder. |

## Clean up

Delete or restrict the API key in APIs and Services, Credentials when you no
longer need it.
