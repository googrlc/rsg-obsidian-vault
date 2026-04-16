# RSG Client Intake & Assessment — Dify Node Build Guide
# For Claude Code | 2026-04-08
#
# INSTRUCTIONS FOR CLAUDE CODE:
# 1. Open Dify → duplicate "RSG Commercial Assessment" workflow
# 2. Rename duplicate to "RSG Client Intake & Assessment"
# 3. Update app name and description (see below)
# 4. Add/modify nodes exactly as specified in this file
# 5. Wire edges as specified in the EDGE MAP at the bottom
# ---------------------------------------------------------------

## APP NAME & DESCRIPTION
# Name: RSG Client Intake & Assessment
# Description (paste exactly into Dify description field):
#
#   Gretchen — use this for every new client or prospect. Upload dec pages,
#   paste call notes, add driver info, vehicle details, or anything you have.
#   Works for both commercial and personal lines accounts. The agent will
#   research the business or property online, check vehicle values, estimate
#   home rebuild costs, create the client record in EspoCRM, and produce a
#   full assessment report. You don't need to know what type of account it is
#   — the agent figures that out automatically.


## NODE 1 — START (modify existing)
# Keep all existing input variables. ADD these new variables:

# New variable 1:
#   Label: Personal Lines Documents (home, auto dec pages)
#   Variable: personal_files
#   Type: file-list
#   Allowed types: document, image
#   Allowed extensions: .pdf, .jpg, .jpeg, .png
#   Required: false

# New variable 2:
#   Label: Additional Notes (drivers, vehicles, property info)
#   Variable: additional_notes
#   Type: paragraph
#   Max length: 10000
#   Required: false

# ---------------------------------------------------------------

## NODE 2 — DETECT CLIENT TYPE (ADD — insert after Start, before Extract Business Info)
# Node type: LLM
# Title: Detect Account Type
# Description: Figures out if this is a commercial, personal, or both account
# Model: claude-sonnet-4-20250514 | Temp: 0.1
# Vision: enabled (reads all uploaded files)

# SYSTEM PROMPT:
You are an intake classifier for Risk Solutions Group, an insurance agency.
Review all uploaded documents, files, and notes provided.
Determine what type of insurance account this is.

Return ONLY this JSON — no other text:
{
  "client_type": "commercial" | "personal" | "both",
  "client_name": "string — business name or person full name",
  "has_commercial_docs": true | false,
  "has_personal_auto": true | false,
  "has_personal_home": true | false,
  "has_driver_info": true | false,
  "has_vehicle_info": true | false,
  "confidence": 0.0-1.0,
  "reasoning": "one sentence explaining the classification"
}

Rules:
- commercial = business documents, fleet, contractors, BOP, commercial auto
- personal = home, personal auto, personal umbrella
- both = client has both commercial AND personal policies
- If unsure, default to "both" — it is better to over-process than miss data

