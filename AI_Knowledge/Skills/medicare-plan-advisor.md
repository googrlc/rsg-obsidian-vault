---
name: medicare-plan-advisor
description: >
  Full Medicare plan recommendation engine using RSG's live Supabase dataset. Queries county footprints → master plan index → medical/rx matrix → supplemental benefits → provider registry → SSBCI tables. Scores and ranks top 3 plans by client priority.
---

# Medicare Plan Advisor — Recommendation Engine

**Trigger:** Client needs help choosing a Medicare Advantage plan, or agent is comparing plans for AEP/OEP/SEP.

**Output:** Top 3 ranked plans with scoring breakdown, tailored to client priorities.

## Supabase Data Model (RSG Infrastructure)

- **Base URL:** `https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1`
- **Auth:** `Authorization: Bearer {{SUPABASE_SERVICE_ROLE_KEY}}`
- **apikey:** `{{SUPABASE_SERVICE_ROLE_KEY}}`
- **Project:** `wibscqhkvpijzqbhjphg`
- **Plan year:** 2026

### Query Flow (follow this order)

```
medicare_county_footprints (357 rows) — ENTRY POINT
       ↓ plan_id
medicare_master_plan_index (128 plans) — CENTRAL HUB
       ↓ plan_id                  ↓ carrier_id
       ├── medicare_medical_rx_matrix (95 rows)
       ├── medicare_supplemental_benefits (94 rows)
       ├── medicare_provider_registry (17 rows)
       ├── medicare_ssbci_plan_map → medicare_ssbci_logic (13 conditions)
       └── medicare_carriers (11 carriers)
```

## Workflow

### Step 1: Get Client Intake
Collect from client (minimum: county + top priority):

| Field | Required | Example |
|---|---|---|
| County | YES | Fulton, DeKalb, Gwinnett, Cobb |
| Top priority | YES | Budget, Coverage, Doctors, Drugs |
| Current medications | Recommended | Metformin, Eliquis, Symbicort |
| Preferred doctors/hospitals | Recommended | Emory, Piedmont, Grady |
| Chronic conditions | Recommended | Diabetes, COPD, CHF |
| Budget ceiling | Optional | $50/month max premium |
| Dental needs | Optional | Implants, dentures, routine only |

### Step 2: Pull Available Plans by County
```
GET /rest/v1/medicare_county_footprints?county_name=eq.{COUNTY}&status=eq.Active&select=plan_id
```

### Step 3: Get Plan Details
```
GET /rest/v1/medicare_master_plan_index?plan_id=in.({PLAN_IDS})&is_active=is.true&plan_year=eq.2026&select=plan_id,plan_name,carrier_name,plan_type,monthly_premium,moop,part_b_giveback
```

### Step 4: Get Medical/Rx Cost-Sharing
```
GET /rest/v1/medicare_medical_rx_matrix?plan_id=in.({PLAN_IDS})&select=plan_id,pcp_copay,specialist_copay,inpatient_hospital,outpatient_surgery,er_copay,urgent_care_copay,part_d_deductible,rx_tier_1,rx_tier_2,rx_tier_3,rx_tier_4,rx_tier_5
```

### Step 5: Get Supplemental Benefits
```
GET /rest/v1/medicare_supplemental_benefits?plan_id=in.({PLAN_IDS})&select=plan_id,dental_max,dental_annual_max,dental_copay_class_ii,implant_coverage,vision_max,eyewear_allowance,hearing_max,otc_amount,monthly_ssbci_amount,fitness_benefit,transportation_benefit,meals_benefit
```

### Step 6: Check Provider Network (if client has preferred doctors)
```
GET /rest/v1/medicare_provider_registry?county_name=eq.{COUNTY}&select=facility_name,plan_id,network_tier,provider_type
```

Filter results by client's preferred providers. In-network = bonus points.

### Step 7: SSBCI Check (if client has chronic conditions)
```
GET /rest/v1/medicare_ssbci_logic?qualifying_condition=ilike.*{CONDITION}*&select=id,qualifying_condition,benefit_trigger,verification_method
```

If match:
```
GET /rest/v1/medicare_ssbci_plan_map?ssbci_id=eq.{ID}&plan_id=in.({PLAN_IDS})&select=plan_id,monthly_wallet_amount
```

### Step 8: Get Carrier Contact Info
```
GET /rest/v1/medicare_carriers?carrier_name=in.({CARRIER_NAMES})&select=carrier_name,broker_manager,support_phone,website_url
```

## Scoring Matrix

Score each plan 0–100 based on client's stated priority.

### Priority: BUDGET (cost-conscious client)
| Factor | Weight | Scoring |
|---|---|---|
| Monthly premium | 30% | $0 = 100, each $10 = -10 pts |
| Part B giveback | 20% | Each $10 giveback = +15 pts |
| MOOP | 15% | Lower is better: < $3K = 100, $3-5K = 70, $5-7K = 40, > $7K = 10 |
| PCP copay | 15% | $0 = 100, $5 = 80, $10 = 60, $20 = 30, $30+ = 10 |
| Part D deductible | 10% | $0 = 100, > $0 = 30 |
| Rx Tier 1 cost | 10% | $0 = 100, $1-5 = 80, $6-10 = 50, > $10 = 20 |

