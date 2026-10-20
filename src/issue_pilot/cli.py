from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from issue_pilot import __version__
from issue_pilot.client import GitHubClient
from issue_pilot.scorer import score_issue
from issue_pilot.triage import generate_triage_plan
from issue_pilot.utils import parse_issue_url, sanitize_output

load_dotenv()
console = Console(force_terminal=True, legacy_windows=False) if sys.platform == "win32" else Console()


def render_score_badge(score: int) -> str:
    if score >= 80:
        return f"[bold green]{score}/100 [Top][/bold green]"
    elif score >= 60:
        return f"[bold yellow]{score}/100[/bold yellow]"
    else:
        return f"[bold red]{score}/100[/bold red]"


def handle_search(args: argparse.Namespace):
    console.print(f"[bold cyan][*] Searching GitHub for contribution opportunities...[/bold cyan]")
    
    with GitHubClient() as client:
        try:
            issues = client.search_contribution_issues(
                language=args.lang if args.lang != "all" else None,
                min_stars=args.min_stars,
                max_stars=args.max_stars,
                keyword=args.keyword,
                limit=args.limit,
            )
        except Exception as e:
            console.print(f"[bold red]Error fetching issues:[/bold red] {sanitize_output(str(e))}")
            sys.exit(1)

    if not issues:
        console.print("[yellow]No issues found matching your criteria. Try adjusting filters or language.[/yellow]")
        return

    if args.json:
        data = [i.model_dump(mode="json") for i in issues]
        print(json.dumps(data, indent=2))
        return

    table = Table(
        title=f"Top Contribution Opportunities ({len(issues)} found)",
        header_style="bold magenta",
        show_lines=True,
    )
    table.add_column("Score", justify="center", style="cyan", no_wrap=True)
    table.add_column("Repository & #", style="bold green")
    table.add_column("Title", style="white")
    table.add_column("Labels", style="dim")
    table.add_column("Comments", justify="center")
    table.add_column("Action / URL", style="blue")

    for issue in issues:
        labels_str = ", ".join(issue.labels[:3])
        if len(issue.labels) > 3:
            labels_str += f" (+{len(issue.labels) - 3})"

        table.add_row(
            render_score_badge(issue.score),
            f"{issue.repo_name}#{issue.number}",
            issue.title[:65] + ("..." if len(issue.title) > 65 else ""),
            labels_str,
            str(issue.comments_count),
            issue.html_url,
        )

    console.print(table)
    console.print("\n[dim]Tip: Run [bold]issue-pilot triage <URL>[/bold] to generate a full triage guide and PR template.[/dim]\n")


