# RSG HEARTBEAT

## Command Channel
All commands from Lamar come through **#the-boss** (C0ANQUENX4P).
Listen here for all trigger phrases. Post outputs to the designated output channels below — never back to #the-boss unless it's a direct reply confirming you started the task.

## Trigger Phrases → Actions → Output Channels

**"run renewal scan"**
→ Read nowcerts-skill.md. Mint NowCerts token using credentials from agent.json. Call GET /api/InsuredDetailList with agencyId from agent.json. Find policies expiring in 90 days. Post results to **#service-brief (C0AP2MML9L6)**. Ping Lamar for anything expiring ≤14 days.

**"brief me"**
→ Read nowcerts-skill.md + crm-manager.md. Pull expiring policies + open EspoCRM opportunities + today's tasks. Generate 3 non-negotiables. Post to **#the-morning-commander (C0ANYMH87HR)**.

**"pipeline status"**
→ Read crm-manager.md. Pull all open Opportunities from EspoCRM. Post pipeline snapshot by stage with dollar values to **#agency-ops (C0AP4MFKH7U)**.

**"systems check"**
→ Test NowCerts token mint. Test EspoCRM GET /api/v1/Contact. Post health status (✅/❌) to **#systems-check (C0AFHN83ZE3)**.

**"brain dump: [text]"**
→ Triage the text into Act / Schedule / Park / Release. Post organized output to **#the-task-list (C0AH4KJAYTU)**.

**"prep me for [company]"**
→ Read crm-manager.md. Search EspoCRM for company. Pull all linked opportunities, contacts, notes. Post pre-call intel summary to **#client-service (C0AP4MHCLLS)**.

**"commission log: [deal details]"**
→ Read crm-manager.md. Find or create the Opportunity in EspoCRM. Calculate estimated commission. Post summary to **#growth-finance (C0AP89NDTHA)**.

**"what's Gretchen working on"**
→ Read crm-manager.md. Pull all open EspoCRM Tasks assigned to Gretchen. Post to **#agency-ops (C0AP4MFKH7U)**.

## Scheduled Tasks

**Daily 8am ET — Renewal Scan**
Same as "run renewal scan" above. Post to #service-brief (C0AP2MML9L6).

**Weekdays 7am ET — Morning Brief**
Same as "brief me" above. Post to #the-morning-commander (C0ANYMH87HR).

**Monday 9am ET — Pipeline Health**
Pull all open + stale EspoCRM opportunities. Post weekly health to #agency-ops (C0AP4MFKH7U).

**Friday 4pm ET — Commission Flash**
Pull all Closed Won opportunities this week. Calculate commissions. Post to #growth-finance (C0AP89NDTHA).

## Credentials
All credentials are in agent.json. Never hardcode keys in this file.
- NowCerts: see agent.json → nowcerts.username / nowcerts.password / nowcerts.agencyId
- EspoCRM: see agent.json → espocrm.apiKey / espocrm.baseUrl
- Supabase: see agent.json → supabase.serviceKey / supabase.projectUrl

## Response Rules
- Confirm in #the-boss with one line that you're on it: "✅ Running renewal scan → posting to #service-brief"
- Post full output to the designated output channel
- Lamar has ADHD — bullets only, dollar amounts always, dates always
- If urgent (≤14 days to expiry) — say CRITICAL and lead with it

**"task list"** (on demand)
→ Query EspoCRM for all open tasks assigned to Lamar (status != Completed). Query Supabase personal_tasks where status IN ('open','in_progress') via POST __https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/personal_tasks__ with Authorization: Bearer [service key from agent.json]. Combine both lists. Sort by priority then due_date. Post to **#the-task-list (C0AH4KJAYTU)** grouped by: 🔴 URGENT → 🟡 HIGH → ⚪ NORMAL. Format: [emoji] [task name] | Due: [date] | [Work/Personal].

