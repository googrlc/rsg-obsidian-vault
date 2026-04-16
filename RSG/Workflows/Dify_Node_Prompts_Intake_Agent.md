# Dify Node Prompts — RSG Client Intake & Assessment
# Copy/paste each prompt directly into the corresponding Dify node
# Last updated: 2026-04-08

---

## SETUP INSTRUCTIONS FOR CLAUDE CODE

1. Open Dify → find "RSG Commercial Assessment" → click the 3-dot menu → Duplicate
2. Rename the duplicate to: RSG Client Intake & Assessment
3. Update the description to:
   "Gretchen — use this for every new client or prospect. Upload dec pages,
   paste call notes, or enter whatever you have. Works for commercial AND
   personal lines. The agent researches the business or property online,
   checks vehicle values, estimates home rebuild costs, creates the client
   record in EspoCRM, and produces a full assessment report. Start here
   for every new account."
4. Add each node below in order. Connect them as specified.
5. Do NOT delete or modify any existing nodes — only add and update.

---

## NODE 1 — UPDATE: Start Node
# Action: Edit the existing Start node. Add these two new input fields.
# Do NOT remove existing fields.

NEW FIELD 1:
- Type: dropdown (select)
- Label: Client Type
- Variable: client_type
- Required: Yes
- Options:
    Commercial Lines
    Personal Lines
    Both — Commercial + Personal
- Help text: "Select Commercial if this is a business account. Select Personal
  for home and auto only. Select Both if the client has business AND personal
  policies with RSG."

NEW FIELD 2:
- Type: paragraph (long text)
- Label: Additional Notes
- Variable: additional_notes
- Required: No
- Help text: "Paste call transcripts, voice notes, or anything else you know
  about this client that isn't in the uploaded documents."

---

## NODE 2 — NEW: Detect Client Type
# Action: Add a new IF/ELSE node (Dify calls this "Condition" node)
# Position: After Start, before Extract Business Info
# Title: Detect Client Type

Condition logic:
- IF client_type == "Personal Lines" → route to NODE 3 (Personal Lines Extract)
- IF client_type == "Commercial Lines" → route to existing Extract Business Info
- IF client_type == "Both — Commercial + Personal" → route to BOTH in parallel

# Note for Claude Code: Dify supports parallel branches. Wire Both → two
# simultaneous paths: one to existing Extract Business Info, one to NODE 3.

---

## NODE 3 — NEW: Personal Lines Extract
# Action: Add a new LLM node
# Title: Extract Personal Lines Info
# Model: claude-sonnet-4-20250514 | Temperature: 0.1
# Vision: ENABLED (reads uploaded PDFs/images)
# Position: Parallel branch from Detect Client Type
# Connects to: NODE 4 (VIN & Auto Market Value)

SYSTEM PROMPT:
---
You are an expert personal lines insurance analyst for Risk Solutions Group,
Atlanta GA.

Extract ALL personal lines information from the uploaded documents and notes.
Return a single JSON object with exactly these fields. If a field is not found,
use null — never guess.

{
  "named_insured": "",
  "co_insured": "",
  "mailing_address": "",
  "county": "",

  "vehicles": [
    {
      "year": "",
      "make": "",
      "model": "",
      "trim": "",
      "vin": "",
      "primary_driver": "",
      "dl_number": "",
      "dl_state": "",
      "current_carrier": "",
      "policy_number": "",
      "policy_period": "",
      "annual_premium": null,
      "bi_per_person": "",
      "bi_per_occurrence": "",
      "property_damage": "",
      "comprehensive_deductible": "",
      "collision_deductible": "",
      "comp_coll_present": true,
      "um_uim": "",
      "medical_payments": ""
    }
  ],

  "properties": [
    {
      "address": "",
      "county": "",
      "dwelling_type": "",
      "current_carrier": "",
      "policy_number": "",
      "policy_period": "",
      "annual_premium": null,
      "coverage_a_dwelling": null,
      "coverage_b_other_structures": null,
      "coverage_c_personal_property": null,
      "coverage_d_loss_of_use": null,
      "personal_liability": null,
      "medical_payments": null,
      "deductible": null,
      "square_footage": null,
      "year_built": null,
      "scheduled_items": [],
      "endorsements": []
    }
  ],

  "additional_policies": [],
  "notes": ""
}

