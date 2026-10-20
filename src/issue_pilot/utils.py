from __future__ import annotations

import re
import os
from typing import Optional


def sanitize_output(text: str) -> str:
    """Removes sensitive local system paths, user names, or tokens from console/file outputs."""
    if not text:
        return ""
    # Strip potential token strings (e.g. ghp_xxxx, github_pat_xxxx)
    text = re.sub(r"(ghp_[a-zA-Z0-9]{30,45}|github_pat_[a-zA-Z0-9_]{50,90})", "[REDACTED_TOKEN]", text)
    # Strip local Windows/Unix user paths if any
    text = re.sub(r"[A-Za-z]:\\[Users|home]+[\\\/][a-zA-Z0-9_\-\.]+", "[LOCAL_PATH]", text)
    return text


def parse_issue_url(url_or_shorthand: str) -> tuple[Optional[str], Optional[int]]:
    """Extracts repo_name and issue_number from URLs or shorthand 'owner/repo#123'."""
    url_or_shorthand = url_or_shorthand.strip()
    
    # Format: https://github.com/owner/repo/issues/123
    web_match = re.search(r"github\.com/([^/]+/[^/]+)/issues/(\d+)", url_or_shorthand)
    if web_match:
        return web_match.group(1), int(web_match.group(2))
    
    # Format: owner/repo#123 or owner/repo/123
    shorthand_match = re.search(r"^([^/#]+/[^/#]+)[#/](\d+)$", url_or_shorthand)
    if shorthand_match:
        return shorthand_match.group(1), int(shorthand_match.group(2))

    return None, None
