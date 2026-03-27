#!/usr/bin/env python3
"""
RSG Data Cleanup Script v2
Corrected endpoints, field names, and API key.

Usage:
  python3 rsg-cleanup.py            # dry run (default)
  python3 rsg-cleanup.py --fix      # apply changes to EspoCRM
"""

import requests, re, sys, time
from difflib import SequenceMatcher

# ── Credentials ───────────────────────────────────────────────────────────────
NOWCERTS_USERNAME  = "lamar@risk-solutionsgroup.com"
NOWCERTS_PASSWORD  = "dcp1vwv*RCF9fpz*dfh"
NOWCERTS_AGENCY_ID = "09d93486-1536-48d7-9096-59f1f62b6f51"
NOWCERTS_TOKEN_URL = "https://api.nowcerts.com/api/token"
NOWCERTS_BASE      = "https://api.nowcerts.com/api"

ESPO_BASE          = "https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1"
ESPO_HEADERS       = {"X-Api-Key": "7ceea464REPLACEME", "Content-Type": "application/json"}

DRY_RUN = "--fix" not in sys.argv
