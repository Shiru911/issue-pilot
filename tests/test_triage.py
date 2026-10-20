import pytest
from datetime import datetime, timezone
from issue_pilot.models import Issue
from issue_pilot.triage import generate_triage_plan


def test_generate_triage_plan():
    issue = Issue(
        id=123,
        number=88,
        title="fix: async client timeout on Windows",
        html_url="https://github.com/fast/network/issues/88",
        repo_name="fast/network",
        labels=["bug", "help wanted"],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        comments_count=1,
        assignees_count=0,
        body="Steps to reproduce:\n```python\nimport network\nnetwork.fetch()\n```\nIt fails with TimeoutError.",
    )

    report = generate_triage_plan(issue)
    assert report.issue_number == 88
    assert report.repo_name == "fast/network"
    assert "Resolves #88" in report.pr_body_template
    assert any("bug" in p.lower() for p in report.key_points)
    assert len(report.suggested_steps) >= 3
    assert len(report.test_strategy) >= 2
