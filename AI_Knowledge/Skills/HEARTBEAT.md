# RSG HEARTBEAT

## Command Channel
All commands through **#the-boss** (C0ANQUENX4P).
Confirm in #the-boss with one line. Post full output to designated channel.

---

## RSG TEAM
- **Lamar** — EspoCRM user ID: `69bdad92458da2204`
- **Gretchen** — EspoCRM user ID: `69bdf81552aaa`

---

## PIPELINE ENTRY RULES

### Entry Thresholds (when policy enters EspoCRM pipeline)
- **Commercial LOB** → Enter at **60 days** before expiration
  - Commercial Auto, General Liability, Workers Comp, BOP, Umbrella, E&O, Inland Marine, Fleet
- **Personal Lines LOB** → Enter at **30 days** before expiration
  - Personal Auto, Homeowners, Condo, Renters, HO, PAP, Boat, Motorcycle

### Stage Mapping — Commercial (enters at 60 days)
| Days to Expiry | Stage |
|---|---|
| 31–60 days | Renewal Notice Sent |
| 15–30 days | Markets Out / Shopping |
| 8–14 days | Quoted |
| ≤7 days | Presented to Client |
| PENDING CANCEL | Presented to Client + 🚨 flag |

### Stage Mapping — Personal Lines (enters at 30 days)
| Days to Expiry | Stage |
|---|---|
| 15–30 days | Renewal Notice Sent |
| 8–14 days | Markets Out / Shopping |
| 4–7 days | Quoted |
| ≤3 days | Presented to Client |
| PENDING CANCEL | Presented to Client + 🚨 flag |

### Rules
- **Bound / Renewed** and **Non-Renewal / Lost** = MANUAL ONLY. Never auto-assign.
- Never downgrade a stage. If EspoCRM already shows a later stage, leave it.
- If LOB is unclear → default to Personal Lines (30 day threshold).


---

## GRETCHEN'S RENEWAL TASK + EMAIL TEMPLATE

### When to create the task
- **Commercial policy:** Create task when policy enters pipeline at 60 days out
- **Personal Lines policy:** Create task when policy enters pipeline at 30 days out
- Only create ONCE per policy. Check for existing task before creating.

### Create Task in EspoCRM
POST https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1/Task
Header: X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
Body:
{
  "name": "Send Renewal Notice — {insuredName} ({LOB})",
  "status": "Not Started",
  "priority": "High",
  "dateEnd": "{expirationDate minus 25 days for personal, minus 55 days for commercial}",
  "assignedUserId": "69bdf81552aaa",
  "parentType": "Opportunity",
  "parentId": "{opportunity id}",
  "description": "EMAIL TEMPLATE BELOW — copy, personalize, and send to client.\n\n---\n\nSUBJECT: Your {LOB} Policy Renewal — Action Needed\n\nHi {insuredName},\n\nI hope you're doing well! I'm reaching out because your {LOB} policy with {carrierName} is coming up for renewal on {expirationDate}.\n\nHere's a quick summary of your current coverage:\n• Policy #: {policyNumber}\n• Carrier: {carrierName}\n• Line of Business: {LOB}\n• Current Premium: ${premium}/year\n• Expiration Date: {expirationDate}\n\nWe want to make sure you have the best coverage at the best rate. Here's what we're doing for you:\n✅ Reviewing your current coverage for any gaps\n✅ Shopping the market for competitive options\n✅ Preparing renewal options for your review\n\nPlease reply to this email or call us at [AGENCY PHONE] if:\n• Your business/vehicle/property details have changed\n• You'd like to adjust your coverage\n• You have any questions about your policy\n\nWe'll be back in touch shortly with your renewal options. We appreciate your continued trust in Risk Solutions Group!\n\nBest regards,\nGretchen Coates\nRisk Solutions Group\n[PHONE] | [EMAIL]\nhttps://risk-solutionsgroup.com\n\n---\n\nNOTE TO GRETCHEN: Personalize the bracketed fields before sending. Check NowCerts for any recent changes to this account. Flag Lamar if client mentions shopping elsewhere or has complaints."
}


---

## TRIGGER: "@Personal Assistant run renewal scan" OR "@Personal Assistant sync pipeline"
**Output channel:** #service-brief (C0AP2MML9L6)

### Step 1 — Mint NowCerts Token
POST https://api.nowcerts.com/api/token
Body: grant_type=password&username=lamar@risk-solutionsgroup.com&password=dcp1vwv*RCF9fpz*dfh&client_id=ngAuthApp

