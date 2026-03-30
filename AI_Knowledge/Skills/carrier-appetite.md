---
name: carrier-appetite
description: >
  Queries Supabase carrier_appetite, commission_rules, gl_class_codes, and wc_class_codes to determine which carriers want a given class of business and what commission rates apply.
---

# Carrier Appetite — Who Wants This Risk?

**Trigger:** Agent needs to know which carriers to approach for a specific LOB, industry, or class code.

**Output:** Appetite check with carriers, appetite levels, commission rates, and exclusions.

## Data Sources

### Supabase (RSG Infrastructure)
- **Base URL:** `https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1`
- **Auth Header:** `Authorization: Bearer {{SUPABASE_SERVICE_ROLE_KEY}}`
- **Always include:** `apikey: {{SUPABASE_SERVICE_ROLE_KEY}}`

### Tables Used
| Table | Rows | Purpose |
|---|---|---|
| `carrier_appetite` | — | Appetite level by carrier + LOB + state |
| `commission_rules` | 216 | Commission rates by carrier + LOB + MGA + state |
| `gl_class_codes` | 1,154 | GL code validation and restrictions |
| `wc_class_codes` | 156 | WC code validation and state context |

## Workflow

### Step 1: Validate the Class of Business

**If given an industry/description:**
```
GET /rest/v1/gl_class_codes?or=(description.ilike.*{QUERY}*,typical_businesses.ilike.*{QUERY}*)&select=gl_code,description,category,residential_only,combined_allowed,height_limit_ft,max_stories&limit=10
```

```
GET /rest/v1/wc_class_codes?or=(description.ilike.*{QUERY}*,typical_duties.ilike.*{QUERY}*)&select=wc_code,description,category,state,typical_payroll_type&limit=10
```

**If given a specific code:**
```
GET /rest/v1/gl_class_codes?gl_code=eq.{CODE}&select=*
```

### Step 2: Check Carrier Appetite
```
GET /rest/v1/carrier_appetite?lob=eq.{LOB}&active=is.true&states_approved=cs.{"{STATE}"}&select=carrier_name,appetite_level,min_premium,max_premium,key_requirements,exclusions,notes&order=appetite_level.asc
```

Appetite levels (best to worst):
1. `preferred` — carrier actively wants this class
2. `standard` — will write it, normal underwriting
3. `non-standard` — will consider with restrictions or higher rates
4. `declined` — won't write it

### Step 3: Pull Commission Rates for Each Carrier
For each carrier returned with appetite `preferred` or `standard`:
```
GET /rest/v1/commission_rules?carrier_name=eq.{CARRIER}&lob=eq.{LOB}&state=in.({STATE},ALL)&active=is.true&order=lookup_priority.asc&limit=1&select=nb_percent,renewal_percent,mga_name,revenue_split_percent,split_counterparty,commission_basis,min_premium,max_premium,tier_label,ee_min,ee_max
```

**lookup_priority logic** (lower = more specific match):
1. Specific MGA + specific state
2. Specific MGA + ALL states
3. Direct + specific state
4. Direct + ALL states

### Step 4: Flag Restrictions
From GL codes, flag if:
- `residential_only = true` — commercial work excluded
- `height_limit_ft` set — height restriction applies
- `max_stories` set — story cap applies
- `combined_allowed = false` — cannot combine with other GL codes

From carrier appetite, flag if:
- `exclusions` array is non-empty — list each exclusion
- `key_requirements` array is non-empty — list each requirement

## Output Format — Appetite Check

```
🏢 APPETITE CHECK: {LOB} — {INDUSTRY/CLASS}
State: {state} | GL: {code} | WC: {code}

CARRIERS THAT WANT IT:
🟢 {carrier} — PREFERRED
   NB: {nb_percent}% | Renewal: {renewal_percent}% | via {mga_name}
   RSG keeps: {revenue_split_percent}% | Min premium: ${min}
   Requirements: {key_requirements}

🟡 {carrier} — STANDARD
   NB: {nb_percent}% | Renewal: {renewal_percent}% | via {mga_name}
   RSG keeps: {revenue_split_percent}%

🔴 {carrier} — DECLINED
   Reason: {exclusions}

⚠️ RESTRICTIONS:
- {height/story/residential flags from GL codes}
- {exclusions from carrier appetite}

💰 BEST COMMISSION PLAY:
{carrier} via {mga_name} — {nb_percent}% NB, RSG net {revenue_split_percent}%
Est. commission on ${premium} premium: ${calculated}
```

## RSG Carrier Hierarchy (Preferred Markets)
When multiple carriers have appetite, prioritize by:
1. **Direct appointments** (revenue_split_percent = 100%) over MGA
2. **Higher NB commission** when splits are equal
3. **Preferred appetite** over standard
4. **SmartChoice** (70/30 split) only when no direct option exists

## Common LOB Values
`General Liability`, `Workers Compensation`, `Commercial Auto`, `BOP`, `Professional Liability`, `Umbrella`, `Personal Auto`, `Homeowners`, `Builders Risk`, `Transportation`, `Life Insurance`, `Group Benefits`

## Error Handling
- No appetite data for this LOB/state → fall back to commission_rules carriers as proxy
- No GL code match → suggest broadening search term or manual lookup
- Multiple GL codes match → present all, ask user to confirm which applies
