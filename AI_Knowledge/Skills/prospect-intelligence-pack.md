# Prospect Intelligence Pack — RSG
**Version:** 2.0 | **Updated:** 2026-03-30
**Replaces:** v1.0 (web scrape + LLM synthesis only)

A fully automated pre-call intelligence workflow for RSG. Given a company name, this skill runs a
structured 10-source research sweep, extracts every usable data point (SIC, NAICS, SOS entity data,
LinkedIn, BBB, FMCSA, OSHA, news, social), writes all fields directly into the EspoCRM Account and
Lead records using exact field names, and delivers a pre-call brief to Slack. Lamar gets an opener,
objection handler, and pain points — all before he picks up the phone.

---

## When to Use This Skill

- "Run prospect intel on [Company]"
- "Research [Company] before my call"
- "Prep me for [Company]"
- "What do we know about [Company]?"
- "assess: [Company]" (triggers full assessment + intel pack)
- A new Lead is created in EspoCRM (automated trigger)
- "intel: [Company]" or "run intel on [Company]"

---

## Two Modes

| Mode | Trigger | Sources | Time |
|---|---|---|---|
| **Full Pack** | Default | All 10 sources | 5–8 min |
| **Quick Pack** | "quick intel: [company]" | Website + SOS + LinkedIn only | <2 min |

Default = Full Pack unless Lamar says "quick."


---

## Credentials

| Credential | Value |
|---|---|
| NowCerts token | Mint fresh: POST https://api.nowcerts.com/api/token |
| NowCerts username | lamar@risk-solutionsgroup.com |
| NowCerts password | {{NOWCERTS_PASSWORD}} |
| NowCerts agency ID | 09d93486-1536-48d7-9096-59f1f62b6f51 |
| EspoCRM base URL | https://{{ESPOCRM_HOST}}/api/v1 |
| EspoCRM API key | 3d34836b07bb327db8d8fa6b63430c4e |
| Supabase URL | https://wibscqhkvpijzqbhjphg.supabase.co |
| Supabase key | eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndpYnNjcWhrdnBpanpxYmhqcGhnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDE0NTkyNiwiZXhwIjoyMDg5NzIxOTI2fQ.VnacqnPjUzxnqTh9Sxt0YXEc4CWjeLeTRYedsRM003I |

---

## Phase 1 — Intake

Before researching, confirm:
1. **Business name** — exact legal name if known, or DBA
2. **State of operation** — determines which SOS records to pull
3. **Line of business interest** — what coverage are we targeting?
4. **EspoCRM check** — search Accounts + Leads before creating anything

Search EspoCRM first:
```
GET /api/v1/Account?searchParams[name]={company_name}&maxSize=5
GET /api/v1/Lead?searchParams[accountName]={company_name}&maxSize=5
```
If Account exists → update it. If Lead exists → update it. If neither → create Account first, then Lead.

**Guard:** If Account field `intelRun` = true AND `intelRunDate` is within last 7 days →
STOP and post: "⚠️ Intel already run for {company_name} on {intelRunDate}. Check EspoCRM Account."
Unless Lamar says "re-run" → proceed anyway.


---

## Phase 2 — 10-Source Research Protocol

Work through every source. For each one, record what you found, what was NOT found, and the URL used.

---

### SOURCE 1 — Business Website
Navigate to company website. Read: homepage, /about, /services, /contact, /team.

**Extract → EspoCRM fields:**
| Data Point | Field Name |
|---|---|
| DBA / trade name | `intelDba` |
| Physical address | `billingAddressStreet/City/State/PostalCode` |
| Phone | `phoneNumber` |
| Email | `emailAddress` |
| Website URL | `website`, `intelWebsite` |
| Services offered | `intelWebsiteNotes` |
| Year founded / "since YYYY" | `intelYearsInBusiness`, `cYearBusinessEst` |
| Employee clues (team page) | `intelEmployeeCount` |
| Fleet / vehicle mentions | `intelFleetSize` |
| Certifications / licenses | `intelWebsiteNotes` |
| Owner / principal names | Lead `firstName`, `lastName` |

---

### SOURCE 2 — Secretary of State (SOS) / Business Registry

