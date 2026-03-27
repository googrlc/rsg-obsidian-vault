# Prospect Intelligence Pack — RSG

A fully automated pre-call intelligence workflow for RSG. Given a prospect company name, this skill authenticates to NowCerts, scrapes the company's website, LinkedIn, Google News, and BBB, synthesizes research into structured sales intel, writes the output back to the EspoCRM Lead record, and posts findings to Slack. Lamar gets a 10-second AI summary plus deep research notes, pain points, conversation openers, and cross-sell signals — all before he picks up the phone.

---

## When to Use This Skill

- User says "Run prospect intel on [Company]"
- User says "Research [Company] before my call"
- User says "Prep me for [Company]"
- User says "What do we know about [Company]?"
- User says "assess: [Company]" (triggers full assessment + intel pack)
- A new Lead is created in EspoCRM (automated trigger)

---

## Credentials

| Credential | Value |
|---|---|
| NowCerts token | Mint fresh: POST https://api.nowcerts.com/api/token |
| NowCerts username | lamar@risk-solutionsgroup.com |
| NowCerts password | {{NOWCERTS_PASSWORD}} |
| NowCerts agency ID | 09d93486-1536-48d7-9096-59f1f62b6f51 |
| EspoCRM base URL | https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1 |
| EspoCRM API key | 3d34836b07bb327db8d8fa6b63430c4e |
| Supabase URL | https://wibscqhkvpijzqbhjphg.supabase.co |
| Supabase key | eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndpYnNjcWhrdnBpanpxYmhqcGhnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDE0NTkyNiwiZXhwIjoyMDg5NzIxOTI2fQ.VnacqnPjUzxnqTh9Sxt0YXEc4CWjeLeTRYedsRM003I |

---

## Parameters

| Parameter | Required | Description |
|---|---|---|
| company_name | ✅ | Business name to research |
| contact_name | No | Primary contact if known |
| call_date | No | Date of call (defaults to today) |
| dot_number | No | FMCSA DOT# (for trucking) |
| espocrm_lead_id | No | Auto-populated if triggered from EspoCRM |


---

## Step 0 — Mint NowCerts Token

```
POST https://api.nowcerts.com/api/token
Content-Type: application/x-www-form-urlencoded
Body: grant_type=password&username=lamar@risk-solutionsgroup.com&password={{NOWCERTS_PASSWORD}}&client_id=ngAuthApp
```
Extract: access_token → nowcerts_token

---

## Step 1 — NowCerts Client Lookup

```
GET https://api.nowcerts.com/api/InsuredDetailList
Params: agencyId=09d93486-1536-48d7-9096-59f1f62b6f51&active=True
Header: Authorization: Bearer {nowcerts_token}
```
Search results for company_name match. Extract: existing policies, premium, carriers, LOB.
If found → set existing_client = true, pull all policies.
If not found → set existing_client = false, existing_policies = null.

---

## Step 2 — EspoCRM Lead Lookup / Create

```
GET https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1/Lead?searchParams[accountName]={company_name}&maxSize=5
Header: X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
```
If lead found → use existing lead ID for write-back.
If not found AND triggered manually → create lead:
```
POST /api/v1/Lead
{
  "accountName": "{company_name}",
  "status": "New",
  "source": "Prospect Intelligence Pack",
  "description": "Auto-created by Intel Pack — {date}"
}
```

**Guard:** If lead description already contains "Intel Pack Run: ✅" → STOP. Post to Slack:
"⚠️ Intel already run for {company_name}. Check EspoCRM Lead record."

---

## Step 3 — FMCSA Lookup (Trucking Only)

If dot_number provided OR company name contains trucking/transport/freight/logistics/carrier:
```
GET https://mobile.fmcsa.dot.gov/qc/services/carriers/{dot_number}?webKey={{FMCSA_WEB_KEY}}
```
Extract: power_units, drivers, OOS_rate, operation_classification, safety_rating
If no DOT number → search: GET https://mobile.fmcsa.dot.gov/qc/services/carriers?name={company_name}&webKey={{FMCSA_WEB_KEY}}

---

## Step 4 — Web Research

**Company website:**
Navigate to company website or search "site:company.com OR {company_name} official website"
Read: homepage, /about, /services, /contact
Extract: what they do, size signals, locations, fleet size, employee count hints

**LinkedIn:**
Search: https://www.linkedin.com/search/results/companies/?keywords={company_name}
Read: about, employee_count, specialties, recent_posts, follower_count

**Contact LinkedIn (if contact_name provided):**
Search: https://www.linkedin.com/search/results/people/?keywords={contact_name}+{company_name}
Read: headline, summary, tenure, recent_activity

