# RSG HEARTBEAT

## Command Channel
All commands from Lamar come through **#the-boss** (C0ANQUENX4P).
Listen here for all trigger phrases. Post outputs to the designated output channels below — never back to #the-boss unless it's a direct reply confirming you started the task.

## Trigger Phrases → Actions → Output Channels

**"run renewal scan"**
→ Read nowcerts-skill.md. Mint NowCerts token using credentials from agent.json. Call GET /api/InsuredDetailList with agencyId from agent.json. Find policies expiring in 90 days. Post results to **#service-brief (C0AP2MML9L6)**. Ping Lamar for anything expiring ≤14 days.

**"brief me"**
→ Read nowcerts-skill.md. Pull expiring policies + open Zoho CRM deals + today's tasks (via MCP `user-ZohoMCP`). Generate 3 non-negotiables. Post to **#the-morning-commander (C0ANYMH87HR)**.

**"pipeline status"**
→ Pull all open Deals from Zoho CRM (MCP `user-ZohoMCP`). Post pipeline snapshot by stage with dollar values to **#agency-ops (C0AP4MFKH7U)**.

**"systems check"**
→ Test NowCerts token mint. Test Zoho CRM connectivity (fetch one Contact via `user-ZohoMCP`). Post health status (✅/❌) to **#systems-check (C0AFHN83ZE3)**.

**"brain dump: [text]"**
→ Triage the text into Act / Schedule / Park / Release. Post organized output to **#the-task-list (C0AH4KJAYTU)**.

**"prep me for [company]"**
→ Search Zoho CRM (MCP `user-ZohoMCP`) for the company. Pull all linked deals, contacts, notes. Post pre-call intel summary to **#client-service (C0AP4MHCLLS)**.

**"commission log: [deal details]"**
→ Find or create the Deal in Zoho CRM. Calculate estimated commission. Post summary to **#growth-finance (C0AP89NDTHA)**.

**"what's Gretchen working on"**
→ Pull all open Zoho CRM Tasks assigned to Gretchen. Post to **#agency-ops (C0AP4MFKH7U)**.

## Scheduled Tasks

**Daily 8am ET — Renewal Scan**
Same as "run renewal scan" above. Post to #service-brief (C0AP2MML9L6).

**Weekdays 7am ET — Morning Brief**
Same as "brief me" above. Post to #the-morning-commander (C0ANYMH87HR).

**Monday 9am ET — Pipeline Health**
Pull all open + stale Zoho CRM deals. Post weekly health to #agency-ops (C0AP4MFKH7U).

**Friday 4pm ET — Commission Flash**
Pull all Closed Won deals this week. Calculate commissions. Post to #growth-finance (C0AP89NDTHA).

## Credentials
All credentials are in 1Password / agent environment config. Never hardcode keys in this file.
- NowCerts: username / password / agencyId (see nowcerts-skill.md)
- Zoho CRM: OAuth via MCP `user-ZohoMCP`
- Supabase: service key / project URL (1Password)

## Response Rules
- Confirm in #the-boss with one line that you're on it: "✅ Running renewal scan → posting to #service-brief"
- Post full output to the designated output channel
- Lamar has ADHD — bullets only, dollar amounts always, dates always
- If urgent (≤14 days to expiry) — say CRITICAL and lead with it

**"task list"** (on demand)
→ Query Zoho CRM for all open tasks assigned to Lamar (status != Completed). Query Supabase personal_tasks where status IN ('open','in_progress') via POST __https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/personal_tasks__ with Authorization: Bearer [service key from 1Password]. Combine both lists. Sort by priority then due_date. Post to **#the-task-list (C0AH4KJAYTU)** grouped by: 🔴 URGENT → 🟡 HIGH → ⚪ NORMAL. Format: [emoji] [task name] | Due: [date] | [Work/Personal].

**"task list Gretchen"** (on demand)
→ Query Zoho CRM for all open tasks assigned to Gretchen (status != Completed). Post to **#the-task-list (C0AH4KJAYTU)**.

## Scheduled Tasks (additions)

**Daily 8am ET — Task Digest**
Pull all open tasks from Zoho CRM (Lamar + Gretchen) + Supabase personal_tasks. Post to **#the-task-list (C0AH4KJAYTU)**. Flag anything due today or overdue as 🔴 URGENT. Flag anything open 3+ days with no status change as ⚠️ STALE.

**Daily 3pm ET — Overdue Check**
Query Zoho CRM and Supabase for tasks due today that are still Not Started or open. Post only those to **#the-boss (C0ANQUENX4P)** — no noise, just what's slipping. If nothing overdue, post nothing.

