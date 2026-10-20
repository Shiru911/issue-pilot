from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
import httpx

from issue_pilot.models import Issue, Repository
from issue_pilot.scorer import score_issue


class GitHubClient:
    """Privacy-conscious, zero-telemetry client for the GitHub REST API."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN") or None
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "IssuePilot-OSS-Client/0.1.0",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token.strip()}"

        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers=headers,
            timeout=20.0,
            follow_redirects=True,
        )

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_rate_limit(self) -> Dict[str, Any]:
        """Check current GitHub API rate limit status without exposing sensitive headers."""
        try:
            resp = self.client.get("/rate_limit")
            resp.raise_for_status()
            data = resp.json()
            core = data.get("resources", {}).get("core", {})
            search = data.get("resources", {}).get("search", {})
            return {
                "core_limit": core.get("limit", 0),
                "core_remaining": core.get("remaining", 0),
                "search_limit": search.get("limit", 0),
                "search_remaining": search.get("remaining", 0),
                "authenticated": bool(self.token),
            }
        except httpx.HTTPError as e:
            return {
                "error": str(e),
                "authenticated": bool(self.token),
            }

    def search_contribution_issues(
        self,
        language: Optional[str] = "python",
        labels: Optional[List[str]] = None,
        min_stars: int = 100,
        max_stars: Optional[int] = None,
        keyword: Optional[str] = None,
        limit: int = 15,
    ) -> List[Issue]:
        """Searches GitHub for high-quality open contribution opportunities."""
        labels = labels or ["good first issue", "help wanted"]

        # Build search query
        query_parts = ["is:issue", "is:open", "no:assignee"]
        if language:
            query_parts.append(f"language:{language}")

        # Stars range
        if max_stars:
            query_parts.append(f"stars:{min_stars}..{max_stars}")
        elif min_stars:
            query_parts.append(f"stars:>={min_stars}")

        # Labels query: label:"good first issue",label:"help wanted"
        label_queries = [f'label:"{l}"' for l in labels]
        if label_queries:
            query_parts.append(f"({' OR '.join(label_queries)})")

        if keyword:
            query_parts.append(keyword)

        full_query = " ".join(query_parts)

        params = {
            "q": full_query,
            "sort": "updated",
            "order": "desc",
            "per_page": min(limit, 50),
        }

        resp = self.client.get("/search/issues", params=params)
        resp.raise_for_status()
        data = resp.json()

        items = data.get("items", [])
        issues: List[Issue] = []

        for item in items:
            # Skip PRs that might sneak in
            if "pull_request" in item:
                continue
            issue = Issue.from_github_api(item)
            score, reasons = score_issue(issue)
            issue.score = score
            issue.score_reasons = reasons
            issues.append(issue)

        # Sort by opportunity score descending
        issues.sort(key=lambda x: x.score, reverse=True)
        return issues[:limit]

    def get_issue(self, repo_name: str, issue_number: int) -> Issue:
        """Retrieves and scores a single issue by repo full_name and issue number."""
        resp = self.client.get(f"/repos/{repo_name}/issues/{issue_number}")
        resp.raise_for_status()
        data = resp.json()
        issue = Issue.from_github_api(data)
        score, reasons = score_issue(issue)
        issue.score = score
        issue.score_reasons = reasons
        return issue