### Step 2 — Pull Active Insureds + Policies
GET https://api.nowcerts.com/api/InsuredDetailList
Params: agencyId=09d93486-1536-48d7-9096-59f1f62b6f51&active=True
For each insured, get policies:
GET https://api.nowcerts.com/api/policysByInsuredDatabaseId?insuredDatabaseId={databaseId}&agencyId=09d93486-1536-48d7-9096-59f1f62b6f51

### Step 3 — Filter by LOB threshold
- Commercial LOB → include if expirationDate ≤ 60 days from today
- Personal LOB → include if expirationDate ≤ 30 days from today
- Skip if already Bound/Renewed or Non-Renewal/Lost in EspoCRM

### Step 4 — For each policy: Find or create Account
GET /api/v1/Account?searchParams[name]={insuredName}&maxSize=5
Strip LLC/Inc/Ltd suffixes for matching.
If not found → POST /api/v1/Account {"name": "{insuredName}"}

### Step 5 — For each policy: Find or create Opportunity
Search: GET /api/v1/Opportunity?searchParams[name]={insuredName}&maxSize=10
Match if: name contains insuredName AND closeDate within 45 days of expirationDate AND stage NOT Bound/Renewed or Non-Renewal/Lost
- If found → UPDATE stage + closeDate + amount (never downgrade stage)
- If not found → CREATE:
  POST /api/v1/Opportunity
  {
    "name": "{insuredName} — {LOB} Renewal {YEAR}",
    "stage": "{stage per LOB rules}",
    "closeDate": "{expirationDate}",
    "amount": {premium},
    "accountId": "{id}",
    "description": "NowCerts Sync | Policy: {policyNumber} | Carrier: {carrierName} | LOB: {lineOfBusiness} | Days: {N} | Type: {Commercial|Personal}"
  }

### Step 6 — Create Gretchen's Task (NEW entries only, at pipeline entry point)
When creating a NEW Opportunity (not updating existing), create task per template above.
Check for existing task with same name before creating — no duplicates.

### Step 7 — Special flags
- PENDING CANCEL → stage = "Presented to Client", add 🚨 to description, ping Lamar in #the-boss
- Expiring TODAY or TOMORROW → ping Lamar in #the-boss regardless of stage

### Step 8 — Post Summary to #service-brief
```
✅ PIPELINE SYNC COMPLETE — {DATE}
📥 {N} policies evaluated
🆕 {N} new opportunities created
✏️ {N} existing opportunities updated
📋 {N} tasks created for Gretchen
⏭️ {N} skipped (already bound/lost)

🔴 CRITICAL — Contact TODAY:
• {Client | LOB | Exp Date | $Premium}

⚠️ PENDING CANCEL:
• {names}
```

---

## TRIGGER: "@Personal Assistant brief me" OR scheduled 7am ET weekdays
**Output channel:** #the-morning-commander (C0ANYMH87HR)
Run pipeline sync silently, pull Gretchen's open tasks + Lamar's critical renewals.
Post 3 non-negotiables. Lead with revenue at risk.

---

## TRIGGER: "@Personal Assistant pipeline status"
**Output channel:** #agency-ops (C0AP4MFKH7U)
Pull open Opportunities by stage. Show count + $ per stage. Split Commercial vs Personal.

---

## TRIGGER: "@Personal Assistant systems check"
**Output channel:** #systems-check (C0AFHN83ZE3)
Test NowCerts token + EspoCRM contact GET. Report ✅/❌.

---

## TRIGGER: "@Personal Assistant brain dump: [text]"
**Output channel:** #the-task-list (C0AH4KJAYTU)
Triage into Act / Schedule / Park / Release.

---

## TRIGGER: "@Personal Assistant prep me for [company]"
**Output channel:** #client-service (C0AP4MHCLLS)
**Note:** If full intel has NOT been run yet → run prospect-intelligence-pack.md v2.0 first, post to #sales-brief, then post condensed pre-call summary to #client-service.
If intel already run (check `intelRun` = true on Account) → pull existing EspoCRM Account intel fields and post pre-call summary directly.

---

## KEY RULES
- Lamar has ADHD. Bullets only. Dollar amounts always. Dates always.
- Never auto-close a deal. Bound/Renewed and Non-Renewal/Lost = manual only.
- Never downgrade a stage already set in EspoCRM.
- Never create duplicate tasks or opportunities.
- Always ping Lamar for PENDING CANCEL or expiring within 2 days.
- Never silently fail — always post status even on error.

