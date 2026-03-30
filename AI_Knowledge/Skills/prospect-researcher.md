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
| `commission_rules` | Commission rates by carrier + LOB + state |

## Workflow

### Step 1: Identify the Prospect's Class Codes
```
GET /rest/v1/gl_class_codes?or=(description.ilike.*{INDUSTRY}*,category.ilike.*{INDUSTRY}*,typical_businesses.ilike.*{INDUSTRY}*)&select=gl_code,description,category,residential_only,height_limit_ft&limit=5
```

```
GET /rest/v1/wc_class_codes?or=(description.ilike.*{INDUSTRY}*,category.ilike.*{INDUSTRY}*,typical_duties.ilike.*{INDUSTRY}*)&select=wc_code,description,category,typical_payroll_type&limit=5
```

### Step 2: Check Carrier Appetite
```
GET /rest/v1/carrier_appetite?lob=eq.{LOB}&active=is.true&states_approved=cs.{"{STATE}"}&select=carrier_name,appetite_level,min_premium,max_premium,key_requirements,exclusions
```

### Step 3: Pull Commission Rates for Matching Carriers
```
GET /rest/v1/commission_rules?carrier_name=eq.{CARRIER}&lob=eq.{LOB}&state=in.({STATE},ALL)&active=is.true&order=lookup_priority.asc&limit=1&select=nb_percent,renewal_percent,mga_name,revenue_split_percent
```

### Step 4: Check EspoCRM for Existing Records
Read `AI_Knowledge/Skills/crm-manager.md` — search Account and Contact by company name to avoid duplicate outreach.

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
- No carrier appetite data → note "appetite data not loaded for this LOB" and fall back to commission_rules carriers
- EspoCRM down → skip CRM check, note in output
