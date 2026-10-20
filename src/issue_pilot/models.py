from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class IssueLabel(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    color: Optional[str] = None


class Repository(BaseModel):
    full_name: str
    html_url: str
    description: Optional[str] = None
    stars: int = 0
    forks: int = 0
    open_issues_count: int = 0
    language: Optional[str] = None
    updated_at: Optional[datetime] = None


class Issue(BaseModel):
    id: int
    number: int
    title: str
    html_url: str
    repo_name: str
    labels: List[str] = Field(default_factory=list)
    state: str = "open"
    created_at: datetime
    updated_at: datetime
    comments_count: int = 0
    assignees_count: int = 0
    body: Optional[str] = ""
    is_pull_request: bool = False
    score: int = 0
    score_reasons: List[str] = Field(default_factory=list)

    @classmethod
    def from_github_api(cls, data: Dict[str, Any]) -> Issue:
        labels = [l.get("name", "") for l in data.get("labels", []) if isinstance(l, dict)]
        html_url = data.get("html_url", "")
        # repo_name extracted from html_url: https://github.com/owner/repo/issues/123
        parts = html_url.split("/")
        repo_name = f"{parts[3]}/{parts[4]}" if len(parts) >= 5 else "unknown/unknown"

        return cls(
            id=data.get("id", 0),
            number=data.get("number", 0),
            title=data.get("title", ""),
            html_url=html_url,
            repo_name=repo_name,
            labels=labels,
            state=data.get("state", "open"),
            created_at=datetime.fromisoformat(data.get("created_at", "").replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data.get("updated_at", "").replace("Z", "+00:00")),
            comments_count=data.get("comments", 0),
            assignees_count=len(data.get("assignees", []) or []),
            body=data.get("body") or "",
            is_pull_request="pull_request" in data,
        )


class TriageReport(BaseModel):
    issue_number: int
    repo_name: str
    title: str
    html_url: str
    problem_summary: str
    key_points: List[str]
    suggested_steps: List[str]
    test_strategy: List[str]
    pr_title_template: str
    pr_body_template: str