---

## TRIGGER: "task: [description]" OR "email task: [description]"
**Output channel:** #the-task-list (C0AH4KJAYTU)

### Format Lamar uses in #the-boss:
```
task: Call Dream Chaser Trucking about renewal — assign Lamar — due Friday
task: Send renewal email to Trees of Georgia — assign Gretchen — due tomorrow
email task: Follow up with FryBaby on pending cancel — assign Lamar — urgent
```

### What the agent does:
1. Parse the message for:
   - Task description (the main text)
   - Assignee: "assign Lamar" → userId `69bdad92458da2204` | "assign Gretchen" → userId `69bdf81552aaa`
   - Due date: convert plain language to ISO date (tomorrow, Friday, next week, etc.)
   - Priority: "urgent" or "critical" → High | everything else → Normal
   - Linked client: if a known client name appears → search EspoCRM Account and link

2. Create task in EspoCRM:
POST https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1/Task
Header: X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
{
  "name": "{task description}",
  "status": "Not Started",
  "priority": "{High|Normal}",
  "dateEnd": "{due date ISO}",
  "assignedUserId": "{userId}",
  "parentType": "Account",
  "parentId": "{account id if found}",
  "description": "Created via #the-boss by Lamar | {original message}"
}

3. If message contains an email template (multi-line with Subject:) → append full email to task description

4. Confirm in #the-boss: "✅ Task created → assigned to {name} | due {date} | linked to {client or 'no client found'}"
5. Post to #the-task-list: full task details

---

## TRIGGER: "task status" OR "what's pending"
**Output channel:** #the-task-list (C0AH4KJAYTU)

Pull all open EspoCRM tasks:
GET https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1/Task?searchParams[status]=Not Started&maxSize=50
GET https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1/Task?searchParams[status]=In Progress&maxSize=50

Group by assignee. Post:
```
📋 OPEN TASKS — {DATE}

👤 LAMAR ({N} tasks):
• {task name} | due {date} | {priority} | {linked client}

👤 GRETCHEN ({N} tasks):
• {task name} | due {date} | {priority} | {linked client}
```

---

## SCHEDULED: Stale Task Scan
**Runs:** Every weekday at 8:30 AM ET
**Output channel:** #the-task-list (C0AH4KJAYTU)

Pull all open tasks (Not Started + In Progress).
Flag as STALE if:
- Due date has passed → OVERDUE
- Status = "Not Started" and created more than 3 days ago → STUCK
- Status = "In Progress" and not modified in 5+ days → STALE

POST stale report to #the-task-list:
```
⚠️ STALE TASK REPORT — {DATE}

🔴 OVERDUE:
• {task} | assigned {name} | was due {date} | {client}

🟡 STUCK (not started 3+ days):
• {task} | assigned {name} | created {date} | {client}

🟠 STALE (in progress, no update 5+ days):
• {task} | assigned {name} | last updated {date} | {client}
```

If Gretchen has overdue tasks → also ping her directly in #client-service
If Lamar has overdue tasks → ping him in #the-boss

---

---

## TRIGGER: "service request: [client] [type] [details]"
**Posted by:** Gretchen or Lamar in #client-service (C0AP4MHCLLS)
**Output:** Task in EspoCRM + acknowledgement email draft posted back to #client-service

### Format:
```
service request: Gloria Freeman | COI | needs certificate for new job site by Friday
service request: Trees of Georgia | policy change | add vehicle 2024 Freightliner VIN#12345
service request: Matthew Cain | claim | hail damage to condo roof, incident 3/26
service request: Sharon Mitchell | general | needs proof of insurance for lease renewal
```

### Request Type → Priority + SLA
| Type | Priority | SLA |
|---|---|---|
| COI | High | Same business day |
| Claim | High | Same business day |
| Policy Change / Endorsement | High | Same business day |
| General Question | Normal | Within 1 business day |

### What the agent does:
1. Parse: client name, request type, details
2. Search EspoCRM for Account by client name
3. Create Task:
POST /api/v1/Task
{
  "name": "{type} Request — {clientName}",
  "status": "Not Started",
  "priority": "{High|Normal per type}",
  "dateEnd": "{today for High, tomorrow for Normal}",
  "assignedUserId": "69bdf81552aaa",
  "parentType": "Account",
  "parentId": "{account id}",
  "description": "Request Type: {type}\nDetails: {details}\nLogged: {datetime}\nLogged by: {Gretchen|Lamar}"
}

