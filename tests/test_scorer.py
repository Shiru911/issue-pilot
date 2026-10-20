import pytest
from datetime import datetime, timezone, timedelta
from issue_pilot.models import Issue
from issue_pilot.scorer import score_issue


def create_dummy_issue(**kwargs) -> Issue:
    defaults = {
        "id": 1,
        "number": 10,
        "title": "Fix typo in documentation",
        "html_url": "https://github.com/foo/bar/issues/10",
        "repo_name": "foo/bar",
        "labels": [],
        "state": "open",
        "created_at": datetime.now(timezone.utc) - timedelta(days=5),
        "updated_at": datetime.now(timezone.utc) - timedelta(days=2),
        "comments_count": 1,
        "assignees_count": 0,
        "body": "Here is a detailed explanation of the issue with reproduction steps and ```python code example```.",
        "is_pull_request": False,
    }
    defaults.update(kwargs)
    return Issue(**defaults)


def test_scorer_pull_request_skipped():
    issue = create_dummy_issue(is_pull_request=True)
    score, reasons = score_issue(issue)
    assert score == 0
    assert "Pull Request" in reasons[0]


def test_scorer_high_priority_labels():
    issue = create_dummy_issue(labels=["good first issue", "bug"])
    score, reasons = score_issue(issue)
    assert score >= 75
    assert any("good first issue" in r for r in reasons)


def test_scorer_penalizes_assigned_issues():
    unassigned = create_dummy_issue(assignees_count=0)
    assigned = create_dummy_issue(assignees_count=1)

    score_unassigned, _ = score_issue(unassigned)
    score_assigned, _ = score_issue(assigned)

    assert score_unassigned > score_assigned
    assert score_unassigned - score_assigned >= 40  # +20 bonus vs -30 penalty


def test_scorer_penalizes_wontfix_or_duplicate():
    issue = create_dummy_issue(labels=["wontfix", "duplicate"])
    score, reasons = score_issue(issue)
    assert score < 30
    assert any("wontfix" in r for r in reasons)
