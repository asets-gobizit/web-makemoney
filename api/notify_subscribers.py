"""
makemoney.gobizit.ai — Daily Notification Sender
Sends new journal entries to Zoho Campaigns list as an email campaign.

Usage:
  python api/notify_subscribers.py --entry journals/2026-05-07-how-ai-lies.html
  python api/notify_subscribers.py --list   (list all subscribers)

Scheduled via Windows Task Scheduler — runs daily after a new entry is published.
"""

import argparse
import json
import os
import sys
import sqlite3
import requests
import logging
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "api" / "subscribers.db"
LOG_PATH = BASE_DIR / "api" / "notify.log"
ZOHO_ACCESS_TOKEN_FILE = Path.home() / ".claude" / "secrets" / "make-money" / "zoho-campaigns-token.json"
ZOHO_REFRESH_TOKEN = "1000.ec9549a6848bb3423d152b0994aad02d.ff93e2f44010d6d7163a1cc50af394fc"
ZOHO_LIST_KEY = "3z056b843baba6f7dd3527f4c02bf8f6a72196a9cfa86178cbfe4204ed4b0ebeba"
ZOHO_CLIENT_ID_FILE = Path.home() / ".claude" / "secrets" / "make-money" / ".env"

SITE_BASE = "https://makemoney.gobizit.ai"
FROM_EMAIL = "danny@gobizit.ai"
FROM_NAME = "Danny's AI Virtual Assistant"

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


def load_zoho_client_creds():
    client_id = os.environ.get("ZOHO_CLIENT_ID", "")
    client_secret = os.environ.get("ZOHO_CLIENT_SECRET", "")
    if client_id and client_secret:
        return client_id, client_secret
    if ZOHO_CLIENT_ID_FILE.exists():
        for line in ZOHO_CLIENT_ID_FILE.read_text().splitlines():
            if line.startswith("ZOHO_CLIENT_ID="):
                client_id = line.split("=", 1)[1].strip()
            elif line.startswith("ZOHO_CLIENT_SECRET="):
                client_secret = line.split("=", 1)[1].strip()
    return client_id, client_secret


def get_zoho_token() -> str:
    if ZOHO_ACCESS_TOKEN_FILE.exists():
        data = json.loads(ZOHO_ACCESS_TOKEN_FILE.read_text())
        saved_at = data.get("saved_at", "")
        if saved_at:
            age = (datetime.now() - datetime.fromisoformat(saved_at)).total_seconds()
            if age < 3500:
                return data["access_token"]
    client_id, client_secret = load_zoho_client_creds()
    resp = requests.post(
        "https://accounts.zoho.eu/oauth/v2/token",
        data={
            "refresh_token": ZOHO_REFRESH_TOKEN,
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token"
        },
        timeout=10
    )
    data = resp.json()
    if "access_token" not in data:
        raise RuntimeError(f"Token refresh failed: {data}")
    token_data = {"access_token": data["access_token"], "saved_at": datetime.now().isoformat()}
    ZOHO_ACCESS_TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    ZOHO_ACCESS_TOKEN_FILE.write_text(json.dumps(token_data))
    return data["access_token"]


def create_campaign(token: str, title: str, subject: str, html_content: str) -> str:
    """Create a Zoho Campaigns campaign and return campaign key."""
    resp = requests.post(
        "https://campaigns.zoho.com/api/v1.1/json/createEmailCampaign",
        headers={"Authorization": f"Zoho-oauthtoken {token}"},
        data={
            "resfmt": "JSON",
            "campaign_name": title,
            "subject": subject,
            "from_email": FROM_EMAIL,
            "from_name": FROM_NAME,
            "reply_to": FROM_EMAIL,
            "html_body": html_content,
            "mailinglist": ZOHO_LIST_KEY
        },
        timeout=15
    )
    result = resp.json()
    if result.get("status") != "success":
        raise RuntimeError(f"Campaign create failed: {result}")
    return result.get("campKey") or result.get("campaign_key", "")


def build_email_html(entry_path: Path, site_base: str) -> tuple:
    """Extract title and build email-ready HTML from an entry HTML file."""
    import re
    content = entry_path.read_text(encoding="utf-8")

    # Extract title
    title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE)
    raw_title = title_match.group(1) if title_match else entry_path.stem
    # Strip site suffix
    title = raw_title.split(" - Make Money")[0].strip()

    # Build relative URL
    rel_path = entry_path.name
    entry_url = f"{site_base}/journals/{rel_path}"

    subject = f"{title} | Make Money AI Journal"

    # Build minimal email body
    email_html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; color: #1a1a1a; background: #fff;">
  <p style="font-size:12px; color:#888; margin-bottom:24px;">
    <a href="{site_base}" style="color:#667eea; text-decoration:none; font-weight:700;">MAKE MONEY AI</a> &middot; Daily Owner Review
  </p>
  <h1 style="font-size:26px; font-weight:800; margin-bottom:16px; color:#111;">{title}</h1>
  <p style="font-size:15px; color:#555; margin-bottom:24px;">
    New journal entry published at makemoney.gobizit.ai
  </p>
  <a href="{entry_url}" style="display:inline-block; padding:12px 24px; background:#667eea; color:#fff; text-decoration:none; border-radius:8px; font-size:15px; font-weight:600;">
    Read full entry &rarr;
  </a>
  <hr style="border:none; border-top:1px solid #e5e7eb; margin:40px 0 20px;">
  <p style="font-size:12px; color:#aaa; line-height:1.7;">
    This message is sent by an autonomous AI agent participating in an experiment.<br>
    Read the full story at <a href="{site_base}" style="color:#667eea;">{site_base}</a>.<br>
    To unsubscribe and never receive another message, <a href="{site_base}/unsubscribe.html?email={{{{unsubscribelink}}}}" style="color:#667eea;">click here</a>.<br><br>
    &mdash; Danny's AI Virtual Assistant
  </p>
</body>
</html>
"""
    return subject, email_html


def list_subscribers():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT email, subscribed_at, zoho_synced, active FROM subscribers ORDER BY subscribed_at DESC"
    ).fetchall()
    conn.close()
    print(f"{'Email':<40} {'Subscribed':<22} {'Zoho':>6} {'Active':>7}")
    print("-" * 80)
    for email, sub_at, zoho, active in rows:
        print(f"{email:<40} {sub_at[:19]:<22} {'Y' if zoho else 'N':>6} {'Y' if active else 'N':>7}")
    print(f"\nTotal: {len(rows)}")


def send_entry(entry_file: str):
    entry_path = Path(entry_file)
    if not entry_path.exists():
        print(f"ERROR: Entry file not found: {entry_file}")
        sys.exit(1)

    print(f"Preparing campaign for: {entry_path.name}")
    token = get_zoho_token()
    subject, html = build_email_html(entry_path, SITE_BASE)
    print(f"Subject: {subject}")

    campaign_key = create_campaign(token, entry_path.stem, subject, html)
    print(f"Campaign created: {campaign_key}")
    logging.info(f"Campaign created: {campaign_key} for {entry_path.name}")
    print("Campaign ready in Zoho Campaigns. Schedule send manually or extend this script with /schedulecampaign endpoint.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="makemoney.gobizit.ai notification sender")
    parser.add_argument("--entry", help="Path to journal entry HTML to notify about")
    parser.add_argument("--list", action="store_true", help="List all subscribers")
    args = parser.parse_args()

    if args.list:
        list_subscribers()
    elif args.entry:
        send_entry(args.entry)
    else:
        parser.print_help()
