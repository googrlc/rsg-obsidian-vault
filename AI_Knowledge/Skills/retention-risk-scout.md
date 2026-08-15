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
| Expiring in ≤30 days with no renewal deal in Zoho CRM | +35 | NowCerts expiry + Zoho CRM renewal pipeline check |
| Expiring in 31–60 days with no outreach logged | +25 | NowCerts expiry + Zoho CRM activity check |
| No contact logged in Zoho CRM in 90+ days | +20 | Zoho CRM last activity date on Account |
| Single policy only (no cross-sell) | +10 | Policy count per client = 1 |
| Premium increased >15% vs prior term | +15 | NowCerts premium comparison |
| Prior non-renewal on record | +20 | Zoho CRM renewal stage = Lost in past 12mo |
| No email on file | +5 | Zoho CRM contact email blank |
| Commercial Auto only (highest churn LOB) | +10 | LOB = Commercial Auto |

### Risk Tiers
- **🔴 CRITICAL (70–100):** Immediate action — Lamar calls personally
- **🟠 HIGH (50–69):** Action this week — Lamar or Gretchen outreach
- **🟡 MEDIUM (30–49):** Watch — add to renewal pipeline if not there
- **🟢 LOW (0–29):** Healthy — no action needed

---

## Step 1 — Mint NowCerts Token

POST https://api.nowcerts.com/api/token
Body: grant_type=password&username=lamar@risk-solutionsgroup.com&password={{NOWCERTS_PASSWORD}}&client_id=ngAuthApp

---

## Step 2 — Pull All Active Policies from NowCerts

GET https://api.nowcerts.com/api/InsuredDetailList?agencyId=09d93486-1536-48d7-9096-59f1f62b6f51&active=True
Authorization: Bearer {token}

For each insured, capture:
- insuredId, insuredName
- All policies: policyNumber, expirationDate, lineOfBusiness, premium
- Group policies by insuredId to get per-client picture

---

## Step 3 — Pull Renewal Pipeline from Zoho CRM

Via Zoho CRM (MCP `user-ZohoMCP`), query Deals:
- Stage in (Identified, Outreach Sent, Quote Requested, Proposal Sent, Negotiating)
- Fields: Deal Name, Stage, Account, Closing Date, Owner
- Max 100 records

Build a set of account IDs that already have active renewal deals.

---

## Step 4 — Pull Last Activity Dates from Zoho CRM

Via Zoho CRM (MCP `user-ZohoMCP`), query Accounts:
- Fields: Account Name, Last Activity Date, Email, Owner
- Max 200 records

Also pull recent lost renewals (last 12 months): Deals where Stage = Lost and Closing Date is within the last 12 months.

---

## Step 5 — Score Every Client

For each active client in NowCerts:
1. Find their soonest expiring policy
2. Check if they have an active renewal deal in Zoho CRM
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

## Step 7 — Create Zoho CRM Tasks for CRITICAL Clients

For each CRITICAL client with no renewal deal, create a Task via Zoho CRM (MCP `user-ZohoMCP`):

```
{
  "Subject": "⚠️ RETENTION RISK: {client_name} — renewal outreach needed",
  "Status": "Not Started",
  "Priority": "High",
  "Due_Date": "{today + 2 days}",
  "Description": "Risk score: {score}. Exp: {exp_date}. Premium: ${premium}. Reason: {top_risk_reason}. No active renewal deal found — create one and initiate outreach immediately.",
  "What_Id": "{account_id}"
}
```

Only create tasks if no open task already exists for this client re: renewal.

---

## Error Handling

| Error | Action |
|-------|--------|
| NowCerts token fails | Post to #systems-check: "❌ Retention Risk Scout: NowCerts auth failed" |
| Zoho CRM unreachable | Post report using NowCerts data only; flag "⚠️ CRM data unavailable — scores may be incomplete" |
| No clients score ≥30 | Post: "✅ Retention scan complete — no high-risk clients detected. Book looks stable." |
| Task creation fails | Log to #systems-check; continue with report |

---

## Notes
- LLM: **Anthropic** (revenue-critical — directly tied to retention rate)
- Primary output: **#the-boss (C0ANQUENX4P)**
- Secondary output: **#service-brief (C0AP2MML9L6)**
- Zoho CRM tasks: auto-created for CRITICAL clients only
- Schedule: **Wednesday 9:00 AM ET** (mid-week action window)
- Gretchen receives the #service-brief version (plain English, no jargon)
- This is the single highest-leverage agent for fixing the 54.92% retention problem
