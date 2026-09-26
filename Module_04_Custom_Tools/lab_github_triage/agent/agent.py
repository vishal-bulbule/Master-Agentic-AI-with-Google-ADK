# Author: Vishal Bulbule
# Date: 2026-09-22

"""Lab: GitHub issue triage agent with human approval for every write.

Four tools, two of them gated by `require_confirmation`:
    list_open_issues(repo)                read
    get_issue(repo, number)               read
    add_label(repo, number, label)        write, requires confirmation
    comment_on_issue(repo, number, text)  write, requires confirmation

The reads run freely so the agent can investigate. Each write pauses the run
until a human approves it, so nothing reaches GitHub without review. Needs
`GITHUB_PERSONAL_ACCESS_TOKEN` in the environment.
"""

import os

from github import Auth, Github
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool


def _client() -> Github:
    """Builds a PyGithub client from the env-var token."""
    token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        raise RuntimeError(
            "GITHUB_PERSONAL_ACCESS_TOKEN is not set. Add it to .env "
            "(see agent/.env.example)."
        )
    return Github(auth=Auth.Token(token), per_page=100)


def list_open_issues(repo: str) -> dict:
    """Lists up to 30 open issues on a GitHub repository.

    Args:
        repo: Repository as `owner/name`, for example `google/adk-python`.

    Returns:
        `{"status": "success", "repo": ..., "issues": [{"number", "title", "labels"}]}`,
        or `status` "error" with an `error_message`.
    """
    try:
        # Scan a bounded window (one API page of 100) so a PR-heavy repo
        # cannot trigger unbounded paging. The issues API also returns pull
        # requests; skip them, and cap the result to keep the context small.
        issues = _client().get_repo(repo).get_issues(state="open")
        rows = [
            {
                "number": issue.number,
                "title": issue.title,
                "labels": [label.name for label in issue.labels],
            }
            for issue in issues[:100]
            if issue.pull_request is None
        ][:30]
    except Exception as exc:  # noqa: BLE001  (surface any API failure to the model)
        return {"status": "error", "error_message": str(exc)}
    return {"status": "success", "repo": repo, "issues": rows}


def get_issue(repo: str, number: int) -> dict:
    """Fetches the full body, state, and labels of one issue.

    Args:
        repo: Repository as `owner/name`.
        number: Issue number.

    Returns:
        `status` "success" with an `issue` dict, or `status` "error".
    """
    try:
        issue = _client().get_repo(repo).get_issue(number)
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error_message": str(exc)}
    return {
        "status": "success",
        "issue": {
            "number": issue.number,
            "title": issue.title,
            "body": issue.body or "",
            "state": issue.state,
            "labels": [label.name for label in issue.labels],
            "url": issue.html_url,
        },
    }


def add_label(repo: str, number: int, label: str) -> dict:
    """Adds a label to an issue. This is a write and requires confirmation.

    Args:
        repo: Repository as `owner/name`.
        number: Issue number.
        label: The label to add. GitHub creates it if it does not exist.

    Returns:
        `status` "success" with the label added, or `status` "error".
    """
    try:
        issue = _client().get_repo(repo).get_issue(number)
        issue.add_to_labels(label)
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error_message": str(exc)}
    return {"status": "success", "repo": repo, "number": number, "label_added": label}


def comment_on_issue(repo: str, number: int, text: str) -> dict:
    """Posts a comment on an issue. This is a write and requires confirmation.

    Args:
        repo: Repository as `owner/name`.
        number: Issue number.
        text: The comment body. Markdown is supported.

    Returns:
        `status` "success" with `comment_id` and `url`, or `status` "error".
    """
    try:
        comment = _client().get_repo(repo).get_issue(number).create_comment(text)
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error_message": str(exc)}
    return {
        "status": "success",
        "comment_id": comment.id,
        "url": comment.html_url,
    }


root_agent = LlmAgent(
    name="github_triage_agent",
    model="gemini-3.5-flash",
    description="Triages open GitHub issues, proposing labels and comments for human approval.",
    instruction=(
        "You triage GitHub issues. When asked to triage a repo:\n"
        "1. Call list_open_issues to see what is open.\n"
        "2. For each issue that looks unlabelled or mislabelled, call get_issue to read it.\n"
        "3. Propose labels (bug, enhancement, question, docs, and so on) via add_label.\n"
        "4. Where helpful, draft a clarifying comment via comment_on_issue.\n"
        "Write tools require human confirmation. Before each write, tell the user what "
        "you intend to do so they have context when the approval prompt appears.\n"
        "Always cite issue numbers when summarizing."
    ),
    tools=[
        list_open_issues,
        get_issue,
        FunctionTool(func=add_label, require_confirmation=True),
        FunctionTool(func=comment_on_issue, require_confirmation=True),
    ],
)
