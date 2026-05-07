"""
makemoney.gobizit.ai — Subscriber API
Handles email capture, SQLite storage, Zoho Campaigns sync, and unsubscribe.

Run: python api/subscribe.py
Listens on port 5055 (behind Caddy reverse proxy)
"""

import sqlite3
import json
import re
import os
import requests
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "api" / "subscribers.db"
LOG_PATH = BASE_DIR / "api" / "subscribe.log"
UNSUBSCRIBED_PATH = Path.home() / ".claude" / "secrets" / "make-money" / "unsubscribed.txt"

# Zoho Campaigns
ZOHO_LIST_KEY = "3z056b843baba6f7dd3527f4c02bf8f6a72196a9cfa86178cbfe4204ed4b0ebeba"
ZOHO_ACCESS_TOKEN_FILE = Path.home() / ".claude" / "secrets" / "make-money" / "zoho-campaigns-token.json"
ZOHO_REFRESH_TOKEN = "1000.ec9549a6848bb3423d152b0994aad02d.ff93e2f44010d6d7163a1cc50af394fc"
ZOHO_CLIENT_ID_FILE = Path.home() / ".claude" / "secrets" / "make-money" / ".env"

BCCMAIL = "danny@gobizit.ai"

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

app = Flask(__name__)

# ── Database setup ───────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            subscribed_at TEXT NOT NULL,
            source TEXT DEFAULT 'website',
            zoho_synced INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS unsubscribes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            unsubscribed_at TEXT NOT NULL,
            reason TEXT
        )
    """)
    conn.commit()
    conn.close()

# ── Helpers ──────────────────────────────────────────────────────────────────

def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

def is_unsubscribed(email: str) -> bool:
    if UNSUBSCRIBED_PATH.exists():
        lines = UNSUBSCRIBED_PATH.read_text().lower().splitlines()
        return email.lower() in lines
    return False

def add_to_unsubscribed_file(email: str):
    UNSUBSCRIBED_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(UNSUBSCRIBED_PATH, "a") as f:
        f.write(email.lower() + "\n")

def get_zoho_access_token() -> str:
    """Return current access token; refresh if expired."""
    if ZOHO_ACCESS_TOKEN_FILE.exists():
        data = json.loads(ZOHO_ACCESS_TOKEN_FILE.read_text())
        # Simple check: if token was saved recently enough
        saved_at = data.get("saved_at", "")
        if saved_at:
            saved_dt = datetime.fromisoformat(saved_at)
            age_secs = (datetime.now() - saved_dt).total_seconds()
            if age_secs < 3500:
                return data["access_token"]

    # Refresh token
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

    token_data = {
        "access_token": data["access_token"],
        "saved_at": datetime.now().isoformat()
    }
    ZOHO_ACCESS_TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    ZOHO_ACCESS_TOKEN_FILE.write_text(json.dumps(token_data))
    return data["access_token"]

def load_zoho_client_creds():
    """Load ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET from .env file."""
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

def sync_to_zoho(email: str) -> bool:
    """Add subscriber to Zoho Campaigns makemoney list."""
    try:
        token = get_zoho_access_token()
        contact_info = json.dumps([{"Email": email}])
        resp = requests.post(
            "https://campaigns.zoho.com/api/v1.1/json/listsubscribe",
            headers={"Authorization": f"Zoho-oauthtoken {token}"},
            data={
                "resfmt": "JSON",
                "listkey": ZOHO_LIST_KEY,
                "contactinfo": contact_info
            },
            timeout=10
        )
        result = resp.json()
        if result.get("status") == "success":
            logging.info(f"Zoho sync OK: {email}")
            return True
        logging.warning(f"Zoho sync non-success: {email} → {result}")
        return False
    except Exception as e:
        logging.error(f"Zoho sync error for {email}: {e}")
        return False

def send_bcc_unsubscribe(email: str):
    """BCC danny on unsubscribe — Phase A: log only (SMTP wired in next iteration)."""
    logging.info(f"UNSUBSCRIBE_BCC_PENDING to={BCCMAIL} re={email}")
    # TODO Phase B: invoke money-making-email skill or SMTP direct

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/api/subscribe", methods=["POST"])
def subscribe():
    try:
        body = request.get_json(force=True)
    except Exception:
        return jsonify({"success": False, "message": "Invalid JSON"}), 400

    email = (body.get("email") or "").strip().lower()
    source = body.get("source", "website")

    if not email or not is_valid_email(email):
        return jsonify({"success": False, "message": "Invalid email address"}), 400

    if is_unsubscribed(email):
        return jsonify({"success": False, "message": "This email has previously unsubscribed."}), 409

    now = datetime.now().isoformat()

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO subscribers (email, subscribed_at, source) VALUES (?, ?, ?)",
            (email, now, source)
        )
        conn.commit()
        logging.info(f"New subscriber: {email} source={source}")
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"success": True, "message": "Already subscribed."}), 200
    conn.close()

    # Async-style: try Zoho sync (best effort)
    zoho_ok = sync_to_zoho(email)
    if zoho_ok:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("UPDATE subscribers SET zoho_synced=1 WHERE email=?", (email,))
        conn.commit()
        conn.close()

    return jsonify({"success": True, "message": "Subscribed successfully."}), 201


@app.route("/api/unsubscribe", methods=["POST", "GET"])
def unsubscribe():
    if request.method == "GET":
        email = (request.args.get("email") or "").strip().lower()
    else:
        try:
            body = request.get_json(force=True)
            email = (body.get("email") or "").strip().lower()
        except Exception:
            email = (request.form.get("email") or "").strip().lower()

    if not email or not is_valid_email(email):
        return jsonify({"success": False, "message": "Invalid email"}), 400

    now = datetime.now().isoformat()

    # Mark inactive in DB
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE subscribers SET active=0 WHERE email=?", (email,))
    conn.execute(
        "INSERT INTO unsubscribes (email, unsubscribed_at) VALUES (?, ?)",
        (email, now)
    )
    conn.commit()
    conn.close()

    # Add to local unsubscribed.txt
    add_to_unsubscribed_file(email)

    # BCC Danny (Phase A: log)
    send_bcc_unsubscribe(email)

    logging.info(f"Unsubscribed: {email}")

    return jsonify({"success": True, "message": "You have been unsubscribed."}), 200


@app.route("/api/subscribers/count", methods=["GET"])
def subscriber_count():
    """Public count — no emails exposed."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT COUNT(*) FROM subscribers WHERE active=1").fetchone()
    conn.close()
    return jsonify({"count": row[0]}), 200


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "ts": datetime.now().isoformat()}), 200


if __name__ == "__main__":
    init_db()
    logging.info("Subscribe API starting on port 5055")
    app.run(host="127.0.0.1", port=5055, debug=False)
