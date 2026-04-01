# RSG Operations Architecture — 2026

**Risk Solutions Group** — 2-person insurance agency (Atlanta, GA)
Lamar Coates (Owner/Producer) + Gretchen (CSR/Personal Lines)
~$385K active premium | 104 policies | 13 LOBs | GA, AL, FL, SC, TN
Last updated: 2026-04-01

---

## Quick Reference

| System | URL / ID |
|---|---|
| OpenClaw | openclaw-larau-u69864.vm.elestio.app |
| n8n | n8n-zpvua-u69864.vm.elestio.app |
| EspoCRM | rrespocrm-rsg-u69864.vm.elestio.app |
| Supabase | wibscqhkvpijzqbhjphg (us-east-1) |
| NowCerts API | https://api.nowcerts.com/api |
| NowCerts Agency ID | 09d93486-1536-48d7-9096-59f1f62b6f51 |
| Vault repo | github.com/googrlc/rsg-obsidian-vault |
| Vault local | ~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/ |

---

## Layer 1: Infrastructure

### Elestio Cloud (3 VMs)

| Server | Host | Purpose |
|---|---|---|
| OpenClaw | openclaw-larau-u69864.vm.elestio.app | AI agent orchestrator — 15 agents, 13 skills, Slack hub |
| n8n | n8n-zpvua-u69864.vm.elestio.app | Workflow automation — NowCerts/EspoCRM sync, email, error handling |
| EspoCRM | rrespocrm-rsg-u69864.vm.elestio.app | CRM — accounts, contacts, leads, opportunities, policies, renewals |

### Supabase

| Project | ID | Purpose |
|---|---|---|
| RSG Infrastructure | wibscqhkvpijzqbhjphg | Class codes, carrier appetite, commission ledger, Medicare plan data |

### Lamar's Mac (Local Services)

| Service | Location | Purpose |
|---|---|---|
| Claude Code | CLI / VS Code | Development, architecture, skill authoring |
| RSG Slack Bot | ~/rsg-slack-bot/ | Morning + sales briefings via Claude to Slack |

### Obsidian Vault

| Location | Purpose |
|---|---|
| ~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/ | Local — Obsidian app, Claude Code, filesystem |
| github.com/googrlc/rsg-obsidian-vault | Git mirror — OpenClaw reads skills via GITHUB_VAULT_TOKEN |

---

## Layer 2: Systems of Record

**One-Way Rule:** Data flows FROM systems of record TO dashboards. Never reverse.

| System | Truth Domain |
|---|---|
| NowCerts | Policy truth (AMS) |
| EspoCRM | Pipeline truth (CRM) |
| Supabase | Analytics/rules truth |
| Obsidian | Knowledge truth |

### NowCerts / Momentum (AMS)
- Auth: POST https://api.nowcerts.com/api/token (client_id=ngAuthApp)
- Token expiry: ~60 min — remint per session
- Key data: policies, premiums, expiration dates, carriers, insureds

### EspoCRM (CRM)
- API: https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1
- Auth: X-Api-Key header
- Modules: Account, Contact, Lead, Opportunity, Policy, Renewal, Commission, Task, Call, Meeting
- Redesign spec: v1.7, 20 sections, 80 acceptance criteria

### Supabase Tables — Commercial Insurance

| Table | Rows | Purpose |
|---|---|---|
| gl_class_codes | 1,154 | GL class codes — descriptions, categories, restrictions |
| wc_class_codes | 156 | WC class codes — duties, payroll types |
| operations_to_codes | 51 | Operation keyword to code mapping |
| wc_red_flag_pairings | — | Prohibited WC code combinations |
| carrier_appetite | — | Carrier appetite by class/state |
| commission_rules | 216 | Rate cards by carrier/LOB/MGA/state |
| commission_ledger | — | Expected vs actual commission per policy |
| commission_reconciliation | — | Flagged discrepancies |
| personal_tasks | — | Lamar's personal task list |

### Supabase Tables — Medicare

| Table | Rows | Purpose |
|---|---|---|
| medicare_master_plan_index | 128 | All MA plans — premiums, MOOP, Part B giveback |
| medicare_county_footprints | 357 | Plan availability by GA county |
| medicare_medical_rx_matrix | 95 | Copays, Rx tiers, deductibles |
| medicare_supplemental_benefits | 94 | Dental, vision, OTC, SSBCI, fitness, transport |
| medicare_provider_registry | 17 | Hospital/provider network by plan and county |
| medicare_ssbci_logic | 13 | Chronic conditions that unlock SSBCI wallet |
| medicare_ssbci_plan_map | — | SSBCI conditions to plans with wallet amounts |
| medicare_carriers | 11 | Carrier contact directory |
| medicare_eligibility_plan_map | — | Eligibility/Medicaid matrix |

---

## Layer 3: Obsidian Vault Structure

