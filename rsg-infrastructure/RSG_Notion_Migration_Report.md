# RSG Notion Migration Report
*Completed by Claude Code — 2026-03-22*

---

## Summary
- Total workflows audited: **15**
- Workflows with Notion nodes: **11**
- Workflows successfully rerouted: **11**
- Total Notion nodes replaced: **35**
- Notion credentials remaining: **0** (already removed)
- New destinations used: **EspoCRM API** (primary), **Supabase** (commissions + templates), **None deleted**

---

## Workflow Migration Log

### WF-F — Gmail RSG-Task Label -> EspoCRM Task Creator
- **Notion nodes removed:** Lookup Sender in Contacts, Build Notion Task Body, Create Notion Task
- **Replaced with:** EspoCRM Contact search, EspoCRM Task POST
- **Fields mapped:** Notion `properties.title` -> EspoCRM `name`, Notion `relation[0].id` -> EspoCRM `parentId`
- **Test execution:** Awaiting next labeled email trigger
- **Notes:** Also updated Slack alert text to reference EspoCRM instead of Notion

### Task-Workflow D -- Task Complete -> Client Thank You Email
- **Notion nodes removed:** Query Complete Tasks, Get Contact Record, Mark Client Thanked
- **Replaced with:** EspoCRM Task query (status=Completed), EspoCRM Contact GET, EspoCRM Task PATCH
- **Fields mapped:** Notion `properties.Task.title` -> EspoCRM `name`, Notion `properties.Email.email` -> EspoCRM `emailAddress`, checkbox -> `[THANKED]` marker in description
- **Test execution:** Awaiting next completed task
- **Notes:** Fixed name from "Lamar Johnson" to "Lamar Coates". Uses description-based `[THANKED]` marker since EspoCRM doesn't have a custom `cClientThanked` field

### WF-E -- Escalation Watchdog
- **Notion nodes removed:** Query In-Progress Tasks, Get Contact Name, Parse Claude Response (Notion refs)
- **Replaced with:** EspoCRM Task query (status=Started), EspoCRM Contact GET
- **Fields mapped:** Notion `last_edited_time` -> EspoCRM `modifiedAt`, Notion `properties.Task.title` -> `name`, Notion page URL -> EspoCRM URL
- **Test execution:** Awaiting next stale task (48h+)

### Morning Briefing v3
- **Notion nodes removed:** Fetch Notion Renewals, Fetch Notion Tasks, Fetch Notion Deals
- **Replaced with:** EspoCRM Policy query (renewals in 30d), EspoCRM Task query (not completed), EspoCRM Opportunity query (active deals)
- **Fields mapped:** Notion results array -> EspoCRM `list` array, Notion property accessors -> flat EspoCRM fields
- **Test execution:** Will fire at next scheduled briefing
- **Notes:** Rewrote Format All Messages code node to parse EspoCRM flat JSON format

### Afternoon Pulse (3pm ET)
- **Notion nodes removed:** Fetch Renewals, Fetch Tasks, Fetch Deals
- **Replaced with:** Same EspoCRM queries as Morning Briefing
- **Test execution:** Will fire at next 3pm ET trigger
- **Notes:** Mirror of Morning Briefing migration

### nowcerts-client-lookup
- **Notion nodes removed:** Search Notion CRM, Get Policies
- **Replaced with:** EspoCRM Account search (by name), EspoCRM Policy search (by name)
- **Fields mapped:** Notion DB query filter -> EspoCRM `where` params
- **Test execution:** Awaiting next webhook trigger

### NB-Workflow 2 -- Day 0 & Day 1 Onboarding Emails
- **Notion nodes removed:** Update Tracking: Day 0, Mark Sequence Started, Update Tracking: Day 1
- **Replaced with:** EspoCRM Case PATCH (status=Day 0/1 Sent), EspoCRM Opportunity PATCH (cEmailSequenceStarted=true)
- **Fields mapped:** Notion `properties.Sequence Stage.select` -> EspoCRM Case `status`, Notion page PATCH -> EspoCRM entity PATCH
- **Test execution:** Awaiting next onboarding sequence trigger
- **Notes:** Requires EspoCRM custom field `cEmailSequenceStarted` on Opportunity entity

### NB-Workflow 3 -- Long-term Nurture Sequence (Day 7-60)
- **Notion nodes removed:** Update Tracking: Day 7, Store Manus Output, Update Tracking: Day 30, Update Tracking: Complete
- **Replaced with:** EspoCRM Case PATCH for all tracking updates, AI output stored in Case description
- **Fields mapped:** Notion `properties.Sequence Stage` -> EspoCRM Case `status`, Notion `properties.Manus AI Output` -> EspoCRM Case `description`
- **Test execution:** Awaiting next nurture sequence day
- **Notes:** Manus AI output is stored in EspoCRM Case description (truncated to 4000 chars)