**Google News (last 12 months):**
Navigate: https://news.google.com/search?q={company_name}&hl=en-US&tbs=qdr:y
Read: top 10 headlines and snippets

**BBB Profile:**
Search: "{company_name} BBB site:bbb.org"
Read: rating, accreditation, complaint_count, complaint_categories

---

## Step 5 — Industry Code Lookup (Live Web Search)

### NAICS Code Lookup
Search naics.com for the business type:
- Navigate: `https://www.naics.com/search/?q={business_type_keywords}`
- Or browse: `https://www.naics.com/six-digit-naics/`
- Extract: 6-digit NAICS code + title + description
- Verify the code matches the business operations described

### SIC Code Lookup
Search Census Bureau SIC list:
- Navigate: `https://www.census.gov/naics/?58967?=&chart=&slc=&s=0000&nc=&view=&q={keywords}&search=Search`
- Or: `https://siccode.com/page/what-is-a-sic-code` for cross-reference
- Extract: 4-digit SIC code + description

### Supabase Risk Profile Lookup
Once industry is identified, match to RSG risk scoring matrix:
```
GET https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/risk_scoring_matrix?industry=eq.{industry}&select=*
Header: apikey: {supabase_key}
```
Also match to GL/WC codes via operations table:
```
GET /rest/v1/operations_to_codes?keywords=ilike.%{keyword}%&select=operation_name,keywords,notes
```
If no exact industry match → use closest industry by type (e.g., "Tree Service" → use "Landscaping" multipliers).
Extract: base_premium_factor, gl_multiplier, wc_multiplier, auto_multiplier, commission_rate

---

## Step 6 — Synthesize with LLM

Feed all research to Claude. Request structured JSON response with these exact keys:

| Key | Description |
|---|---|
| ai_summary | 2–3 sentence pre-call brief (10 second read) |
| web_research | Full notes: Company Overview, Fleet/Payroll/Property Exposure, News Signals, BBB Standing, Existing RSG Relationship |
| pain_points | 2–4 specific pain points or coverage gaps |
| ai_confidence | High / Medium / Low |
| insight_exposure | Specific LOB observation — fleet size, payroll, property, cargo, GL, WC |
| insight_signal | News/LinkedIn/BBB signal that opens a door OR flags underwriting difficulty |
| insight_objection | What might make this account hard to price, place, or retain |
| insight_opener | One specific non-generic question Lamar can lead with |
| insight_relationship | Existing RSG book info if NowCerts found; otherwise null |
| estimated_premium | Estimated annual premium range based on risk scoring matrix |
| suggested_lobs | Array of recommended lines of business to quote |
| aflac_opportunity | true/false — does employee count suggest Aflac Group Benefits? |

Confidence: High = 4-5 good sources | Medium = 2-3 | Low = minimal data

---

## Step 7 — Write Back to EspoCRM Lead

```
PUT https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1/Lead/{lead_id}
Header: X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
{
  "description": "Intel Pack Run: ✅ {date}\n\nAI SUMMARY:\n{ai_summary}\n\nPAIN POINTS:\n{pain_points}\n\nWEB RESEARCH:\n{web_research}\n\nESTIMATED PREMIUM: {estimated_premium}\nSUGGESTED LOBs: {suggested_lobs}\nAFLAC OPPORTUNITY: {aflac_opportunity}",
  "status": "Assigned"
}
```

---

## Step 8 — Post to Slack #sales-brief

Post to #sales-brief (C0AP1BCEURK):

```
🔍 INTEL PACK — {company_name} | {date}

🧠 {ai_summary}

📌 PAIN POINTS: {pain_points}
📊 CONFIDENCE: {ai_confidence}
💰 EST. PREMIUM: {estimated_premium}
📋 SUGGESTED LOBs: {suggested_lobs}
{aflac_line if aflac_opportunity}

💡 OPENER: {insight_opener}
⚠️ WATCH: {insight_objection}

🔗 EspoCRM Lead updated. Ready to call.
```

If existing RSG client → also note: "⚡ EXISTING CLIENT — {existing policies summary}"
If Aflac opportunity → add: "🦆 AFLAC TARGET — {employee_count} employees"

---

## Edge Cases

| Scenario | Action |
|---|---|
| Intel Pack already run (guard triggered) | Stop, post warning to Slack |
| Company not in EspoCRM | Create lead, proceed |
| NowCerts auth fails | Continue without existing relationship data |
| Website inaccessible | Use Google search fallback |
| LinkedIn session expired | Continue, note fallback |
| LLM returns malformed JSON | Retry once with explicit JSON-only instruction |
| All sources fail | Set confidence: Low, still write available data |
| FMCSA key not set | Skip FMCSA step, note in output |