4. Post acknowledgement draft to #client-service for Gretchen to review + send:

---

### ACKNOWLEDGEMENT EMAIL TEMPLATES (Gretchen reviews and sends)

**COI Request:**
```
SUBJECT: Your Certificate of Insurance Request — Risk Solutions Group

Hi {clientFirstName},

Thank you for reaching out! We received your request for a Certificate of Insurance and we're on it.

What we need from you (if not already provided):
• Certificate holder name and address
• Any specific language or additional insured requirements
• Date needed by

We'll have this to you by end of business today. If you need it sooner, reply to this email or call us directly.

Best,
Gretchen Coates
Risk Solutions Group
[PHONE] | gretchen@risk-solutionsgroup.com
```

**Policy Change / Endorsement:**
```
SUBJECT: Policy Change Request Received — Risk Solutions Group

Hi {clientFirstName},

We received your request to make changes to your policy and we're processing it now.

Change requested: {details}

We'll confirm the change with your carrier and follow up with written confirmation. Most endorsements are processed within 1 business day. If this is urgent or time-sensitive, please let us know.

Best,
Gretchen Coates
Risk Solutions Group
[PHONE] | gretchen@risk-solutionsgroup.com
```

**Claim Report:**
```
SUBJECT: Claim Report Received — We're Here to Help

Hi {clientFirstName},

We're sorry to hear about your situation. We received your claim report and want to make sure you're taken care of.

Here's what happens next:
1. We're reviewing your coverage details now
2. We'll connect you with your carrier's claims team
3. We'll follow up to make sure your claim is moving forward

Incident details noted: {details}

Please don't hesitate to call us directly if you have urgent questions or need immediate assistance.

Best,
Gretchen Coates
Risk Solutions Group
[PHONE] | gretchen@risk-solutionsgroup.com
```

**General Question:**
```
SUBJECT: We Got Your Message — Risk Solutions Group

Hi {clientFirstName},

Thanks for reaching out! We received your message and someone from our team will be back to you within 1 business day.

Your question: {details}

If this is urgent, please call us directly at [PHONE].

Best,
Gretchen Coates
Risk Solutions Group
[PHONE] | gretchen@risk-solutionsgroup.com
```

---

## TRIGGER: "completed: [task description or client name]"
**Posted by:** Gretchen in #client-service
**Output:** Completion email draft posted to #client-service

### What the agent does:
1. Search EspoCRM for matching open task by client name or description
2. Update task status → "Completed"
3. Post completion email draft to #client-service:

**COI Completion:**
```
SUBJECT: Your Certificate of Insurance is Ready

Hi {clientFirstName},

Your Certificate of Insurance is attached to this email and ready to use.

Coverage details:
• Policy #: {policyNumber}
• Carrier: {carrierName}
• Effective: {effectiveDate}
• Expires: {expirationDate}

If the certificate holder needs any changes or if you need additional copies, just let us know.

Best,
Gretchen Coates
Risk Solutions Group
[PHONE] | gretchen@risk-solutionsgroup.com
```

**Policy Change Completion:**
```
SUBJECT: Your Policy Change is Confirmed

Hi {clientFirstName},

Your policy has been updated! Here's a summary of what changed:

Change made: {details}
Effective date: {today}
Policy #: {policyNumber}
Carrier: {carrierName}

You'll receive official confirmation from {carrierName} shortly. Please review and contact us if anything looks incorrect.

Best,
Gretchen Coates
Risk Solutions Group
[PHONE] | gretchen@risk-solutionsgroup.com
```

**General Completion:**
```
SUBJECT: Following Up on Your Request — Risk Solutions Group

Hi {clientFirstName},

We wanted to follow up on your recent request: {details}

{GRETCHEN: Add resolution/answer here before sending}

Please don't hesitate to reach out if you have any other questions. We're always happy to help!

Best,
Gretchen Coates
Risk Solutions Group
[PHONE] | gretchen@risk-solutionsgroup.com
```

---

---

## AFLAC GROUP BENEFITS SALES ENGINE

### Target Profile
Employers with 5+ employees already in RSG's book.
LOBs that signal employee headcount: Commercial Auto (fleet = employees), General Liability, Workers Comp, BOP.
Workers Comp clients are the BEST targets — if they have WC, they have employees, full stop.

### TRIGGER: "@Personal Assistant aflac scan"
**Output channel:** #sales-brief (C0AP1BCEURK)

