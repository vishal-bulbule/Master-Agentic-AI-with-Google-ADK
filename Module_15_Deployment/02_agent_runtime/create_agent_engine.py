# Author: Vishal Bulbule
# Date: 2026-09-22

"""Create an empty Agent Runtime instance with the Agent Platform SDK.

An instance with no agent code is still useful: it provides managed sessions
and Memory Bank, which an agent running anywhere else (locally, on Cloud Run)
can use through `VertexAiSessionService` or `--session_service_uri=agentengine://<id>`.

This creates a billable resource in your project. Delete it when you are done:
`client.agent_engines.delete(name=<resource name>)`.
"""

import os

import vertexai
from dotenv import load_dotenv

load_dotenv()

client = vertexai.Client(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    # Agent Runtime is regional; "global" is not a valid location here.
    location=os.environ.get("AGENT_RUNTIME_LOCATION", "us-central1"),
)

agent_engine = client.agent_engines.create(
    config={
        "display_name": "greet-agent-sessions",
        "description": "Sessions and memory for greet_agent",
    }
)
print(agent_engine.api_resource.name)