def handle_triage(args: argparse.Namespace):
    repo_name, issue_number = parse_issue_url(args.target)
    if not repo_name or not issue_number:
        console.print("[bold red]Invalid issue identifier.[/bold red] Use full URL (https://github.com/owner/repo/issues/123) or shorthand (owner/repo#123).")
        sys.exit(1)

    console.print(f"[bold cyan][*] Fetching and analyzing {repo_name}#{issue_number}...[/bold cyan]")

    with GitHubClient() as client:
        try:
            issue = client.get_issue(repo_name, issue_number)
        except Exception as e:
            console.print(f"[bold red]Failed to fetch issue:[/bold red] {sanitize_output(str(e))}")
            sys.exit(1)

    report = generate_triage_plan(issue)

    if args.export:
        out_path = Path(args.export)
        content = f"# Triage Plan: {report.repo_name}#{report.issue_number}\n\n"
        content += f"**Issue:** [{report.title}]({report.html_url})\n\n"
        content += f"## Problem Summary\n{report.problem_summary}\n\n"
        content += f"## Recommended Next Steps\n" + "\n".join(f"- {s}" for s in report.suggested_steps) + "\n\n"
        content += f"## Testing Strategy\n" + "\n".join(f"- {t}" for t in report.test_strategy) + "\n\n"
        content += f"## Ready-to-use PR Description\n\n```markdown\n{report.pr_body_template}\n```\n"
        out_path.write_text(content, encoding="utf-8")
        console.print(f"[bold green][OK] Triage report exported to:[/bold green] {out_path}")
        return

    # Render interactive terminal report
    console.print(Panel(
        f"[bold white]{report.title}[/bold white]\n"
        f"[dim]{report.html_url}[/dim]\n\n"
        f"Opportunity Score: {render_score_badge(issue.score)}\n"
        f"Score Breakdown: {', '.join(issue.score_reasons)}",
        title=f"Issue Triage: {report.repo_name}#{report.issue_number}",
        border_style="green",
    ))

    console.print(Panel("\n".join(f"- {p}" for p in report.key_points), title="Key Traits", border_style="cyan"))
    console.print(Panel("\n".join(f"- {s}" for s in report.suggested_steps), title="Suggested Action Plan", border_style="yellow"))
    console.print(Panel("\n".join(f"- {t}" for t in report.test_strategy), title="Testing Strategy", border_style="magenta"))

    console.print(Panel(
        f"[bold]PR Title Proposal:[/bold] {report.pr_title_template}\n\n"
        f"[bold]PR Body Markdown:[/bold]\n{report.pr_body_template}",
        title="Ready-to-use Pull Request Draft",
        border_style="blue",
    ))


def handle_doctor(args: argparse.Namespace):
    console.print(Panel(
        f"IssuePilot v{__version__}\n"
        f"Privacy Mode: [bold green]Active (Zero Telemetry, 100% Local)[/bold green]",
        title="IssuePilot Health & Diagnostics",
        border_style="cyan",
    ))

    with GitHubClient() as client:
        status = client.get_rate_limit()

    if "error" in status:
        console.print(f"[red]GitHub API Connection Error:[/red] {sanitize_output(status['error'])}")
    else:
        auth_badge = "[bold green]Authenticated (Token active)[/bold green]" if status["authenticated"] else "[bold yellow]Anonymous Public Access[/bold yellow]"
        table = Table(show_header=False, box=None)
        table.add_row("Authentication:", auth_badge)
        table.add_row("Core API Remaining:", f"{status['core_remaining']} / {status['core_limit']}")
        table.add_row("Search API Remaining:", f"{status['search_remaining']} / {status['search_limit']}")
        console.print(table)


def main():
    parser = argparse.ArgumentParser(
        prog="issue-pilot",
        description="Privacy-first AI-ready Open Source Issue Scout and Triage Engine.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Search command
    search_parser = subparsers.add_parser("search", help="Search open source issues ready for contributions.")
    search_parser.add_argument("--lang", default="python", help="Programming language filter (e.g. python, typescript, go, rust, or 'all'). Default: python")
    search_parser.add_argument("--min-stars", type=int, default=100, help="Minimum repository star count. Default: 100")
    search_parser.add_argument("--max-stars", type=int, default=None, help="Maximum repository star count.")
    search_parser.add_argument("--keyword", default=None, help="Additional keyword search filter.")
    search_parser.add_argument("--limit", type=int, default=10, help="Maximum number of issues to display. Default: 10")
    search_parser.add_argument("--json", action="store_true", help="Output results in JSON format.")
    search_parser.set_defaults(func=handle_search)

    # Triage command
    triage_parser = subparsers.add_parser("triage", help="Analyze an issue and generate an actionable triage plan & PR draft.")
    triage_parser.add_argument("target", help="Issue URL or shorthand identifier (e.g. owner/repo#123).")
    triage_parser.add_argument("--export", help="Export the triage report to a Markdown file.")
    triage_parser.set_defaults(func=handle_triage)

    # Doctor command
    doctor_parser = subparsers.add_parser("doctor", help="Check API rate limit status and privacy safeguards.")
    doctor_parser.set_defaults(func=handle_doctor)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
