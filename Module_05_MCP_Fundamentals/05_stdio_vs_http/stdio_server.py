# Author: Vishal Bulbule
# Date: 2026-09-22

"""The stdio transport, FastMCP's default.

The host launches this script as a child process and exchanges
newline-delimited JSON-RPC over its stdin and stdout. There is no port and no
network. Compare with http_server.py: the tool code is identical and only the
`mcp.run()` call differs.

Run:
    npx @modelcontextprotocol/inspector python stdio_server.py
"""

from fastmcp import FastMCP

mcp = FastMCP("transport-demo-stdio")


@mcp.tool()
def ping() -> dict:
    """Health check that every MCP client can call.

    Returns:
        A dict with status and the reply "pong".
    """
    return {"status": "success", "reply": "pong"}


@mcp.tool()
def add(a: int, b: int) -> dict:
    """Add two integers.

    Args:
        a: First integer.
        b: Second integer.

    Returns:
        A dict with status and the sum.
    """
    return {"status": "success", "result": a + b}


if __name__ == "__main__":
    mcp.run()
