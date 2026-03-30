---
name: medication-formulary
description: >
  Drug formulary lookup using CMS Medicare Plan Finder API and OpenFDA. Cross-checks drug coverage tiers against RSG's Supabase medicare_medical_rx_matrix and medicare_master_plan_index. Includes SSBCI chronic condition cross-check and Extra Help eligibility.
---

# Medication Formulary — Drug Coverage Lookup

**Trigger:** Client asks "Does my plan cover [drug]?" or agent needs to compare Rx costs across plans.

**Output:** Drug tier, estimated copay by plan, and SSBCI eligibility check.

## Data Sources

### 1. OpenFDA Drug API (free, no key)
Look up drug details — generic name, brand name, active ingredients, drug class.

**Search by brand name:**
```
GET https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{DRUG_NAME}"&limit=1
```

**Search by generic name:**
```
GET https://api.fda.gov/drug/label.json?search=openfda.generic_name:"{DRUG_NAME}"&limit=1
```

**Key fields:**
- `openfda.brand_name` — brand name(s)
- `openfda.generic_name` — generic name(s)
- `openfda.substance_name` — active ingredient(s)
- `openfda.pharm_class_epc` — pharmacological class (e.g., "HMG-CoA Reductase Inhibitor")
- `openfda.route` — oral, injection, topical, etc.
- `indications_and_usage` — what the drug treats

### 2. CMS Medicare Plan Finder — Formulary Search
```
GET https://data.cms.gov/data-api/v1/dataset/a]part-d-formulary/data?filter[ndc]="{NDC_CODE}"&filter[contract_id]="{CONTRACT}"&filter[plan_id]="{PLAN}"
```

> **Note:** CMS formulary data is updated quarterly. For real-time tier checks during AEP/OEP, cross-reference with plan-specific formulary PDFs on carrier websites.

### 3. RSG Supabase — Plan Rx Cost-Sharing
- **Base URL:** `https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1`
- **Auth:** `Authorization: Bearer {{SUPABASE_SERVICE_ROLE_KEY}}`
- **apikey:** `{{SUPABASE_SERVICE_ROLE_KEY}}`

#### `medicare_medical_rx_matrix` (95 rows)
Per-plan cost-sharing for Rx tiers:

| Column | Content |
|---|---|
| `plan_id` | FK to medicare_master_plan_index |
| `part_d_deductible` | Part D drug deductible |
| `rx_tier_1` | Preferred generic copay |
| `rx_tier_2` | Generic copay |
| `rx_tier_3` | Preferred brand copay |
| `rx_tier_4` | Non-preferred drug copay |
| `rx_tier_5` | Specialty tier copay (usually 25-33%) |

#### `medicare_master_plan_index` (128 plans)
Plan details — carrier, premium, MOOP, Part B giveback.

### 4. RSG Supabase — SSBCI Logic
#### `medicare_ssbci_logic` (13 conditions)
Chronic conditions that unlock SSBCI wallet benefits:

| Column | Content |
|---|---|
| `qualifying_condition` | e.g., Diabetes, CHF, COPD, Chronic Kidney Disease |
| `verification_method` | How the condition is verified |
| `benefit_trigger` | What unlocks (grocery, OTC, utility allowance) |
| `verification_deadline_days` | Days to verify after enrollment |

#### `medicare_ssbci_plan_map`
Links SSBCI conditions to specific plans and wallet amounts:

| Column | Content |
|---|---|
| `ssbci_id` | FK to medicare_ssbci_logic |
| `plan_id` | FK to medicare_master_plan_index |
| `monthly_wallet_amount` | $ per month for this condition on this plan |

## Workflow

### Step 1: Identify the Drug
Search OpenFDA for the drug name:
```
GET https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{DRUG}"&limit=1
```

If no result, try generic:
```
GET https://api.fda.gov/drug/label.json?search=openfda.generic_name:"{DRUG}"&limit=1
```

Extract: brand name, generic name, drug class, route, indications.

### Step 2: Determine Typical Tier
Standard Medicare Part D tier structure:
| Tier | What's On It | Typical Cost |
|---|---|---|
| 1 | Preferred generics | $0–$10 copay |
| 2 | Generics | $5–$20 copay |
| 3 | Preferred brands | $35–$50 copay |
| 4 | Non-preferred drugs | 25–40% coinsurance |
| 5 | Specialty (cost > ~$830/month) | 25–33% coinsurance |

### Step 3: Pull Plan-Specific Rx Costs from Supabase
If client has a specific plan or county:

**Get plans available in county:**
```
GET /rest/v1/medicare_county_footprints?county_name=eq.{COUNTY}&status=eq.Active&select=plan_id
```

