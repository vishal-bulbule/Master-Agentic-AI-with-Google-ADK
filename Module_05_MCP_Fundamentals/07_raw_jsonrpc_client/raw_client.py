# Author: Vishal Bulbule
# Date: 2026-09-22

"""Call an MCP server with the low-level `mcp` SDK client.

FastMCP hides the protocol. This client talks to the weather server in
03_fastmcp_first_server/ with the official `mcp` SDK's ClientSession, the same
layer ADK's McpToolset is built on, so you can see each JSON-RPC step:
initialize, tools/list, tools/call.

Notice that a tool result has two forms: `content` (a list of text blocks, for
models) and `structured_content` (the JSON object, for code). FastMCP fills
both when a tool returns a dict.

Run:
    python raw_client.py
"""

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PATH = (
    Path(__file__).resolve().parent.parent / "03_fastmcp_first_server" / "server.py"
)

# sys.executable starts the server with the same interpreter (and installed
# packages) as this script. A bare "python" may resolve to another install.
SERVER = StdioServerParameters(command=sys.executable, args=[str(SERVER_PATH)])


async def call_and_print(session: ClientSession, city: str) -> None:
    print(f"tools/call -> get_weather(city={city!r})")
    result = await session.call_tool("get_weather", {"city": city})
    for block in result.content:
        print("  content           :", getattr(block, "text", block))
    print("  structured_content:", json.dumps(result.structured_content))
    print("  is_error          :", result.is_error)
    print()


async def main() -> None:
    print(f"Launching MCP server: {SERVER_PATH.name}\n")

    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            print("Server info :", init.server_info.name, init.server_info.version)
            print("Protocol    :", init.protocol_version)
            print()

            tools = await session.list_tools()
            print("tools/list response:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description.splitlines()[0]}")
                print(f"    input_schema: {json.dumps(tool.input_schema, indent=6)}")
            print()

            await call_and_print(session, "Pune")
            await call_and_print(session, "Mumbai")


if __name__ == "__main__":
    asyncio.run(main())
