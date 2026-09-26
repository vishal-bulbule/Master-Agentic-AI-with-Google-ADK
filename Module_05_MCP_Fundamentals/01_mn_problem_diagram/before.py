# Author: Vishal Bulbule
# Date: 2026-09-22

"""Before MCP: every app ships its own Slack adapter.

Three LLM apps each re-implement the same Slack integration: auth, the
send-message call, error handling, and the tool schema given to the LLM.
Notice that the three schemas describe the same capability in three
different shapes. Multiply this by every service and you get M x N.

This is a simulation; no network calls are made.
"""


class AppASlackAdapter:
    """App A, a customer-support bot."""

    def __init__(self, token: str) -> None:
        self.token = token

    def post(self, channel: str, text: str) -> dict:
        return {"ok": True, "channel": channel, "text": text, "via": "AppA"}

    def schema_for_llm(self) -> dict:
        return {
            "name": "slack_post",
            "description": "Send a Slack message",
            "parameters": {"channel": "str", "text": "str"},
        }


class AppBSlackClient:
    """App B, a release-notes generator. Same job, different field names."""

    def __init__(self, slack_token: str) -> None:
        self.slack_token = slack_token

    def send_message(self, room: str, body: str) -> dict:
        return {"status": "sent", "room": room, "body": body, "via": "AppB"}

    def tool_def(self) -> dict:
        return {
            "tool": "send_slack",
            "desc": "Posts to Slack",
            "args": {"room": "string", "body": "string"},
        }


class AppCSlack:
    """App C, a daily standup summarizer. A third reimplementation."""

    def __init__(self, auth: str) -> None:
        self.auth = auth

    def message(self, target: str, msg: str) -> dict:
        return {"sent": True, "target": target, "msg": msg, "via": "AppC"}

    def describe(self) -> dict:
        return {
            "fn": "message",
            "summary": "Send to slack",
            "fields": ["target", "msg"],
        }


def main() -> None:
    print("=== BEFORE MCP ===")
    print("Three apps, three Slack adapters, three schemas.\n")

    a = AppASlackAdapter("xoxb-A")
    b = AppBSlackClient("xoxb-B")
    c = AppCSlack("xoxb-C")

    print("App A schema :", a.schema_for_llm())
    print("App B schema :", b.tool_def())
    print("App C schema :", c.describe())
    print()
    print("Each app sends the same message in a different shape:")
    print(" ", a.post("#general", "Hello"))
    print(" ", b.send_message("#general", "Hello"))
    print(" ", c.message("#general", "Hello"))
    print()
    print("Same capability, 3 implementations. Multiply by 10 services: M x N.")


if __name__ == "__main__":
    main()
