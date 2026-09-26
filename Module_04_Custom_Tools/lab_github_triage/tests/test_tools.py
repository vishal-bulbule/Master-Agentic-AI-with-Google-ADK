# Author: Vishal Bulbule
# Date: 2026-09-22

"""Tool tests for the triage agent against a fake GitHub: no token, no model.

`Github` in `agent.agent` is replaced with a small in-memory fake holding
three issues, then each tool function is called directly. This checks the
tool wiring and return shapes. Confirmation gating happens in the runner, so
these direct calls bypass it; `test_writes_require_confirmation` checks the
wiring instead.

Run from the lab folder:
    pytest tests
"""

from types import SimpleNamespace

import pytest
from google.adk.tools import FunctionTool

from agent import agent as triage


class _FakeIssue:
    def __init__(self, number: int, title: str, body: str = "", labels=()):
        self.number = number
        self.title = title
        self.body = body
        self.state = "open"
        self.pull_request = None
        self.labels = [SimpleNamespace(name=name) for name in labels]
        self.html_url = f"https://github.com/demo/repo/issues/{number}"
        self.comments: list[str] = []

    def add_to_labels(self, label: str) -> None:
        self.labels.append(SimpleNamespace(name=label))

    def create_comment(self, text: str) -> SimpleNamespace:
        self.comments.append(text)
        comment_id = 1000 + len(self.comments)
        return SimpleNamespace(
            id=comment_id,
            html_url=f"{self.html_url}#issuecomment-{comment_id}",
        )


class _FakeRepo:
    def __init__(self) -> None:
        pull_request = _FakeIssue(4, "Fix typo", "PR body")
        pull_request.pull_request = object()
        self.issues = {
            1: _FakeIssue(1, "Crash on startup when GOOGLE_API_KEY missing",
                          "Seeing a stack trace on first run."),
            2: _FakeIssue(2, "Add docs for OpenAPI tool",
                          "Would love an example using OpenAPIToolset."),
            3: _FakeIssue(3, "Typo in README", "There's a typo in line 14.",
                          labels=["docs"]),
            # The issues API also returns pull requests; the tool skips them.
            4: pull_request,
        }

    def get_issues(self, state: str = "open"):
        return list(self.issues.values())

    def get_issue(self, number: int) -> _FakeIssue:
        if number not in self.issues:
            raise KeyError(f"issue {number} not found")
        return self.issues[number]


@pytest.fixture
def repo(monkeypatch) -> _FakeRepo:
    """Points the tools at one shared fake repo and sets a dummy token."""
    fake_repo = _FakeRepo()
    fake_github = SimpleNamespace(get_repo=lambda name: fake_repo)
    monkeypatch.setenv("GITHUB_PERSONAL_ACCESS_TOKEN", "fake-token")
    monkeypatch.setattr(triage, "Github", lambda *args, **kwargs: fake_github)
    return fake_repo


def test_list_open_issues_skips_pull_requests(repo):
    result = triage.list_open_issues("demo/repo")
    assert result["status"] == "success"
    assert [row["number"] for row in result["issues"]] == [1, 2, 3]
    assert result["issues"][2]["labels"] == ["docs"]


def test_get_issue(repo):
    result = triage.get_issue("demo/repo", 1)
    assert result["status"] == "success"
    assert result["issue"]["title"].startswith("Crash on startup")
    assert result["issue"]["url"].endswith("/issues/1")


def test_get_issue_unknown_number_returns_error(repo):
    result = triage.get_issue("demo/repo", 99)
    assert result["status"] == "error"
    assert "99" in result["error_message"]


def test_add_label(repo):
    result = triage.add_label("demo/repo", 1, "bug")
    assert result == {
        "status": "success", "repo": "demo/repo", "number": 1, "label_added": "bug",
    }
    assert "bug" in [label.name for label in repo.issues[1].labels]


def test_comment_on_issue(repo):
    result = triage.comment_on_issue("demo/repo", 2, "Thanks! Working on docs.")
    assert result["status"] == "success"
    assert result["url"].endswith(f"#issuecomment-{result['comment_id']}")
    assert repo.issues[2].comments == ["Thanks! Working on docs."]


def test_missing_token_returns_error(monkeypatch):
    monkeypatch.delenv("GITHUB_PERSONAL_ACCESS_TOKEN", raising=False)
    result = triage.list_open_issues("demo/repo")
    assert result["status"] == "error"
    assert "GITHUB_PERSONAL_ACCESS_TOKEN is not set" in result["error_message"]


def test_writes_require_confirmation():
    # The reads are plain functions; the writes are FunctionTool objects with
    # require_confirmation=True. ADK has no public getter for the flag.
    gated = {
        tool.name: tool._require_confirmation
        for tool in triage.root_agent.tools
        if isinstance(tool, FunctionTool)
    }
    assert gated == {"add_label": True, "comment_on_issue": True}