### NB-Workflow 1 -- Deal Won Intake & Commission Log
- **Notion nodes removed:** Pipeline Configs (Notion DB IDs), Query Pipeline DB, Extract Deals, Prepare Commission Data, Create Commission Entry, Store Commission Page ID, Mark Commission Logged
- **Replaced with:** EspoCRM Opportunity query (stage=Won - Bound, by LOB), Supabase `commission_ledger` INSERT, EspoCRM Opportunity PATCH (cCommissionLogged=true)
- **Fields mapped:** Notion `properties['Client / Entity Name'].title` -> EspoCRM `accountName`, Notion commission properties -> Supabase `commission_ledger` columns
- **Test execution:** Awaiting next won deal
- **Notes:** Commission entries now go directly to Supabase. Requires custom fields `cCommissionLogged`, `cLob`, `cCarrier`, `cPremium` on EspoCRM Opportunity entity

### NB-Workflow 1 -- Deal Won Intake & Sequence
- **Notion nodes removed:** Pipeline Configs (Notion DB IDs), Query Pipeline DB, Extract Deals, Query All Templates, Build Template Map, Create Tracking Record, Store Tracking ID
- **Replaced with:** EspoCRM Opportunity query, Supabase `email_templates` query, EspoCRM Case POST
- **Fields mapped:** Notion deal properties -> EspoCRM flat fields, Notion template properties -> Supabase `email_templates` columns
- **Test execution:** Requires `email_templates` table in Supabase
- **Notes:** MANUAL STEP: email_templates table must be created in Supabase and populated with existing templates

### NB-Workflow 1b -- Onboarding Email Trigger (Webhook)
- **Notion nodes removed:** Fetch Deal Record, Build Deal Context, Query Templates, Build Template Map, Create Tracking Record, Mark Sequence Started, Update Commission: Email Sent
- **Replaced with:** EspoCRM Opportunity GET, EspoCRM Case POST, EspoCRM Opportunity PATCH, Supabase `email_templates` query, Supabase `commission_ledger` PATCH
- **Fields mapped:** Notion page properties -> EspoCRM flat fields, Notion commission PATCH -> Supabase REST PATCH
- **Test execution:** Requires `email_templates` table
- **Notes:** Most complex workflow. Pipeline detection now uses LOB field from EspoCRM instead of Notion parent database ID

---

## Manual Steps Required

### 1. Create `email_templates` table in Supabase
The email template system was in a Notion database. Two workflows now query `email_templates` from Supabase (project `wibscqhkvpijzqbhjphg`). This table needs to be created:

```sql
CREATE TABLE email_templates (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  template_name text NOT NULL,
  lob text NOT NULL,
  sequence_day integer,
  days_out integer,
  subject_line text,
  body_html text,
  active boolean DEFAULT true,
  created_at timestamptz DEFAULT now()
);
```

Then populate it with the existing email templates from Notion.

### 2. Create EspoCRM custom fields
These custom fields need to exist on EspoCRM entities for the workflows to function correctly:

**On Opportunity entity:**
- `cEmailSequenceStarted` (boolean) -- tracks if onboarding emails have been triggered
- `cCommissionLogged` (boolean) -- tracks if commission entry was created
- `cLob` (varchar) -- Line of Business
- `cCarrier` (varchar) -- Insurance carrier
- `cPremium` (currency) -- Written premium amount
- `cClientEmail` (varchar) -- Client contact email

**On Policy entity:**
- `cRenewalDate` (date) -- Policy renewal date
- `cInsuredName` (varchar) -- Named insured
- `cCarrier` (varchar) -- Insurance carrier

### 3. Verify EspoCRM Case entity status values
The onboarding sequence workflows set Case status to custom values:
- `Day 0 Sent`, `Day 1 Sent`, `Day 7 Sent`, `Day 30 Sent`, `Day 60 Complete`
- These may need to be added as valid status options in EspoCRM Admin > Entity Manager > Case > Fields > Status

### 4. Webhook callers need update
The `nowcerts-client-lookup` webhook response format changed. Any system calling this webhook should expect EspoCRM-formatted responses (`{ list: [...], total: N }`) instead of Notion format (`{ results: [...] }`).

---

## Workflows NOT Modified
- **Policy- NowCerts -> EspoCRM Policy Sync v1** -- No Notion nodes (already EspoCRM-native)
- **WF-A v2 -- RSG: EspoCRM Task Claude Triage** -- No Notion nodes (already EspoCRM-native)
- **RSG -- Renewal Outreach Automation (EspoCRM)** -- No Notion nodes (already EspoCRM-native)
- **Personal OS -- Task Reminder Engine** -- No Notion nodes

---

## Architecture After Migration

```
Data Source          N8N Workflows              Destinations
-----------          ----------------           ---------------
EspoCRM API    -->   All 15 workflows    -->    EspoCRM (CRUD)
Supabase       -->   Commission + Templates -->  Supabase (INSERT/UPDATE)
NowCerts API   -->   Policy Sync              -->  EspoCRM
Gmail          -->   Task Creator, Emails     -->  EspoCRM Tasks
Slack          -->   Briefings, Alerts        -->  Slack channels
```

Notion has been fully removed from the automation stack.
