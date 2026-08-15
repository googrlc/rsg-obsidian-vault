# RSG Operations Architecture — 2026

**Risk Solutions Group** — 2-person insurance agency (Atlanta, GA)
Lamar Coates (Owner/Producer) + Gretchen (CSR/Personal Lines)
~$385K active premium | 104 policies | 13 LOBs | GA, AL, FL, SC, TN
Last updated: 2026-08-14

> **2026-08-14 — Amy front door locked.** Users talk to Amy only through Microsoft 365 Copilot Chat. Specialists are hidden sub-agents. Teams and SharePoint are not agent channels. Canonical Amy doc: [[03-Systems/Architecture/Amy-Copilot-Chat-Architecture]]. Schema recon: [[rsg-infrastructure/Supabase-Recon-2026-08-14]].
>
> **CRM of record is Zoho CRM.** All pipeline, task, and renewal work runs through Zoho CRM (MCP: `user-ZohoMCP`).

---

## Quick Reference

| System | URL / ID |
|---|---|
| Zoho CRM | CRM of record (MCP: `user-ZohoMCP`) |
| Supabase | wibscqhkvpijzqbhjphg (us-east-1) |
| NowCerts API | https://api.nowcerts.com/api |
| NowCerts Agency ID | 09d93486-1536-48d7-9096-59f1f62b6f51 |
| Vault repo | github.com/googrlc/rsg-obsidian-vault |
| Vault local | ~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/ |

---

## Layer 1: Infrastructure

### Servers

| Server | Provider | Purpose |
|---|---|---|
| Elestio VMs | Elestio | Nextcloud (file hosting), LiteLLM (LLM gateway) |
| hermes-vps | DigitalOcean | Hermes agent (Penny/Mattermost) — see [[rsg-infrastructure/Hermes-VPS-DigitalOcean]] |
| Hostinger VPS | Hostinger | Web services via Cloudflare Tunnel `rsg-tunnel` (Hermes, Homebase, Carriers, Command Center) |

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
| github.com/googrlc/rsg-obsidian-vault | Git mirror — agents read skills from the GitHub mirror |

---

## Layer 2: Systems of Record

**One-Way Rule:** Data flows FROM systems of record TO dashboards. Never reverse.

| System | Truth Domain |
|---|---|
| NowCerts | Policy truth (AMS) |
| Zoho CRM | Pipeline truth (CRM) |
| Supabase | Analytics/rules truth |
| Obsidian | Knowledge truth |

### NowCerts / Momentum (AMS)
- Auth: POST https://api.nowcerts.com/api/token (client_id=ngAuthApp)
- Token expiry: ~60 min — remint per session
- Key data: policies, premiums, expiration dates, carriers, insureds

### Zoho CRM (CRM of record)
- Access: MCP server `user-ZohoMCP` (live 2026-08-14)
- Modules: Accounts, Contacts, Leads, Deals, Tasks, Cases
- Custom modules: `Policies`, `Renewals`, `Renewal_Events`, `AMS_Write_Queue`

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
│   ├── Skills/               ← nowcerts-skill, prospect-researcher,
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
    ├── data dictionary.txt
    └── Credentials/