1. Pull all active NowCerts insureds
2. Filter for clients with ANY of: Workers Comp, BOP, Commercial GL, fleet Commercial Auto (3+ vehicles)
3. Search EspoCRM for each — check if "Aflac" or "Group Benefits" opportunity already exists
4. For clients with NO existing Aflac opportunity → flag as target
5. Post to #sales-brief:

```
💼 AFLAC OPPORTUNITY SCAN — {DATE}

🎯 {N} clients identified as Aflac targets

TOP PRIORITY (Workers Comp clients = confirmed employees):
• {Client} | WC Carrier: {carrier} | WC Premium: ${amt} | Est. employees: {N}

STRONG TARGETS (Fleet / GL / BOP):
• {Client} | LOB: {lob} | Premium: ${amt}

Already in pipeline: {N} accounts (skip)
```

6. For top 5 targets → also create EspoCRM Lead:
POST /api/v1/Lead
{
  "firstName": "",
  "lastName": "",
  "accountName": "{insuredName}",
  "status": "New",
  "source": "Existing Client",
  "description": "Aflac Group Benefits opportunity | Current RSG client | LOB: {lob} | Premium: ${amt} | Identified: {date}"
}

---

### TRIGGER: "aflac: [client name]"
**Output channel:** #sales-brief (C0AP1BCEURK)

Pre-call prep for a specific Aflac conversation:
1. Pull client from EspoCRM + NowCerts
2. Post talk track:

```
🦆 AFLAC PREP — {clientName}

CURRENT RSG RELATIONSHIP:
• Policies: {list}
• Total premium: ${amt}
• Client since: {date}
• Last contact: {date}

AFLAC OPPORTUNITY:
• Est. employees: {from WC or fleet size}
• Best products to lead with:
  - Accident Insurance (appeals to contractors/drivers — high risk jobs)
  - Short-Term Disability (protects income — resonates with owner-operators)
  - Critical Illness (tax-free benefit — easy yes for business owners)

TALK TRACK:
"Hey {firstName}, I've been reviewing your coverage and I want to make sure 
your team is fully protected. We work with Aflac to offer voluntary benefits 
your employees get at no cost to you as the employer — accident, disability, 
critical illness. It's a great retention tool and costs you nothing to offer. 
Can I get 15 minutes to show you what this looks like for your team?"

OBJECTION HANDLERS:
• "Too expensive" → "Zero cost to you as employer. Employees pay through payroll deduction."
• "Already have health insurance" → "Aflac covers the gaps — deductibles, lost wages, daily expenses."
• "Too small" → "We work with groups as small as 5. You qualify."
• "Not interested" → "Completely understand. Can I leave you some info for when your situation changes?"
```

---

### AFLAC FOLLOW-UP AUTOMATION

**Stale Aflac leads** (no activity in 5 days) → flag in #sales-brief daily at 8am:
```
⚠️ AFLAC LEADS GOING COLD:
• {client} | Last activity: {date} | Stage: {stage}
  → Suggested action: {call/email/text}
```

### AFLAC PIPELINE STAGES (add to EspoCRM Lead status)
1. New — identified, not yet contacted
2. Contacted — reached out, no response
3. Conversation — had initial talk, interested
4. Enrolled — presented, employees signing up
5. Active Group — Aflac in force
6. Not Interested — closed lost

---

---

## CROSS-SELL ENGINE (Existing Clients)

### TRIGGER: "@Personal Assistant cross-sell scan"
**Output channel:** #sales-brief (C0AP1BCEURK)

1. Pull all active NowCerts insureds
2. For each client, list their current LOBs
3. Identify gaps by client type:

**Trucking/Fleet clients missing:**
- No GL → flag (every trucker needs GL)
- No Physical Damage → flag
- No Occupational Accident → flag (owner-operators)

**Contractors missing:**
- No GL → critical flag
- No Workers Comp → flag
- No Tools & Equipment → flag

**Personal Lines clients missing:**
- Has Personal Auto, no Homeowners → flag
- Has Homeowners, no Umbrella → flag (if premium > $2K)
- Has Auto + HO, no Life → flag

4. Post weekly cross-sell targets to #sales-brief:
```
💰 CROSS-SELL OPPORTUNITIES — {DATE}

🔥 HIGH VALUE (missing critical coverage):
• {Client} | Has: {lob} | Missing: {lob} | Est. premium: ${range}

📋 STANDARD OPPORTUNITIES:
• {Client} | Has: {lob} | Missing: {lob}

Total estimated new premium opportunity: ${total}
```