**Get Rx tiers for those plans:**
```
GET /rest/v1/medicare_medical_rx_matrix?plan_id=in.({PLAN_IDS})&select=plan_id,part_d_deductible,rx_tier_1,rx_tier_2,rx_tier_3,rx_tier_4,rx_tier_5
```

**Get plan names and premiums:**
```
GET /rest/v1/medicare_master_plan_index?plan_id=in.({PLAN_IDS})&select=plan_id,plan_name,carrier_name,monthly_premium,part_b_giveback
```

### Step 4: SSBCI Cross-Check
If the drug treats a chronic condition, check if it qualifies for SSBCI benefits:

**Get all qualifying conditions:**
```
GET /rest/v1/medicare_ssbci_logic?select=id,qualifying_condition,benefit_trigger,verification_method
```

**Match drug class to condition:**
- Metformin / insulin → Diabetes
- Lisinopril / amlodipine → CHF / Hypertension
- Albuterol / Symbicort → COPD / Asthma
- Eliquis / warfarin → Cardiovascular Disease
- Donepezil / memantine → Dementia

**If match found, get wallet amounts:**
```
GET /rest/v1/medicare_ssbci_plan_map?ssbci_id=eq.{SSBCI_ID}&select=plan_id,monthly_wallet_amount
```

### Step 5: Extra Help (LIS) Eligibility Check
Low Income Subsidy reduces Part D costs dramatically. Flag if client mentions:
- Income below 150% FPL ($22,590 single / $30,660 couple in 2026)
- Qualifies for Medicaid, SSI, or Medicare Savings Program
- Has limited assets (< $17,220 single / $34,360 couple)

**Extra Help tiers:**
| Level | Part D Premium | Deductible | Generic Copay | Brand Copay |
|---|---|---|---|---|
| Full LIS | $0 | $0 | $0–$4.50 | $0–$11.20 |
| Partial LIS | 75% subsidy | $117 | $4.50 | $11.20 |

## Output Format — Drug Coverage Brief

```
💊 FORMULARY CHECK: {DRUG_NAME}
Brand: {BRAND} | Generic: {GENERIC}
Class: {PHARM_CLASS} | Route: {ROUTE}
Treats: {INDICATIONS_SUMMARY}

TYPICAL TIER: {TIER} — {TIER_DESCRIPTION}

PLAN COMPARISON ({COUNTY} County, 2026):
Plan | Premium | Tier | Est. Copay | Part D Deductible
{Plan 1} | ${premium}/mo | T{tier} | ${copay} | ${deductible}
{Plan 2} | ${premium}/mo | T{tier} | ${copay} | ${deductible}
{Plan 3} | ${premium}/mo | T{tier} | ${copay} | ${deductible}

💡 CHEAPEST FOR THIS DRUG: {Plan} — ${copay}/fill + ${premium}/mo

🏥 SSBCI CHECK:
{✅ "{DRUG} treats {CONDITION} — qualifies for SSBCI wallet on {X} plans"
 or ❌ "No SSBCI match for this drug class"}
{If match: "SSBCI wallet: ${amount}/mo on {Plan} — covers OTC, grocery, utilities"}

💰 EXTRA HELP FLAG:
{If applicable: "⚠️ Ask about income/assets — Extra Help could reduce copays to $0-$11"}
```

## Common Drug → Condition Mapping (Quick Reference)

| Drug Class | Common Drugs | SSBCI Condition |
|---|---|---|
| Diabetes (oral) | Metformin, Jardiance, Ozempic | Diabetes |
| Diabetes (insulin) | Humalog, Lantus, Novolog | Diabetes |
| Heart failure | Entresto, Coreg, Lasix | CHF |
| Blood thinners | Eliquis, Xarelto, Warfarin | Cardiovascular |
| COPD/Asthma | Symbicort, Spiriva, Albuterol | COPD |
| Statins | Atorvastatin, Rosuvastatin, Crestor | Cardiovascular |
| ACE/ARB | Lisinopril, Losartan, Amlodipine | CHF / Hypertension |
| Dementia | Donepezil, Memantine, Namenda | Dementia |
| Depression | Sertraline, Escitalopram, Duloxetine | Mental Health |
| Kidney | Sevelamer, Calcitriol | Chronic Kidney Disease |

## Error Handling
- OpenFDA returns no results → drug may be too new or OTC. Try alternate spelling or generic name.
- Drug is OTC only → not covered under Part D. Check if plan OTC allowance covers it (via supplemental_benefits).
- CMS formulary data stale → note "Verify with carrier formulary PDF for most current tier"
- Multiple drugs to check → process each sequentially, present comparison table