**Weekly Monday 9am ET — Stale Task Sweep**
Find all tasks open 5+ days with no status update in either Zoho CRM or Supabase. Post to **#the-boss (C0ANQUENX4P)** with: task name, days open, assigned to. Ask Lamar to disposition each one (done/park/defer/delegate/drop).

**"agency snapshot"** (on demand or weekly)
→ POST to Supabase agency_snapshots table via __https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/agency_snapshots__. Pull active_premium, policy_count, client_count, retention_rate from NowCerts. Pull pipeline_value + pipeline_count from Zoho CRM open deals. Insert row with source='auto'. Compare to prior snapshot (ORDER BY snapshot_date DESC LIMIT 2) and compute delta_premium + delta_retention. Post summary to **#growth-finance (C0AP89NDTHA)**: premium, policies, clients, retention%, milestone gate, week-over-week delta. Flag if retention < 65% (⚠️) or < 55% (🔴 CRITICAL).

**Weekly Monday 8am ET — Agency Performance Snapshot**
Same as "agency snapshot" above. Auto-runs weekly so trend data never has a gap.

**"book health"** / **"book check"** / **"how's the book"** / **"agency scorecard"** / **"weekly scorecard"** (on demand or weekly)
→ Read book-health-monitor.md. Pull active_premium, policy_count, client_count, retention_rate from NowCerts. Pull open pipeline value + deal count from Zoho CRM. Pull prior snapshot from Supabase agency_snapshots for week-over-week delta. Save new snapshot row with source='book-health-monitor'. Compute Gate 1 progress ($425K / 60% retention). Build renewal radar: bucket policies into ≤14 days (🔴), 15–30 days (🟡), 31–60 days (📋), 61–90 days (📋) — include premium at risk per bucket. Post full scorecard to **#the-boss (C0ANQUENX4P)**. If any policy ≤14 days: lead scorecard with CRITICAL RENEWALS block. Confirm start with one line in #the-boss: "📋 Book Health Monitor running → scorecard incoming". Use Anthropic.

**Weekly Monday 10am ET — Book Health Scorecard**
Same as "book health" above. Auto-runs every Monday at 10am ET so Lamar starts the week knowing exactly where the agency stands. Never skip — even if NowCerts is slow, post with available data and flag gaps.

## Task Disposition Commands (v2.0)
When Lamar replies to any task alert with one of these single words, act immediately — no confirmation needed:

**`done`** → Set Zoho CRM task status = Completed. Log to Supabase agent_logs. Confirm in #the-boss.
**`park`** → Clear due date, status = Deferred. Confirm in #the-boss.
**`defer [date]`** → Set due date = that date. Confirm in #the-boss.
**`delegate`** → Reassign task to Gretchen. DM Gretchen in plain English with what's needed. Confirm in #the-boss.
**`drop`** → Set status = Cancelled. Confirm in #the-boss.

## Revenue Commands (v2.0)

**"book health"** / **"book check"** / **"how's the book"**
→ Already defined above. Also triggers on these aliases.

**"cold leads"**
→ Pull all Zoho CRM Leads with no activity in 7+ days (last activity > 7 days or null). Show: name, phone, last contact date, recommended action. Post to **#the-boss (C0ANQUENX4P)**.

**"renewals"**
→ Read nowcerts-skill.md. Pull all renewals expiring in 60 days from Zoho CRM. Group by pipeline stage with urgency flag. Post to **#the-boss (C0ANQUENX4P)**.

**"commissions"**
→ Read commission-reconciliation.md. Pull Supabase commission_ledger: estimated vs posted vs variance. Show what's missing or overdue. Post to **#growth-finance (C0AP89NDTHA)**.

**"marketing"**
→ Query Supabase marketing_ideas. Pull top 3 unactioned ideas sorted by created_date. Show idea + recommended next step. Post to **#the-boss (C0ANQUENX4P)**.

## Lead Creation from Email or Text (v2.0)
When Lamar pastes an email or text with prospect info (name, phone, referral, insurance need):
1. Extract: Name, Phone, Email, referral source, insurance need
2. Create Zoho CRM Lead immediately — Lead_Status=New, Lead_Source=Word of Mouth (if referral)
3. Create Follow Up task assigned to Lamar due tomorrow
4. Post confirmation to **#the-boss (C0ANQUENX4P)**: lead name + next action
5. Log to Supabase agent_logs

Valid Lead source values: Call, Email, Existing Customer, Partner, Public Relations, Web Site, Campaign, Word of Mouth, Other

## Win Confirmations (v2.0)
When a deal closes (Deal stage = Closed Won) or a renewal saves:
→ Post win summary to **#rsg-wins (C0ANFKMDRUH)**: client name, premium, LOB, effective date.

## Client Data Dual-Write Policy