**"task list Gretchen"** (on demand)
→ Query EspoCRM for all open tasks assigned to Gretchen (assignedUserId=U09MVBFV9C7, status != Completed). Post to **#the-task-list (C0AH4KJAYTU)**.

## Scheduled Tasks (additions)

**Daily 8am ET — Task Digest**
Pull all open tasks from EspoCRM (Lamar + Gretchen) + Supabase personal_tasks. Post to **#the-task-list (C0AH4KJAYTU)**. Flag anything due today or overdue as 🔴 URGENT. Flag anything open 3+ days with no status change as ⚠️ STALE.

**Daily 3pm ET — Overdue Check**
Query EspoCRM and Supabase for tasks due today that are still Not Started or open. Post only those to **#the-boss (C0ANQUENX4P)** — no noise, just what's slipping. If nothing overdue, post nothing.

**Weekly Monday 9am ET — Stale Task Sweep**
Find all tasks open 5+ days with no status update in either EspoCRM or Supabase. Post to **#the-boss (C0ANQUENX4P)** with: task name, days open, assigned to. Ask Lamar to disposition each one (done/park/defer/delegate/drop).

**"agency snapshot"** (on demand or weekly)
→ POST to Supabase agency_snapshots table via __https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/agency_snapshots__. Pull active_premium, policy_count, client_count, retention_rate from NowCerts. Pull pipeline_value + pipeline_count from EspoCRM open opportunities. Insert row with source='auto'. Compare to prior snapshot (ORDER BY snapshot_date DESC LIMIT 2) and compute delta_premium + delta_retention. Post summary to **#growth-finance (C0AP89NDTHA)**: premium, policies, clients, retention%, milestone gate, week-over-week delta. Flag if retention < 65% (⚠️) or < 55% (🔴 CRITICAL).

**Weekly Monday 8am ET — Agency Performance Snapshot**
Same as "agency snapshot" above. Auto-runs weekly so trend data never has a gap.

**"book health"** / **"book check"** / **"how's the book"** / **"agency scorecard"** / **"weekly scorecard"** (on demand or weekly)
→ Read book-health-monitor.md. Pull active_premium, policy_count, client_count, retention_rate from NowCerts. Pull open pipeline value + deal count from EspoCRM. Pull prior snapshot from Supabase agency_snapshots for week-over-week delta. Save new snapshot row with source='book-health-monitor'. Compute Gate 1 progress ($425K / 60% retention). Build renewal radar: bucket policies into ≤14 days (🔴), 15–30 days (🟡), 31–60 days (📋), 61–90 days (📋) — include premium at risk per bucket. Post full scorecard to **#the-boss (C0ANQUENX4P)**. If any policy ≤14 days: lead scorecard with CRITICAL RENEWALS block. Confirm start with one line in #the-boss: "📋 Book Health Monitor running → scorecard incoming". Use Anthropic.

**Weekly Monday 10am ET — Book Health Scorecard**
Same as "book health" above. Auto-runs every Monday at 10am ET so Lamar starts the week knowing exactly where the agency stands. Never skip — even if NowCerts is slow, post with available data and flag gaps.

## Task Disposition Commands (v2.0)
When Lamar replies to any task alert with one of these single words, act immediately — no confirmation needed:

**`done`** → Set EspoCRM task status = Completed. Log to Supabase agent_logs. Confirm in #the-boss.
**`park`** → Set dateEnd = null, status = Inbox. Confirm in #the-boss.
**`defer [date]`** → Set dateEnd = that date. Confirm in #the-boss.
**`delegate`** → Reassign task to Gretchen. DM Gretchen in plain English with what's needed. Confirm in #the-boss.
**`drop`** → Set status = Cancelled. Confirm in #the-boss.

## Revenue Commands (v2.0)

**"book health"** / **"book check"** / **"how's the book"**
→ Already defined above. Also triggers on these aliases.

