---
name: prospect-researcher
description: >
  Pre-call intel skill for contractors and fleet operators. Queries Supabase carrier_appetite, gl_class_codes, and wc_class_codes to build a 60-second Prospect Brief before any sales call.
---

# Prospect Researcher — Pre-Call Intel

**Trigger:** Agent receives a company name, industry, or NAICS code before a sales call.

**Output:** 60-second Prospect Brief posted to **#the-boss (C0ANQUENX4P)**

## Data Sources

### Supabase (RSG Infrastructure)
- **Base URL:** `https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1`
- **Auth Header:** `Authorization: Bearer {{SUPABASE_SERVICE_ROLE_KEY}}`
- **Always include:** `apikey: {{SUPABASE_SERVICE_ROLE_KEY}}`

### Tables Used
| Table | Purpose |
|---|---|
| `carrier_appetite` | Which carriers want this class of business |
| `gl_class_codes` | GL code lookup by industry/description (1,154 codes) |
| `wc_class_codes` | WC code lookup by job type/description (156 codes) |
| `operations_to_codes` | Fallback operation-to-code mapping with specialty flags |
| `wc_red_flag_pairings` | Prohibited WC code combinations |
| `commission_rules` | Commission rates by carrier + LOB + state |

## Workflow

### Step 1: Identify the Prospect's GL Class Codes
```
GET /rest/v1/gl_class_codes?or=(description.ilike.*{INDUSTRY}*,category.ilike.*{INDUSTRY}*,typical_businesses.ilike.*{INDUSTRY}*)&select=gl_code,description,category,residential_only,height_limit_ft&limit=5
```

### Step 2: WC Class Code Auto-Suggest

Based on the prospect's operation type, query RSG's Supabase wc_class_codes table. Try up to 3 keyword variations. If no match is found, DO NOT guess — report it as a gap.

**Query sequence — try in order until results return:**

Attempt 1 — primary operation keyword:
```
GET /rest/v1/wc_class_codes?description=ilike.*{PRIMARY_KEYWORD}*&select=wc_code,description,category,typical_duties,typical_payroll_type&limit=5
```

Attempt 2 — if 0 results, try secondary keyword (broader term):
```
GET /rest/v1/wc_class_codes?search_keywords=ilike.*{SECONDARY_KEYWORD}*&select=wc_code,description,category,typical_duties,typical_payroll_type&limit=5
```

Attempt 3 — if still 0 results, try operations_to_codes:
```
GET /rest/v1/operations_to_codes?keywords=ilike.*{KEYWORD}*&select=operation_name,keywords,requires_pollution,specialty_market_required,prohibited_flags&limit=5
```

**STRICT RULES — NO EXCEPTIONS:**
- If all 3 attempts return 0 results → DO NOT suggest any WC code
- DO NOT use general knowledge to guess codes
- DO NOT suggest "similar" codes that weren't returned by the database
- Report the gap clearly so the table can be updated

**Red Flag Check (only if codes found):**
```
GET /rest/v1/wc_red_flag_pairings?wc_code_id=eq.{UUID}&select=flagged_wc_code_id
```

**Output — Match Found:**
```
WC CLASS CODES (from RSG database):
• {Code} — {Description} — {Payroll Type}
• {Code} — {Description} — {Payroll Type}
Keywords matched: {keyword used}
⚠️ Red flags: {any prohibited pairings or specialty_market_required = true}
```

**Output — No Match Found:**
```
⚠️ WC CLASS CODES: NO MATCH IN RSG DATABASE
Operation searched: {prospect operation type}
Keywords tried: {keyword 1}, {keyword 2}, {keyword 3}
Table gap flagged: YES → post to #systems-check for table update

ACTION NEEDED: Add WC codes for "{operation type}" to wc_class_codes table
```

**When no match — also post to #systems-check (C0AFHN83ZE3):**
```
🗂️ WC TABLE GAP DETECTED
Prospect: {company name}
Operation: {operation type}
Keywords tried: {list}
No matching WC class codes found in wc_class_codes table.
Action: Update table with correct codes for this operation type.
```

### Step 3: Check Carrier Appetite
```
GET /rest/v1/carrier_appetite?lob=eq.{LOB}&active=is.true&states_approved=cs.{"{STATE}"}&select=carrier_name,appetite_level,min_premium,max_premium,key_requirements,exclusions
```

### Step 4: Pull Commission Rates for Matching Carriers
```
GET /rest/v1/commission_rules?carrier_name=eq.{CARRIER}&lob=eq.{LOB}&state=in.({STATE},ALL)&active=is.true&order=lookup_priority.asc&limit=1&select=nb_percent,renewal_percent,mga_name,revenue_split_percent
```

### Step 5: Check EspoCRM for Existing Records
Read `crm-manager.md` — search Account and Contact by company name to avoid duplicate outreach.

## Output Format — 60-Second Prospect Brief

Post to **#the-boss**:
```
🎯 PROSPECT BRIEF: {COMPANY NAME}
Industry: {industry} | State: {state}
GL Codes: {code} — {description}
WC Codes: {code} — {description}

CARRIER APPETITE:
✅ {carrier} — {appetite_level} | NB: {nb_percent}% | Min: ${min_premium}
✅ {carrier} — {appetite_level} | NB: {nb_percent}% | Min: ${min_premium}
❌ {carrier} — declined ({exclusion reason})

EXISTING IN CRM: {Yes — link | No — clean prospect}

TALKING POINTS:
- {Industry-specific risk to mention}
- {Coverage gap common in this class}
- {Competitive angle based on carrier appetite}
```

## Industry-Specific Risk Triggers

### Contractors (Roofing, GC, Concrete, Excavation)
- Subcontractor coverage gaps — always ask about sub usage
- Height restrictions — check `height_limit_ft` and `max_stories` on GL codes
- Residential vs commercial mix — `residential_only` flag matters
- Tools & equipment floater

### Fleet / Trucking / Hauling
- DOT number and fleet size
- Radius of operations (local vs long-haul)
- Cargo type and value
- Driver MVR quality

### Electrical / Plumbing / HVAC
- License verification
- New construction vs service/repair mix
- Warranty and completed ops exposure

## Error Handling
- No GL codes found → broaden search to category, suggest manual NAICS lookup
- No WC codes found → DO NOT GUESS. Follow the 3-attempt sequence above, then post gap to #systems-check
- No carrier appetite data → note "appetite data not loaded for this LOB" and fall back to commission_rules carriers
- EspoCRM down → skip CRM check, note in output
