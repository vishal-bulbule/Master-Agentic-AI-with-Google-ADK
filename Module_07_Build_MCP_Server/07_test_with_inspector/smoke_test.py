# Author: Vishal Bulbule
# Date: 2026-09-22

"""Scripted smoke test for an MCP server, no Inspector needed.

Starts ../01_fastmcp_hello/server.py over stdio with the low-level `mcp`
client and checks the three things every host relies on: the initialize
handshake, the advertised tool list, and one real tool call. It exits
non-zero on any failure, so it can gate a CI job.

Run:
    python smoke_test.py
"""

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = Path(__file__).resolve().parent.parent / "01_fastmcp_hello" / "server.py"


async def main() -> int:
    # sys.executable runs the server with this interpreter and its packages.
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER_SCRIPT)])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            print(f"OK   initialize  -> {init.server_info.name} (protocol {init.protocol_version})")

            tools = await session.list_tools()
            names = [tool.name for tool in tools.tools]
            print(f"OK   list_tools  -> {names}")
            if "get_weather" not in names:
                print("FAIL expected a get_weather tool")
                return 1

            result = await session.call_tool("get_weather", {"city": "Pune"})
            if result.is_error:
                print(f"FAIL call_tool returned an error: {result.content}")
                return 1
            if (result.structured_content or {}).get("status") != "success":
                print(f"FAIL unexpected result: {result.structured_content}")
                return 1
            print(f"OK   call_tool   -> {json.dumps(result.structured_content)}")

    print("\nAll smoke checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