**"cold leads"**
→ Read crm-manager.md. Pull all EspoCRM Leads with no activity in 7+ days (lastActivityDate > 7 days or null). Show: name, phone, last contact date, recommended action. Post to **#the-boss (C0ANQUENX4P)**.

**"renewals"**
→ Read crm-manager.md + nowcerts-skill.md. Pull all renewals expiring in 60 days from EspoCRM. Group by pipeline stage with urgency flag. Post to **#the-boss (C0ANQUENX4P)**.

**"commissions"**
→ Read commission-reconciliation.md. Pull Supabase commission_ledger: estimated vs posted vs variance. Show what's missing or overdue. Post to **#growth-finance (C0AP89NDTHA)**.

**"marketing"**
→ Query Supabase marketing_ideas. Pull top 3 unactioned ideas sorted by created_date. Show idea + recommended next step. Post to **#the-boss (C0ANQUENX4P)**.

## Lead Creation from Email or Text (v2.0)
When Lamar pastes an email or text with prospect info (name, phone, referral, insurance need):
1. Extract: Name, Phone, Email, referral source, insurance need
2. Create EspoCRM Lead immediately — status=New, source=Word of Mouth (if referral)
3. Create Follow Up task assigned to Lamar due tomorrow
4. Post confirmation to **#the-boss (C0ANQUENX4P)**: lead name + next action
5. Log to Supabase agent_logs

Valid Lead source values: Call, Email, Existing Customer, Partner, Public Relations, Web Site, Campaign, Word of Mouth, Other

## Win Confirmations (v2.0)
When a deal closes (Opportunity stage = Closed Won) or a renewal saves:
→ Post win summary to **#rsg-wins (C0ANFKMDRUH)**: client name, premium, LOB, effective date.

## Client Data Dual-Write Policy

**Any time client or policy data is created or updated, write to BOTH EspoCRM AND Supabase. Never write to only one.**

**New client / account created**
→ 1. Create Account in EspoCRM (read crm-manager.md for field schema). Capture the returned `id`.
→ 2. Upsert matching row in Supabase `clients` table: POST `https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/clients` with `espocrm_id`, `name`, `phone`, `email`, `state`, `source`, `created_at`. Use `Prefer: resolution=merge-duplicates` header.
→ 3. Confirm both writes in #the-boss: "✅ [Client name] added to EspoCRM + Supabase"

**New policy / opportunity logged**
→ 1. Create or update Opportunity in EspoCRM with premium, LOB, effective date, stage.
→ 2. Upsert to Supabase `policies` table: `espocrm_opportunity_id`, `client_id`, `lob`, `premium`, `effective_date`, `expiration_date`, `carrier`, `status`.
→ 3. If commission data is available: also insert to `commission_ledger` with estimated_commission, split_type (direct/smartchoice), policy_id.

**Lead converted to client**
→ 1. Convert Lead → Account + Contact + Opportunity in EspoCRM.
→ 2. Move Supabase `leads` row to `clients` table. Set `converted_at` timestamp. Preserve original `source` and `referral_source`.

**Renewal saved (Closed Won)**
→ 1. Update EspoCRM Opportunity stage = Closed Won.
→ 2. Update Supabase `policies` row: set `status = active`, update `expiration_date`, log `renewed_at`.
→ 3. Post to **#rsg-wins (C0ANFKMDRUH)**.

**Write failure handling**
→ If EspoCRM write succeeds but Supabase fails: log to Supabase `agent_logs` with `sync_status = espo_only`. Post to **#systems-check** so it can be reconciled. Never silently drop the Supabase write.
→ If Supabase write succeeds but EspoCRM fails: same — log `sync_status = supabase_only` and alert **#systems-check**.

## EspoCRM Field Edge Case Handling

Before ANY EspoCRM write, read espocrm-field-reference.md for the target module. Do not guess field names or enum values.

**Invalid enum values**
→ Check valid options in espocrm-field-reference.md before writing. If the value isn't in the list, map to closest valid option or use "Other". Never pass a raw string that isn't a valid enum — EspoCRM will silently drop the field or return a 400.