---

## FMCSA NEW CARRIER LEAD GEN

### TRIGGER: "@Personal Assistant fmcsa leads"
**Output channel:** #sales-brief (C0AP1BCEURK)

1. Search FMCSA public API for new motor carrier registrations:
GET https://mobile.fmcsa.dot.gov/qc/services/carriers/Georgia?webKey=YOUR_KEY
Filter: registration date within last 30 days, state = GA, operation type = carrier

2. For each new carrier:
- Check if already an RSG client (search NowCerts by company name)
- Check if already in EspoCRM
- If new → create Lead in EspoCRM + post to #sales-brief

3. Post:
```
🚛 NEW FMCSA REGISTRATIONS — {DATE}
{N} new Georgia carriers registered in last 30 days

NEW PROSPECTS:
• {Company} | DOT#: {dot} | MC#: {mc} | City: {city} | Operation: {type}
  → Power units: {N} | Drivers: {N}
  → Est. Commercial Auto premium: ${range}
```

**Note:** FMCSA web key needed. Get free key at: https://mobile.fmcsa.dot.gov/developer/home.page
Add to .env as: FMCSA_WEB_KEY=your_key_here

---

## PIPELINE FOLLOW-UP AUTOMATION

### Runs daily at 9am ET — check all open EspoCRM Opportunities
Flag any Opportunity with:
- No activity note in 3+ days AND stage is NOT "Renewal Notice Sent"
- Post to #sales-brief:

```
📞 FOLLOW-UP NEEDED — {DATE}

These deals are going cold:
• {Client} | {LOB} | Stage: {stage} | Last activity: {N} days ago | ${premium}
  → Suggested: {call/email based on stage}
```

For each stale deal → draft a follow-up message in #sales-brief:
```
SUGGESTED FOLLOW-UP for {client}:
"Hey {firstName}, just checking in on your {LOB} renewal/quote. 
We have {carrier} quoting at ${range} — wanted to make sure you had 
the latest options before {expiry date}. Good time to connect?"
```

---

---

## TRIGGER: "@Personal Assistant assess: [company name]" OR "assess: [company]" OR "intel: [company]" OR "run intel on [company]" OR "prep me for [company]" OR "quick intel: [company]"
**Output channel:** #sales-brief (C0AP1BCEURK)
**Skill:** prospect-intelligence-pack.md v2.0

Full commercial risk assessment. Combines 11-source prospect intelligence + underwriting analysis + EspoCRM Account + Lead creation with all intel fields populated.

### What Lamar provides:
```
assess: Dream Chaser Trucking
assess: Atlanta Concrete LLC | poured concrete contractor, 8 employees, Atlanta GA
assess: Southeast Transport | DOT# 3421567 | long haul trucking, 12 power units
intel: Trees of Georgia LLC
run intel on Self Storage of Atlanta
quick intel: ABC Plumbing (runs Website + SOS + LinkedIn only — <2 min)
assess: (document attached — ACORD app or dec page)
```

### Step 1 — Run Prospect Intelligence Pack v2.0
Execute ALL phases from prospect-intelligence-pack.md.
Sources: Website, SOS, SIC/NAICS, LinkedIn, Google Business, BBB, FMCSA (if fleet), OSHA, Google News, Social Media, NowCerts.
Write ALL intel fields to EspoCRM Account. Create Lead linked to Account.
Collect: company profile, existing RSG relationship, FMCSA data, risk signals, SIC/NAICS codes, social profiles.

### Step 2 — SIC/NAICS + Underwriting Analysis
**Already completed in Step 1 (prospect-intelligence-pack.md v2.0 Phase 2, Source 3).**
Fields written: `intelNaics`, `intelSic`, `sicCode`, `industry` (exact enum).

**RSG Operations match:** Query Supabase for GL/WC code suggestions:
```
GET https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/operations_to_codes?keywords=ilike.%{keyword}%&select=operation_name,keywords,notes
Header: apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndpYnNjcWhrdnBpanpxYmhqcGhnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDE0NTkyNiwiZXhwIjoyMDg5NzIxOTI2fQ.VnacqnPjUzxnqTh9Sxt0YXEc4CWjeLeTRYedsRM003I
```

### Step 3 — Pull Risk Scoring Matrix
```
GET /rest/v1/risk_scoring_matrix?industry=eq.{matched_industry}&select=*
```
Extract: base_premium_factor, all LOB multipliers, commission_rate.

