# Author: Vishal Bulbule
# Date: 2026-09-22

"""Publish an existing ADK FunctionTool as an MCP server.

`lookup_customer` is an ordinary ADK tool function. `adk_to_mcp_tool_type`
converts its ADK declaration (name, docstring, parameter schema) into an MCP
`Tool`, and the call handler runs it through `FunctionTool.run_async`, the same
path the ADK runtime uses. One function, two consumers: ADK agents in process,
and any MCP host over stdio.

This uses the low-level `mcp` SDK because `adk_to_mcp_tool_type` returns a raw
MCP `Tool` object. To publish a whole agent rather than a tool, ADK also has
`google.adk.tools.mcp_tool.to_mcp_server(agent)` (experimental).

Run:
    python server.py
Inspect:
    npx @modelcontextprotocol/inspector python server.py
"""

import asyncio
import json

import mcp_types
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.mcp_tool import adk_to_mcp_tool_type
from mcp.server.context import ServerRequestContext
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

# Stand-in for a CRM.
_CUSTOMERS = {
    "C-100": {"name": "Acme Corp", "tier": "Enterprise", "ltv": 240000},
    "C-200": {"name": "Globex Inc", "tier": "Growth", "ltv": 56000},
}


def lookup_customer(customer_id: str) -> dict:
    """Look up a customer by ID.

    Args:
        customer_id: Customer ID, for example "C-100".

    Returns:
        A dict with status and the customer's name, tier, and lifetime value,
        or status "error" and a message if the ID is unknown.
    """
    customer = _CUSTOMERS.get(customer_id)
    if customer is None:
        return {"status": "error", "error": f"Customer {customer_id} not found"}
    return {"status": "success", "customer_id": customer_id, **customer}


adk_tool = FunctionTool(lookup_customer)


async def list_tools(
    ctx: ServerRequestContext, params: mcp_types.PaginatedRequestParams | None
) -> mcp_types.ListToolsResult:
    return mcp_types.ListToolsResult(tools=[adk_to_mcp_tool_type(adk_tool)])


async def call_tool(
    ctx: ServerRequestContext, params: mcp_types.CallToolRequestParams
) -> mcp_types.CallToolResult:
    if params.name != adk_tool.name:
        return mcp_types.CallToolResult(
            content=[mcp_types.TextContent(type="text", text=f"Unknown tool: {params.name}")],
            is_error=True,
        )
    # No ADK session exists here, so there is no ToolContext. Tools that read
    # or write tool_context.state cannot be bridged this way.
    result = await adk_tool.run_async(args=params.arguments or {}, tool_context=None)
    return mcp_types.CallToolResult(
        content=[mcp_types.TextContent(type="text", text=json.dumps(result))],
        structured_content=result,
        is_error=result.get("status") == "error",
    )


server = Server(
    "adk-bridge", version="0.1.0", on_list_tools=list_tools, on_call_tool=call_tool
)


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
