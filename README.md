# IssuePilot

[![CI](https://github.com/your-username/issue-pilot/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/issue-pilot/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Privacy: Zero-Telemetry](https://img.shields.io/badge/Privacy-100%25_Local_%26_Zero_Telemetry-green.svg)](#privacy--security-first)

**IssuePilot** is a privacy-first, developer-friendly CLI engine designed to discover, evaluate, and triage high-signal open-source contribution opportunities across GitHub.

---

## Highlights

* **Privacy & Security First:** Zero telemetry, no remote analytics, no data tracking. Runs 100% locally on your machine.
* **Smart Opportunity Scoring:** Evaluates open issues from 0 to 100 based on freshness, label relevance (`good first issue`, `help wanted`, `bug`), assignee availability, and discussion clarity.
* **Automated Triage & PR Generator:** Generates reproduction checklists, step-by-step action plans, testing strategies, and clean Conventional Commit PR drafts ready for submission.
* **Anonymous or Token-Powered:** Works out-of-the-box anonymously using GitHub's public API, or optionally with a personal access token for higher limits.
* **Universal Terminal UI:** Rendered with `rich` tables and colorized progress indicators compatible with all platforms.

---

## Quick Start

### 1. Installation

Clone and install with pip:

```bash
git clone https://github.com/your-username/issue-pilot.git
cd issue-pilot
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -e .
```

### 2. Check System Health & Privacy Safeguards

```bash
issue-pilot doctor
```

### 3. Search for Contribution Opportunities

Find Python issues in repositories with at least 500 stars:

```bash
issue-pilot search --lang python --min-stars 500 --limit 10
```

Find TypeScript opportunities:

```bash
issue-pilot search --lang typescript --min-stars 1000 --limit 5
```

### 4. Triage an Issue and Generate PR Draft

Pass a full URL or shorthand (`owner/repo#number`):

```bash
issue-pilot triage https://github.com/pallets/flask/issues/5000
```

Export the triage plan directly to Markdown:

```bash
issue-pilot triage owner/repo#123 --export triage_plan.md
```

---

## Opportunity Scoring Rubric

IssuePilot rates issues using a weighted 100-point rubric:

| Criteria | Impact | Reason |
| :--- | :---: | :--- |
| **Labels** (`good first issue`, `help wanted`) | `+15 to +25` | Explicit invitation from maintainers |
| **No Assignee** | `+20` | Free for community pickup; avoids duplicate work |
| **Active Maintainership** (updated ≤ 14 days) | `+10` | Responsive repository |
| **Rich Description / Code Samples** | `+10` | Easy to understand and reproduce |
| **Existing Assignee** | `-30` | Work is already underway by another contributor |
| **Stale (inactive > 180 days)** | `-20` | High risk of being ignored or abandoned |
| **Negative Labels** (`wontfix`, `duplicate`, `blocked`) | `-30 to -50` | Unviable for contribution |

---

## Configuration

Copy `.env.example` to `.env` if you wish to use a personal token:

```env
GITHUB_TOKEN=your_token_here
```

*Note: `.env` is strictly ignored by `.gitignore` to prevent accidental credential leakage.*

---

## Running Tests

Run the comprehensive test suite with `pytest`:

```bash
pytest
```

---

## License

This project is licensed under the [MIT License](LICENSE).
