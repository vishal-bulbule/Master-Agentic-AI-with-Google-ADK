<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Lab: `techtrapture-mcp`, from stdio to Cloud Run

## What this shows

A complete MCP server built with FastMCP over a sample course catalog, run
locally over stdio, packaged for Cloud Run over Streamable HTTP, and used by
an ADK agent (`course_advisor/`) through both transports with the same agent
code. Only the connection parameters change.

| Primitive | Name | Purpose |
|---|---|---|
| Tool (read) | `get_course(slug)` | Course summary by slug |
| Tool (write) | `enroll_student(course_slug, email)` | Records an enrollment, returns an `enrollment_id` |
| Resources | `course://adk-bootcamp`, `course://mcp-deep-dive`, `course://gemini-prompting` | Course brochures as markdown, one per course |
| Prompt | `recommend_courses(interests)` | Recommendation prompt template |

| File | Purpose |
|---|---|
| `courses.py` | In-memory catalog and enrollment list |
| `server_stdio.py` | Defines the server once; `python server_stdio.py` serves it over stdio |
| `server_http.py` | Imports the same server and serves it over stateless Streamable HTTP at `/mcp` |
| `course_advisor/` | ADK agent: starts `server_stdio.py` over stdio by default, uses the HTTP server when `MCP_URL` is set |
| `Dockerfile`, `requirements.txt`, `.dockerignore` | Container that runs `server_http.py` on `$PORT` |

The brochures are registered as concrete resources rather than one
`course://{slug}` template: templates are not returned by `resources/list`,
and ADK's `load_mcp_resource` tool can only read listed resources.

Enrollments are kept in process memory: they disappear on restart and are
not shared between Cloud Run instances. That is fine for the lab and wrong
for production, where the write belongs in a database.

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)), virtual environment active.
- A `.env` with your Gemini settings for the agent (see
  `course_advisor/.env.example`). On Agent Platform (formerly Vertex AI) the
  model `gemini-3.5-flash` needs `GOOGLE_CLOUD_LOCATION=global`.
- Node.js with `npx`, for MCP Inspector.
- Steps 1 and 2 need nothing running first: the agent starts
  `server_stdio.py` itself. Step 3 needs the HTTP server running (the step
  gives the command).
- For the container and deploy steps: Docker (optional), the `gcloud` CLI, and
  a project with billing and these APIs enabled:
  `gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com`

## Run it

All commands run from `Module_07_Build_MCP_Server/lab_techtrapture_mcp`.

### Step 1: the stdio server in Inspector

```bash
npx @modelcontextprotocol/inspector python server_stdio.py
```

- **Tools**: `get_course` with `slug` = `adk-bootcamp`, then `enroll_student`
  with `course_slug` = `mcp-deep-dive` and `email` = `test@example.com`. The
  result has an `enrollment_id`.
- **Resources**: list resources and read `course://gemini-prompting`.
- **Prompts**: `recommend_courses` with `interests` = `agents and protocols`.
  The result is the advisor prompt, not a recommendation.

### Step 2: the ADK agent over stdio

1. `adk web`
2. Open http://localhost:8000 and select `course_advisor` in the agent dropdown.
3. Send: "I'm new to agents. Which course should I start with, and what does it cost?"

Terminal alternative: `adk run course_advisor`.

### Step 3: the HTTP server, and the same agent against it

1. In one terminal: `PORT=8090 python server_http.py`
2. Check it: `npx @modelcontextprotocol/inspector --cli http://localhost:8090/mcp --method tools/list`
3. Add `MCP_URL=http://localhost:8090/mcp` to your `.env` (or export it in the
   shell), then run `adk web` again and send the same prompt.

With Docker instead of step 3.1:

```bash
docker build -t techtrapture-mcp .
docker run --rm -p 8090:8080 techtrapture-mcp
```

### Step 4: deploy to Cloud Run and point the agent at it

```bash
gcloud run deploy techtrapture-mcp \
  --source . \
  --region us-central1 \
  --no-allow-unauthenticated
```

Cloud Build builds the image from the Dockerfile, pushes it to Artifact
Registry, and Cloud Run prints the service URL. Set
`MCP_URL=<service URL>/mcp` and restart `adk web`.

With `--no-allow-unauthenticated`, callers need `roles/run.invoker` and an
identity token: add `headers={"Authorization": f"Bearer {identity_token}"}`
to `StreamableHTTPConnectionParams` in `course_advisor/agent.py` (see the
comment there). For a short-lived test you can deploy with
`--allow-unauthenticated` instead, then delete the service.

## Try it

- "I'm new to agents. Which course should I start with, and what does it cost?"
- "Show me the brochure for mcp-deep-dive."
- "Enroll me in mcp-deep-dive with test@example.com." Then confirm the email.

## What to look for

- In the Events view, `get_course` calls before the answer: the price comes
  from the server, not from the model.
- For the brochure, a `load_mcp_resource` call with
  `resource_names: ["mcp-deep-dive-brochure"]`. ADK lists the server's
  resources in the instruction and inserts the one it loads into the next
  model request. MCP prompts are not exposed to the model; they are for users
  of a host UI.
- `enroll_student` only after you confirm the email, and the
  `enrollment_id` in its response.
- `server_http.py` has no tool code. Both transports serve one `mcp` object,
  so they cannot drift apart. The HTTP server logs one `POST /mcp` per
  JSON-RPC message; with `stateless_http=True` there is no `mcp-session-id`.

## Common errors

| Symptom | Cause and fix |
|---|---|
| `Address already in use` | Another process holds the port. Pick another `PORT` and update `MCP_URL`. |
| Agent runs without the course tools | With `MCP_URL` set, the HTTP server is not running or the URL lacks `/mcp`. Unset `MCP_URL` to go back to stdio. |
| Agent does not see a tool you just added | Restart `adk web`; the tool list is fetched when the toolset connects. |
| Slow first request on Cloud Run | Cold start. `--min-instances 1` removes it at the cost of an idle instance. |
| 403 from Cloud Run | The caller lacks `roles/run.invoker`, or no identity token was sent. |

## Clean up

```bash
gcloud run services delete techtrapture-mcp --region us-central1
docker rmi techtrapture-mcp          # if you built locally
rm -rf course_advisor/.adk           # local sessions from adk web / adk run
```

Remove `MCP_URL` from your `.env` when you are done.
