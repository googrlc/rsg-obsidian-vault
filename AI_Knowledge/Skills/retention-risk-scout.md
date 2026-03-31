---
name: retention-risk-scout
description: >
  Proactively scores every active RSG client for retention risk and posts a
  prioritized at-risk list to #the-boss and #service-brief. Triggers on
  "retention scan", "who's at risk", "risk report", "retention check",
  "who might cancel", or on the Wednesday 9am ET weekly auto-schedule.
  Revenue-critical — uses Anthropic. This is the most important agent for
  fixing RSG's 54.92% retention rate.
---

# Retention Risk Scout

## Purpose
Every lost policy is a direct hit to the book. This agent proactively identifies
clients at risk of non-renewal BEFORE they cancel — giving Lamar and Gretchen
time to intervene. Target: move retention from 54.92% → 75%+.

---

## Trigger Phrases
- "retention scan"
- "who's at risk"
- "risk report"
- "retention check"
- "who might cancel"
- "retention risk"

**Scheduled:** Every Wednesday 9:00 AM ET (mid-week so action can happen same week)

---

## Risk Scoring Model

Score each active client 0–100. Higher = more at risk of non-renewal.

### Risk Factors (additive)

| Factor | Points | How to Detect |
|--------|--------|---------------|
| Expiring in ≤30 days with no renewal opportunity in EspoCRM | +35 | NowCerts expiry + EspoCRM renewal pipeline check |
| Expiring in 31–60 days with no outreach logged | +25 | NowCerts expiry + EspoCRM activity check |
| No contact logged in EspoCRM in 90+ days | +20 | EspoCRM last activity date on Account |
| Single policy only (no cross-sell) | +10 | Policy count per client = 1 |
| Premium increased >15% vs prior term | +15 | NowCerts premium comparison |
| Prior non-renewal on record | +20 | EspoCRM renewal stage = Lost in past 12mo |
| No email on file | +5 | EspoCRM contact email blank |
| Commercial Auto only (highest churn LOB) | +10 | LOB = Commercial Auto |

### Risk Tiers
- **🔴 CRITICAL (70–100):** Immediate action — Lamar calls personally
- **🟠 HIGH (50–69):** Action this week — Lamar or Gretchen outreach
- **🟡 MEDIUM (30–49):** Watch — add to renewal pipeline if not there
- **🟢 LOW (0–29):** Healthy — no action needed

---

## Step 1 — Mint NowCerts Token

POST https://api.nowcerts.com/api/token
Body: grant_type=password&username=lamar@risk-solutionsgroup.com&password=dcp1vwv*RCF9fpz*dfh&client_id=ngAuthApp

---

## Step 2 — Pull All Active Policies from NowCerts

GET https://api.nowcerts.com/api/InsuredDetailList?agencyId=09d93486-1536-48d7-9096-59f1f62b6f51&active=True
Authorization: Bearer {token}

For each insured, capture:
- insuredId, insuredName
- All policies: policyNumber, expirationDate, lineOfBusiness, premium
- Group policies by insuredId to get per-client picture

---

## Step 3 — Pull Renewal Pipeline from EspoCRM

GET https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1/Opportunity
  ?where[0][type]=in&where[0][attribute]=stage&where[0][value][]=Identified
  &where[0][value][]=Outreach Sent&where[0][value][]=Quote Requested
  &where[0][value][]=Proposal Sent&where[0][value][]=Negotiating
  &select=name,stage,accountId,closeDate,assignedUserName
  &maxSize=100
X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e

Build a set of accountIds that already have active renewal opportunities.

---

## Step 4 — Pull Last Activity Dates from EspoCRM

GET https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1/Account
  ?select=id,name,lastActivityDate,emailAddress,assignedUserName
  &maxSize=200
X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e

Also pull recent lost renewals (last 12 months):
GET https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1/Opportunity
  ?where[0][type]=in&where[0][attribute]=stage&where[0][value][]=Lost
  &where[1][type]=after&where[1][attribute]=closeDate&where[1][value]=12_months_ago
  &select=accountId,name,closeDate
  &maxSize=100
X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e

---

## Step 5 — Score Every Client

For each active client in NowCerts:
1. Find their soonest expiring policy
2. Check if they have an active renewal opportunity in EspoCRM
3. Check last activity date
4. Count their policies (cross-sell indicator)
5. Check for prior lost renewal
6. Apply scoring model above
7. Assign risk tier

Only surface clients with score ≥ 30 (MEDIUM and above) in the report.

---

## Step 6 — Post Risk Report

**Confirm start in #the-boss:** "🔍 Retention Risk Scout scanning → report incoming"

**Post summary to #the-boss (C0ANQUENX4P):**

```
🎯 *RETENTION RISK REPORT — {date}*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current retention: *54.92%* → Target: 75%

🔴 *CRITICAL ({count} clients — act today)*
• {Client} | Exp: {date} | ${premium} | Score: {N} | {top reason}
• {Client} | Exp: {date} | ${premium} | Score: {N} | {top reason}

🟠 *HIGH RISK ({count} clients — this week)*
• {Client} | Exp: {date} | ${premium} | Score: {N} | {top reason}

🟡 *WATCH ({count} clients — add to pipeline)*
• {Client} | Exp: {date} | ${premium} | Score: {N}

💰 *PREMIUM AT RISK*
• Critical: ${sum}
• High: ${sum}
• Total exposed: ${total}

🎯 *IF YOU SAVE EVERY CRITICAL CLIENT: +{X} pts retention*
```

**Post detailed action list to #service-brief (C0AP2MML9L6):**
For each CRITICAL and HIGH client, generate a specific action:
```
🔴 {Client} — CALL TODAY
• Policy exp: {date} ({N} days) | ${premium} | {LOB}
• Last contact: {date} ({N} days ago)
• No renewal opp in CRM — create one now
• Suggested: Personal call from Lamar, then Gretchen follows up with quote
```

---

## Step 7 — Create EspoCRM Tasks for CRITICAL Clients

For each CRITICAL client with no renewal opportunity:

POST https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1/Task
X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
Content-Type: application/json

{
  "name": "⚠️ RETENTION RISK: {client_name} — renewal outreach needed",
  "status": "Inbox",
  "priority": "High",
  "dateStart": "{today}",
  "dateDue": "{today + 2 days}",
  "description": "Risk score: {score}. Exp: {exp_date}. Premium: ${premium}. Reason: {top_risk_reason}. No active renewal opportunity found — create one and initiate outreach immediately.",
  "parentType": "Account",
  "parentId": "{account_id}"
}

Only create tasks if no open task already exists for this client re: renewal.

---

## Error Handling

| Error | Action |
|-------|--------|
| NowCerts token fails | Post to #systems-check: "❌ Retention Risk Scout: NowCerts auth failed" |
| EspoCRM unreachable | Post report using NowCerts data only; flag "⚠️ CRM data unavailable — scores may be incomplete" |
| No clients score ≥30 | Post: "✅ Retention scan complete — no high-risk clients detected. Book looks stable." |
| Task creation fails | Log to #systems-check; continue with report |

---

## Notes
- LLM: **Anthropic** (revenue-critical — directly tied to retention rate)
- Primary output: **#the-boss (C0ANQUENX4P)**
- Secondary output: **#service-brief (C0AP2MML9L6)**
- EspoCRM tasks: auto-created for CRITICAL clients only
- Schedule: **Wednesday 9:00 AM ET** (mid-week action window)
- Gretchen receives the #service-brief version (plain English, no jargon)
- This is the single highest-leverage agent for fixing the 54.92% retention problem
