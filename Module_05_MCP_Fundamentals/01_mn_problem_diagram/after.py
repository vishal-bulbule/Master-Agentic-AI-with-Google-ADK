# Author: Vishal Bulbule
# Date: 2026-09-22

"""After MCP: one Slack MCP server, one client interface, three apps.

The Slack vendor (or the community) writes one MCP server. Every app talks to
it through the same client interface, and the tool schema comes from the
server, so no app invents its own. Adding a fourth app needs no Slack code.

This is a simulation of the shape of MCP; the real protocol (JSON-RPC over
stdio or HTTP) starts in 03_fastmcp_first_server/.
"""

from dataclasses import dataclass
from typing import Any


class SlackMCPServer:
    """Stands in for a real Slack MCP server process."""

    def list_tools(self) -> list[dict]:
        return [
            {
                "name": "slack_post_message",
                "description": "Post a message to a Slack channel.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "channel": {"type": "string"},
                        "text": {"type": "string"},
                    },
                    "required": ["channel", "text"],
                },
            }
        ]

    def call_tool(self, name: str, args: dict[str, Any]) -> dict:
        if name != "slack_post_message":
            raise ValueError(f"Unknown tool {name}")
        return {"ok": True, "channel": args["channel"], "text": args["text"]}


@dataclass
class MCPClient:
    """The one client interface every host implements."""

    # A real client holds a stdio or HTTP transport instead of the object.
    server: SlackMCPServer

    def list_tools(self) -> list[dict]:
        return self.server.list_tools()

    def call_tool(self, name: str, args: dict[str, Any]) -> dict:
        return self.server.call_tool(name, args)


def app_a(client: MCPClient) -> None:
    result = client.call_tool(
        "slack_post_message", {"channel": "#general", "text": "Hello from A"}
    )
    print("App A (support bot)   :", result)


def app_b(client: MCPClient) -> None:
    result = client.call_tool(
        "slack_post_message", {"channel": "#general", "text": "Hello from B"}
    )
    print("App B (release notes) :", result)


def app_c(client: MCPClient) -> None:
    result = client.call_tool(
        "slack_post_message", {"channel": "#general", "text": "Hello from C"}
    )
    print("App C (standup bot)   :", result)


def main() -> None:
    print("=== AFTER MCP ===")
    print("One server, one schema, three apps reuse it.\n")

    client = MCPClient(server=SlackMCPServer())

    print("Tools advertised by the server (the same for every app):")
    for tool in client.list_tools():
        print(f"  {tool['name']}: {tool['description']}")
    print()

    app_a(client)
    app_b(client)
    app_c(client)
    print()
    print("One implementation. A new app needs no Slack code.")
    print("A new service is usable by every app. M x N became M + N.")


if __name__ == "__main__":
    main()