```

---

## Layer 4: AI Access Points

| Tool | Where | Purpose |
|---|---|---|
| Claude Code | Mac CLI / VS Code | Development, architecture, skill authoring |
| Claude (claude.ai) | Web + Obsidian Local REST API | Knowledge work, vault read/write |
| Hermes | DigitalOcean hermes-vps + Hostinger | Internal agent — Slack hub, scheduled briefings |
| ChatGPT | Web | Ad-hoc AI work |
| Amy | Microsoft 365 Copilot Chat | Sole user-facing interface — specialists are hidden sub-agents |
| LiteLLM | Elestio | LLM gateway — model routing for agents |
| Nextcloud | Elestio | File hosting / document exchange |

### Environment / Secrets
All API keys and tokens live in 1Password. Never commit credentials to the vault.

---

## Layer 5: Agent Personas (15)

Persona prompts are platform-agnostic and live in [[03-Systems/Agents/Persona-Design]]. They run through Claude, Hermes, or Amy sub-agents.

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
| Renewal Watchdog | Expiring policy monitoring, Zoho renewal sync | #service-brief |
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

## Layer 6: Skills (12 Registered)

| Skill | File | Category |
|---|---|---|
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
| #systems-check | C0AFHN83ZE3 | Health checks, WC gaps, automation errors |
| #the-study | C0AP89HLJKE | Ministry prep |

---

## Layer 8: Trigger Phrases (#the-boss)

| Phrase | Action |
|---|---|
| "brief me" | Renewals + pipeline + tasks + 3 non-negotiables |
| "run renewal scan" | NowCerts 90-day expiring → #service-brief |
| "pipeline status" | Open Zoho Deals by stage |
| "systems check" | NowCerts + Zoho CRM connectivity test |
| "brain dump: [text]" | Triage → Act / Schedule / Park / Release |
| "prep me for [company]" | Zoho search + prospect brief |
| "commission log: [deal]" | Find/create deal + commission calc |
| "what's Gretchen working on" | Gretchen's open Zoho tasks |
| "task list" | Lamar tasks (Zoho + Supabase) |
| "task list Gretchen" | Gretchen's Zoho tasks |

---

## Layer 9: Automation

> **2026-08-14:** Legacy workflow automation is retired. Automation now runs through Claude/Hermes scheduled tasks and Zoho-native workflows/blueprints. Rebuild any still-needed automation (onboarding emails, renewal outreach, policy sync) against Zoho CRM before relying on it.

---

## Layer 10: Scheduled Automations

### Scheduled Tasks (Hermes / Claude)

| Schedule | Task | Output |
|---|---|---|
| Weekdays 7am ET | Morning Brief | #the-morning-commander |
| Daily 8am ET | Renewal Scan (90-day) | #service-brief |
| Daily 8am ET | Task Digest | #the-task-list |
| Daily 3pm ET | Overdue Check | #the-boss (if items slipping) |
| Monday 9am ET | Pipeline Health | #agency-ops |
| Monday 9am ET | Stale Task Sweep (5+ days) | #the-boss |
| Friday 4pm ET | Commission Flash | #growth-finance |

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
    → Post-call: Zoho Lead/Deal created
    → Quote → Follow-up sequence (outreach-templates)
    → Won → Zoho workflow → commission_ledger
```

### Renewal Cycle
```
Day -90: expiry detected → Zoho Renewal (Identified)
Day -60 commercial / -30 personal: renewal-prep skill
    → route to Lamar (commercial) or Gretchen (personal)
    → first touch email (Template 4)
Day -30/-14: Options delivery
    → current carrier + 2-3 alternatives
    → renewal proposal (Template 5)
    → Zoho stage: Proposal Sent
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
| Overdue tasks | 3pm daily check | #the-boss |
| Stale tasks | Monday sweep 5+ days | #the-boss |

---

## Layer 13: Security & Credentials

| Credential | Storage | Rotates |
|---|---|---|
| NowCerts password | 1Password | Manual |
| Zoho CRM | MCP `user-ZohoMCP` (OAuth) | OAuth refresh |
| Supabase service role key | 1Password | On project recreate |
| Slack bot/app tokens | 1Password | Manual |
| GitHub vault token | 1Password | On expiry |
| Anthropic API key | 1Password | Manual |
| SSH keys (Elestio / DigitalOcean / Hostinger) | 1Password (ed25519) | Manual |

- Zoho CRM: OAuth via MCP
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
| Agent personas | 15 |
| Registered skills | 12 |
| Slack channels | 11 |
| Supabase tables | 18 |
| Obsidian vault files | 2,109+ |
| States active | GA, AL, FL, SC, TN |
