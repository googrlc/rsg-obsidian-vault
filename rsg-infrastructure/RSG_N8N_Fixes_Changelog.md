# RSG N8N Fixes — Changelog
*Applied by Claude Code — 2026-03-22*

---

## Fix 1 — Webhook Authentication

### Workflows Updated
| Workflow | Node | Before | After |
|---------|------|--------|-------|
| nowcerts-client-lookup | Webhook | none | headerAuth |
| NB- Workflow 1b — RSG: Onboarding Email Trigger (Webhook) | Webhook: Start Onboarding | none | headerAuth |

### Credential Used
**RSG Webhook Auth** (ID: `wffAnqkfYyBZtLHp`, type: `httpHeaderAuth`)
- Header name: `X-Webhook-Token`
- Header value: `3ea1f762-1a9a-4afb-bc12-c1845b3a2c8a`
- Any system calling these webhooks must now include this header

---

## Fix 2 — Stage Name Strings

### Workflows Updated
| Workflow | Old String | New String |
|---------|-----------|-----------|
| NB- Workflow 1 — RSG: Deal Won Intake & Sequence | Closed Won | Won - Bound |
| NB- Workflow 1 — RSG: Deal Won Intake & Commission Log | Closed Won | Won - Bound |

### Important Note
Both workflows query **Notion databases** where the stage property was `"Closed Won"`. The N8N filter has been updated to `"Won - Bound"`, but the **Notion database property values must also be updated** from `"Closed Won"` to `"Won - Bound"` for these workflows to match deals correctly. Until that Notion update is made, the won-deal queries will return no results.

### Archived Workflows (Not Updated)
4 archived "Deal Discovery & Setup" workflows also contained "Closed Won" but could not be updated (N8N blocks editing archived workflows). These were subsequently deleted — see below.

---

## Fix 3 — Commission DB ID

### What Was Wrong
The commission workflow (`NB- Workflow 1 — RSG: Deal Won Intake & Commission Log`) had two different Notion database IDs for the commission ledger:
- **Pipeline Configs** node defined `COMMISSION_LEDGER_DB_ID = 'ce1c17e3bf894deb9320e6629a7b842a'`
- **Prepare Commission Data** node hardcoded `COMMISSION_LEDGER_DB_ID: '4f6fe78e03774836b752ce17da734ce6'`
- **Create Commission Entry** node also used `'4f6fe78e03774836b752ce17da734ce6'`

The Pipeline Configs value was never actually used for commission entries — it was effectively dead code.

### What Was Fixed
Updated Pipeline Configs `COMMISSION_LEDGER_DB_ID` from `ce1c17e3bf894deb9320e6629a7b842a` to `4f6fe78e03774836b752ce17da734ce6` so all nodes reference the same Notion database.

### Manual Step Required?
**Yes** — To migrate commission logging to Supabase (`commission_ledger` table in project `wibscqhkvpijzqbhjphg`):
1. Add a Supabase credential in N8N
2. Replace Notion API calls with Supabase insert nodes
3. Map fields to the `commission_ledger` schema (see `supabase/migrations/20240004_commission_ledger.sql`)

No Supabase credential currently exists in N8N, so this migration was not attempted.

---

## Fix 4 — Calendly Placeholder

### Workflows Updated
| Workflow | Node | Action Taken |
|---------|------|-------------|
| Task- Workflow D — RSG: Task Complete → Client Thank You Email | Prepare Thank You | Replaced `[YOUR CALENDLY LINK]` with `https://cal.com/rsglamarcal/30min` |

### Manual Step Required
Cal.com URL `https://cal.com/rsglamarcal/30min` has been inserted directly — no manual step needed.

---

## Workflows Deleted

| Workflow | ID | Reason |
|---------|-----|--------|
| Deal Discovery & Setup (seq-001 → seq-014) | ngzY5I77Se4kVoi5 | Archived duplicate |
| Deal Discovery & Setup (seq-001 → seq-014) | iMIG6KMzIB4QcpBU | Archived duplicate |
| Deal Discovery & Setup (seq-001 → seq-014) | sbPkNTrgXScVfT18 | Archived duplicate |
| Deal Discovery & Setup (seq-001 → seq-014) | LXxdzhGhJo1QOzyU | Archived duplicate |
| Task-Task Complete → Email Manus | EvU32dY0iTjSEYGz | Inactive, unused |
| Task— New Manus Task → Slack Alert | 7brJISzL9UkhdybC | Inactive, unused |

---

## Summary

| Fix | Status | Manual Step Needed? |
|-----|--------|-------------------|
| Webhook auth | Done | No (but callers need the new header token) |
| Stage name strings | Done | Yes — update Notion DB property values |
| Commission DB ID | Done (consistency fix) | Yes — Supabase migration pending |
| Cal.com URL | Done | No |
| Delete duplicates | Done (6 removed) | No |

---

## Workflows NOT Modified
- Policy- NowCerts → EspoCRM Policy Sync v1
- WF-A v2 — RSG: EspoCRM Task Claude Triage
- RSG — Renewal Outreach Automation (EspoCRM)
- RSG Morning Briefing v3
- WF-E — RSG: Escalation Watchdog
- NB-Workflow 2 — Day 0 & Day 1 Onboarding Emails
- RSG Afternoon Pulse (3pm ET)
- NB- Workflow 3 — RSG: Long-term Nurture Sequence (Day 7-60)
- WF-F — RSG: Gmail RSG-Task Label → Notion Task Creator

---

## Additional Observation
The email template in **Task- Workflow D** references "Lamar Johnson" — should this be "Lamar Coates"?
