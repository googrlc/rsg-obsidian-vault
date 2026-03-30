---
name: renewal-prep
description: >
  Renewal pipeline workflow skill. Manages 60-day commercial / 30-day personal thresholds, coordinates NowCerts policy data with EspoCRM renewals pipeline. Targets improving RSG's 54.92% retention rate.
---

# Renewal Prep — Pipeline Workflow

**Goal:** Never lose a renewal to neglect. Current retention: 54.92% — target: 75%+.

## Thresholds
| Line | Pipeline Entry | First Touch | Final Push |
|---|---|---|---|
| Commercial | 60 days out | 45 days out | 21 days out |
| Personal Lines | 30 days out | 21 days out | 10 days out |

## Data Sources

### NowCerts (System of Record)
Read `AI_Knowledge/Skills/nowcerts-skill.md` for auth and endpoints.
- Pull expiring policies via InsuredDetailList
- Key fields: `expirationDate`, `premium`, `carrierName`, `lineOfBusiness`, `commercialName`

### EspoCRM (Pipeline Tracking)
Read `AI_Knowledge/Skills/crm-manager.md` for auth and endpoints.
- Module: `Renewal` — tracks pipeline stage, urgency, notes
- Module: `Policy` — links to account, tracks status

### Supabase (Commission Intelligence)
- **Base URL:** `https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1`
- **Auth:** `Bearer {{SUPABASE_SERVICE_ROLE_KEY}}`
- Table: `commission_rules` — lookup renewal commission rate for the carrier/LOB

## Workflow

### Step 1: Pull Expiring Policies from NowCerts
Mint token per `nowcerts-skill.md`. Fetch all policies expiring in next 90 days.

Filter into urgency tiers:
- **🔴 CRITICAL:** 0–14 days
- **🟡 URGENT:** 15–30 days
- **🟢 WATCH:** 31–60 days
- **📋 PIPELINE:** 61–90 days

### Step 2: Match to EspoCRM Renewals
For each expiring policy:
1. Search EspoCRM `Renewal` by account name + LOB
2. If renewal exists → check stage, update if stale
3. If no renewal → create one:
```
POST /api/v1/Renewal
{
  "accountId": "{ACCOUNT_ID}",
  "expiringPolicyId": "{POLICY_ID}",
  "lineOfBusiness": "{LOB}",
  "currentCarrier": "{CARRIER}",
  "pipelineStage": "Identified",
  "urgency": "{TIER}",
  "expirationDate": "{EXP_DATE}",
  "currentPremium": {PREMIUM}
}
```

### Step 3: Calculate Renewal Commission
```
GET /rest/v1/commission_rules?carrier_name=eq.{CARRIER}&lob=eq.{LOB}&state=in.({STATE},ALL)&active=is.true&order=lookup_priority.asc&limit=1&select=renewal_percent,revenue_split_percent,mga_name
```
- Renewal commission = `premium * renewal_percent * revenue_split_percent / 100`
- Note SmartChoice policies: `revenue_split_percent = 70`

### Step 4: Route by Line
| Line | Assigned To | Channel |
|---|---|---|
| Commercial (GL, WC, Auto, BOP, Umbrella) | Lamar | #agency-ops |
| Personal Lines (Home, Auto, Renters) | Gretchen | #client-service |
| Life / Health / Medicare | Lamar | #agency-ops |

### Step 5: Generate Renewal Brief
Post to the appropriate channel:
```
🔄 RENEWAL PIPELINE — {DATE}

🔴 CRITICAL (0-14 days):
• {Client} | {LOB} | {Carrier} | ${premium} | Exp: {date}
  Commission at stake: ${amount} | Stage: {stage}
  ⚠️ Action: {specific next step}

🟡 URGENT (15-30 days):
• {Client} | {LOB} | {Carrier} | ${premium} | Exp: {date}

🟢 WATCH (31-60 days):
• {Client} | {LOB} | {Carrier} | ${premium} | Exp: {date}

RETENTION MATH:
Renewals due this month: {count}
Bound so far: {count} ({percent}%)
Revenue at risk: ${total}
```

## Retention Playbook — Closing the 54.92% Gap

### Why Renewals Slip
1. **No early touch** — client shops when they feel forgotten
2. **Rate shock with no context** — premium increase with no explanation
3. **No alternative quoted** — single carrier = take it or leave it

### Fix: Triple-Touch Sequence
1. **Early touch** (45 days / 21 days): "We're reviewing your renewal — any changes to operations?"
2. **Options delivery** (30 days / 14 days): Present current carrier renewal + 1-2 alternatives
3. **Close call** (21 days / 10 days): Decision meeting — bind or remarket

### Remarket Triggers
- Premium increase > 15%
- Claims in the last 12 months
- Client explicitly unhappy with carrier
- Carrier appetite downgraded for this class

### Win-Back for Lost Renewals
- If renewal lost → update EspoCRM Renewal stage to "Lost", fill `lostReason`
- Set EspoCRM Task: re-quote in 10 months
- Log to commission_ledger as lost revenue for tracking

## Error Handling
- NowCerts token failure → alert #systems-check, skip NowCerts data
- EspoCRM 404 on account → create Account first, then Renewal
- Duplicate renewal detected → update existing, don't create new
