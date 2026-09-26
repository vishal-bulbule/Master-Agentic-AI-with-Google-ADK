# Author: Vishal Bulbule
# Date: 2026-09-22

"""GitHub issue-triage agent over GitHub's official remote MCP server.

The agent connects to https://api.githubcopilot.com/mcp/ over Streamable HTTP
with a personal access token. Two layers keep it read-only: the
`X-MCP-Readonly` header makes the server drop every write tool, and
`tool_filter` narrows what is left to three issue-reading tools. The agent
reads issues, summarizes them, and proposes labels in chat; it cannot comment,
label, or close anything.

Compare with Module 4's lab_github_triage/, which wrote the same tools by hand
with PyGithub.
"""

import logging
import os

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

GITHUB_MCP_URL = "https://api.githubcopilot.com/mcp/"
GITHUB_TOKEN = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "")

if not GITHUB_TOKEN:
    logging.warning(
        "GITHUB_PERSONAL_ACCESS_TOKEN is not set. The GitHub MCP server will "
        "reject the connection with 401 Unauthorized."
    )

server_headers = {
    # Only the issues toolset, and only its read tools.
    "X-MCP-Toolsets": "issues",
    "X-MCP-Readonly": "true",
}
if GITHUB_TOKEN:
    server_headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

root_agent = LlmAgent(
    name="github_triage_mcp_agent",
    model="gemini-3.5-flash",
    description="Triages GitHub issues through the GitHub MCP server (read-only).",
    instruction=(
        "You are a GitHub triage assistant. When the user names a repository "
        "(format 'owner/repo'):\n"
        "1. Call list_issues to fetch open issues (use search_issues for "
        "keyword searches).\n"
        "2. Summarize each issue in one sentence. Call issue_read if the title "
        "and body are not enough.\n"
        "3. Suggest 1 to 3 labels per issue, for example 'bug', 'documentation', "
        "'enhancement', 'good first issue'.\n"
        "You are read-only. If the user asks you to comment on, label, or close "
        "an issue, explain that you cannot and give them the text to post "
        "themselves."
    ),
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=GITHUB_MCP_URL,
                headers=server_headers,
                timeout=30,
            ),
            tool_filter=["list_issues", "search_issues", "issue_read"],
        )
    ],
)
