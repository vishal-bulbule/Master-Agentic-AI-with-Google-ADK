<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Setup

Everything you need before running the modules. Sections 1 to 4 are one-time
setup. Section 5 lists extra requirements for individual modules, so you only
set up what you are about to use.

## 1. Accounts and keys

| Provider | What you need | Needed for |
|---|---|---|
| Google AI Studio | Gemini API key | Every module (or use Agent Platform instead, see below) |
| Google Cloud | Project with billing enabled | Modules 13, 15, and any module if you use Agent Platform |
| GitHub | Fine-grained personal access token, read-only access to public repositories and issues | Modules 4, 6 |
| Google Maps Platform | API key | Module 6 |
| Anthropic | API key (optional) | Module 3, LiteLLM sample only |

There are two ways to reach Gemini:

- **Gemini API key** (simplest). Get one at https://aistudio.google.com/apikey.
- **Agent Platform (formerly Vertex AI)**. Uses your Google Cloud project and
  `gcloud` credentials. The default model in these samples, `gemini-3.5-flash`,
  is served from the `global` location, so set `GOOGLE_CLOUD_LOCATION=global`.

## 2. Local tools

| Tool | Version | Used in |
|---|---|---|
| Python | 3.10 or later (tested on 3.12) | Every module |
| Node.js and npm | Current LTS | Modules 5, 6 (MCP servers launched with `npx`) |
| Google Cloud CLI (`gcloud`) | Latest | Modules 13, 15 |
| Docker | Latest | Modules 7, 15 |
| Claude Desktop | Latest | Module 5 only |
| `jq` | Any (optional) | Reading JSON output in Modules 2 and 15 |

MCP Inspector (Modules 5 and 7) needs no install: `npx @modelcontextprotocol/inspector`.

## 3. Python environment

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 4. Credentials

Copy the example file at the repository root and fill in the keys you have:

```bash
cp .env.example .env
```

`adk web` and `adk run` look for a `.env` file in the agent folder first and
then in each parent folder, and use the first one they find. A single `.env` at
the repository root therefore works for every agent. Each agent folder also has
a `.env.example` listing only the variables that agent needs, if you prefer to
keep a separate `.env` per agent. A `.env` in an agent folder replaces the root
one entirely; the two are not merged.

`.env` files are ignored by git. Never commit one.

If you use Agent Platform, authenticate once:

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### Google Cloud APIs

Enable these on your project before Modules 13 and 15:

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  cloudtrace.googleapis.com \
  discoveryengine.googleapis.com
```

### Cost control

Set a budget alert before you start (Cloud Console, Billing, Budgets). Every
sample uses a Flash model by default. Delete anything you deploy when you are
done (see section 6).

## 5. Module-specific requirements

| Module | Extra setup |
|---|---|
| 0 AI Foundations | None. The multimodal sample draws its own chart, or takes an image path |
| 1 Agents Landscape | Optional: clone https://github.com/google/adk-samples next to this repository to explore Google's sample agents |
| 3 LlmAgent and Model Choice | `ANTHROPIC_API_KEY` for the LiteLLM sample. The routing sample compares Flash with a Pro model; your project must allow the Pro model |
| 4 Custom Tools | `GITHUB_PERSONAL_ACCESS_TOKEN` for the GitHub triage lab |
| 5 MCP Fundamentals | Claude Desktop. Back up its `claude_desktop_config.json` before editing it |
| 6 MCP Client | Node.js, `GITHUB_PERSONAL_ACCESS_TOKEN`, `GOOGLE_MAPS_API_KEY` |
| 7 Build MCP Server | Docker for the container sample; a Google Cloud project for the Cloud Run sample |
| 11 Streaming and Live API | A microphone and a browser with mic access for the voice samples |
| 12 A2A Protocol | Ports 8000 (adk web) and 8081 (the remote agent on `adk api_server --a2a`) free on localhost |
| 13 Grounding | A Vertex AI Search data store for the search tool sample (the sample README explains how to create one) |
| 14 Evaluation and Observability | Cloud Trace API enabled if you want traces in Cloud Trace rather than on the console |
| 15 Deployment | Google Cloud project, the APIs above, and the IAM roles listed in the module README |

## 6. Clean up

Delete only what you created. List first, then delete by name:

```bash
gcloud run services list
gcloud run services delete SERVICE_NAME --region REGION

gcloud secrets list
gcloud secrets delete SECRET_NAME
```

Also remove any Vertex AI Search data store (Module 13) you created, and
revoke API keys and tokens you no longer need.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `adk: command not found` | Virtual environment not active | `source .venv/bin/activate` |
| Agent missing from the `adk web` dropdown | Missing `__init__.py`, or the variable is not named `root_agent` | See `Module_02_First_ADK_Agent/common_failures/` |
| `404 NOT_FOUND` for a model on Agent Platform | Model not served in your location | Set `GOOGLE_CLOUD_LOCATION=global` |
| `FAILED_PRECONDITION` naming `vertexai.allowedGenAIModels` | Your organization policy blocks that model | Use an allowed model or ask your admin |
| `npx` hangs on first run | It is downloading the MCP server package | Wait for the first run to finish |
| `Permission denied` during Cloud Run deploy | Cloud Build service account lacks roles | See `Module_15_Deployment/README.md` |
