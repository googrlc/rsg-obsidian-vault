# NB-WF1 — Deal Won Intake & Commission Log
**n8n ID:** `UFwZUwlHi1ERwSXP`
**Status:** 🔴 Broken — stage string mismatch
**Last reviewed:** March 2026

---

## What This Workflow Does

When a deal is marked Won in EspoCRM, this workflow fires three actions in sequence: creates a commission record, sends Lamar a Slack alert, and creates a follow-up task for Gretchen. It is also the upstream trigger for NB-WF2 (Day 0 onboarding email).

---

## Action Steps

### Node 1 — Trigger: EspoCRM Poll
**Type:** Polling trigger (runs every 5 minutes)
**Action:** Queries EspoCRM for Opportunity records where Stage has changed
**Filter condition:** `stage = "✅ Won - Bound"` ← EXACT string required
**Broken value currently:** `stage = "Won-Bound"` ← what the workflow currently checks
**Fields pulled:** id, name, amount, accountId, accountName, assignedUserId, closeDate, type (LOB)

---

### Node 2 — Filter: Check Not Already Processed
**Type:** IF node
**Action:** Checks whether `commissionLogged` checkbox on the Opportunity is false
**Purpose:** Prevents duplicate commission records on re-polls
**Condition:** `commissionLogged != true`
**If true:** Continue to Node 3
**If false:** Stop — skip this record entirely

---

### Node 3 — Create Commission Record in EspoCRM
**Type:** HTTP Request — POST
**Auth:** `X-Api-Key` header
**Endpoint:** `POST /api/v1/Commission`
**Action:** Creates a new Commission entity linked to the Opportunity
**Payload fields written:**
- `name` → "Commission — {accountName} — {closeDate}"
- `opportunityId` → Opportunity ID
- `accountId` → Account ID
- `amount` → Opportunity amount × commission rate
- `lob` → Opportunity type (LOB)
- `status` → "Pending"
- `closeDate` → Opportunity close date
- `assignedUserId` → Lamar's EspoCRM user ID

---

### Node 4 — Mark Opportunity as Commission Logged
**Type:** HTTP Request — PATCH
**Auth:** `X-Api-Key` header
**Endpoint:** `PATCH /api/v1/Opportunity/{id}`
**Action:** Sets `commissionLogged = true` on the Opportunity record
**Payload:** `{ "commissionLogged": true }`
**Purpose:** Prevents Node 2 from reprocessing this record on next 5-minute poll

---

### Node 5 — Slack Dopamine Alert to Lamar
**Type:** HTTP Request — POST (Slack webhook)
**Endpoint:** `$env.SLACK_WEBHOOK_URL`
**Channel:** #agency-ops
**Action:** Posts a win notification to Lamar's Slack immediately on close
**Message format:**
```
💰 NEW WIN — {accountName}
LOB: {lob}
Amount: ${amount}
Close Date: {closeDate}
Commission logged ✅
```

---

### Node 6 — Create Follow-Up Task for Gretchen
**Type:** HTTP Request — POST
**Auth:** `X-Api-Key` header
**Endpoint:** `POST /api/v1/Task`
**Action:** Creates an onboarding task in EspoCRM assigned to Gretchen
**Payload fields written:**
- `name` → "New Client Onboarding — {accountName}"
- `status` → "Not Started"
- `priority` → "High"
- `accountId` → Account ID from Opportunity
- `assignedUserId` → Gretchen's EspoCRM user ID (hardcoded)
- `dateStart` → today
- `dateDue` → today + 1 day
- `description` → "Enter policy into NowCerts. Send welcome email. Confirm coverage effective date."

---

### Node 7 — Error Handler
**Type:** Route to Global Error Workflow
**Action:** On any node failure, passes error details to `RSG — Global Error Workflow` (ID: `lWeQqSjVGaDEqTsS`)
**That workflow then posts to:** #systems-check
**Payload passed:** workflow name, failed node name, error message, opportunity ID

---

## Dependencies

| Dependency | Required Value | Status |
|---|---|---|
| EspoCRM Stage string | `✅ Won - Bound` | 🔴 Fix Node 1 — wrong string |
| EspoCRM API Key | `X-Api-Key` header | 🟢 Set |
| Slack Webhook URL | `$env.SLACK_WEBHOOK_URL` | 🟢 Set |
| commissionLogged field | Checkbox on Opportunity entity | 🟡 Verify field exists in EspoCRM |
| Gretchen's EspoCRM User ID | Hardcoded in Node 6 | 🟡 Verify correct ID |
| Global Error Workflow | ID: `lWeQqSjVGaDEqTsS` | 🟢 Active |

---

## The Fix — One Line Change in Node 1

```
CURRENT (broken):  stage = "Won-Bound"
CORRECT:           stage = "✅ Won - Bound"
```

This single change unblocks all three outputs and triggers NB-WF2 downstream.

---

## Downstream Triggered By This Workflow

- **NB-WF2** — Day 0 & Day 1 onboarding emails (triggers after commission logged)
- **NB-WF3** — Long-term nurture sequence Day 7–60 (triggers after NB-WF2 completes)
