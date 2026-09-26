# Author: Vishal Bulbule
# Date: 2026-09-22

"""The Streamable HTTP transport.

The same two tools as stdio_server.py, served over HTTP at one endpoint. The
server runs on its own and any number of clients connect to its URL. This is
the transport you deploy to Cloud Run or any other HTTP platform.

Run:
    python http_server.py
Then connect MCP Inspector (Transport: Streamable HTTP) to
http://127.0.0.1:8000/mcp
"""

from fastmcp import FastMCP

mcp = FastMCP("transport-demo-http")


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
    # "http" is FastMCP's name for the Streamable HTTP transport.
    mcp.run(transport="http", host="127.0.0.1", port=8000, path="/mcp")