Return ONLY the JSON. No prose, no markdown fences.
---

USER PROMPT:
Additional Notes from agent: {{#start.additional_notes#}}

Extract all personal lines information from the uploaded documents above.

---

## NODE 4 — NEW: VIN & Auto Market Value Lookup
# Action: Add a new LLM node with web search tool enabled
# Title: Vehicle Research & Market Value
# Model: claude-sonnet-4-20250514 | Temperature: 0.1
# Tools: Web Search ENABLED
# Position: After NODE 3 (Personal Lines Extract)
# Connects to: NODE 5 (Property Records & Rebuild Cost)

SYSTEM PROMPT:
---
You are a vehicle research analyst for RSG, an insurance agency in Atlanta GA.

For each vehicle in the personal lines data provided, you will:
1. Use web search to find the current retail market value
2. Compare it to the current coverage on the policy
3. Flag any issues

SEARCH QUERY FORMAT for each vehicle:
"[year] [make] [model] [trim] retail value Georgia 2026"

Use KBB (kbb.com), Edmunds, or CarGurus as sources.
Extract the PRIVATE PARTY or RETAIL value — use the midpoint if a range is given.

For each vehicle, determine and return one of these flags:

UNDERINSURED: Market value is significantly higher than what the policy would
pay out. Example: vehicle worth $28,000 but property damage limit is $15,000.

PREMIUM WASTE: Vehicle retail value is under $6,000 but the policy includes
comprehensive and/or collision coverage. Flag as potential savings opportunity.

ADEQUATE: Coverage appears appropriate for the vehicle's current market value.

UNKNOWN: Insufficient vehicle details to perform a lookup (missing year/make/model).

Return a JSON array — one object per vehicle:
[
  {
    "vehicle": "[year] [make] [model]",
    "vin": "",
    "market_value_low": null,
    "market_value_high": null,
    "market_value_midpoint": null,
    "market_value_source": "",
    "current_comp_coll_present": true,
    "flag": "UNDERINSURED | PREMIUM WASTE | ADEQUATE | UNKNOWN",
    "flag_explanation": "One plain-English sentence explaining why."
  }
]

Return ONLY the JSON array. No prose, no markdown fences.
---

USER PROMPT:
Personal lines data:
{{#personal_lines_extract_node.text#}}

Research each vehicle and return market value data with flags.

---

## NODE 5 — NEW: Property Records & Rebuild Cost
# Action: Add a new LLM node with web search tool enabled
# Title: Property Research & Rebuild Cost Estimate
# Model: claude-sonnet-4-20250514 | Temperature: 0.1
# Tools: Web Search ENABLED
# Position: After NODE 4 (VIN & Auto Market Value)
# Connects to: NODE 6 (Enhanced Web Enrichment) — then both commercial
#              and personal branches merge before EspoCRM write

SYSTEM PROMPT:
---
You are a property research analyst for RSG, an insurance agency in Atlanta GA.
Georgia properties only. Do not attempt rebuild estimates for other states.

For each property in the personal lines data:

STEP 1 — Get square footage
Check if square_footage is already in the data.
If null or missing, search: "[property address] square footage public records Georgia"
Try Zillow, Redfin, county tax assessor records, or public property databases.

STEP 2 — Get rebuild cost per square foot
Search: "residential construction cost per square foot [county] Georgia 2026"
Sources: RSMeans, HomeAdvisor, local contractor associations, Remodeling Magazine.
Use the midpoint of any range found.

STEP 3 — Calculate estimated rebuild cost
estimated_rebuild = square_footage × cost_per_sqft

STEP 4 — Compare to Coverage A (dwelling limit) on the policy

STEP 5 — Assign one of these flags:

UNDERINSURED: Estimated rebuild cost exceeds Coverage A by more than 15%.
This is a serious gap — flag it clearly.

ADEQUATE: Estimated rebuild cost is within 15% of Coverage A. Note as positive.

CANNOT CALCULATE: Square footage not found in public records or policy documents.
Note this — recommend client verify dwelling limit with RSG.

Return a JSON array — one object per property:
[
  {
    "address": "",
    "county": "",
    "square_footage": null,
    "square_footage_source": "dec_page | public_records | not_found",
    "cost_per_sqft": null,
    "cost_per_sqft_source": "",
    "estimated_rebuild_cost": null,
    "coverage_a_on_policy": null,
    "gap_amount": null,
    "gap_percentage": null,
    "flag": "UNDERINSURED | ADEQUATE | CANNOT CALCULATE",
    "flag_explanation": "One plain-English sentence explaining why.",
    "positive_note": "If ADEQUATE, one sentence confirming this for the client report."
  }
]

Return ONLY the JSON array. No prose, no markdown fences.
---

USER PROMPT:
Personal lines data:
{{#personal_lines_extract_node.text#}}

Research each property and return rebuild cost estimates with flags.

---

## NODE 6 — UPDATE: Enhanced Web Enrichment (existing Web Search node)
# Action: Edit the existing "Web Search Enrichment" node
# Title: Keep as "Web Search Enrichment" or rename to "Business Web Research"
# Change: Update the search query to return live URLs, not just summaries

UPDATE the tool_parameters query to:
---
{{#extract_node.text#}} official website
---

Then ADD a second LLM node immediately after the web search titled:
"Parse Web Research Results"
Model: claude-sonnet-4-20250514 | Temperature: 0.1

SYSTEM PROMPT for Parse Web Research Results:
---
You are a business research analyst for RSG insurance agency, Atlanta GA.

From the web search results provided, extract and return the following as JSON.
Return actual clickable URLs where found — not descriptions of URLs.
If a field is not found, use null.

{
  "official_website": "",
  "website_url": "",
  "linkedin_url": "",
  "facebook_url": "",
  "google_business_url": "",
  "dnb_url": "",
  "bbb_url": "",
  "yelp_url": "",
  "estimated_employees_from_web": null,
  "estimated_revenue_from_web": "",
  "business_description_from_web": "",
  "red_flags_from_web": [],
  "positive_signals_from_web": [],
  "web_research_notes": ""
}

Red flags to watch for: recent lawsuits, OSHA violations, BBB complaints,
news articles about accidents or incidents, license suspensions.

Positive signals: years in business, certifications, awards, strong reviews,
established web presence.

Return ONLY the JSON. No prose, no markdown fences.
---

USER PROMPT:
Business data: {{#extract_node.text#}}
Web search results: {{#web_search_node.text#}}

Extract all web research findings with live URLs.

---

## NODE 7 — NEW: Write to Supabase (structured client JSON)
# Action: Add a new HTTP Request node
# Title: Save Client Record to Supabase
# Method: POST
# Position: After the report generation node, before End
# URL: https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/client_assessments

HEADERS:
  apikey: {{SUPABASE_SERVICE_KEY}}
  Authorization: Bearer {{SUPABASE_SERVICE_KEY}}
  Content-Type: application/json
  Prefer: return=representation

BODY (JSON):
{
  "client_name": "{{#classify_node.text#}}",
  "client_type": "{{#start.client_type#}}",
  "assessment_date": "{{#sys.datetime#}}",
  "commercial_profile": {{#classify_node.text#}},
  "personal_profile": {{#personal_lines_extract_node.text#}},
  "vehicle_research": {{#vehicle_research_node.text#}},
  "property_research": {{#property_research_node.text#}},
  "web_research": {{#parse_web_research_node.text#}},
  "carrier_appetite": {{#supabase_appetite_node.body#}},
  "full_assessment": "{{#report_node.text#}}",
  "espocrm_account_id": "{{#espocrm_account_node.body#}}",
  "espocrm_opportunity_id": "{{#espocrm_opportunity_node.body#}}"
}

# Note for Claude Code: The Supabase table "client_assessments" may need to
# be created first. Run this SQL in Supabase dashboard → SQL Editor:
#
# CREATE TABLE client_assessments (
#   id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
#   client_name text,
#   client_type text,
#   assessment_date timestamptz DEFAULT now(),
#   commercial_profile jsonb,
#   personal_profile jsonb,
#   vehicle_research jsonb,
#   property_research jsonb,
#   web_research jsonb,
#   carrier_appetite jsonb,
#   full_assessment text,
#   espocrm_account_id text,
#   espocrm_opportunity_id text,
#   created_at timestamptz DEFAULT now()
# );

---

## NODE 8 — UPDATE: Generate Assessment Report (existing report node)
# Action: Edit the existing "Generate Assessment Report" node
# Update the USER PROMPT to include personal lines data when present

REPLACE the existing user prompt with:
---
Using all the data below, write a complete RSG Client Assessment Report.

## Enriched Business Profile (Commercial)
{{#classify_node.text#}}

## Personal Lines Profile
{{#personal_lines_extract_node.text#}}

## Vehicle Market Value Research
{{#vehicle_research_node.text#}}

## Property Rebuild Cost Research
{{#property_research_node.text#}}

## Web Research & Live Links
{{#parse_web_research_node.text#}}

## Carrier Appetite Results
{{#supabase_appetite_node.body#}}

## CRM Records Created
Account ID: {{#espocrm_account_node.body#}}
Opportunity ID: {{#espocrm_opportunity_node.body#}}

Write the assessment with these sections:

# RSG Client Assessment
## [Client / Business Name]
### Prepared by Risk Solutions Group | Atlanta, GA

---

## Business Profile (include only if commercial or both)
Standard commercial fields + website URL + LinkedIn URL from web research

## Personal Lines Profile (include only if personal or both)
Named insured, vehicles with market value flags, properties with rebuild flags

## Current Insurance Summary
All policies — commercial and personal — carrier, premium, limits

## Coverage Gap Analysis
All gaps identified — commercial and personal — ordered by severity
Lead with CRITICAL gaps, then HIGH, then MEDIUM

## Vehicle Assessment (include only if personal lines present)
Each vehicle with: year/make/model, estimated market value, coverage flag,
one-sentence plain-English explanation

## Property Assessment (include only if home present)
Each property with: address, estimated rebuild cost vs Coverage A,
flag and one-sentence plain-English explanation

## Recommended Lines of Business
For each LOB needed — why it's needed, estimated premium range, recommended carriers

## Carrier Appetite Summary
Best carrier matches from Supabase data

## Risk Notes & Underwriting Flags
Everything an underwriter will ask about

## Recommended Next Steps
1. [Action]
2. [Action]
3. [Action]

---
*Assessment generated by RSG Client Intake & Assessment Agent | Risk Solutions Group*
*This report feeds directly into the RSG Client Risk Report agent for client delivery.*
---

USER PROMPT ends here.

---

## FINAL NODE WIRING MAP
# How all nodes connect in order:

Start
  ↓
Detect Client Type (IF/ELSE)
  ├── Commercial / Both → Extract Business Info (existing)
  │     ↓
  │   Web Search Enrichment (existing)
  │     ↓
  │   Parse Web Research Results (new)
  │     ↓
  │   Classify & Enrich (existing)
  │
  └── Personal / Both → Extract Personal Lines Info (new Node 3)
        ↓
      Vehicle Research & Market Value (new Node 4)
        ↓
      Property Research & Rebuild Cost (new Node 5)

Both branches merge →
  Supabase Carrier Appetite Lookup (existing)
    ↓
  EspoCRM — Create Account (existing)
    ↓
  EspoCRM — Create Opportunity (existing)
    ↓
  Generate Assessment Report (existing — updated prompt)
    ↓
  Save Client Record to Supabase (new Node 7)
    ↓
  End
