import pytest
from issue_pilot.utils import sanitize_output, parse_issue_url


def test_sanitize_output_tokens():
    sensitive_token = "ghp_1234567890abcdefghijklmnopqrstuvwxyzAB"
    raw_text = f"Failed with authentication token {sensitive_token} in log"
    sanitized = sanitize_output(raw_text)
    assert "[REDACTED_TOKEN]" in sanitized
    assert sensitive_token not in sanitized


def test_parse_issue_url():
    # Full URL
    repo, num = parse_issue_url("https://github.com/astral-sh/uv/issues/1234")
    assert repo == "astral-sh/uv"
    assert num == 1234

    # Shorthand with #
    repo, num = parse_issue_url("tiangolo/fastapi#5678")
    assert repo == "tiangolo/fastapi"
    assert num == 5678

    # Invalid input
    repo, num = parse_issue_url("not-a-valid-issue")
    assert repo is None
    assert num is None
