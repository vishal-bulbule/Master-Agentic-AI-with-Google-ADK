# Author: Vishal Bulbule
# Date: 2026-09-22

"""OpenAPI tools: generate one tool per operation from a spec.

Instead of writing a Python function per endpoint, point `OpenAPIToolset` at
an OpenAPI 3.x spec and ADK creates one `RestApiTool` per operation. The tool
name comes from `operationId`, the description from `summary` and
`description`, and the parameters from the spec's parameters and request
body.

The spec's server is `httpbin.org`, which echoes each request back, so the
sample needs no backend and no secret. The agent sees the echoed request as
the tool result.
"""

from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.tools.openapi_tool import OpenAPIToolset

SPEC_PATH = Path(__file__).resolve().parent.parent / "petstore.yaml"

petstore_toolset = OpenAPIToolset(
    spec_str=SPEC_PATH.read_text(),
    spec_str_type="yaml",
)


root_agent = LlmAgent(
    name="petstore_agent",
    model="gemini-3.5-flash",
    description="Talks to a Pet Store API generated from an OpenAPI spec.",
    instruction=(
        "You manage a tiny pet store. You have three tools generated from the OpenAPI spec: "
        "list_pets, get_pet, and create_pet. Pick the right one for the user's request. "
        "The backend is an echo service, so report what was sent and the HTTP result."
    ),
    tools=[petstore_toolset],
)
