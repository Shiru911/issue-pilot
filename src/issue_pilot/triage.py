from __future__ import annotations

import re
from typing import List
from issue_pilot.models import Issue, TriageReport


def generate_triage_plan(issue: Issue) -> TriageReport:
    """Generates an actionable, privacy-safe triage plan and PR draft for a given issue."""
    body = issue.body or ""
    
    # Extract code blocks if any
    code_blocks = re.findall(r"```(?:[a-zA-Z0-9_\-]+)?\s*(.*?)\s*```", body, flags=re.DOTALL)
    
    # Identify key traits
    key_points: List[str] = []
    if "bug" in [l.lower() for l in issue.labels] or "fix" in issue.title.lower():
        key_points.append("Identified as a Bug/Fix issue.")
    if "doc" in [l.lower() for l in issue.labels] or "doc" in issue.title.lower():
        key_points.append("Identified as a Documentation enhancement.")
    if code_blocks:
        key_points.append(f"Contains {len(code_blocks)} code/trace snippet(s) in description.")
    if not key_points:
        key_points.append("General feature or enhancement request.")

    # Suggested development steps
    suggested_steps = [
        f"1. Clone repository `{issue.repo_name}` and create a local feature branch: `git checkout -b fix/issue-{issue.number}`.",
        "2. Reproduce the scenario locally using minimal test cases before touching production code.",
        "3. Implement the minimal necessary change to address the issue without regressing other features.",
        "4. Run existing test suites and linters to confirm zero side effects.",
        "5. Commit with an atomic, conventional commit message.",
    ]

    # Test Strategy
    test_strategy = [
        "Create an explicit unit test that fails without your fix and passes with your fix.",
        "Verify edge cases: null/empty inputs, unexpected types, and boundary values.",
        "Run the repository's full test suite (e.g., pytest, npm test, cargo test).",
    ]

    # Clean conventional PR title
    # Format: fix(scope): title or feat(scope): title
    is_bug = any("bug" in l.lower() for l in issue.labels) or "error" in issue.title.lower()
    prefix = "fix" if is_bug else "feat"
    # Clean up issue title
    clean_title = re.sub(r"^(fix|bug|feature|feat|docs?):?\s*", "", issue.title, flags=re.I).strip()
    pr_title_template = f"{prefix}: {clean_title}"

    # Structured PR Body Template
    pr_body_template = f"""## Description
Resolves #{issue.number}

{clean_title}

## Changes Made
- Identified root cause in relevant module.
- Applied clean, minimal fix addressing the issue.
- Added comprehensive unit tests covering this scenario.

## Checklist
- [x] Code conforms to project style guides and passes linters.
- [x] Unit tests added and passing locally.
- [x] Verified zero side effects on existing workflows.
"""

    # Summarize problem in a concise sentence
    first_paragraph = body.strip().split("\n\n")[0] if body else issue.title
    problem_summary = first_paragraph[:300] + ("..." if len(first_paragraph) > 300 else "")

    return TriageReport(
        issue_number=issue.number,
        repo_name=issue.repo_name,
        title=issue.title,
        html_url=issue.html_url,
        problem_summary=problem_summary,
        key_points=key_points,
        suggested_steps=suggested_steps,
        test_strategy=test_strategy,
        pr_title_template=pr_title_template,
        pr_body_template=pr_body_template,
    )
