# Author: Vishal Bulbule
# Date: 2026-09-22

"""Tool authentication: a service API key and a per-user OAuth request.

Two patterns:
1. Env-var API key: one service-level secret, read at call time.
2. Per-user OAuth: the tool calls `tool_context.request_credential(...)`,
   ADK emits an `adk_request_credential` function call for the client to
   run the consent flow, and on a later call `get_auth_response(...)`
   returns the user's credential.

The OAuth endpoints and client id below are placeholders, so the consent
step cannot complete. The sample shows the request shape. Never hard-code
real credentials in agent code: use `.env` or a secret manager for service
keys and ADK's auth flow for per-user OAuth.
"""

import os

from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows
from google.adk.agents import LlmAgent
from google.adk.auth import AuthConfig, AuthCredential, AuthCredentialTypes, OAuth2Auth
from google.adk.tools import ToolContext


def get_weather_via_apikey(city: str) -> dict:
    """Calls a fictional weather API authenticated with an env-var API key.

    Args:
        city: The city to look up.

    Returns:
        `status` "success" with canned weather data, or `status` "error"
        when `WEATHER_API_KEY` is not set.
    """
    # Read at call time so the agent still loads without the key; the tool
    # then reports the problem to the model instead of crashing at import.
    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key:
        return {
            "status": "error",
            "error_message": "WEATHER_API_KEY is not set, so the upstream API cannot be called.",
        }
    # A real tool would send the key upstream, for example in an
    # Authorization header. Never return the key itself to the model.
    return {"status": "success", "city": city, "temp_c": 27}


# The scheme tells ADK what the upstream expects. Replace the URLs, scopes,
# and client credentials with values from your OAuth provider.
CALENDAR_AUTH = AuthConfig(
    auth_scheme=OAuth2(
        flows=OAuthFlows(
            authorizationCode=OAuthFlowAuthorizationCode(
                authorizationUrl="https://example.com/oauth/authorize",
                tokenUrl="https://example.com/oauth/token",
                scopes={"calendar.read": "Read the user's calendar"},
            )
        )
    ),
    raw_auth_credential=AuthCredential(
        auth_type=AuthCredentialTypes.OAUTH2,
        oauth2=OAuth2Auth(
            client_id=os.environ.get("OAUTH_CLIENT_ID", "your-client-id"),
            client_secret=os.environ.get("OAUTH_CLIENT_SECRET", "your-client-secret"),
        ),
    ),
)


def list_calendar_events(tool_context: ToolContext) -> dict:
    """Lists the user's calendar events using per-user OAuth.

    On the first call there is no credential yet, so the tool requests one
    and returns `status` "pending". After the client completes the consent
    flow, the next call finds the credential and proceeds.

    Returns:
        `status` "pending" while authorization is outstanding, or
        `status` "success" with `events`.
    """
    credential = tool_context.get_auth_response(CALENDAR_AUTH)
    if credential is None:
        tool_context.request_credential(CALENDAR_AUTH)
        return {
            "status": "pending",
            "message": "Asked the user to authorize calendar access. Retry after they approve.",
        }
    # A real tool would call the Calendar API with credential.oauth2.access_token.
    return {
        "status": "success",
        "events": [{"title": "Design review", "start": "2026-05-23T10:00:00+05:30"}],
    }


root_agent = LlmAgent(
    name="auth_demo_agent",
    model="gemini-3.5-flash",
    description="Demonstrates env-var API key and per-user OAuth tool auth.",
    instruction=(
        "You have two tools: get_weather_via_apikey (uses a service API key) and "
        "list_calendar_events (requires per-user OAuth). Pick the right one for the request. "
        "If a tool returns status='pending', tell the user authorization is needed."
    ),
    tools=[get_weather_via_apikey, list_calendar_events],
)
