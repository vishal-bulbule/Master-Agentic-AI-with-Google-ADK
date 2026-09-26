# Author: Vishal Bulbule
# Date: 2026-09-22

"""Several MCP servers in one agent.

Two `McpToolset` instances in one tools list: the filesystem server (filtered
to read-only tools) and the knowledge-graph memory server. ADK merges the
discovered tools, so to the model this is one larger tool list.

Tool names must be unique across all toolsets. These two servers use distinct
names; for servers that overlap, set `tool_name_prefix` on each McpToolset or
narrow them with `tool_filter`.
"""

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

FILESYSTEM_ROOT = "/tmp/mcp-demo"
# Without MEMORY_FILE_PATH the memory server writes inside the npx cache,
# which is easy to lose and hard to find. A fixed path makes the stored graph
# easy to inspect and delete.
MEMORY_FILE = "/tmp/mcp-demo-memory.jsonl"

filesystem_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", FILESYSTEM_ROOT],
        ),
        timeout=30,
    ),
    tool_filter=["read_text_file", "list_directory"],
)

memory_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-memory"],
            env={"MEMORY_FILE_PATH": MEMORY_FILE},
        ),
        timeout=30,
    ),
)

root_agent = LlmAgent(
    name="multi_server_agent",
    model="gemini-3.5-flash",
    description="Reads files and remembers facts about the user across sessions.",
    instruction=(
        "You have two sets of tools:\n"
        f"1. Reading files in {FILESYSTEM_ROOT} (read_text_file, list_directory). "
        "Use absolute paths.\n"
        "2. A persistent knowledge graph (create_entities, add_observations, "
        "create_relations, search_nodes, read_graph, and others).\n"
        "When the user shares a fact about themselves, store it in the knowledge "
        "graph with an entity named 'user'. When asked what you remember, search "
        "the graph. When asked to summarize a file, read it first."
    ),
    tools=[filesystem_toolset, memory_toolset],
)
