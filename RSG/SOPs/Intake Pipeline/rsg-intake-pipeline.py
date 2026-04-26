#!/usr/bin/env python3
"""
RSG Intake Pipeline
Watches 00 Inbox, parses docs with Claude AI, routes to Supabase + EspoCRM.
"""

import os, json, base64, shutil, re, requests, logging
from datetime import datetime, date, timedelta
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
INBOX_DIR     = Path("/Users/lamarcoates/Documents/RSG/00 Inbox")
PROCESSED_DIR = INBOX_DIR / "processed"
FAILED_DIR    = INBOX_DIR / "failed"
LOG_FILE      = INBOX_DIR / "intake.log"

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
SUPABASE_URL  = "https://wibscqhkvpijzqbhjphg.supabase.co"
SUPABASE_KEY  = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndpYnNjcWhrdnBpanpxYmhqcGhnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDE0NTkyNiwiZXhwIjoyMDg5NzIxOTI2fQ.VnacqnPjUzxnqTh9Sxt0YXEc4CWjeLeTRYedsRM003I"
ESPO_BASE     = "https://{{ESPOCRM_HOST}}/api/v1"
ESPO_KEY      = "3d34836b07bb327db8d8fa6b63430c4e"
SLACK_TOKEN   = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL = "C0AFHN83ZE3"  # #systems-check

SKIP_FILES    = {"README.md","watcher.log","intake.log",".DS_Store",
                 ".gitignore",".sweep-log.txt",".localized"}
SUPPORTED_EXT = {".pdf",".png",".jpg",".jpeg",".txt",".md",".csv",".xlsx"}

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
log = logging.getLogger("rsg-intake")

# ── Helpers ───────────────────────────────────────────────────────────────────
def espo_get(path):
    try:
        r = requests.get(f"{ESPO_BASE}{path}",
                         headers={"X-Api-Key": ESPO_KEY}, timeout=15)
        return r.json() if r.ok else None
    except: return None

def espo_post(path, data):
    try:
        r = requests.post(f"{ESPO_BASE}{path}",
                          headers={"X-Api-Key": ESPO_KEY, "Content-Type": "application/json"},
                          json=data, timeout=15)
        return r.json() if r.ok else None
    except: return None

def espo_put(path, data):
    try:
        r = requests.put(f"{ESPO_BASE}{path}",
                         headers={"X-Api-Key": ESPO_KEY, "Content-Type": "application/json"},
                         json=data, timeout=15)
        return r.json() if r.ok else None
    except: return None

def supa_post(table, data):
    try:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}",
                          headers={"apikey": SUPABASE_KEY,
                                   "Authorization": f"Bearer {SUPABASE_KEY}",
                                   "Content-Type": "application/json",
                                   "Prefer": "return=representation"},
                          json=data, timeout=15)
        return r.json() if r.ok else None
    except: return None

def slack_post(msg):
    if not SLACK_TOKEN: return
    try:
        requests.post("https://slack.com/api/chat.postMessage",
                      headers={"Authorization": f"Bearer {SLACK_TOKEN}",
                               "Content-Type": "application/json"},
                      json={"channel": SLACK_CHANNEL, "text": msg}, timeout=10)
    except: pass

def file_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def read_text(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    except: return ""