### Step 4 — Estimate Premium Ranges
For each suggested LOB, calculate:
- GL: base_premium_factor × gl_multiplier × (employee_count or revenue factor)
- WC: payroll estimate × wc_multiplier
- Commercial Auto: per-vehicle estimate × auto_multiplier
- Umbrella: base umbrella estimate × umbrella_multiplier

### Step 5 — Build Assessment + Create EspoCRM Records

**Create/update EspoCRM Lead:**
```
POST /api/v1/Lead
{
  "accountName": "{company_name}",
  "status": "New",
  "source": "Assessment",
  "industry": "{matched_industry}",
  "description": "ASSESSMENT COMPLETE — {date}\n\n{full assessment summary}"
}
```

**Create EspoCRM Opportunity (if assessment warrants it):**
Only if estimated_premium > $500 AND no red flags blocking placement:
```
POST /api/v1/Opportunity
{
  "name": "{company_name} — {primary_lob} New Business",
  "stage": "Prospect",
  "amount": {estimated_premium_midpoint},
  "closeDate": "{today + 60 days}",
  "description": "Assessment: {ai_summary}\nRed flags: {red_flags}\nSuggested LOBs: {suggested_lobs}"
}
```

**Save to Supabase risk_assessments:**
```
POST https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/risk_assessments
{
  "assessment_name": "{company_name} - {date}",
  "assessment_date": "{today}",
  "commercial_name": "{company_name}",
  "review_status": "Needs Review",
  "line_of_business": "{primary_lob}",
  "ai_confidence": {confidence_score},
  "underwriting_summary": "{full underwriting notes}",
  "red_flags": ["{red_flag_1}", "{red_flag_2}"],
  "favorable_factors": ["{factor_1}"],
  "coverage_requirements": ["{req_1}"],
  "deal_link": "{espocrm_opportunity_url}"
}
```

### Step 6 — Post Assessment to #sales-brief

```
📋 RISK ASSESSMENT — {company_name} | {date}

🏭 OPERATION: {matched_operation}
📊 INDUSTRY: {industry} | Risk Level: {High/Medium/Low}
🤝 RSG STATUS: {Existing Client / New Prospect}

💰 PREMIUM ESTIMATES:
• {LOB}: ${low}–${high}/yr
• {LOB}: ${low}–${high}/yr
TOTAL EST: ${total_low}–${total_high}/yr

✅ FAVORABLE:
• {factor_1}
• {factor_2}

⚠️ RED FLAGS:
• {flag_1}
• {flag_2}

📋 SUGGESTED LOBs: {list}
🔑 KEY ENDORSEMENTS NEEDED: {list}

📊 CONFIDENCE: {High/Medium/Low}
💡 NEXT STEP: {specific recommended action}

🔗 EspoCRM Lead created | Assessment saved to Supabase
```

### Step 7 — Create Lamar Task
```
POST /api/v1/Task
{
  "name": "Follow up — {company_name} assessment",
  "assignedUserId": "69bdad92458da2204",
  "priority": "High",
  "dateEnd": "{today + 2 days}",
  "description": "Assessment complete. Est. premium: ${range}. LOBs: {list}. Red flags: {flags}."
}
```

---

---

## COMMISSION TRACKING ENGINE

### TRIGGER: EspoCRM Opportunity moves to "Bound / Renewed"
**Also triggered by:** "@Personal Assistant log commission: [deal details]"
**Output channel:** #growth-finance (C0AP89NDTHA)

### How to identify New Business vs Renewal
- If Opportunity name contains "Renewal" OR linked to existing NowCerts policy → **Renewal**
- If brand new client or new LOB for existing client → **New Business**
- This distinction drives retention rate calculations

### Step 1 — Pull Opportunity details from EspoCRM
```
GET https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1/Opportunity/{id}
Header: X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
```
Extract: name, amount (premium), stage, closeDate, accountId, accountName, description

### Step 2 — Identify LOB and Carrier
Parse opportunity name and description for:
- LOB: Commercial Auto / Personal Auto / Homeowners / GL / WC / Condo / BOP / Umbrella
- Carrier: PROGRESSIVE / STATE AUTO / SAFECO / ALLSTATE / etc.

### Step 3 — Look up commission rate from Supabase
```
GET https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/commission_rules?lob=eq.{lob}&carrier=eq.{carrier}&select=commission_rate,lamar_split
Header: apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndpYnNjcWhrdnBpanpxYmhqcGhnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDE0NTkyNiwiZXhwIjoyMDg5NzIxOTI2fQ.VnacqnPjUzxnqTh9Sxt0YXEc4CWjeLeTRYedsRM003I
```
If carrier-specific rate found → use it
If no carrier match → fall back to LOB-only rate
If no LOB match → use 12% default

