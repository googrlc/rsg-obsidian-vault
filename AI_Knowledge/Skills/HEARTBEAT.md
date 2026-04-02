# RSG Heartbeat — Scheduled Agent Tasks

## Identity
This file defines all scheduled/recurring tasks that run automatically without user prompting. These are RSG's automated revenue protection and daily ops triggers.

---

## Credentials

| Key | Value | Status |
|---|---|---|
| SUPABASE_SERVICE_KEY | (stored in agent .env) | ✅ Active — used for ALL tables including personal_tasks |
| SUPABASE_ANON_KEY | (stored in agent .env) | ✅ Active — read-only public queries |
| SUPABASE_URL | https://wibscqhkvpijzqbhjphg.supabase.co | ✅ Static — never changes |
| SUPABASE_PROJECT_ID | wibscqhkvpijzqbhjphg | ✅ Static |
| ESPOCRM_API_KEY | (stored in agent .env) | ✅ Active |
| NOWCERTS_CLIENT_ID | ngAuthApp | ✅ Active |

> Supabase project: `rsg-infrastructure` (ID: `wibscqhkvpijzqbhjphg`, us-east-1)
> Full table reference: see `supabase-data-layer` skill in Claude Code skills

---

## Schedule: Morning Commander
**Runs:** Every weekday at 7:00 AM ET (cron: `0 7 * * 1-5`)
**Agent:** morning-commander
**Channel:** #the-morning-commander

**Task:**
1. Mint NowCerts token
2. Pull all policies expiring in next 90 days from NowCerts
3. Pull open Opportunities from EspoCRM (stages: Prospecting, Qualification, Proposal)
4. Pull open Tasks from EspoCRM assigned to Lamar or Gretchen due today
5. Count new Leads created in last 7 days in EspoCRM
6. Post to #the-morning-commander in this format:

```
🌅 *RSG Morning Brief — {DATE}*

🔴 *RENEWAL CRITICAL (0-14 days): {COUNT}*
{LIST each: Client | LOB | Expiry | Premium}

🟡 *RENEWAL URGENT (15-30 days): {COUNT}*
{LIST each: Client | LOB | Expiry}

📋 *PIPELINE OPEN: {COUNT} deals | ${TOTAL_VALUE} est. premium*
{LIST top 5 by close date}

✅ *TODAY'S TASKS: {COUNT}*
{LIST: Task | Assigned To | Due}

🎯 *YOUR 3 NON-NEGOTIABLES TODAY:*
1. {Highest urgency renewal action}
2. {Most valuable pipeline action}
3. {Lead follow-up or new business action}

Revenue Sheriff is watching. Make it count.
```

---

## Schedule: Renewal Watchdog Scan
**Runs:** Every day at 8:00 AM ET and 2:00 PM ET (cron: `0 8,14 * * *`)
**Agent:** renewal-watchdog
**Channel:** #service-brief

**Task:**
1. Mint NowCerts token
2. Pull policies expiring in next 90 days
3. For each expiring policy:
   a. Search EspoCRM for existing renewal Opportunity
   b. If Opportunity exists → update stage/notes if needed
   c. If Opportunity does NOT exist → create it in EspoCRM
4. Post summary to #service-brief:

```
🔄 *Renewal Watchdog Scan — {TIME}*

📥 Synced {COUNT} policies to EspoCRM pipeline
🆕 Created {COUNT} new renewal opportunities
✏️ Updated {COUNT} existing records

🔴 CRITICAL (needs contact today):
{LIST: Client | LOB | Exp Date | Premium | EspoCRM link}
```

5. If any CRITICAL policies found → also ping @Lamar in #service-brief

---

## Schedule: Pipeline Health Check
**Runs:** Every Monday at 9:00 AM ET (cron: `0 9 * * 1`)
**Agent:** revenue-sheriff
**Channel:** #agency-ops

**Task:**
1. Pull all EspoCRM Opportunities created in last 30 days
2. Pull all Opportunities with no activity in last 7 days (stale)
3. Pull total pipeline value by stage
4. Post weekly pipeline health to #agency-ops:

```
📊 *RSG Weekly Pipeline — Week of {DATE}*

💰 *Total Pipeline Value:* ${TOTAL}
├── Prospecting: {COUNT} deals | ${VALUE}
├── Qualification: {COUNT} deals | ${VALUE}
├── Proposal: {COUNT} deals | ${VALUE}
└── Negotiation: {COUNT} deals | ${VALUE}

⚠️ *STALE (no activity 7+ days): {COUNT}*
{LIST: Deal | Stage | Last Activity | Assigned}

🏆 *Won last 7 days: {COUNT} | ${VALUE}*

Focus Guard is watching your pipeline drift, Lamar.
```

---

## Schedule: Commission Flash
**Runs:** Every Friday at 4:00 PM ET (cron: `0 16 * * 5`)
**Agent:** rsg-cfo
**Channel:** #growth-finance

**Task:**
1. Pull all EspoCRM Opportunities moved to `Closed Won` in current week
2. Calculate estimated commissions (Commercial: 12%, Personal: 10%)
3. Post weekly commission summary to #growth-finance

---

## Schedule: Systems Check
**Runs:** Every day at 6:00 AM ET (cron: `0 6 * * *`)
**Agent:** automation-triage-nurse
**Channel:** #systems-check

**Task:**
1. Test NowCerts token mint — confirm API is reachable
2. Test EspoCRM API endpoint — confirm `/api/v1/Contact` returns 200
3. Report health status to #systems-check:

```
🏥 *Daily Systems Check — {TIME}*
NowCerts API: {✅ OK / ❌ FAIL}
EspoCRM API: {✅ OK / ❌ FAIL}
OpenClaw Gateway: ✅ Running (you're reading this)
```