# USER PROMPT:
Transcription Notes: {{#start.transcription_notes#}}
Additional Notes: {{#start.additional_notes#}}

Review all uploaded files and notes above and classify this account.


## NODE 3 — EXTRACT BUSINESS INFO (modify existing)
# Keep existing prompt. REPLACE the system prompt with this expanded version:

# SYSTEM PROMPT:
You are an expert commercial insurance analyst for Risk Solutions Group (RSG),
an Atlanta-based independent insurance agency.

Extract ALL available business information from the provided documents and notes.
Return a JSON object with these exact fields:

{
  "business_name": "",
  "dba": "",
  "business_address": "",
  "city": "",
  "state": "",
  "zip": "",
  "county": "",
  "phone": "",
  "email": "",
  "website": "",
  "owner_name": "",
  "business_type": "",
  "years_in_business": "",
  "number_of_employees": "",
  "annual_revenue": "",
  "fleet_size": "",
  "vehicles": [
    {
      "year": "",
      "make": "",
      "model": "",
      "trim": "",
      "vin": "",
      "use": ""
    }
  ],
  "drivers": [
    {
      "name": "",
      "dl_number": "",
      "dl_state": "",
      "dob": "",
      "cdl": true | false
    }
  ],
  "current_carrier": "",
  "current_premium": "",
  "policy_expiration": "",
  "current_coverages": [],
  "current_limits": {},
  "coverage_gaps": [],
  "special_notes": ""
}

If a field is not found, leave it as empty string or empty array.
Return ONLY the JSON object, no other text.

# USER PROMPT (keep existing structure, add personal_files reference):
Transcription Notes: {{#start.transcription_notes#}}
Additional Notes: {{#start.additional_notes#}}

Extract all business and commercial insurance information from the uploaded
documents and notes above.


## NODE 4 — EXTRACT PERSONAL LINES INFO (ADD NEW — runs parallel to Extract Business Info)
# Node type: LLM
# Title: Extract Personal Lines Info
# Description: Pulls home and personal auto details from uploaded docs
# Model: claude-sonnet-4-20250514 | Temp: 0.1
# Vision: enabled — point at personal_files AND start.files
# Only run if: detect_node.client_type = "personal" OR "both"

# SYSTEM PROMPT:
You are an expert personal lines insurance analyst for Risk Solutions Group.
Extract ALL personal lines insurance information from the uploaded documents.

Return ONLY this JSON — no other text:
{
  "named_insured": "",
  "mailing_address": "",
  "personal_auto_policies": [
    {
      "carrier": "",
      "policy_number": "",
      "policy_period": "",
      "premium": "",
      "premium_period": "annual | 6-month",
      "vehicles": [
        {
          "year": "",
          "make": "",
          "model": "",
          "trim": "",
          "vin": "",
          "bi_per_person": "",
          "bi_per_occurrence": "",
          "property_damage": "",
          "comp_deductible": "",
          "coll_deductible": "",
          "has_comp_coll": true | false
        }
      ],
      "drivers": [
        {
          "name": "",
          "dl_number": "",
          "dl_state": "",
          "dob": ""
        }
      ]
    }
  ],
  "homeowners_policies": [
    {
      "carrier": "",
      "policy_number": "",
      "policy_period": "",
      "premium": "",
      "property_address": "",
      "county": "",
      "coverage_a_dwelling": "",
      "coverage_b_other_structures": "",
      "coverage_c_personal_property": "",
      "coverage_d_loss_of_use": "",
      "liability": "",
      "medical_payments": "",
      "deductible": "",
      "square_footage": "",
      "endorsements": []
    }
  ],
  "umbrella_policies": [],
  "other_personal_policies": []
}

If a field is not found, leave as empty string.
Return ONLY the JSON — no other text.

# USER PROMPT:
Transcription Notes: {{#start.transcription_notes#}}
Additional Notes: {{#start.additional_notes#}}

Extract all personal lines insurance information from the uploaded documents
and notes above.


## NODE 5 — WEB SEARCH ENRICHMENT (modify existing)
# Keep Bing web search node. UPDATE the query to be richer:

# Tool: Bing Web Search
# Title: Web Search — Business Enrichment
# Query (replace existing):
{{#extract_node.text#}} site:linkedin.com OR site:dnb.com OR official website
revenue employees reviews BBB

# After this node, ADD a second web search node for the business website:

## NODE 5B — SCRAPE BUSINESS WEBSITE (ADD NEW)
# Node type: Tool — Bing Web Search (or HTTP Request if website URL found)
# Title: Web Search — Business Website & Presence
# Description: Finds the business website and checks what it says about them
# Query:
"{{#extract_node.business_name#}}" {{#extract_node.city#}} GA official website
contact about services

# This gives us the live URL + snippet to include in the assessment report.


## NODE 6 — VIN LOOKUP & AUTO MARKET VALUE (ADD NEW)
# Node type: Tool — Bing Web Search (one search per vehicle)
# Title: Web Search — Vehicle Market Values
# Description: Looks up current retail value for each personal auto vehicle
# Run condition: personal_extract_node.personal_auto_policies is not empty

# For each vehicle found in personal_extract_node, run this search:
# Query template (repeat per vehicle):
{{vehicle.year}} {{vehicle.make}} {{vehicle.model}} {{vehicle.trim}}
retail value private party Georgia 2026 site:kbb.com OR site:edmunds.com
OR site:cargurus.com

# After search results return, pass to this LLM node:

## NODE 6B — INTERPRET VEHICLE VALUES (ADD NEW)
# Node type: LLM
# Title: Interpret Vehicle Market Values
# Description: Compares market value to current coverage, flags gaps
# Model: claude-sonnet-4-20250514 | Temp: 0.1

# SYSTEM PROMPT:
You are a personal lines insurance analyst. Review the vehicle data and
web search results. For each vehicle determine current market value and
compare to existing coverage.

Return ONLY this JSON:
{
  "vehicle_valuations": [
    {
      "year": "",
      "make": "",
      "model": "",
      "trim": "",
      "estimated_retail_value": 0,
      "value_source": "KBB | Edmunds | CarGurus | estimated",
      "current_bi_limit": "",
      "current_pd_limit": "",
      "has_comp_coll": true | false,
      "flag": "UNDERINSURED | PREMIUM_WASTE | ADEQUATE | UNKNOWN",
      "flag_reason": ""
    }
  ]
}

Flag rules:
- UNDERINSURED: vehicle value significantly exceeds liability limits OR
  vehicle is worth >$15k with no comp/coll
- PREMIUM_WASTE: vehicle retail value under $6,000 with comp/coll coverage
  (client is paying for more than the car is worth)
- ADEQUATE: coverage is reasonable for the vehicle value
- UNKNOWN: could not determine market value from search results

# USER PROMPT:
Vehicle Data: {{#personal_extract_node.text#}}
Web Search Results: {{#vehicle_search_node.text#}}

Analyze each vehicle and return the valuation JSON.


## NODE 7 — PROPERTY RECORDS & REBUILD COST (ADD NEW)
# Node type: Tool — Bing Web Search (two searches)
# Title: Web Search — Property Records & Rebuild Cost
# Description: Finds sq footage from public records and GA rebuild cost
# Run condition: personal_extract_node.homeowners_policies is not empty

# Search 1 — square footage (if not already on dec page):
# Query:
{{#personal_extract_node.property_address#}} square footage property records
Fulton County OR DeKalb County OR {{#personal_extract_node.county#}} GA
site:qpublic.net OR site:zillow.com OR site:redfin.com

# Search 2 — rebuild cost per sq ft by county:
# Query:
residential construction cost per square foot
{{#personal_extract_node.county#}} Georgia 2026 rebuild replacement cost

# After searches return, pass to this LLM node:

## NODE 7B — INTERPRET REBUILD COST (ADD NEW)
# Node type: LLM
# Title: Interpret Home Rebuild Cost
# Description: Calculates estimated rebuild cost and compares to Coverage A
# Model: claude-sonnet-4-20250514 | Temp: 0.1

# SYSTEM PROMPT:
You are a property insurance analyst for Risk Solutions Group in Atlanta, GA.
Review the homeowners policy data, public property records, and construction
cost data. Calculate estimated rebuild cost and compare to Coverage A.

Return ONLY this JSON:
{
  "property_address": "",
  "county": "",
  "square_footage": 0,
  "sq_footage_source": "dec_page | public_records | estimated | not_found",
  "cost_per_sqft": 0,
  "cost_source": "web_search | default_estimate",
  "estimated_rebuild_cost": 0,
  "coverage_a_current": 0,
  "gap_amount": 0,
  "gap_percentage": 0,
  "flag": "UNDERINSURED | ADEQUATE | CANNOT_CALCULATE",
  "flag_reason": "",
  "default_cost_used": true | false
}

Flag rules:
- UNDERINSURED: estimated rebuild > Coverage A by more than 15%
- ADEQUATE: estimated rebuild is within 15% of Coverage A
- CANNOT_CALCULATE: square footage not found anywhere — note this clearly

Default cost per sq ft if search returns nothing: use $165/sq ft for
metro Atlanta, $145/sq ft for rural Georgia counties.
Always note when a default is used.

# USER PROMPT:
Homeowners Policy Data: {{#personal_extract_node.text#}}
Property Records Search: {{#property_search_node.text#}}
Rebuild Cost Search: {{#rebuild_cost_search_node.text#}}

Calculate the rebuild cost estimate and return the JSON.


## NODE 8 — CLASSIFY & ENRICH (modify existing)
# Keep existing node. UPDATE system prompt to include personal lines + website:

# SYSTEM PROMPT (replace existing):
You are a commercial insurance underwriting expert. Using the extracted
business data, personal lines data, and web search results, produce a
complete enriched client profile.

Return ONLY this JSON:
{
  "client_type": "commercial | personal | both",
  "business_name": "",
  "dba": "",
  "full_address": "",
  "county": "",
  "owner_name": "",
  "business_type": "",
  "naics_code": "",
  "naics_description": "",
  "sic_code": "",
  "sic_description": "",
  "years_in_business": "",
  "estimated_employees": "",
  "estimated_revenue": "",
  "fleet_size": "",
  "website": "",
  "website_summary": "2 sentence summary of what their website says about them",
  "linkedin_url": "",
  "current_carrier": "",
  "current_premium": "",
  "policy_expiration": "",
  "current_coverages": [],
  "coverage_gaps": [],
  "lines_of_business_needed": [],
  "risk_notes": ""
}

For lines_of_business_needed use exact RSG LOB names:
Commercial Auto, General Liability, Workers Comp, Commercial Property,
BOP, Inland Marine, Umbrella/Excess, Professional Liability,
Cyber Liability, Surety Bond, Personal Auto, Homeowners, Personal Umbrella

IMPORTANT: Include the actual website URL in the "website" field if found.
Include a plain English summary of what the business website says they do
in "website_summary" — this goes directly into the client report.

Return ONLY the JSON — no other text.

# USER PROMPT (replace existing):
Extracted Business Data: {{#extract_node.text#}}
Personal Lines Data: {{#personal_extract_node.text#}}
Business Web Search: {{#web_search_node.text#}}
Website Search: {{#website_search_node.text#}}

Classify and enrich the full client profile.


## NODE 9 — SUPABASE CARRIER APPETITE LOOKUP (keep existing — no changes needed)
# URL: https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/carrier_appetite
# ?select=carrier_name,lob,state,appetite_notes,min_premium,max_premium
# &state=eq.GA&order=carrier_name
# No changes needed.

## NODE 10 — ESPOCRM CREATE ACCOUNT (modify existing)
# Keep existing POST to /api/v1/Account
# UPDATE body to include personal lines fields:

# Body (replace existing):
{
  "name": "{{#classify_node.business_name#}}",
  "primaryFirstName": "{{#classify_node.owner_name#}}",
  "type": "Commercial Lines",
  "billingAddressStreet": "{{#classify_node.full_address#}}",
  "billingAddressCity": "{{#classify_node.city#}}",
  "billingAddressState": "GA",
  "billingAddressPostalCode": "{{#classify_node.zip#}}",
  "industry": "{{#classify_node.naics_description#}}",
  "website": "{{#classify_node.website#}}",
  "annualRevenue": "{{#classify_node.estimated_revenue#}}",
  "numberOfEmployees": "{{#classify_node.estimated_employees#}}",
  "description": "Auto-created by RSG Client Intake & Assessment Agent.\nNAICS: {{#classify_node.naics_code#}} — {{#classify_node.naics_description#}}\nSIC: {{#classify_node.sic_code#}}\nWebsite: {{#classify_node.website#}}\n{{#classify_node.website_summary#}}"
}

## NODE 11 — ESPOCRM CREATE OPPORTUNITY (keep existing — no changes needed)

## NODE 12 — SUPABASE WRITE CLIENT JSON (ADD NEW)
# Node type: HTTP Request
# Title: Supabase — Save Client Assessment Record
# Description: Saves the full structured client record for the Risk Report agent
# Method: POST
# URL: https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/client_assessments
# Headers:
#   apikey: {{SUPABASE_SERVICE_KEY}}
#   Authorization: Bearer {{SUPABASE_SERVICE_KEY}}
#   Content-Type: application/json
#   Prefer: return=representation

# Body:
{
  "client_name": "{{#classify_node.business_name#}}",
  "client_type": "{{#classify_node.client_type#}}",
  "assessment_date": "{{#sys.date#}}",
  "enriched_profile": {{#classify_node.text#}},
  "personal_lines_data": {{#personal_extract_node.text#}},
  "vehicle_valuations": {{#vehicle_value_node.text#}},
  "rebuild_assessment": {{#rebuild_node.text#}},
  "carrier_appetite": {{#supabase_appetite_node.body#}},
  "espocrm_account_id": "{{#espocrm_account_node.body#}}",
  "espocrm_opportunity_id": "{{#espocrm_opportunity_node.body#}}",
  "status": "assessment_complete"
}

# NOTE FOR CLAUDE CODE: Create the Supabase table first if it doesn't exist:
# Table name: client_assessments
# Run this SQL in Supabase SQL editor:
#
# create table client_assessments (
#   id uuid default gen_random_uuid() primary key,
#   client_name text,
#   client_type text,
#   assessment_date date,
#   enriched_profile jsonb,
#   personal_lines_data jsonb,
#   vehicle_valuations jsonb,
#   rebuild_assessment jsonb,
#   carrier_appetite jsonb,
#   espocrm_account_id text,
#   espocrm_opportunity_id text,
#   status text,
#   created_at timestamptz default now()
# );