**URLs by state:**
- GA: https://ecorp.sos.ga.gov/BusinessSearch
- AL: https://arc-sos.state.al.us/cgi/corpname.mbr/output
- FL: https://search.sunbiz.org
- SC: https://businessfilings.sc.gov
- TN: https://tnbear.tn.gov/ECommerce/FilingSearch.aspx

**Extract → EspoCRM fields:**
| Data Point | Field Name |
|---|---|
| Legal entity name (exact) | `intelLegalName` |
| Entity type | `intelEntityType` — enum: LLC, Corp, Sole Prop, Partnership, Other |
| Business entity | `businessEntity` — enum: Sole Proprietor, LLC, Corporation, S-Corp, Partnership, Non-Profit, Other |
| Formation / incorporation date | `cYearBusinessEst` |
| Active / Dissolved / Revoked | Note in `intelWebsiteNotes` |
| Principal officers / members | Lead `firstName`, `lastName`, `title` |
| FEIN (if listed) | `fein` |
| Registered agent address | `intelWebsiteNotes` |

SOS is authoritative for legal name and entity type. Use it over website data if they conflict.


---

### SOURCE 3 — SIC / NAICS Code Lookup

**URLs:**
- NAICS: https://www.naics.com/search/?q={business_type_keywords}
- SIC: https://siccode.com or https://www.osha.gov/data/sic-manual
- Cross-reference: https://www.census.gov/naics/

**Extract → EspoCRM fields:**
| Data Point | Field Name |
|---|---|
| 6-digit NAICS code + description | `intelNaics` |
| 4-digit SIC code | `intelSic`, `sicCode` |
| Industry classification | `industry` — MUST use exact enum value (see mapping below) |

**Industry enum mapping — pick the closest valid value:**
```
Construction / Contracting         → Construction
Tree Service / Landscaping         → Landscaping Services / Tree Care
Trucking / Freight / Transport     → Transportation
Auto Repair / Dealer               → Automotive
Real Estate / Property Mgmt / Storage → Real Estate
Restaurant / Food Service / Catering → Food & Beverage
Healthcare / Medical / Dental      → Healthcare
Technology / IT / Software         → Technology
Staffing / HR / Temp Agency        → Service
Legal / Law Firm                   → Legal
Manufacturing / Fabrication        → Manufacturing
Retail Store                       → Retail
Wholesale / Distribution           → Wholesale
Agriculture / Farming              → Agriculture
Education / Training               → Education
Insurance / Financial Services     → Finance
Hospitality / Hotel / Lodging      → Hospitality
```
If uncertain → document reasoning in `intelWebsiteNotes` and pick best match.

**Also run Supabase operations lookup for GL/WC class codes:**
```
GET /rest/v1/operations_to_codes?keywords=ilike.%{keyword}%&select=operation_name,keywords,notes
Header: apikey: {supabase_key}
```
Note matched codes in `intelWebsiteNotes`.

---

### SOURCE 4 — LinkedIn
**URL:** https://www.linkedin.com/search/results/companies/?keywords={company_name}

**Extract → EspoCRM fields:**
| Data Point | Field Name |
|---|---|
| Company page URL | `intelLinkedinUrl`, `linkedinUrl` |
| Employee count (LinkedIn estimate) | `intelEmployeeCount` |
| Recent posts / activity | `intelLinkedinNotes` |
| Hiring activity (growth signal) | `intelGrowthIndicator`, `intelSignalLinkedin` |
| Owner / key employee names | Lead `firstName`, `lastName` |
| New contracts, locations, equipment posts | `intelSignalLinkedin` |

**Growth signals to capture:**
- "We're hiring!" → growth flag → `intelGrowthIndicator`
- New location opened → expansion flag
- New equipment posted → fleet/property exposure increase
- Key person departure → relationship risk


---

### SOURCE 5 — Google Business Profile + Reviews
Search Google: `"{company_name}" {city} {state}`

**Extract → EspoCRM fields:**
| Data Point | Field Name |
|---|---|
| Verified address + phone | Confirm / update `billingAddress`, `phoneNumber` |
| Google rating + review count | Add to `intelWebsiteNotes` |
| Review themes (complaints, praise) | `communicationNotes` |
| Photos (fleet, crew, equipment) | Note in `intelWebsiteNotes` |

