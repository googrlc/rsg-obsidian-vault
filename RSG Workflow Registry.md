# RSG Workflow Registry
**Last Updated:** March 2026
**Status Key:** 🟢 Working | 🔴 Broken | 🟡 Untested | ⚫ Deactivate

---

## n8n Workflows (18 total)

### New Business

| # | Name | n8n ID | Status | Use Case | Tools / Integrations |
|---|---|---|---|---|---|
| 1 | NB-WF1 — Deal Won Intake & Commission Log | `UFwZUwlHi1ERwSXP` | 🔴 Broken | Triggers on Won deal → logs commission record, Slack dopamine alert, creates Gretchen follow-up task | EspoCRM, Slack |
| 2 | NB-WF2 — Day 0 & Day 1 Onboarding Emails | `qbMMleTF4xQDJNGo` | 🟢 Working | Sends welcome + next steps emails immediately after deal is won | EspoCRM, Gmail |
| 3 | NB-WF3 — Long-term Nurture Sequence (Day 7–60) | `J9lZZBwUA2888qkP` | 🟢 Working | Drip email sequence post-onboarding — cross-sell touchpoints, referral ask | EspoCRM, Gmail |
| 4 | WF2 — NB Commission Auto-Create | `waqicelWdspuaCdf` | 🔴 Broken | Creates commission tracking record in EspoCRM when new business closes | EspoCRM |

**Root cause (WF1, WF2):** Won-stage string mismatch — workflow checks for `Won-Bound` but EspoCRM stores `✅ Won - Bound`. Triggers have never fired.

---

### Renewals

| # | Name | n8n ID | Status | Use Case | Tools / Integrations |
|---|---|---|---|---|---|
| 5 | WF1 — Renewal Auto-Create | `0npEnsS6D2hpjBfK` | 🟢 Working | NowCerts → EspoCRM nightly sync — creates renewal pipeline records for expiring policies, routes by LOB | NowCerts API, EspoCRM |
| 6 | RSG — Renewal Outreach Automation | `ptlLTDUBj0XhTRTH` | 🔴 Broken | Sends renewal outreach emails at Day 0 / Day 30 / Day 60 based on expiration date | EspoCRM, Gmail |
| 7 | WF5 — Renewal Stage Auto-Update on Outreach | `wZZooWpIdBqoj5G4` | 🔴 Broken | Advances renewal record stage in EspoCRM after each outreach email sends | EspoCRM |
| 8 | WF3 — Renewal Commission Auto-Create | `zlzLty9lJmtrPWuI` | 🔴 Broken | Creates commission record when a renewal closes | EspoCRM |
| 9 | RSG — Renewal Retention & Commission Report | `NQCSJ2YzT3CK5Mjb` | 🟡 Untested | Scheduled report on renewal pipeline health and commission totals → posts to Slack | EspoCRM, Slack |

**Root cause (WF6, WF7, WF8):** Day 30 email has unfilled `{{MANUS_AI_PERSONALIZATION}}` placeholder. Stage strings likely mismatched same as NB workflows.

---

### Data Sync

