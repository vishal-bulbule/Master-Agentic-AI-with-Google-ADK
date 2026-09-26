# Author: Vishal Bulbule
# Date: 2026-09-22

"""A plain text agent for showing token streaming in adk web.

Nothing in the agent is streaming-specific. Streaming is chosen per run:
the adk web More options > Streaming checkbox sends streaming=true to
/run_sse, which runs the agent with RunConfig(streaming_mode=StreamingMode.SSE).
The same agent runs streamed or not without a code change.

It uses a standard Gemini model, not a Live model: token streaming is text in,
text out over run_async(), not the Live API.
"""

from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    name="token_stream_tutor",
    model="gemini-3.5-flash",
    instruction=(
        "You are a concise tutor. When asked to explain something, write one "
        "short paragraph of 5 to 7 sentences. No bullet points, no preamble."
    ),
)