---

### SOURCE 6 — BBB (Better Business Bureau)
**URL:** https://www.bbb.org/search?find_text={company_name}&find_country=USA

**Extract → EspoCRM fields:**
| Data Point | Field Name |
|---|---|
| BBB rating (A+, A, B, C, D, F, NR) | `intelBbbRating`, `bbbRating` |
| Accreditation status | `intelBbbAccredited` (Boolean) |
| Number of open complaints | `intelBbbComplaints` |
| Complaint categories | `intelBbbNotes` |
| Years in business (BBB record) | Cross-check `cYearBusinessEst` |

**Auto-flag rule:** 3+ open complaints OR rating below B → add to `intelUnderwritingFlag`

---

### SOURCE 7 — FMCSA / DOT (Motor Carriers Only)
**URL:** https://safer.fmcsa.dot.gov/CompanySnapshot.aspx
**SMS scores:** https://ai.fmcsa.dot.gov/SMS

**ONLY run if:** business has fleet, trucks, delivery, transport, landscaping with trailers, or construction.
Skip for offices, retail, professional services.

**API (if DOT# known):**
```
GET https://mobile.fmcsa.dot.gov/qc/services/carriers/{dot_number}?webKey={{FMCSA_WEB_KEY}}
```
**Search by name:**
```
GET https://mobile.fmcsa.dot.gov/qc/services/carriers?name={company_name}&webKey={{FMCSA_WEB_KEY}}
```

**Extract → EspoCRM fields:**
| Data Point | Field Name |
|---|---|
| Number of power units | `intelFleetSize` |
| Number of drivers | Note in `intelWebsiteNotes` |
| Cargo / commodity type | `intelCargoType` |
| Operating radius | `intelOperatingRadius` |
| Safety rating | `intelUnderwritingFlag` if Conditional/Unsat |
| Crash data (fatal, injury, tow) | `intelDotIncidents` |
| Owner-operators on payroll | `intelOwnerOperators` (Boolean) |
| Insurance filing on file | Note carrier in `intelWebsiteNotes` |

**Red flags → add to `intelUnderwritingFlag`:**
- OOS rate >10%
- Unsafe Driving BASIC >75%
- Active federal intervention
- Fatal crashes in last 24 months


---

### SOURCE 8 — OSHA Inspection Records
**URL:** https://www.osha.gov/establishments/search

Search by company name and state.

**Extract → EspoCRM field:**
| Data Point | Field Name |
|---|---|
| Inspection history, citations, penalties | `intelOshaViolations` |

**Auto-flag → `intelUnderwritingFlag`:** Willful or repeat citations, $10K+ penalties, citations in last 3 years.

---

### SOURCE 9 — Google News
Search: `"{company_name}" {city} (lawsuit OR fire OR accident OR settlement OR "workers comp" OR claim)`
Also: `"{company_name}" site:news.google.com`

**Extract → EspoCRM fields:**
| Data Point | Field Name |
|---|---|
| Lawsuits, legal actions | `intelNewsNotes`, `intelUnderwritingFlag` |
| Fire, flood, property damage events | `intelNewsNotes` |
| Workplace accidents / injuries | `intelNewsNotes`, `intelUnderwritingFlag` |
| Expansions, awards, new contracts | `intelSignalNews`, `intelGrowthIndicator` |

---

### SOURCE 10 — Social Media (Facebook, Instagram, X)
- Facebook: https://www.facebook.com/search/pages/?q={company_name}
- Instagram: https://www.instagram.com/{handle} (guess from website or name)
- X: https://x.com/search?q={company_name}

**Extract → EspoCRM field:**
| Data Point | Field Name |
|---|---|
| Active profiles (URLs) | `intelLinkedinNotes` (append other social URLs here) |
| Last post date (active?) | Note in `intelLinkedinNotes` |
| Fleet photos, job sites, crew size | Note in `intelLinkedinNotes` |
| Customer complaints in comments | `intelWebsiteNotes` |

---

### SOURCE 11 — NowCerts Existing Client Check
```
POST https://api.nowcerts.com/api/token
Body: grant_type=password&username=lamar@risk-solutionsgroup.com&password={{NOWCERTS_PASSWORD}}&client_id=ngAuthApp

GET https://api.nowcerts.com/api/InsuredDetailList
Params: agencyId=09d93486-1536-48d7-9096-59f1f62b6f51&active=True
Header: Authorization: Bearer {nowcerts_token}
```
Search results for company name. If found → extract existing policies, premiums, carriers, LOBs.
Write to `insightRelationship`: "Existing RSG client — {LOBs} with {carriers}, ${total_premium}/yr since {date}"
If not found → `insightRelationship` = "No existing RSG relationship found."


---

## Phase 3 — Synthesis

After all sources are exhausted, write these synthesis fields:

### `intelAiSummary`
3–5 sentence executive brief:
1. What the business does and how big it is
2. Key exposures / LOBs they likely need
3. Notable risk flags or underwriting concerns
4. Growth signals or timing triggers
5. Recommended angle for Lamar

### `intelPainPoints`
2–4 specific pain points based on industry, size, and findings. Be specific, not generic.
- ❌ Bad: "They may have gaps in coverage"
- ✅ Good: "5-truck fleet with DOT# but no hired/non-owned auto on file per FMCSA"

### `intelCrossSell`
Coverage gaps or add-ons visible from research. Examples:
- Fleet found → Commercial Auto + GL + Umbrella bundle
- Employees found → Workers Comp
- Owns real estate → Commercial Property or Landlord
- Professional services → E&O / Professional Liability
- Owner visible → Key Person Life, Group Benefits

### `insightSignal`
One-line trigger — why is NOW the right time to call?
Examples:
- "Hired 3 people in 90 days — payroll exposure just went up"
- "BBB complaint filed 2 months ago — probably unhappy with current carrier"
- "Google shows new second location — property exposure just doubled"

### `insightOpener`
Lamar's first 2 sentences on the phone. Specific to what was found. No generic openers.
- ❌ Bad: "Hi, I'm calling about your insurance needs."
- ✅ Good: "Hey [name], I was looking at your Google reviews — 4.8 stars with 60+ reviews for a landscaping
  operation your size is impressive. I work with a few similar crews in Atlanta and I think I found a gap
  worth 90 seconds of your time."

### `insightObjection`
Most likely objection + suggested handle:
- "We already have an agent" → "Not asking to replace them today — when does your GL come up?"
- "We're good" → "My job is to find what your current carrier missed. Can I send you one thing to look at?"

### `intelConfidence`
Enum: High / Medium / Low
- High = 6+ sources returned data, legal name confirmed via SOS, SIC/NAICS locked, owner identified
- Medium = 3–5 sources, some gaps
- Low = 1–2 sources only

### `intelSourcesHit` — count of sources that returned usable data (integer)
### `intelSources` — comma-separated list of all URLs actually used
### `intelPackLastRun` — today's date-time
### `intelRun` — set to true
### `intelRunBy` — "prospect-intelligence-pack v2.0"


---

## Phase 4 — CRM Write: Account Record

Navigate to EspoCRM Account. If none exists, create at `{base}/#Account/create` first.
Use API for programmatic updates:
```
PUT https://{{ESPOCRM_HOST}}/api/v1/Account/{id}
Header: X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
```

Write ALL of the following fields in a single PATCH/PUT call:

```json
{
  "name": "{legal name or DBA}",
  "accountType": "Prospect",
  "accountStatus": "Active",
  "website": "{url}",
  "websiteUrl": "{url}",
  "phoneNumber": "{phone}",
  "emailAddress": "{email}",
  "billingAddressStreet": "{street}",
  "billingAddressCity": "{city}",
  "billingAddressState": "{state}",
  "billingAddressPostalCode": "{zip}",
  "industry": "{exact enum value}",
  "sicCode": "{4-digit SIC}",
  "businessEntity": "{enum: LLC | Corporation | Sole Proprietor | S-Corp | Partnership | Non-Profit | Other}",
  "fein": "{if found}",
  "numberOfEmployees": "{best estimate}",
  "linkedinUrl": "{url}",
  "bbbRating": "{rating}",
  "intelLegalName": "{exact SOS name}",
  "intelDba": "{DBA if different}",
  "intelEntityType": "{enum: LLC | Corp | Sole Prop | Partnership | Other}",
  "cYearBusinessEst": "{year}",
  "intelYearsInBusiness": "{calculated integer}",
  "intelWebsite": "{url}",
  "intelNaics": "{6-digit code — description}",
  "intelSic": "{4-digit code — description}",
  "intelEmployeeCount": "{LinkedIn or website count}",
  "intelAnnualRevenueEst": "{estimated range}",
  "intelFleetSize": "{number if applicable}",
  "intelLinkedinUrl": "{url}",
  "intelBbbRating": "{rating}",
  "intelBbbAccredited": "{true|false}",
  "intelBbbComplaints": "{integer}",
  "intelBbbNotes": "{complaint summary}",
  "intelDotIncidents": "{integer if applicable}",
  "intelCargoType": "{if trucking}",
  "intelOperatingRadius": "{if trucking}",
  "intelOwnerOperators": "{true|false}",
  "intelOshaViolations": "{summary or 'No record found'}",
  "intelWebsiteNotes": "{website research notes}",
  "intelLinkedinNotes": "{linkedin + social media notes}",
  "intelNewsNotes": "{news research notes}",
  "intelSignalLinkedin": "{growth/activity signal}",
  "intelSignalNews": "{news signal}",
  "intelGrowthIndicator": "{growth summary}",
  "intelUnderwritingFlag": "{red flags or 'None identified'}",
  "intelAiSummary": "{3-5 sentence brief}",
  "intelPainPoints": "{bullet list}",
  "intelCrossSell": "{bullet list}",
  "intelSources": "{comma-separated URLs}",
  "intelSourcesHit": "{integer}",
  "intelConfidence": "{High|Medium|Low}",
  "intelRun": true,
  "intelRunBy": "prospect-intelligence-pack v2.0",
  "intelRunDate": "{ISO datetime}",
  "intelPackLastRun": "{ISO datetime}",
  "keyFindings": "{2-3 most important findings}",
  "insightSignal": "{one-line timing trigger}",
  "insightOpener": "{Lamar's opening line}",
  "insightObjection": "{objection + handle}",
  "insightRelationship": "{existing RSG relationship or 'None'}",
  "coverageGaps": "{inferred gaps}"
}
```


---

## Phase 5 — Lead Record Create / Update

If Lead doesn't exist, create it:
```
POST https://{{ESPOCRM_HOST}}/api/v1/Lead
Header: X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
```

```json
{
  "firstName": "{owner first name from SOS or LinkedIn}",
  "lastName": "{owner last name}",
  "title": "{title — owner, president, etc.}",
  "accountName": "{DBA or legal name}",
  "phoneNumber": "{business phone}",
  "emailAddress": "{business or owner email}",
  "website": "{business URL}",
  "addressStreet": "{street}",
  "addressCity": "{city}",
  "addressState": "{two-letter state}",
  "addressPostalCode": "{zip}",
  "industry": "{exact enum value — same as Account}",
  "insuranceInterest": "{e.g. Commercial Auto, General Liability}",
  "source": "Campaign",
  "status": "New",
  "priority": "{Hot if timing trigger found | Warm default | Cold if no signals}",
  "currentCarrier": "{if found in research}",
  "currentlyInsured": "{true|false|leave blank if unknown}",
  "estimatedPremium": "{rough estimate in dollars}",
  "description": "Intel Pack v2.0 — {date}\n\nPAIN POINTS:\n{intelPainPoints}\n\nCROSS-SELL:\n{intelCrossSell}\n\nSOURCES HIT: {count}/{total}",
  "aiSummary": "{intelAiSummary full text}",
  "assignedUserId": "69bdad92458da2204"
}
```

After creating Lead → link it to the Account in EspoCRM.
After creating Account → confirm Lead appears in related panel. If not, link manually.

---

## Phase 6 — Slack Pre-Call Brief

Post to #sales-brief (C0AP1BCEURK):

```
🔍 INTEL PACK v2 — {company_name} | {date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 WHAT THEY DO
{intelAiSummary — first 2 sentences}

👤 WHO TO CALL
{firstName} {lastName} | {title} | {phoneNumber} | {emailAddress}

🏢 PROFILE
Industry: {industry} | SIC: {sicCode} | NAICS: {intelNaics}
Entity: {businessEntity} | Founded: {cYearBusinessEst}
Employees: {intelEmployeeCount} | Revenue Est.: {intelAnnualRevenueEst}
Fleet: {intelFleetSize or "N/A"} | DOT: {dot# or "N/A"}

🔗 DIGITAL
Website: {website}
LinkedIn: {intelLinkedinUrl or "Not found"}
BBB: {intelBbbRating} | Accredited: {intelBbbAccredited} | Open Complaints: {intelBbbComplaints}

⚠️ FLAGS
{intelUnderwritingFlag or "None identified"}
{intelOshaViolations or "No OSHA record found"}

💡 PAIN POINTS
{intelPainPoints}

📈 CROSS-SELL
{intelCrossSell}

📣 OPENER
"{insightOpener}"

🎯 OBJECTION + HANDLE
{insightObjection}

⏰ WHY NOW
{insightSignal}

🤝 RSG RELATIONSHIP
{insightRelationship}

🔎 Confidence: {intelConfidence} | Sources hit: {intelSourcesHit}/11
✅ EspoCRM Account + Lead updated
```

If existing RSG client → add: "⚡ EXISTING CLIENT — {existing policies summary}"


---

## Edge Cases

| Scenario | Action |
|---|---|
| Intel already run within 7 days | STOP, post warning, unless Lamar says "re-run" |
| Business not in EspoCRM | Create Account first, then Lead |
| No website found | Note in `intelWebsite` = "No website" — this is a signal (informal operation). Set confidence Low/Medium. |
| SOS returns no record | Note "Not found in {state} SOS — may be sole prop or registered elsewhere." Try neighboring states. |
| LinkedIn shows 0 employees | Use "1–5 estimated" — note unconfirmed |
| FMCSA returns no record | Record "No DOT/MC found — likely no commercial vehicle ops." Don't skip. |
| Data conflicts across sources | Note conflict in `intelWebsiteNotes`. SOS is authoritative for legal name/entity. |
| Business appears inactive | Check SOS status, Google "permanently closed," last LinkedIn post. If closed → set `accountStatus` = Inactive. Do NOT create Lead. |
| NowCerts auth fails | Continue without existing relationship data. Note in `insightRelationship`. |
| LLM returns malformed JSON | Retry once with explicit JSON-only prompt. |
| All sources fail | Set `intelConfidence` = Low. Still write available data. Never silently skip. |

---

## Source Checklist (run in order, check off each)

```
[ ] 1.  Business Website          → intelWebsite, intelDba, phone, email, address
[ ] 2.  Secretary of State        → intelLegalName, intelEntityType, cYearBusinessEst
[ ] 3.  SIC / NAICS Lookup        → sicCode, intelSic, intelNaics, industry (enum)
[ ] 4.  LinkedIn                  → intelLinkedinUrl, intelEmployeeCount, intelSignalLinkedin
[ ] 5.  Google Business + Reviews → address confirm, rating, review themes
[ ] 6.  BBB                       → intelBbbRating, intelBbbAccredited, intelBbbComplaints
[ ] 7.  FMCSA / DOT (if fleet)   → intelFleetSize, intelDotIncidents, intelCargoType
[ ] 8.  OSHA                      → intelOshaViolations
[ ] 9.  Google News               → intelNewsNotes, intelSignalNews
[ ] 10. Social Media              → intelLinkedinNotes (other platform URLs)
[ ] 11. NowCerts Client Check     → insightRelationship (existing RSG book)

SYNTHESIS:
[ ] intelAiSummary written
[ ] intelPainPoints written (specific, not generic)
[ ] intelCrossSell written
[ ] insightOpener written (specific, not generic)
[ ] insightObjection written
[ ] insightSignal written
[ ] intelConfidence set (High / Medium / Low)
[ ] intelSourcesHit count set
[ ] intelUnderwritingFlag populated or confirmed "None"
[ ] intelPackLastRun set to now
[ ] intelRun = true

CRM:
[ ] Account record fully written (all fields in Phase 4 JSON)
[ ] Lead record created and linked to Account
[ ] Slack brief posted to #sales-brief
[ ] Task created for Lamar (follow-up in 2 days)
```