| # | Name | n8n ID | Status | Use Case | Tools / Integrations |
|---|---|---|---|---|---|
| 10 | Policy — NowCerts → Nightly Policy Updates | `lsgUVFg7RoeDtOLF` | 🟢 Working | Nightly sync of all policy data from NowCerts into EspoCRM. Foundation workflow — everything downstream depends on this | NowCerts API, EspoCRM |
| 11 | NowCerts Client Lookup | `sIYk2ZQObh8GqCpo` | 🟢 Working | On-demand client lookup from NowCerts API — triggered by other workflows or manual webhook | NowCerts API |
| 12 | RSG — Account Rollup Fields *(NEW)* | Kyjizvgp5fHKKR6z | 🟢 Working | 53 accounts live. Runs every 6 hours — calculates totalActivePremium, activePolicyCount, nextXDate, nextXDateLob per account and writes back to EspoCRM | EspoCRM, Slack (#systems-check) |

---

### Tasks & Alerts

| # | Name | n8n ID | Status | Use Case | Tools / Integrations |
|---|---|---|---|---|---|
| 13 | Task-WF D — Task Complete → Client Thank You | `bsm2iy6m1Tjx2MJz` | 🟡 Untested | When a task is marked complete in EspoCRM, sends client a thank you / follow-up email | EspoCRM, Gmail |
| 14 | WF-E — Escalation Watchdog | `8w54qlueIikaBw7c` | ⚫ DELETED | Monitors stalled records and missed SLAs — fires alerts when renewals/tasks haven't been touched within thresholds | EspoCRM, Slack |
| 15 | WF-F — Gmail RSG-Task Label → EspoCRM Task Creator | `23kKCvM0tddkVMGk` | 🟢 Working | Label a Gmail email "RSG-Task" → auto-creates a task in EspoCRM | Gmail, EspoCRM |
| 16 | RSG Afternoon Pulse (3pm ET) | `3KJRFIwkTtCFexO3` | ⚫ DELETED | Daily 3pm Slack digest — replaced by Morning Commander (OpenClaw). requireMention: false now live on #the-boss | Slack |
| 17 | Personal OS — Task Reminder Engine | `X88iqwjGkbOwQ3Dc` | ⚫ DELETED | Personal task reminders for Lamar — replaced by Task Finisher + Focus Guard (OpenClaw) | Slack |

---

### Infrastructure

| # | Name | n8n ID | Status | Use Case | Tools / Integrations |
|---|---|---|---|---|---|
| 18 | RSG — Global Error Workflow | `lWeQqSjVGaDEqTsS` | 🟢 Working | Catch-all error handler — all workflows route failures here → posts to #systems-check | Slack (#systems-check) |

---

---

## OpenClaw Agents (14 deployed)

**Instance:** `openclaw-larau-u69864.vm.elestio.app`
**Default Model:** claude-3-5-sonnet-latest (all except Shepherding Assistant)

| # | Agent ID | Name | Slack Channel | Use Case | Replaces / Complements |
|---|---|---|---|---|---|
| 01 | revenue-sheriff | Revenue Sheriff | #agency-ops, #sales-brief | ADHD accountability, pipeline pressure, deal follow-through | Complements NB workflows |
| 02 | morning-commander | Morning Commander | #daily-ops-digest, #the-morning-commander | Daily briefing — 3 non-negotiables, pipeline snapshot | Replaces Afternoon Pulse (WF16) |
| 03 | operations-foreman | Operations Foreman | #client-service | Lamar ↔ Gretchen delegation, task hand-off, team coordination | Complements Task-WF D |
| 04 | deal-coach | Deal Coach | #client-service | Pre-call prep, objection handling, commercial account strategy | Standalone |
| 05 | renewal-watchdog | Renewal Watchdog | #service-brief | Renewal pipeline protection, flags at-risk accounts, urgency triage | Replaces WF-E Escalation Watchdog |
| 06 | focus-guard | Focus Guard | #agency-ops | Drift detection, pattern-interrupt for ADHD hyperfocus on non-revenue work | Standalone |
| 07 | brain-dump-butler | Brain Dump Butler | Any | Idea triage — Act / Schedule / Park / Release framework | Standalone |
| 08 | task-finisher | Task Finisher | #the-task-list | Extracts next physical action from vague tasks | Replaces Personal OS Task Reminders (WF17) |
| 09 | automation-triage-nurse | Automation Triage Nurse | #systems-check | Workflow health monitoring, build-vs-fix gating, reads Global Error alerts | Monitors all n8n workflows |
| 10 | reflection-anchor | Reflection Anchor | #the-study | EOD spiritual processing, grounding after high-stress days | Standalone |
| 11 | message-prep-scribe | Message Prep Scribe | #the-study | Sermon / teaching outlines, ministry content prep | Standalone |
| 12 | rsg-cfo | RSG CFO | #growth-finance | Commission tracking, cash flow analysis, revenue reporting | Replaces Renewal Retention Report (WF9) |
| 13 | data-entry-assistant | Data Entry Assistant | #client-service | NowCerts and EspoCRM field-by-field entry guidance for Gretchen | Complements NowCerts Client Lookup (WF11) |
| 14 | shepherding-assistant | Shepherding Assistant | #the-study | Scriptural research — runs on local DeepSeek-R1 model via Ollama on Mac Mini | Standalone |

---

## Fix Queue (Priority Order)

| Priority | Fix | Affected Workflows | Est. Time | Status |
|---|---|---|---|---|
| 1 | Won-stage string mismatch | WF1 (NB-WF1), WF2 (NB Commission), WF3 (Renewal Commission) | 20 min | 🔴 Not started |
| 2 | Day 30 renewal email — fill Manus placeholder | RSG Renewal Outreach (WF6) | 15 min | 🔴 Not started |
| 3 | Wire Automation Triage Nurse to read #systems-check errors | OpenClaw agent config | 20 min | 🔴 Not started |
| 4 | Deactivate redundant workflows | WF14 (Escalation Watchdog), WF16 (Afternoon Pulse), WF17 (Personal OS) | 5 min | 🔴 Not started |
| 5 | Activate Account Rollup workflow after EspoCRM fields confirmed | WF12 (new) | 10 min | 🟡 Building |

---

## Infrastructure Reference

| Component | URL / Value |
|---|---|
| n8n Instance | `n8n-zpvua-u69864.vm.elestio.app` |
| EspoCRM | `https://rrespocrm-rsg-u69864.vm.elestio.app` |
| EspoCRM Auth | `X-Api-Key` header — key in 1Password |
| OpenClaw Gateway | `openclaw-larau-u69864.vm.elestio.app` |
| Slack Error Channel | #systems-check (`C0AFHN83ZE3`) |
| NowCerts Auth | Fresh token per run (~60 min expiry) — credentials in 1Password |
| n8n Slack Alerts | `$env.SLACK_WEBHOOK_URL` → #systems-check |