```
Obsidian Vault/
├── 00-Inbox/
├── AI_Knowledge/
│   ├── Skills/               ← crm-manager, nowcerts-skill, prospect-researcher,
│   │                            renewal-prep, carrier-appetite, outreach-templates,
│   │                            commission-reconciliation, linkedin-prospecting,
│   │                            email-triage, vin-lookup, property-lookup,
│   │                            medication-formulary, medicare-plan-advisor,
│   │                            HEARTBEAT.md, *.json, *.skill
│   ├── Carriers/
│   ├── Insurance Education/
│   ├── Lines of Business/
│   └── Document Inbox/
├── Carriers/
│   ├── Appetites/
│   └── Commissions/
├── RSG/
│   ├── Infrastructure/
│   ├── Workflows/
│   │   └── OpenClaw Build/
│   ├── EspoCRM/
│   ├── SOPs/
│   ├── Templates/
│   └── Clients/
├── RSG Commercial Data model/
│   ├── GL Class Codes/        (1,154 files)
│   ├── WC Class Codes/        (156 files)
│   ├── Operations to Codes/   (51 files)
│   ├── SIC Codes/             (444 files)
│   └── Risk Scoring Matrix/   (52 files)
├── Skills/
├── Github/
├── Ministry/
├── Personal/
├── _Archive/
└── _System/
    ├── RSG-Architecture-2026.md   ← THIS FILE
    ├── RSG Vault Index.md
    ├── RSG Workflow Registry.md
    ├── data dictionary.txt
    └── Credentials/
```

---

## Layer 4: OpenClaw — "The Walled Garden"

Docker container on Elestio. Slack Socket Mode. 15 agents, 13 skills.

### Container Layout
```
/home/node/.openclaw/
├── openclaw.json
├── agents/           ← 15 agent configs
├── skills/           ← 15 skill .md files
├── references/
├── workspace/
│   ├── HEARTBEAT.md
│   ├── IDENTITY.md
│   ├── TOOLS.md
│   ├── USER.md
│   ├── memory/
│   ├── agency-goals/
│   ├── coverages/
│   └── carriers/
└── identity/device.json
```

### MCP Servers (in-container)
- supabase — direct Supabase access (class codes, commission, Medicare)

### Environment Variables
```
ANTHROPIC_API_KEY
OPENAI_API_KEY
SLACK_BOT_TOKEN
SLACK_APP_TOKEN
GITHUB_VAULT_TOKEN
GITHUB_VAULT_REPO        googrlc/rsg-obsidian-vault
GITHUB_VAULT_BRANCH      main
NOWCERTS_PASSWORD
SUPABASE_SERVICE_ROLE_KEY
```

---

## Layer 5: Agents (15 Personas)

### Revenue & Sales

| Agent | Role | Channel |
|---|---|---|
| Deal Coach | Pre-call prep, objection handling, quote follow-ups | #client-service |
| Revenue Sheriff | Pipeline accountability, ADHD-aware pressure | #agency-ops, #sales-brief |
| RSG CFO | Commission tracking, financial clarity, growth math | #growth-finance |

### Operations & Retention

| Agent | Role | Channel |
|---|---|---|
| Morning Commander | Daily briefing, 3 non-negotiables, routing | #the-morning-commander |
| Renewal Watchdog | Expiring policy monitoring, EspoCRM renewal sync | #service-brief |
| Operations Foreman | Delegation, SOP gaps | #client-service |
| Data Entry Assistant | Structured CRM/AMS data entry | — |
| Automation Triage Nurse | Broken workflow triage | #systems-check |

### Focus & Personal

| Agent | Role | Channel |
|---|---|---|
| Personal Assistant | Command center — task routing, morning brief, revenue commands, proactive alerts. System Prompt v2.0 deployed 2026-04-01. | #the-boss |
| Focus Guard | ADHD drift detection, redirect to revenue | #agency-ops |
| Task Finisher | Kills paralysis — single next action | — |
| Brain Dump Butler | Rapid capture → Act/Schedule/Park/Release | — |

### Ministry & Personal

| Agent | Role | Channel |
|---|---|---|
| Shepherding Assistant | Scriptural research, teaching outlines | #the-study |
| Message Prep Scribe | Speaking prep, spiritual message outlines | #the-study |
| Reflection Anchor | End-of-day grounding | — |

---

## Layer 6: Skills (13 Registered)

| Skill | File | Category |
|---|---|---|
| crm-manager | crm-manager.md | CRM/AMS |
| nowcerts-skill | nowcerts-skill.md | CRM/AMS |
| prospect-researcher | prospect-researcher.md | Sales |
| carrier-appetite | carrier-appetite.md | Sales |
| outreach-templates | outreach-templates.md | Sales |
| linkedin-prospecting | linkedin-prospecting.md | Sales |
| renewal-prep | renewal-prep.md | Retention |
| commission-reconciliation | commission-reconciliation.md | Finance |
| vin-lookup | vin-lookup.md | Underwriting |
| property-lookup | property-lookup.md | Underwriting |
| medication-formulary | medication-formulary.md | Medicare |
| medicare-plan-advisor | medicare-plan-advisor.md | Medicare |
| email-triage | email-triage.md | Operations |