**Missing required fields**
→ Required fields by module: Lead (lastName, status), Opportunity (name, stage, amount, closeDate, accountId), Task (name, status, assignedUserId). If data is missing, set a safe default and flag in the post output rather than skipping the record.

**Date format**
→ Always use ISO 8601: `YYYY-MM-DD` for date fields, `YYYY-MM-DD HH:MM:SS` for datetime. Never pass MM/DD/YYYY — EspoCRM will reject or misparse it.

**Relationship / link fields**
→ Use `accountId`, `contactId`, `assignedUserId` — never the name string alone. If you only have a name, do a GET search first to resolve the ID, then write the record.

**Null / empty field behavior**
→ Omit fields you don't have data for — don't pass empty strings or null unless explicitly clearing a field. Passing `""` can overwrite existing values.

**API write failures**
→ On 400/422: log the raw error response to Supabase agent_logs with table=espocrm_errors. Post to **#systems-check (C0AFHN83ZE3)** with: endpoint, payload summary, error code. Do NOT retry more than once without Lamar confirmation.
→ On 401: NowCerts or EspoCRM token likely expired. Re-mint/re-auth and retry once. If still 401, post to **#systems-check** immediately.
→ On 404: Record doesn't exist. Create it fresh rather than updating — but confirm with Lamar first if it's a large record like an Opportunity.

**Gretchen task assignments**
→ Gretchen's EspoCRM assignedUserId: always pull from agent.json → espocrm.gretchenUserId. Never hardcode. When assigning, also post plain-English summary to **#gretchen-tasks**.

