# Author: Vishal Bulbule
# Date: 2026-09-22

"""Talk to an MCP server directly with the `mcp` Python SDK, no ADK.

The script starts the reference filesystem server as a subprocess over stdio,
lists the tools it advertises, then calls two of them against the
`sample_docs/` folder next to this file. This is the raw protocol exchange
that ADK's McpToolset performs for you in later modules.

Requires Node.js (for `npx`). The server is downloaded on first run.

Run:
    python mcp_grounding.py
"""

import asyncio
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

DOCS_DIR = (Path(__file__).parent / "sample_docs").resolve()

SERVER = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", str(DOCS_DIR)],
)


async def main() -> None:
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Tools advertised by the server:")
            for t in tools.tools:
                print(f"  - {t.name}: {(t.description or '')[:70]}")

            result = await session.call_tool("list_directory", {"path": str(DOCS_DIR)})
            print("\nlist_directory result:")
            for c in result.content:
                print(c.text if hasattr(c, "text") else c)

            result = await session.call_tool("read_text_file", {"path": str(DOCS_DIR / "note.txt")})
            print("\nread_text_file result (this is the text you would put in a prompt):")
            for c in result.content:
                print(c.text if hasattr(c, "text") else c)


if __name__ == "__main__":
    asyncio.run(main())