4. If any system FAIL → ping @Lamar immediately in #systems-check

---

---

## Supabase API Reference

**Base URL:** `https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1`

**Required headers on EVERY call:**
```
apikey: {SUPABASE_SERVICE_KEY}
Authorization: Bearer {SUPABASE_SERVICE_KEY}
Content-Type: application/json
```

### Table → Use Case → Key Env Var

| Table | Use Case | Key Required |
|---|---|---|
| `knowledge_chunks` | Carrier appetite, commission, skill retrieval | `SUPABASE_SERVICE_KEY` |
| `commission_rules` | Look up commission rates by carrier/LOB | `SUPABASE_SERVICE_KEY` |
| `commission_ledger` | Log/read actual vs expected payments | `SUPABASE_SERVICE_KEY` |
| `commission_reconciliation` | Open discrepancies — money owed | `SUPABASE_SERVICE_KEY` |
| `carrier_appetite` | Which carriers write which risks | `SUPABASE_SERVICE_KEY` |
| `personal_tasks` | Lamar's personal/ministry task list | `SUPABASE_SERVICE_KEY` |
| `calendar_events` | Lamar's personal calendar events | `SUPABASE_SERVICE_KEY` |
| `medicare_master_plan_index` | Medicare plan lookups | `SUPABASE_SERVICE_KEY` |
| `medicare_county_footprints` | Plans available by GA county | `SUPABASE_SERVICE_KEY` |
| `risk_assessments` | Commercial risk intake records | `SUPABASE_SERVICE_KEY` |
| `risk_scoring_matrix` | Industry risk multipliers | `SUPABASE_SERVICE_KEY` |
| `gl_class_codes` | GL class code lookup (1,154 codes) | `SUPABASE_SERVICE_KEY` |
| `wc_class_codes` | WC class code lookup (156 codes) | `SUPABASE_SERVICE_KEY` |

### Common Query Patterns

**Read open commission discrepancies:**
```
GET /rest/v1/commission_reconciliation?status=eq.open&order=priority.asc
```

**Look up carrier appetite for a LOB:**
```
GET /rest/v1/carrier_appetite?lob=ilike.*Commercial Auto*&appetite_level=eq.preferred
```

**Search knowledge chunks by tag:**
```
GET /rest/v1/knowledge_chunks?tags=cs.{Progressive}&domain=eq.carrier
```

**Read open personal tasks:**
```
GET /rest/v1/personal_tasks?status=eq.open&order=due_date.asc
```

**Insert a personal task:**
```
POST /rest/v1/personal_tasks
Body: {"title":"...", "domain":"personal", "priority":"high", "status":"open", "due_date":"2026-04-01", "source":"claude"}
```

### Error Codes
| Code | Meaning | Fix |
|---|---|---|
| 401 | Bad or missing API key | Check SUPABASE_SERVICE_KEY is set in Elestio env vars |
| 409 | Duplicate key conflict | Use `Prefer: resolution=merge-duplicates` header |
| 42P01 | Table doesn't exist | Migration hasn't run — check rsg-infrastructure migrations |
| 500 | Supabase server error | Project may be paused — check dashboard |

---

## ⚠️ Known Blockers (Updated 2026-03-30)

| Blocker | Status | Workaround |
|---|---|---|
| `industry` field `validationFailure` on Account create/update | Active | Use valid enum only — see crm-manager SKILL.md for full list. Default to `Other` if unlisted. |
| EspoCRM API overdue task query → `Slim Application Error` | Active | Fetch all open tasks, filter overdue client-side. See crm-manager SKILL.md Error Handling section. |
| Supabase `personal_tasks` service key missing from HEARTBEAT.md | **RESOLVED** | `personal_tasks` lives in `rsg-infrastructure`. Use `SUPABASE_SERVICE_KEY` — no separate key needed. |

---

## On-Demand Triggers (User-Initiated)

These run when Lamar or Gretchen messages the agent in Slack:

| Trigger phrase | Agent | Action |
|---|---|---|
| "run renewal scan" | renewal-watchdog | Immediate NowCerts → EspoCRM sync |
| "pipeline status" | revenue-sheriff | Current EspoCRM pipeline snapshot |
| "brief me" | morning-commander | On-demand morning brief |
| "prep me for [company]" | deal-coach | Pre-call intel from EspoCRM + web |
| "log commission [deal]" | rsg-cfo | Manual commission entry to EspoCRM |
| "what's Gretchen working on" | operations-foreman | Pull Gretchen's open EspoCRM tasks |
| "brain dump: [text]" | brain-dump-butler | Triage to Act/Schedule/Park/Release — **ONLY fires when message starts with "brain dump:" prefix. NEVER fires on call notes, intake data, client names, policy numbers, FEIN, carrier names, loss history, or any structured prospect/client data. Those ALWAYS route to call-intake-parser.** |

---

## TRIGGER: "book health" / "book check" / "how's the book" / "agency scorecard" / "weekly scorecard"
**Skill:** book-health-monitor.md
**Output channel:** #the-boss (C0ANQUENX4P)
**Schedule:** Monday 10:00 AM ET (auto) + on-demand

Pull active_premium, policy_count, client_count, retention_rate from NowCerts.
Pull open pipeline value + deal count from EspoCRM.
Pull prior snapshot from Supabase agency_snapshots for week-over-week delta.
Save new snapshot row with source='book-health-monitor'.
Compute Gate 1 progress ($425K / 60% retention).
Build renewal radar: bucket policies into ≤14 days (🔴), 15–30 days (🟡), 31–60 days (📋), 61–90 days (📋).
Post full scorecard to #the-boss. If any policy ≤14 days: lead with CRITICAL RENEWALS block.
Confirm start: "📋 Book Health Monitor running → scorecard incoming"
Uses Anthropic.
