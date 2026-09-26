# Author: Vishal Bulbule
# Date: 2026-09-22

"""Course advisor agent that uses techtrapture-mcp locally or on Cloud Run.

With MCP_URL unset, McpToolset starts ../server_stdio.py as a child process
over stdio. With MCP_URL set (for example https://...run.app/mcp), it connects
to the deployed server over Streamable HTTP. Only the connection parameters
change; the agent and its tools are the same.

McpToolset exposes the server's tools by default. `use_mcp_resources=True`
also gives the agent a load_mcp_resource tool for resources such as
course://{slug}. MCP prompts are meant for users picking templates in a host
UI, so ADK does not expose them to the model.
"""

import os
import sys
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import (
    McpToolset,
    StdioConnectionParams,
    StreamableHTTPConnectionParams,
)
from mcp import StdioServerParameters

# The server files live in the lab folder, one level above this package.
LAB_DIR = Path(__file__).resolve().parent.parent
# adk web and adk run load .env before importing this module, so MCP_URL from
# .env is visible here.
MCP_URL = os.environ.get("MCP_URL")

if MCP_URL:
    # For a Cloud Run service deployed without --allow-unauthenticated, add
    # headers={"Authorization": f"Bearer {identity_token}"}.
    connection_params = StreamableHTTPConnectionParams(url=MCP_URL, timeout=30)
else:
    connection_params = StdioConnectionParams(
        server_params=StdioServerParameters(
            # sys.executable starts the server with the interpreter running
            # adk, which has fastmcp installed.
            command=sys.executable,
            args=[str(LAB_DIR / "server_stdio.py")],
            # server_stdio.py imports courses.py from its own folder.
            cwd=str(LAB_DIR),
        ),
        timeout=30,
    )

root_agent = LlmAgent(
    name="course_advisor",
    model="gemini-3.5-flash",
    description="Recommends courses and enrolls learners through techtrapture-mcp.",
    instruction=(
        "You are a course advisor. Use the MCP tools to look up course details "
        "and prices before you answer; do not guess them. Only call "
        "enroll_student after the user has given and confirmed their email."
    ),
    tools=[McpToolset(connection_params=connection_params, use_mcp_resources=True)],
)