**Any time client or policy data is created or updated, write to BOTH Zoho CRM AND Supabase. Never write to only one.**

**New client / account created**
→ 1. Create Account in Zoho CRM (MCP `user-ZohoMCP`). Capture the returned record `id`.
→ 2. Upsert matching row in Supabase `clients` table: POST `https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/clients` with `zoho_crm_id`, `name`, `phone`, `email`, `state`, `source`, `created_at`. Use `Prefer: resolution=merge-duplicates` header.
→ 3. Confirm both writes in #the-boss: "✅ [Client name] added to Zoho CRM + Supabase"

**New policy / deal logged**
→ 1. Create or update Deal in Zoho CRM with premium, LOB, effective date, stage.
→ 2. Upsert to Supabase `policies` table: `zoho_crm_deal_id`, `client_id`, `lob`, `premium`, `effective_date`, `expiration_date`, `carrier`, `status`.
→ 3. If commission data is available: also insert to `commission_ledger` with estimated_commission, split_type (direct/smartchoice), policy_id.

**Lead converted to client**
→ 1. Convert Lead → Account + Contact + Deal in Zoho CRM.
→ 2. Move Supabase `leads` row to `clients` table. Set `converted_at` timestamp. Preserve original `source` and `referral_source`.

**Renewal saved (Closed Won)**
→ 1. Update Zoho CRM Deal stage = Closed Won.
→ 2. Update Supabase `policies` row: set `status = active`, update `expiration_date`, log `renewed_at`.
→ 3. Post to **#rsg-wins (C0ANFKMDRUH)**.

**Write failure handling**
→ If Zoho CRM write succeeds but Supabase fails: log to Supabase `agent_logs` with `sync_status = zoho_only`. Post to **#systems-check** so it can be reconciled. Never silently drop the Supabase write.
→ If Supabase write succeeds but Zoho CRM fails: same — log `sync_status = supabase_only` and alert **#systems-check**.

## Zoho CRM Field Handling

Before ANY Zoho CRM write, confirm field API names and picklist values for the target module (via `user-ZohoMCP` metadata). Do not guess field names or picklist values.

**Invalid picklist values**
→ Check valid options before writing. If the value isn't in the list, map to closest valid option or use "Other". Never pass a raw string that isn't a valid picklist value — Zoho CRM will reject the write.

**Missing required fields**
→ If required data is missing, set a safe default and flag it in the post output rather than skipping the record.

**Date format**
→ Always use ISO 8601: `YYYY-MM-DD` for date fields, `YYYY-MM-DDTHH:MM:SS` for datetime. Never pass MM/DD/YYYY.

**Relationship / lookup fields**
→ Use record IDs for lookups (Account, Contact, Owner) — never the name string alone. If you only have a name, search first to resolve the ID, then write the record.

**Null / empty field behavior**
→ Omit fields you don't have data for — don't pass empty strings or null unless explicitly clearing a field.

**API write failures**
→ On 400/422: log the raw error response to Supabase agent_logs with table=zoho_errors. Post to **#systems-check (C0AFHN83ZE3)** with: module, payload summary, error code. Do NOT retry more than once without Lamar confirmation.
→ On 401: OAuth token likely expired. Refresh and retry once. If still 401, post to **#systems-check** immediately.
→ On 404: Record doesn't exist. Create it fresh rather than updating — but confirm with Lamar first if it's a large record like a Deal.

**Gretchen task assignments**
→ Gretchen's Zoho CRM user ID: always pull from agent config — never hardcode. When assigning, also post plain-English summary to **#gretchen-tasks**.

