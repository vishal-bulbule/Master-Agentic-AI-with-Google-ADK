<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Lab: run a sample agent from adk-samples

## What this shows

End-to-end check of your environment on a larger, production-style agent from
Google's `adk-samples` repository, and practice reading the Events view on a
multi-tool conversation.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)), so `adk` is on your path.
- [ ] `git`, and whatever the chosen sample's README requires: most use `uv`
      or `poetry`; `data-science` also needs a Google Cloud project with
      BigQuery. Credentials follow each sample's own `.env.example`.
- [ ] A separate virtual environment for the sample, so its dependencies do
      not change this repository's.

## Run it

### 1. Clone the samples repository

```bash
cd ~        # anywhere outside this repository
git clone https://github.com/google/adk-samples.git
cd adk-samples/python/agents
ls
```

You will see folders such as `customer-service`, `data-science` and
`software-bug-assistant`. Sample names and layouts change over time, so read
each sample's own README before running it.

### 2. Pick a sample

- `customer-service/`: the easiest start. Several tools, and the agent loop is
  easy to follow.
- `data-science/`: multi-agent with BigQuery. More setup.

```bash
cd customer-service
cat README.md
```

### 3. Set up credentials and dependencies

Each sample ships a `.env.example`:

```bash
cp .env.example .env
# edit .env and set your credentials, as described in the sample's README
```

Install the sample's dependencies the way its README says (most samples use
`uv` or `poetry`; some use `pip install -r requirements.txt`). Use a separate
virtual environment from this repository's.

### 4. Start `adk web`

Run it from the folder that contains the agent package, as the sample's README
describes. `adk web` lists every folder under the directory you start it in
that contains an `agent.py` or `root_agent.yaml`.

```bash
adk web --port 8000
```

Open http://localhost:8000 and pick the agent.

## Try it

For `customer-service`:

1. `Hi, I need help with my recent order.`
2. `I want to return a yellow garden cart I bought last week.`
3. `Can you recommend plants for a sunny balcony in Mumbai?`

## What to look for

- The Events view gets new numbered rows on each turn. Click a tool call row
  to see the arguments the model chose in the side panel, and the following
  tool result row to see what the tool returned.
- Pick one event and explain in two sentences what it is and what the agent
  does with it next. For example: "Event 4 is a `function_response` holding
  the JSON returned by `get_product_recommendations`. The model reads it and
  composes the final answer from it."

## Same agent over HTTP

`adk api_server` serves the agent without the web UI, which is how you script
tests or integrate with another application. The app name in the URLs is the
agent folder name; `GET /list-apps` shows the exact names.

```bash
adk api_server --port 8000
```

In another terminal:

```bash
curl http://localhost:8000/list-apps

# Create a session (replace APP with a name from /list-apps)
curl -X POST http://localhost:8000/apps/APP/users/u1/sessions \
  -H "Content-Type: application/json" -d '{"session_id": "s1"}'

# Send a message
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "APP",
    "userId": "u1",
    "sessionId": "s1",
    "newMessage": {"role": "user", "parts": [{"text": "Hi, I need help with my recent order."}]}
  }'

# Read the session: every event, the same data the Events view shows
curl http://localhost:8000/apps/APP/users/u1/sessions/s1
```

## Common errors

- **Missing key or authentication error**: `adk web` loads the `.env` in the
  agent folder or the nearest parent folder. Check that it exists there and
  has your credentials.
- **`ModuleNotFoundError`**: the sample's dependencies are not installed in
  the active virtual environment.
- **Agent not in the list**: `adk web` was started in the wrong folder. Start
  it in the folder that contains the agent package.
- **Unexpected cost**: check which model the sample uses before sending many
  requests, and switch to a Flash model if it defaults to Pro.

## Clean up

Delete the cloned `adk-samples` folder and its virtual environment when you
are done, and any cloud resources the sample's README had you create.
