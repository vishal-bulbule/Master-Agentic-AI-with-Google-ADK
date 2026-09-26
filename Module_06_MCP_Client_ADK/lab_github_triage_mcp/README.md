<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Lab: GitHub Issue Triage over MCP

## What this shows

A GitHub issue-triage agent built on GitHub's official MCP server instead of
hand-written tools. Module 4's `lab_github_triage/` wrapped PyGithub in
`FunctionTool`s with its own auth and error handling. Here the whole
integration is one `McpToolset` pointed at a hosted server, and the agent is
read-only twice over: the server removes write tools (`X-MCP-Readonly`), and
`tool_filter` passes only three read tools to the model.

```python
McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://api.githubcopilot.com/mcp/",
        headers={
            "Authorization": f"Bearer {token}",
            "X-MCP-Toolsets": "issues",
            "X-MCP-Readonly": "true",
        },
    ),
    tool_filter=["list_issues", "search_issues", "issue_read"],
)
```

The `@modelcontextprotocol/server-github` npm package that older tutorials
start over stdio is deprecated. GitHub's official server replaces it, with
different tool names (`issue_read` instead of `get_issue`, `add_issue_comment`
instead of `create_comment`).

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)) and a `.env` with your Gemini
  settings (see `agent/.env.example`; on Agent Platform use
  `GOOGLE_CLOUD_LOCATION=global`).
- A GitHub fine-grained personal access token:
  1. Create it at https://github.com/settings/personal-access-tokens/new.
  2. Repository access: "Public repositories" is enough for public repos. For
     a private repository, select it and grant **Issues: Read-only** (Metadata
     read-only is added automatically).
  3. Add it to your `.env`: `GITHUB_PERSONAL_ACCESS_TOKEN=github_pat_...`
- No Node.js: the server is hosted by GitHub.

## Run it

1. `cd Module_06_MCP_Client_ADK/lab_github_triage_mcp`
2. `adk web`
3. Open http://localhost:8000 and select `agent` in the agent dropdown.
4. Send: "Triage the five most recent open issues in google/adk-python."

Terminal alternative: `adk run agent`.

## Try it

Any public repository works, for example `google/adk-python`:

1. "Triage the five most recent open issues in google/adk-python."
2. "Search that repository for open issues about MCP."
3. "Post your label suggestions as a comment on the first issue."

## What to look for

- Prompt 1: a `list_issues` call in the Events view (click it to see the
  `owner`, `repo`, and `state` arguments), then one line and suggested
  labels per issue.
- Prompt 2: a `search_issues` call with a `query` argument.
- Prompt 3: the agent declines and gives you the comment text instead. There
  is no write tool in its tool list, so this does not depend on the model
  following the instruction.

To allow commenting in your own copy, remove the `X-MCP-Readonly` header, add
`add_issue_comment` to `tool_filter`, grant the token **Issues: Read and
write**, and consider `require_confirmation=True` on the McpToolset so every
tool call waits for user approval.

## Common errors

| Symptom | Cause and fix |
|---|---|
| The run ends with no answer, and the log shows `create_session` failing | `GITHUB_PERSONAL_ACCESS_TOKEN` is missing or rejected, so the toolset cannot reach `api.githubcopilot.com`. Set a valid token and run again. |
| Tool calls return "Resource not accessible by personal access token" | The fine-grained token does not cover that repository. |
| A tool named in `tool_filter` never appears | The GitHub server renamed or regrouped it. List the server's tools with MCP Inspector (`npx @modelcontextprotocol/inspector`, transport Streamable HTTP, URL above, plus an `Authorization` header) and update the filter. |

## Clean up

Revoke the token at https://github.com/settings/personal-access-tokens when
you no longer need it.
