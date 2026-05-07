"""
makemoney.gobizit.ai — Daily Journal Generator
Monitors sources and generates both Danny Owner Reviews and Money Making AI action logs.

Sources monitored:
  - Nio Learning Log (Obsidian)
  - git commits (web-makemoney + pka.db repo)
  - pka.db task completions (scope=business/make-money)
  - Coord Log new entries

Usage:
  python api/generate_journal.py --what danny   (generate Danny Owner Review template)
  python api/generate_journal.py --what ai       (generate Money Making AI daily log)
  python api/generate_journal.py --what both
  python api/generate_journal.py --date 2026-05-07
"""

import argparse
import sqlite3
import subprocess
import json
from datetime import datetime, date
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent.parent
OBSIDIAN = Path("C:/Users/dansk/Claude/Obsidian@Claude")
PKA_DB = Path("C:/Users/dansk/Claude/@team-ai.biz/data/pka.db")
NIO_LOG = OBSIDIAN / "AI Team" / "Nio Learning Log.md"
COORD_LOG = OBSIDIAN / "Architecture" / "Claude Setup" / "Nio-CEO Coordination Log.md"
OWNER_REVIEWS_DIR = OBSIDIAN / "Make Money" / "Daily Owner Reviews"
AI_ACTIONS_DIR = OBSIDIAN / "Make Money" / "Money Making AI Daily Actions"
JOURNALS_WEB_DIR = BASE_DIR / "journals"


# ── Data fetchers ─────────────────────────────────────────────────────────────

def get_completed_tasks(for_date: str) -> list:
    """Fetch tasks completed today from pka.db scope=business/make-money."""
    if not PKA_DB.exists():
        return []
    try:
        conn = sqlite3.connect(str(PKA_DB))
        rows = conn.execute(
            """SELECT title, description, assigned_to, updated_at
               FROM tasks
               WHERE scope='business/make-money'
               AND status='done'
               AND date(updated_at) = ?
               ORDER BY updated_at DESC""",
            (for_date,)
        ).fetchall()
        conn.close()
        return [{"title": r[0], "desc": r[1], "agent": r[2], "at": r[3]} for r in rows]
    except Exception as e:
        return [{"error": str(e)}]


def get_recent_experiments(for_date: str) -> list:
    """Fetch experiment knowledge rows from pka.db."""
    if not PKA_DB.exists():
        return []
    try:
        conn = sqlite3.connect(str(PKA_DB))
        rows = conn.execute(
            """SELECT title, content, tags, created_at
               FROM knowledge
               WHERE scope='business/make-money'
               AND (tags LIKE '%experiment%' OR tags LIKE '%make-money%')
               AND date(created_at) = ?
               ORDER BY created_at DESC""",
            (for_date,)
        ).fetchall()
        conn.close()
        return [{"title": r[0], "content": r[1], "tags": r[2], "at": r[3]} for r in rows]
    except Exception as e:
        return []


def get_git_commits(for_date: str) -> list:
    """Get today's git commits from web-makemoney repo."""
    try:
        result = subprocess.run(
            ["git", "log", f"--after={for_date} 00:00", f"--before={for_date} 23:59",
             "--pretty=format:%h %s", "--all"],
            cwd=str(BASE_DIR),
            capture_output=True, text=True, timeout=10
        )
        lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
        return lines
    except Exception:
        return []


def get_coord_log_entries(for_date: str) -> list:
    """Read today's Coord Log entries mentioning Money Making AI."""
    if not COORD_LOG.exists():
        return []
    try:
        lines = COORD_LOG.read_text(encoding="utf-8").splitlines()
        today_entries = [
            l for l in lines
            if for_date in l and ("Money Making AI" in l or "make-money" in l.lower())
        ]
        return today_entries
    except Exception:
        return []


def get_subscriber_count() -> int:
    db_path = BASE_DIR / "api" / "subscribers.db"
    if not db_path.exists():
        return 0
    try:
        conn = sqlite3.connect(str(db_path))
        row = conn.execute("SELECT COUNT(*) FROM subscribers WHERE active=1").fetchone()
        conn.close()
        return row[0]
    except Exception:
        return 0


# ── Template builders ─────────────────────────────────────────────────────────