### Step 4 — Calculate and log to Supabase
```
POST https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/commission_ledger
{
  "espocrm_opportunity_id": "{opportunity_id}",
  "espocrm_account_id": "{account_id}",
  "client_name": "{accountName}",
  "lob": "{lob}",
  "carrier": "{carrier}",
  "annual_premium": {amount},
  "commission_rate": {rate},
  "lamar_split": {lamar_split},
  "business_type": "{New Business|Renewal}",
  "bound_date": "{closeDate}",
  "effective_date": "{closeDate}",
  "payment_expected_date": "{closeDate + 60 days}",
  "payment_received": false,
  "notes": "Auto-logged from EspoCRM Opportunity"
}
```

### Step 5 — Post to #growth-finance
```
💰 COMMISSION LOGGED — {date}

{"🆕 NEW BUSINESS" if new else "🔄 RENEWAL"} | {clientName}
📋 LOB: {lob} | Carrier: {carrier}
💵 Premium: ${premium:,} | Rate: {rate}%
💰 Gross Commission: ${gross:,}
🤝 Lamar Commission: ${lamar:,}
📅 Expected payment: {payment_expected_date}
📊 EspoCRM: {opportunity_name}
```

If New Business → also post dopamine hit to #agency-ops:
```
🚀 NEW CLIENT CLOSED — {clientName}
${premium:,} premium | ${lamar:,} commission
```

---

## SCHEDULED: Weekly Commission Flash
**Runs:** Every Friday at 4:00 PM ET
**Output channel:** #growth-finance (C0AP89NDTHA)

```
GET https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/commission_ledger?bound_date=gte.{start_of_week}&select=*
```

Also pull YTD:
```
GET /rest/v1/commission_ledger?bound_date=gte.{start_of_year}&select=*
```

Post to #growth-finance:
```
📊 RSG COMMISSION FLASH — Week of {date}

THIS WEEK:
🆕 New Business: {N} policies | ${new_premium:,} premium | ${new_commission:,} commission
🔄 Renewals: {N} policies | ${renewal_premium:,} premium | ${renewal_commission:,} commission
💰 Week Total: ${week_total:,}

YTD TOTALS:
📈 Total Premium Written: ${ytd_premium:,}
💰 Total Commission Earned: ${ytd_commission:,}
🆕 New Business Premium: ${ytd_new:,}
🔄 Renewal Premium: ${ytd_renewal:,}
📊 Retention Rate: {renewal / (renewal + lost) * 100:.0f}%

⚠️ PENDING PAYMENTS ({N} overdue):
• {client} | ${commission:,} | expected {date} | {days} days overdue
```

---

## SCHEDULED: Payment Tracking Scan
**Runs:** Every Monday at 9:00 AM ET
**Output channel:** #growth-finance (C0AP89NDTHA)

Check for unpaid commissions past expected date:
```
GET /rest/v1/commission_ledger?payment_received=eq.false&payment_expected_date=lte.{today}&select=*
```

If any overdue → post alert:
```
⚠️ COMMISSION PAYMENTS OVERDUE — {date}

{N} payments not yet received:
• {client} | {carrier} | {lob} | ${commission:,} | expected {date} | {N} days overdue

Action: Verify with carrier portal or call carrier AR department.
Type "@Personal Assistant payment received: {client}" when payment arrives.
```

---

## TRIGGER: "@Personal Assistant payment received: [client/carrier]"
**Output channel:** #growth-finance

Find matching commission_ledger record, update payment_received = true, payment_received_date = today.
Post confirmation: "✅ Commission payment logged for {client} — ${amount:,}"

---

## TRIGGER: "@Personal Assistant commission status"
**Output channel:** #growth-finance

Pull full commission summary: YTD totals, pending payments, new vs renewal split, retention rate.

---

## RETENTION RATE CALCULATION
Retention Rate = Renewals Bound / (Renewals Due) × 100

To calculate:
1. Pull all renewal opportunities created in last 12 months from EspoCRM
2. Count those that reached "Bound / Renewed" stage
3. Count those that reached "Non-Renewal / Lost" stage
4. Rate = Bound / (Bound + Lost) × 100
Target: 80%+ | RSG current: ~55% (critical gap — flag if trending down)

---
