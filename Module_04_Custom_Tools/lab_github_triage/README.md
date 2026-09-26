<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Lab: GitHub Issue Triage Agent

## What this shows

An agent that reads a repository's open issues, proposes labels and
clarifying comments, and waits for human approval before any write reaches
GitHub. It combines plain function tools with `require_confirmation` gating.

| Tool | What it does | Confirmation? |
|---|---|---|
| `list_open_issues(repo)` | Returns up to 30 open issues (pull requests excluded) with their labels. | no |
| `get_issue(repo, number)` | Full body, state, and labels for one issue. | no |
| `add_label(repo, number, label)` | Adds a label (GitHub creates it if missing). | yes |
| `comment_on_issue(repo, number, text)` | Posts a comment. | yes |

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)). `PyGithub` is in
      the root `requirements.txt`.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`agent/.env.example`](agent/.env.example):
      `GOOGLE_API_KEY`, or Agent Platform (formerly Vertex AI) with
      `GOOGLE_CLOUD_LOCATION=global`.
- [ ] A GitHub fine-grained personal access token
      (GitHub, Settings, Developer settings, Personal access tokens) in
      `GITHUB_PERSONAL_ACCESS_TOKEN`. Reading public repositories needs only
      public read access. `add_label` and `comment_on_issue` need
      **Issues: Read and write** on the target repository; use a repository
      you own for the write path.

## Run it

1. `cd Module_04_Custom_Tools/lab_github_triage`
2. `adk web`
3. Open http://localhost:8000 and pick `agent` in the app dropdown in the top bar.
4. Send: "Triage the repo `your-org/your-repo`. Propose labels for unlabelled
   issues and draft a polite comment on any that need more info from the
   reporter."

Terminal alternative: `adk run agent` (approve or reject writes by typing
`yes` or anything else).

## What to look for

- `list_open_issues`, then a few `get_issue` calls, run without prompts.
- Each `add_label` or `comment_on_issue` stops with an
  `adk_request_confirmation` function call; `adk web` shows a confirmation
  card under that row in the Events view.
- Tick **Confirmed** and click **Submit**, and the write goes through. Submit
  with the box unticked and the tool body never runs;
  the agent reports that the action was rejected and moves on.

## Test the tools without a token

`tests/test_tools.py` replaces PyGithub with an in-memory fake repository
holding three issues and a pull request, then calls each tool function
directly. It needs no token and makes no model call, so it checks tool
wiring and return shapes, the missing-token error, and that both write
tools are wrapped with `require_confirmation=True`. The confirmation prompt
itself only fires in a real run (see What to look for). From this folder:

```bash
pytest tests
```

Expected: `7 passed`.

## Common errors

| Symptom | Cause |
|---|---|
| Every tool returns `GITHUB_PERSONAL_ACCESS_TOKEN is not set` | The token is missing from `.env`. The tools report it instead of crashing, and the agent relays it. |
| `403` on `add_label` or `comment_on_issue` | The token lacks Issues write access on that repository. |

## Clean up

Remove any test labels or comments the agent posted on your repository, and
revoke the token when you are done (GitHub, Settings, Developer settings).

## Deliverable

- The working agent (`agent/agent.py`).
- A screenshot or transcript of the approval prompt firing for `add_label` or
  `comment_on_issue` against a repository you own.
