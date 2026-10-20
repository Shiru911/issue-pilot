import pytest
from datetime import datetime, timezone
from issue_pilot.models import Issue, TriageReport


def test_issue_from_github_api():
    raw_data = {
        "id": 999123,
        "number": 42,
        "title": "Fix memory leak in parser worker",
        "html_url": "https://github.com/cool-org/super-lib/issues/42",
        "labels": [{"name": "bug"}, {"name": "good first issue"}],
        "state": "open",
        "created_at": "2026-01-10T10:00:00Z",
        "updated_at": "2026-01-12T14:30:00Z",
        "comments": 2,
        "assignees": [],
        "body": "There is an issue where memory builds up when parsing large JSON files.",
    }

    issue = Issue.from_github_api(raw_data)
    assert issue.id == 999123
    assert issue.number == 42
    assert issue.repo_name == "cool-org/super-lib"
    assert issue.labels == ["bug", "good first issue"]
    assert issue.assignees_count == 0
    assert issue.comments_count == 2
    assert not issue.is_pull_request