## Skills
* crm-manager: crm-manager.md Agents: Personal Assistant, Revenue Sheriff, Deal Coach, Renewal Watchdog, Data Entry Assistant, Morning Commander Description: Universal EspoCRM skill — accounts, contacts, leads, opportunities, policies, renewals, commissions, tasks, calls, meetings. Navigation URLs and full field reference included.
* nowcerts-skill: nowcerts-skill.md Agents: Personal Assistant, Renewal Watchdog, Revenue Sheriff, Morning Commander Description: NowCerts/Momentum AMS — renewal scans, policy lookups, insured data, daily brief.
* prospect-researcher: prospect-researcher.md Agents: Deal Coach, Revenue Sheriff, Morning Commander Description: Pre-call intel for contractors/fleet operators. Queries Supabase carrier_appetite + gl_class_codes + wc_class_codes. Outputs 60-sec Prospect Brief to #the-boss.
* renewal-prep: renewal-prep.md Agents: Renewal Watchdog, Personal Assistant, Morning Commander Description: Renewal pipeline workflow. 60-day commercial / 30-day personal thresholds. NowCerts + EspoCRM coordination. Retention improvement from 54.92% baseline.
* carrier-appetite: carrier-appetite.md Agents: Deal Coach, Revenue Sheriff, Personal Assistant Description: Queries Supabase carrier_appetite + commission_rules + gl_class_codes + wc_class_codes. Returns appetite check with carriers, commission rates, and exclusions.
* outreach-templates: outreach-templates.md Agents: Deal Coach, Message Prep Scribe, Personal Assistant Description: 8 outreach templates — cold contractor, cold fleet, follow-up, renewal notice, renewal proposal, win-back, referral request, LinkedIn. Personalized with CRM and carrier data.
* commission-reconciliation: commission-reconciliation.md Agents: CFO, Revenue Sheriff Description: Supabase commission_ledger + commission_reconciliation tables. Delta tracking, SmartChoice 70/30 split, chargeback exposure monitoring, discrepancy flagging.
* linkedin-prospecting: linkedin-prospecting.md Agents: Deal Coach, Revenue Sheriff Description: Contractor/fleet targeting on LinkedIn. 3-touch outreach sequence, daily targets (5-10 connects, 5 messages), EspoCRM lead logging.
* email-triage: email-triage.md Agents: Personal Assistant, Morning Commander Description: 5-category email routing — Lamar Now, Lamar Today, Gretchen, Low Priority, Archive. Draft responses, Gmail labels, personal lines routed to Gretchen.
* vin-lookup: vin-lookup.md Agents: Deal Coach, Revenue Sheriff, Personal Assistant Description: Decodes VINs via NHTSA vPIC API — year/make/model/GVWR/body class. GVWR classification (Class 1-8), underwriting flags, batch fleet lookup.
* property-lookup: property-lookup.md Agents: Deal Coach, Revenue Sheriff, Personal Assistant Description: Property data via Census geocoder, FEMA flood maps, Georgia county tax assessors (Fulton/DeKalb/Gwinnett/Cobb), ISO protection class. Returns year built, construction, flood zone, replacement cost.
* medication-formulary: medication-formulary.md Agents: Personal Assistant, Morning Commander Description: Drug formulary lookup via OpenFDA + RSG Supabase medicare_medical_rx_matrix. Rx tier comparison across plans, SSBCI chronic condition cross-check, Extra Help eligibility.
* medicare-plan-advisor: medicare-plan-advisor.md Agents: Personal Assistant, Morning Commander Description: Full Medicare plan recommendation engine. Queries county footprints → master plan index → medical/rx matrix → supplemental benefits → provider registry → SSBCI. Scores and ranks top 3 plans by client priority.
* google-calendar: google-calendar.md
* book-health-monitor: book-health-monitor.md Agents: Book Health Monitor (scheduled + on-demand) Description: Weekly agency book health scorecard. Pulls premium, policies, retention from NowCerts. Pipeline value from EspoCRM. Week-over-week delta from Supabase agency_snapshots. Buckets renewals into ≤14/15-30/31-60/61-90 day radar. Tracks Gate 1 progress ($425K / 60%). Posts scannable scorecard to #the-boss every Monday 10am ET. Uses Anthropic.
* gretchen-daily-queue: gretchen-daily-queue (server-deployed) Agents: Personal Assistant, Morning Commander Description: Generates Gretchen's plain-English daily task queue. Pulls open EspoCRM tasks assigned to Gretchen + personal lines renewals due ≤60 days. Posts to #gretchen-tasks every weekday 8:30am ET.
* retention-risk-scout: retention-risk-scout (server-deployed) Agents: Renewal Watchdog, Revenue Sheriff Description: Scores every active RSG client for retention risk. Posts prioritized at-risk list to #the-boss and #service-brief. Uses policy history, renewal stage, and activity signals.
* market-radar-auto-scraper: market-radar-auto-scraper (server-deployed) Agents: Revenue Sheriff, Deal Coach Description: Daily scraper — Georgia SOS new LLC filings in roofing, trucking, construction. Scores leads, logs to EspoCRM, creates follow-up tasks. Trigger: "run market radar", "scrape GA filings", "check new LLCs".
* overdue-task-actioner: overdue-task-actioner (server-deployed) Agents: Personal Assistant, Focus Guard Description: Scans overdue open tasks, classifies each one, drafts a concrete completion action, posts draft to #the-boss for approval before executing. Trigger: "clear my overdue tasks", "action my overdue tasks", "run overdue task sweep".
* personalized-followup-drafter: personalized-followup-drafter (server-deployed) Agents: Deal Coach, Personal Assistant Description: Reads contact history from CRM, drafts a personalized follow-up email referencing the last conversation. Trigger: "draft a follow-up to [name]", "follow up with [name]".
* pre-renewal-intel: pre-renewal-intel (server-deployed) Agents: Renewal Watchdog, Deal Coach Description: Pre-renewal intelligence briefing — industry news, claims history, business growth signals for a named account. Trigger: "prep renewal for [account]", "renewal intel [account]", "pre-renewal briefing for [account]".
