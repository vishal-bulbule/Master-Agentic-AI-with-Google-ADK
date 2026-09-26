<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 02: Google Search grounding

## What this shows

The shortest path to a grounded agent: add the `google_search` built-in tool.
`google_search` is not a Python function; it tells Gemini to run Google Search
inside the model call, and the response comes back with `grounding_metadata`
listing the pages it used. It works only with Gemini models, every grounded
request is billed for search on top of tokens (see topic 07), and the Gemini
API does not accept a built-in search tool in the same request as function
tools or agent transfer. To combine them, use
`GoogleSearchTool(bypass_multi_tools_limit=True)` from
`google.adk.tools.google_search_tool`; ADK then runs the search as a separate
agent call.

```python
from google.adk.tools import google_search

root_agent = LlmAgent(
    model="gemini-3.5-flash",
    instruction="Use google_search for current information and always cite sources.",
    tools=[google_search],
)
```

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials go in a `.env` at the repository root or in the `agent/` folder; `agent/.env.example` lists the variables (a Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_13_Grounding/02_google_search_grounding`
2. `adk web`
3. Open http://localhost:8000 and select `agent` in the agent dropdown (the agent folder is named `agent`).
4. Send: `Who is the current US president, and when does their term end?`

Terminal alternative: `adk run agent`.

## Try it

The same questions as topic 01, each in a new session:

```
Who is the current US president, and when does their term end?
What is the current Cloud Run on-demand price per vCPU-second?
What is the newest Gemini model Google has released?
```

## What to look for

- The answers are current, where topic 01 answered from memory. The only code
  difference is `tools=[google_search]`.
- Events view: there is no tool call row. The search happens on the model
  side. Click the final response row and open the raw JSON view in the side
  panel: its `groundingMetadata` holds
  `webSearchQueries` (what the model searched for), `groundingChunks` (the
  sources, each with a `web.uri` and `web.title`), and `groundingSupports`
  (which part of the answer each source supports).
- The `Sources:` list at the end of the answer is text the model wrote. The
  metadata is the record of what was actually retrieved; topic 03 builds the
  citations from it instead.

## Clean up

`adk web` and `adk run` keep sessions in `agent/.adk/session.db`. Delete it to start clean: `rm -rf agent/.adk`