## Skills
* nowcerts-skill: nowcerts-skill.md Agents: Personal Assistant, Renewal Watchdog, Revenue Sheriff, Morning Commander Description: NowCerts/Momentum AMS — renewal scans, policy lookups, insured data, daily brief.
* prospect-researcher: prospect-researcher.md Agents: Deal Coach, Revenue Sheriff, Morning Commander Description: Pre-call intel for contractors/fleet operators. Queries Supabase carrier_appetite + gl_class_codes + wc_class_codes. Outputs 60-sec Prospect Brief to #the-boss.
* renewal-prep: renewal-prep.md Agents: Renewal Watchdog, Personal Assistant, Morning Commander Description: Renewal pipeline workflow. 60-day commercial / 30-day personal thresholds. NowCerts + Zoho CRM coordination. Retention improvement from 54.92% baseline.
* carrier-appetite: carrier-appetite.md Agents: Deal Coach, Revenue Sheriff, Personal Assistant Description: Queries Supabase carrier_appetite + commission_rules + gl_class_codes + wc_class_codes. Returns appetite check with carriers, commission rates, and exclusions.
* outreach-templates: outreach-templates.md Agents: Deal Coach, Message Prep Scribe, Personal Assistant Description: 8 outreach templates — cold contractor, cold fleet, follow-up, renewal notice, renewal proposal, win-back, referral request, LinkedIn. Personalized with CRM and carrier data.
* commission-reconciliation: commission-reconciliation.md Agents: CFO, Revenue Sheriff Description: Supabase commission_ledger + commission_reconciliation tables. Delta tracking, SmartChoice 70/30 split, chargeback exposure monitoring, discrepancy flagging.
* linkedin-prospecting: linkedin-prospecting.md Agents: Deal Coach, Revenue Sheriff Description: Contractor/fleet targeting on LinkedIn. 3-touch outreach sequence, daily targets (5-10 connects, 5 messages), Zoho CRM lead logging.
* email-triage: email-triage.md Agents: Personal Assistant, Morning Commander Description: 5-category email routing — Lamar Now, Lamar Today, Gretchen, Low Priority, Archive. Draft responses, Gmail labels, personal lines routed to Gretchen.
* vin-lookup: vin-lookup.md Agents: Deal Coach, Revenue Sheriff, Personal Assistant Description: Decodes VINs via NHTSA vPIC API — year/make/model/GVWR/body class. GVWR classification (Class 1-8), underwriting flags, batch fleet lookup.
* property-lookup: property-lookup.md Agents: Deal Coach, Revenue Sheriff, Personal Assistant Description: Property data via Census geocoder, FEMA flood maps, Georgia county tax assessors (Fulton/DeKalb/Gwinnett/Cobb), ISO protection class. Returns year built, construction, flood zone, replacement cost.
* medication-formulary: medication-formulary.md Agents: Personal Assistant, Morning Commander Description: Drug formulary lookup via OpenFDA + RSG Supabase medicare_medical_rx_matrix. Rx tier comparison across plans, SSBCI chronic condition cross-check, Extra Help eligibility.
* medicare-plan-advisor: medicare-plan-advisor.md Agents: Personal Assistant, Morning Commander Description: Full Medicare plan recommendation engine. Queries county footprints → master plan index → medical/rx matrix → supplemental benefits → provider registry → SSBCI. Scores and ranks top 3 plans by client priority.
* google-calendar: google-calendar.md
* book-health-monitor: book-health-monitor.md Agents: Book Health Monitor (scheduled + on-demand) Description: Weekly agency book health scorecard. Pulls premium, policies, retention from NowCerts. Pipeline value from Zoho CRM. Week-over-week delta from Supabase agency_snapshots. Buckets renewals into ≤14/15-30/31-60/61-90 day radar. Tracks Gate 1 progress ($425K / 60%). Posts scannable scorecard to #the-boss every Monday 10am ET. Uses Anthropic.
* gretchen-daily-queue: gretchen-daily-queue (server-deployed) Agents: Personal Assistant, Morning Commander Description: Generates Gretchen's plain-English daily task queue. Pulls open Zoho CRM tasks assigned to Gretchen + personal lines renewals due ≤60 days. Posts to #gretchen-tasks every weekday 8:30am ET.
* retention-risk-scout: retention-risk-scout (server-deployed) Agents: Renewal Watchdog, Revenue Sheriff Description: Scores every active RSG client for retention risk. Posts prioritized at-risk list to #the-boss and #service-brief. Uses policy history, renewal stage, and activity signals.
* market-radar-auto-scraper: market-radar-auto-scraper (server-deployed) Agents: Revenue Sheriff, Deal Coach Description: Daily scraper — Georgia SOS new LLC filings in roofing, trucking, construction. Scores leads, logs to Zoho CRM, creates follow-up tasks. Trigger: "run market radar", "scrape GA filings", "check new LLCs".
* overdue-task-actioner: overdue-task-actioner (server-deployed) Agents: Personal Assistant, Focus Guard Description: Scans overdue open tasks, classifies each one, drafts a concrete completion action, posts draft to #the-boss for approval before executing. Trigger: "clear my overdue tasks", "action my overdue tasks", "run overdue task sweep".
* personalized-followup-drafter: personalized-followup-drafter (server-deployed) Agents: Deal Coach, Personal Assistant Description: Reads contact history from CRM, drafts a personalized follow-up email referencing the last conversation. Trigger: "draft a follow-up to [name]", "follow up with [name]".
* pre-renewal-intel: pre-renewal-intel (server-deployed) Agents: Renewal Watchdog, Deal Coach Description: Pre-renewal intelligence briefing — industry news, claims history, business growth signals for a named account. Trigger: "prep renewal for [account]", "renewal intel [account]", "pre-renewal briefing for [account]".