### Priority: COVERAGE (wants best protection)
| Factor | Weight | Scoring |
|---|---|---|
| MOOP | 25% | Lower is better (same scale) |
| Inpatient hospital cost | 20% | $0/day = 100, $100-200 = 60, $300+ = 20 |
| Specialist copay | 15% | Lower is better: $0-10 = 100, $20-30 = 60, $40+ = 20 |
| Dental annual max | 15% | > $2K = 100, $1-2K = 70, $500-1K = 40, < $500 = 10 |
| Supplemental benefits | 15% | Score OTC + fitness + transportation + meals (each present = +25) |
| SSBCI wallet | 10% | > $100/mo = 100, $50-100 = 60, $1-50 = 30, $0 = 0 |

### Priority: DOCTORS (wants specific providers)
| Factor | Weight | Scoring |
|---|---|---|
| Preferred providers in-network | 40% | All in-network = 100, some = 50, none = 0 |
| Network tier | 15% | Tier 1 = 100, Tier 2 = 60 |
| Monthly premium | 15% | Same as Budget scale |
| MOOP | 15% | Same as Coverage scale |
| PCP copay | 15% | Same as Budget scale |

### Priority: DRUGS (takes expensive medications)
| Factor | Weight | Scoring |
|---|---|---|
| Rx tier costs for client drugs | 35% | Compare actual copay for each drug |
| Part D deductible | 20% | $0 = 100, > $0 = 30 |
| Monthly premium | 15% | Same as Budget scale |
| MOOP | 15% | Same as Coverage scale |
| SSBCI wallet (if chronic) | 15% | Same as Coverage scale |

## Output Format — Plan Recommendation

```
🏥 MEDICARE PLAN ADVISOR — {COUNTY} County, 2026
Client priority: {PRIORITY}
{Chronic conditions if any} | {Key medications if any}

━━━ TOP 3 RECOMMENDATIONS ━━━

🥇 #{1}: {PLAN_NAME} ({CARRIER})
   Score: {SCORE}/100
   Premium: ${PREMIUM}/mo | MOOP: ${MOOP} | Part B Giveback: ${GIVEBACK}/mo
   PCP: ${PCP} | Specialist: ${SPEC} | ER: ${ER}
   Rx: T1 ${T1} | T2 ${T2} | T3 ${T3} | T4 ${T4} | Part D Ded: ${DED}
   Dental: ${DENTAL_MAX}/yr {implants: ✅/❌} | Vision: ${VISION} | Hearing: ${HEARING}
   OTC: ${OTC} | Fitness: {YES/NO} | Transport: {YES/NO}
   {SSBCI: "💡 SSBCI wallet: ${amount}/mo for {condition}" if applicable}
   {Provider: "✅ {Hospital} in-network (Tier {X})" if checked}
   WHY THIS PLAN: {1-2 sentence explanation tied to client priority}

🥈 #{2}: {PLAN_NAME} ({CARRIER})
   [same format]

🥉 #{3}: {PLAN_NAME} ({CARRIER})
   [same format]

━━━ COMPARISON TABLE ━━━
| | {Plan 1} | {Plan 2} | {Plan 3} |
|---|---|---|---|
| Premium | ${X} | ${X} | ${X} |
| MOOP | ${X} | ${X} | ${X} |
| PCP | ${X} | ${X} | ${X} |
| Specialist | ${X} | ${X} | ${X} |
| Dental Max | ${X} | ${X} | ${X} |
| Rx Tier 1 | ${X} | ${X} | ${X} |
| Score | {X}/100 | {X}/100 | {X}/100 |

━━━ ENROLLMENT NOTES ━━━
Carrier contact: {broker_manager} at {carrier} — {support_phone}
{Enrollment period status: AEP Oct 15 - Dec 7 / OEP Jan 1 - Mar 31 / SEP if qualifying event}
{Extra Help flag if applicable}
```

## Enrollment Period Calendar (2026)

| Period | Dates | Who Can Enroll |
|---|---|---|
| AEP | Oct 15 – Dec 7, 2025 | Anyone with Medicare (for 2026 plans) |
| OEP | Jan 1 – Mar 31, 2026 | Current MA enrollees switching once |
| IEP | 3 months before/after 65th birthday | Turning 65 or new to Medicare |
| SEP | Varies | Qualifying life event (move, lost coverage, LIS, 5-star plan) |

## RSG Active Medicare Carriers (2026)
Aetna, UHC, Devoted Health, Humana, Anthem, HealthSpring, Clear Spring, Clover, Wellcare, Kaiser

## Integration with Other Skills
- Use **medication-formulary.md** for detailed drug tier lookups before scoring
- Log plan recommendation in EspoCRM via **crm-manager.md** as Opportunity (LOB: Medicare)
- If client has chronic conditions → SSBCI data enriches the recommendation

## Error Handling
- County not in footprints table → RSG may not have plans mapped for that county. Note and check CMS Plan Finder directly.
- No Rx matrix data for a plan → plan may be new or not yet loaded. Note "Rx data pending — verify with carrier formulary."
- Provider registry empty for county → provider data is sparse (17 rows total). Fall back to carrier's online provider directory.
- Client can't decide → default to BUDGET priority, present all 3, let them compare.