### Unregistered (vault only, not in HEARTBEAT.md)
- market-radar-auto-scraper.skill
- overdue-task-actioner.skill
- personalized-followup-drafter.skill
- pre-renewal-intel.skill
- prospect-intelligence-pack.md
- rsg-intel-pack.md

---

## Layer 7: Slack Channels

| Channel | ID | Purpose |
|---|---|---|
| #the-boss | C0ANQUENX4P | Lamar command channel (requireMention: false) |
| #the-morning-commander | C0ANYMH87HR | Daily briefings, 3 non-negotiables |
| #daily-ops-digest | C0ANSEP6SSD | Operational digest (NowCerts Canvas) |
| #service-brief | C0AP2MML9L6 | Renewal scan results, expiration alerts |
| #agency-ops | C0AP4MFKH7U | Pipeline status, weekly health |
| #client-service | C0AP4MHCLLS | Pre-call intel, Gretchen routing |
| #growth-finance | C0AP89NDTHA | Commission flash, deal logging |
| #sales-brief | C0AP1BCEURK | New business, quotes |
| #the-task-list | C0AH4KJAYTU | Task digests, brain dump output |
| #systems-check | C0AFHN83ZE3 | Health checks, WC gaps, n8n errors |
| #the-study | C0AP89HLJKE | Ministry prep |

---

## Layer 8: Trigger Phrases (#the-boss)

| Phrase | Action |
|---|---|
| "brief me" | Renewals + pipeline + tasks + 3 non-negotiables |
| "run renewal scan" | NowCerts 90-day expiring → #service-brief |
| "pipeline status" | Open EspoCRM opportunities by stage |
| "systems check" | NowCerts + EspoCRM connectivity test |
| "brain dump: [text]" | Triage → Act / Schedule / Park / Release |
| "prep me for [company]" | EspoCRM search + prospect brief |
| "commission log: [deal]" | Find/create opportunity + commission calc |
| "what's Gretchen working on" | Gretchen's open EspoCRM tasks |
| "task list" | Lamar tasks (EspoCRM + Supabase) |
| "task list Gretchen" | Gretchen's EspoCRM tasks |

---

## Layer 9: n8n Workflows (18 total)

### Working (8)

| # | Name | ID | Trigger |
|---|---|---|---|
| 2 | NB-WF2 Day 0/1 Onboarding | qbMMleTF4xQDJNGo | Won deal |
| 3 | NB-WF3 Long-term Nurture | J9lZZBwUA2888qkP | Post-onboarding |
| 5 | Renewal Auto-Create | 0npEnsS6D2hpjBfK | Nightly |
| 10 | Nightly Policy Updates | lsgUVFg7RoeDtOLF | Nightly |
| 11 | NowCerts Client Lookup | sIYk2ZQObh8GqCpo | On-demand |
| 12 | Account Rollup Fields | Kyjizvgp5fHKKR6z | Every 6hr |
| 15 | Gmail RSG-Task to EspoCRM | 23kKCvM0tddkVMGk | Gmail label |
| 18 | Global Error Workflow | lWeQqSjVGaDEqTsS | Any error |

### Broken (5)

| # | Name | ID | Root Cause |
|---|---|---|---|
| 1 | NB-WF1 Deal Won Intake | UFwZUwlHi1ERwSXP | Stage string mismatch: "Won-Bound" vs "✅ Won - Bound" |
| 4 | NB Commission Auto-Create | waqicelWdspuaCdf | Same stage mismatch |
| 6 | Renewal Outreach | ptlLTDUBj0XhTRTH | Unfilled MANUS_AI_PERSONALIZATION placeholder |
| 7 | Renewal Stage Auto-Update | wZZooWpIdBqoj5G4 | Stage string mismatch |
| 8 | Renewal Commission Auto-Create | zlzLty9lJmtrPWuI | Stage string mismatch |

### Untested (2)

| # | Name | ID |
|---|---|---|
| 9 | Renewal Retention & Commission Report | NQCSJ2YzT3CK5Mjb |
| 13 | Task Complete Thank You | bsm2iy6m1Tjx2MJz |

### Deleted (3)
- WF14: Escalation Watchdog → replaced by Renewal Watchdog agent
- WF16: Afternoon Pulse → replaced by Morning Commander agent
- WF17: Personal OS Task Reminders → replaced by Task Finisher + Focus Guard

---

## Layer 10: Scheduled Automations