def build_danny_review_template(for_date: str, tasks: list, experiments: list, commits: list) -> str:
    dt = datetime.strptime(for_date, "%Y-%m-%d")
    formatted = dt.strftime("%B %d, %Y").replace(" 0", " ") if hasattr(dt, "strftime") else for_date

    task_lines = "\n".join([f"- {t['title']}" for t in tasks]) if tasks else "- (no completed tasks today)"
    exp_lines = "\n".join([f"- {e['title']}" for e in experiments]) if experiments else "- (no experiments logged today)"
    commit_lines = "\n".join([f"- {c}" for c in commits]) if commits else "- (no commits today)"

    return f"""---
title: "Daily Owner Review — {formatted}"
date: {for_date}
author: Danny Nissani
tags: [make-money, build-in-public, daily-owner-review]
scope: business/make-money
---

# Daily Owner Review — {formatted}

*What the AI system did today, what I noticed, and what it means.*

---

## What Shipped Today

{task_lines}

## Experiments Active

{exp_lines}

## Commits

{commit_lines}

---

## What I Noticed

[Danny: write 2-3 sentences about what surprised you, what the AI got right or wrong, what changed your thinking today]

## The One Thing That Mattered

[Danny: one sentence — the most important thing that happened today in the Make Money project]

## Tomorrow's Focus

[Danny: what is the single highest-leverage action for tomorrow]

---

## Free Value for Readers

[Danny: one concrete tip, observation, or data point readers can use today]

---

*Follow the build: makemoney.gobizit.ai*
"""


def build_ai_actions_log(for_date: str, tasks: list, experiments: list, commits: list, coord_entries: list, subscriber_count: int) -> str:
    dt = datetime.strptime(for_date, "%Y-%m-%d")
    formatted = dt.strftime("%B %d, %Y").replace(" 0", " ") if hasattr(dt, "strftime") else for_date

    task_block = ""
    for t in tasks:
        task_block += f"- **{t['title']}** [{t.get('agent', 'unknown')}] — {(t.get('desc') or '')[:100]}\n"
    if not task_block:
        task_block = "- No tasks completed with make-money scope today.\n"

    exp_block = ""
    for e in experiments:
        exp_block += f"- **{e['title']}** — {(e.get('content') or '')[:150]}\n"
    if not exp_block:
        exp_block = "- No new experiments logged today.\n"

    coord_block = ""
    for entry in coord_entries:
        coord_block += f"- {entry.strip()}\n"
    if not coord_block:
        coord_block = "- No make-money coord log entries today.\n"

    commit_block = "\n".join([f"- `{c}`" for c in commits]) if commits else "- No commits today."

    return f"""---
date: {for_date}
agent: Money Making AI
type: daily-actions-log
scope: business/make-money
tags: [make-money, ai-actions, daily-log, build-in-public]
---

# Money Making AI — Daily Actions Log — {formatted}

**Subscribers:** {subscriber_count}
**Experiments active:** see pka.db
**Budget MTD:** [update from Stripe/spend tracker]

---

## Tasks Completed

{task_block}

## Experiments Logged

{exp_block}

## Coord Log Activity

{coord_block}

## Commits Shipped

{commit_block}

---

## Decisions Made Today

[Auto-populated from pka.db knowledge rows with tags=decision,make-money — fill in manually if empty]

## Metrics Check

- Revenue MTD: [check Stripe]
- Visitors today: [check Plausible]
- Conversions: [check Stripe/Gumroad]
- Email subscribers: {subscriber_count}

## Blockers / Escalations

[Any items that need CEO or Danny input — tag 🟡 @@@]

---

*Generated by Money Making AI heartbeat. Scope: business/make-money.*
"""


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Daily journal generator for makemoney.gobizit.ai")
    parser.add_argument("--what", choices=["danny", "ai", "both"], default="both",
                        help="Which journal to generate")
    parser.add_argument("--date", default=date.today().isoformat(),
                        help="Date to generate for (YYYY-MM-DD), default=today")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print output instead of writing files")
    args = parser.parse_args()

    for_date = args.date
    print(f"Generating journals for: {for_date}")

    tasks = get_completed_tasks(for_date)
    experiments = get_recent_experiments(for_date)
    commits = get_git_commits(for_date)
    coord = get_coord_log_entries(for_date)
    sub_count = get_subscriber_count()

    print(f"  Tasks: {len(tasks)} | Experiments: {len(experiments)} | Commits: {len(commits)} | Subscribers: {sub_count}")

    import sys
    # Ensure stdout handles UTF-8 on Windows
    if sys.stdout.encoding != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    if args.what in ("danny", "both"):
        content = build_danny_review_template(for_date, tasks, experiments, commits)
        out_path = OWNER_REVIEWS_DIR / f"{for_date}-owner-review.md"
        if args.dry_run:
            print("\n--- DANNY OWNER REVIEW ---")
            print(content)
        else:
            OWNER_REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
            out_path.write_text(content, encoding="utf-8")
            print(f"  Danny review: {out_path}")

    if args.what in ("ai", "both"):
        content = build_ai_actions_log(for_date, tasks, experiments, commits, coord, sub_count)
        out_path = AI_ACTIONS_DIR / f"{for_date}-ai-actions.md"
        if args.dry_run:
            print("\n--- AI ACTIONS LOG ---")
            print(content)
        else:
            AI_ACTIONS_DIR.mkdir(parents=True, exist_ok=True)
            out_path.write_text(content, encoding="utf-8")
            print(f"  AI actions log: {out_path}")

    print("Done.")


if __name__ == "__main__":
    main()
