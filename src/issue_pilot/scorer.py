from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Tuple
from issue_pilot.models import Issue


HIGH_PRIORITY_LABELS = {
    "good first issue": 25,
    "good-first-issue": 25,
    "beginner friendly": 20,
    "beginner-friendly": 20,
    "easy": 15,
    "up-for-grabs": 20,
    "help wanted": 20,
    "help-wanted": 20,
    "contributions welcome": 20,
    "hacktoberfest": 10,
    "documentation": 15,
    "docs": 15,
    "bug": 10,
}

PENALTY_LABELS = {
    "wontfix": -50,
    "invalid": -50,
    "question": -10,
    "duplicate": -40,
    "blocked": -30,
    "needs discussion": -20,
}


def score_issue(issue: Issue) -> Tuple[int, List[str]]:
    """Calculates an Opportunity Score (0-100) for an open-source issue.
    
    Higher score means the issue is clearer, unassigned, actively maintained,
    and suitable for high-impact contribution.
    """
    if issue.is_pull_request:
        return 0, ["Skipped: Pull Request, not an Issue."]

    score = 40  # Base score
    reasons: List[str] = ["Base opportunity score: +40"]

    # 1. Label Analysis
    matched_labels = []
    for label in issue.labels:
        clean_label = label.lower().strip()
        if clean_label in HIGH_PRIORITY_LABELS:
            pts = HIGH_PRIORITY_LABELS[clean_label]
            score += pts
            matched_labels.append(f"'{label}' (+{pts})")
        if clean_label in PENALTY_LABELS:
            pts = PENALTY_LABELS[clean_label]
            score += pts
            reasons.append(f"Penalty label '{label}' ({pts})")

    if matched_labels:
        reasons.append(f"Contribution-friendly labels: {', '.join(matched_labels)}")

    # 2. Assignee Check
    if issue.assignees_count == 0:
        score += 20
        reasons.append("Unassigned issue (+20)")
    else:
        score -= 30
        reasons.append(f"Already assigned to {issue.assignees_count} user(s) (-30)")

    # 3. Description & Body Richness
    body_len = len(issue.body.strip()) if issue.body else 0
    if body_len > 250:
        score += 10
        reasons.append("Detailed issue description (+10)")
    elif body_len < 40:
        score -= 20
        reasons.append("Vague or very short description (-20)")

    if issue.body and ("```" in issue.body or "reproduce" in issue.body.lower() or "steps" in issue.body.lower()):
        score += 10
        reasons.append("Contains code blocks or reproduction steps (+10)")

    # 4. Activity & Recency
    now = datetime.now(timezone.utc)
    days_since_update = (now - issue.updated_at).days

    if days_since_update <= 14:
        score += 10
        reasons.append("Recently active within 14 days (+10)")
    elif days_since_update > 180:
        score -= 20
        reasons.append(f"Stale issue: inactive for {days_since_update} days (-20)")

    # 5. Comment Count (avoid endless bikeshed discussions)
    if 0 <= issue.comments_count <= 4:
        score += 5
        reasons.append("Clean discussion with few conflicting comments (+5)")
    elif issue.comments_count > 15:
        score -= 10
        reasons.append(f"High comment volume ({issue.comments_count}), potential dispute/complexity (-10)")

    # Bound score between 0 and 100
    final_score = max(0, min(100, score))
    return final_score, reasons