### OpenClaw Heartbeat

| Schedule | Task | Output |
|---|---|---|
| Weekdays 7am ET | Morning Brief | #the-morning-commander |
| Daily 8am ET | Renewal Scan (90-day) | #service-brief |
| Daily 8am ET | Task Digest | #the-task-list |
| Daily 3pm ET | Overdue Check | #the-boss (if items slipping) |
| Monday 9am ET | Pipeline Health | #agency-ops |
| Monday 9am ET | Stale Task Sweep (5+ days) | #the-boss |
| Friday 4pm ET | Commission Flash | #growth-finance |

### n8n Scheduled

| Schedule | Workflow |
|---|---|
| Nightly | Policy Updates (#10) |
| Nightly | Renewal Auto-Create (#5) |
| Every 6hr | Account Rollup (#12) |

### RSG Slack Bot (Mac)

| Schedule | Task |
|---|---|
| 7:00 AM ET | Morning briefing |
| 8:00 AM ET | Sales briefing |

---

## Layer 11: End-to-End Workflows

### New Prospect to Bind
```
"prep me for [company]" in #the-boss
    → prospect-researcher: class codes + carrier appetite
    → Deal Coach: pre-call brief (60 sec)
    → Lamar calls
    → Post-call: EspoCRM Lead/Opportunity created
    → Quote → Follow-up sequence (outreach-templates)
    → Won → n8n WF2/WF3 → commission_ledger
```

### Renewal Cycle
```
Day -90: n8n detects expiry → EspoCRM Renewal (Identified)
Day -60 commercial / -30 personal: renewal-prep skill
    → route to Lamar (commercial) or Gretchen (personal)
    → first touch email (Template 4)
Day -30/-14: Options delivery
    → current carrier + 2-3 alternatives
    → renewal proposal (Template 5)
    → EspoCRM stage: Proposal Sent
Day -21/-10: Close call
    → Won: bind + NowCerts + commission tracking
    → Lost: re-quote task in 10 months
```

### Commission Reconciliation
```
Statement arrives
    → commission-reconciliation skill
    → parse: policy / premium / paid
    → lookup commission_rules: expected rate
    → SmartChoice: RSG net = actual × 0.70
    → Delta ±$1 → auto-match
    → Delta > $200 → high flag
    → Delta > $500 → CRITICAL flag
    → Post Commission Flash to #growth-finance
```

### Medicare Enrollment
```
Client inquiry
    → medicare-plan-advisor skill
    → county footprints → available plans
    → score by priority (budget/coverage/doctors/drugs)
    → top 3 plans + comparison table
    → drug check (medication-formulary)
    → SSBCI wallet match
    → enrollment → NowCerts policy
```

---

## Layer 12: Self-Healing & Gap Detection

| System | Mechanism | Output |
|---|---|---|
| WC class codes | 3-attempt lookup → gap auto-post | #systems-check |
| Stale deals | 14-day auto-stall + digest | #deals |
| Commission deltas | Tolerance-based flagging | #growth-finance |
| System health | "systems check" trigger | #systems-check |
| n8n errors | Global Error Workflow (#18) | #systems-check |
| Overdue tasks | 3pm daily check | #the-boss |
| Stale tasks | Monday sweep 5+ days | #the-boss |

---

## Layer 13: Security & Credentials

| Credential | Storage | Rotates |
|---|---|---|
| NowCerts password | OpenClaw .env, n8n .env | Manual |
| EspoCRM API key | HEARTBEAT.md, n8n .env | Manual |
| Supabase service role key | OpenClaw .env, n8n .env, 1Password | On project recreate |
| Slack bot/app tokens | OpenClaw .env, openclaw.json | Manual |
| GitHub vault token | OpenClaw .env | On expiry |
| Anthropic API key | OpenClaw .env, n8n .env | Manual |
| SSH keys (Elestio) | 1Password (ed25519) | Manual |

- OpenClaw: GATEWAY_TOKEN auth
- EspoCRM: API key (no user RBAC yet)
- Supabase: service role key (RLS disabled)
- Obsidian: local filesystem + private GitHub repo

---

## Current Metrics (2026-03-29)

| Metric | Value |
|---|---|
| Active premium | ~$385K |
| Total policies | 104 |
| Lines of business | 13 |
| RETENTION RATE | 54.92% — TARGET 75%+ CRITICAL |
| Medicare carriers | 10 |
| Medicare plans indexed | 128 |
| GL class codes | 1,154 |
| WC class codes | 156 |
| Commission rules | 216 |
| OpenClaw agents | 15 |
| Registered skills | 13 |
| Slack channels | 11 |
| Supabase tables | 18 |
| n8n workflows | 18 (8 working, 5 broken, 2 untested) |
| Obsidian vault files | 2,109+ |
| States active | GA, AL, FL, SC, TN |
