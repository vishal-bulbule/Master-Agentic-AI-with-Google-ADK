<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 09: Tool Authentication

## What this shows

Two of the three common patterns for giving tools credentials:

| Pattern | When to use | How |
|---|---|---|
| Env-var API key | Service-level secret, same for every user | `os.environ["WEATHER_API_KEY"]` read inside the tool |
| Per-user OAuth | Each user authorizes their own account (mail, calendar, code hosting) | `tool_context.request_credential()` and `tool_context.get_auth_response()` |
| Service account | Backend-to-backend on Google Cloud | Application Default Credentials (not shown) |

`list_calendar_events()` shows the OAuth request:

1. First call: `get_auth_response()` returns `None`.
2. The tool calls `request_credential(CALENDAR_AUTH)` and returns `status="pending"`.
3. ADK emits an `adk_request_credential` function call carrying the
   authorization URL. The client (for example `adk web`) walks the user
   through the provider's consent screen and sends the result back.
4. On the next call, `get_auth_response()` returns the credential and the
   tool uses `credential.oauth2.access_token`.

The `AuthConfig` points at `https://example.com/oauth/*` with a placeholder
client id, so step 3 cannot complete.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`agent/.env.example`](agent/.env.example):
      `GOOGLE_API_KEY`, or Agent Platform (formerly Vertex AI) with
      `GOOGLE_CLOUD_LOCATION=global` (`gemini-3.5-flash` is served from
      `global`).
- [ ] `WEATHER_API_KEY` in the same `.env`. The weather API is fictional,
      so any string works.
- [ ] Optional, to complete the OAuth flow: an OAuth client registered with
      your provider. Replace the URLs and scopes in `CALENDAR_AUTH` and set
      `OAUTH_CLIENT_ID` and `OAUTH_CLIENT_SECRET`.

## Run it

1. `cd Module_04_Custom_Tools/09_tool_auth`
2. `adk web`
3. Open http://localhost:8000 and pick `agent` in the app dropdown in the top bar.
4. Send: "Weather in Mumbai?"

Terminal alternative: `adk run agent`.

## Try it

- "Weather in Mumbai?" (succeeds, or explains that `WEATHER_API_KEY` is missing)
- "List my calendar events for tomorrow." (returns `status: pending` and an auth request)

## What to look for

- Remove `WEATHER_API_KEY` and restart: the weather tool returns an error
  the model explains, instead of the agent failing to load.
- The calendar prompt produces an `adk_request_credential` function call.
  ADK strips the client secret from that request before it reaches the client.

## Common errors

| Symptom | Cause |
|---|---|
| `ValueError: Auth Scheme SecuritySchemeType.oauth2 requires oauth2 in auth_credential` | The `AuthCredential` has no `oauth2=OAuth2Auth(client_id=..., client_secret=...)`; ADK needs the client id to build the authorization URL. |

## Rules of thumb

- Never put user credentials in agent source code, and never return a secret
  (or part of one) in a tool result: the model sees everything a tool returns.
- Service keys: env vars locally, a secret manager in production.
- Use ADK's auth flow for per-user OAuth instead of writing your own.
