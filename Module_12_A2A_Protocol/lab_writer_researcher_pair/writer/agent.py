# Author: Vishal Bulbule
# Date: 2026-09-22

"""Writer agent that calls a remote researcher over A2A.

The researcher is a `RemoteA2aAgent` wrapped in `AgentTool`, so the writer
calls it like a function: the research turn runs in the researcher's process
on port 8081, the findings come back as the tool result, and the writer keeps
control and drafts the brief from them.

Compare 04_consume_remote_agent, where the remote agent is a sub-agent. A
sub-agent receives control through `transfer_to_agent` and its reply is the
final answer, which is right for routing but wrong here: the writer would
never get the findings back to turn them into prose.

Start the researcher first: `adk api_server --a2a --port 8081` from the lab
folder. Set RESEARCHER_URL to reach it somewhere else.
"""

import os

from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import (
    AGENT_CARD_WELL_KNOWN_PATH,
    RemoteA2aAgent,
)
from google.adk.tools import AgentTool

# ADK serves each A2A agent under /a2a/<app_name> on the api_server port.
RESEARCHER_URL = os.environ.get("RESEARCHER_URL", "http://localhost:8081/a2a/researcher")

remote_researcher = RemoteA2aAgent(
    name="researcher",
    description=(
        "Remote research specialist. Give it a topic; it returns 3-6 bullet "
        "points of facts with source URLs."
    ),
    agent_card=f"{RESEARCHER_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
    use_legacy=False,
)

root_agent = LlmAgent(
    name="writer",
    model="gemini-3.5-flash",
    description=(
        "Writes briefs and articles. Delegates fact-finding to the researcher "
        "agent."
    ),
    instruction=(
        "You are a professional writer.\n"
        "You have one tool, `researcher`. It returns factual bullet points "
        "with source URLs. It does not write prose.\n"
        "\n"
        "For any writing request:\n"
        "1. Identify the topic and target length (default 250-350 words).\n"
        "2. Call `researcher` with a focused request.\n"
        "3. When the bullets come back, draft the piece in clear, neutral "
        "prose.\n"
        "4. Cite sources inline as (source: URL) at the end of the relevant "
        "sentence.\n"
        "5. Close with a short 'Sources' list.\n"
        "\n"
        "Never invent statistics. If a number is not in the researcher's "
        "output, leave it out."
    ),
    tools=[AgentTool(agent=remote_researcher)],
)
