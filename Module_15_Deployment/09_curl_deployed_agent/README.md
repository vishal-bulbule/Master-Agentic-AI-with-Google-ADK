<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 09 - Calling the Deployed Agent

## What this shows

How to call an ADK agent served over HTTP: the two auth modes of a Cloud Run service, and
the two requests every conversation needs (create a session, then send a message to
`/run_sse`). The same API is served by `adk api_server` locally, so you can try it
without deploying anything.

## Prerequisites

- For a deployed service: the `greet-agent` service from `../03_adk_deploy_cloud_run/` or
  `greet-agent-custom` from `../08_custom_dockerfile/`, and its URL:

  ```bash
  URL=$(gcloud run services describe greet-agent --region=us-central1 --format="value(status.url)")
  ```

- For a private service: the gcloud CLI logged in (`gcloud auth login`) as an account
  with `roles/run.invoker` on the service (Owners have it; to grant it, see "Public vs
  authenticated" below).
- For the local variant: nothing in Google Cloud. The repository setup
  ([SETUP.md](../../SETUP.md)) and credentials in
  `../03_adk_deploy_cloud_run/greet_agent/.env`.
- `curl` and `bash`.

## Run it

Against a deployed, authenticated service:

1. `cd Module_15_Deployment/09_curl_deployed_agent`
2. `export URL=https://greet-agent-<hash>.us-central1.run.app`
3. `export APP_NAME=greet_agent`
4. `bash test_deployed.sh "Priya"`

Locally, without deploying (the same API that Cloud Run serves):

1. Terminal 1: `cd Module_15_Deployment/03_adk_deploy_cloud_run && adk api_server --port 8000 .`
2. Terminal 2: `cd Module_15_Deployment/09_curl_deployed_agent`
3. `NO_AUTH=1 URL=http://localhost:8000 APP_NAME=greet_agent bash test_deployed.sh "Priya"`

## What to look for

The session response (JSON with `id`, `appName`, `userId`, `state`), then events such as:

```
data: {"content":{"parts":[{"functionCall":{"name":"greet","args":{"name":"Priya"}}}],"role":"model"}, ...}
data: {"content":{"parts":[{"functionResponse":{"name":"greet","response":{"status":"success","message":"Hello, Priya!"}}}],"role":"user"}, ...}
data: {"content":{"parts":[{"text":"Hello, Priya!"}],"role":"model"}, ...}
```

## Public vs authenticated

| Deploy flag | Who can call | When |
|---|---|---|
| `--allow-unauthenticated` | Anyone with the URL | Demos, public APIs |
| `--no-allow-unauthenticated` | Callers with a Google identity token and `roles/run.invoker` on the service | Production, internal services |

With `adk deploy cloud_run`, pass these after `--`, for example
`adk deploy cloud_run ... ./greet_agent -- --no-allow-unauthenticated`.

An identity token is a short-lived (about 1 hour) JWT signed by Google that identifies
the caller:

```bash
TOKEN=$(gcloud auth print-identity-token)
```

Grant another person access:

```bash
gcloud run services add-iam-policy-binding greet-agent \
  --region=us-central1 \
  --member=user:teammate@example.com \
  --role=roles/run.invoker
```

For service-to-service calls, the caller's service account needs `roles/run.invoker`,
and it fetches a token for the service URL as audience (from the metadata server on
Google Cloud, or `gcloud auth print-identity-token --impersonate-service-account=... --audiences=$URL`).

## The two requests

1. Create a session:

   ```bash
   curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
     "$URL/apps/greet_agent/users/u1/sessions" \
     -d '{"session_id": "s1"}'
   ```

   `session_id` is optional; leave it out and the server generates one (returned as
   `id`). In production, take the user id from your auth layer and use a new session
   id per conversation. The older form `POST /apps/<app>/users/<user>/sessions/<id>` is
   deprecated in ADK 2.x.

2. Send a message:

   ```bash
   curl -N -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
     "$URL/run_sse" \
     -d '{
       "app_name": "greet_agent",
       "user_id": "u1",
       "session_id": "s1",
       "new_message": {"role": "user", "parts": [{"text": "Please greet Priya."}]},
       "streaming": false
     }'
   ```

   `/run_sse` answers with server-sent events, one `data: {...}` line per ADK event
   (the tool call, the tool response, the final text). `"streaming": true` adds partial
   text events as the model generates. `/run` takes the same body and returns all events
   as one JSON list.

## Common errors

| Code | Likely cause |
|---|---|
| `401` | Service requires auth and no `Authorization` header was sent |
| `403` | Token is valid but the caller lacks `roles/run.invoker`, or the token audience is wrong |
| `404` | `app_name` does not match the agent folder name, or the session does not exist |
| `500` | The agent failed; read the service logs |

Follow the logs while you test:

```bash
gcloud beta run services logs tail greet-agent --region=us-central1
```

## Clean up

Nothing is created except a session inside the service. If you granted
`roles/run.invoker` to a teammate, remove it when done:

```bash
gcloud run services remove-iam-policy-binding greet-agent --region=us-central1 \
  --member=user:teammate@example.com --role=roles/run.invoker
```
