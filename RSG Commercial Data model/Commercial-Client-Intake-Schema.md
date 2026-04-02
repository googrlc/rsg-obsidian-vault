# Commercial Client Intake Schema
**Last Updated:** 2026-04-01
**Owner:** Lamar Coates — Risk Solutions Group
**Purpose:** Master field reference for all commercial client intake, AI research pre-fill, underwriting submission, and CRM data entry. Every commercial account must be evaluated against this schema before a quote is submitted or a policy is bound.

**Legend:**
- `[R]` = Required — submission cannot proceed without this
- `[O]` = Optional — collect when available
- `[AI]` = AI can research / pre-fill before client call
- `[G]` = Gretchen handles data entry
- `[L]` = Lamar reviews / approves

---

## 1. Business Identity

| Field | Tag | Source | Notes |
|---|---|---|---|
| Legal business name (exact as filed) | [R] | Client / SOS | Must match carrier app exactly |
| DBA / trade name(s) | [R] | Client / Web | All operating names — each may need separate endorsement |
| Entity type | [R] | Client / SOS | LLC, Corp, S-Corp, Sole Prop, Partnership |
| FEIN / EIN | [R] | Client | No exceptions — required by all carriers |
| Date established | [R] | SOS / Web | Years in business is a major rating factor |
| State of formation | [O] | SOS | GA-registered vs. foreign entity — affects admitted carrier eligibility |
| NAICS code | [AI] | AI research | Auto-identify from operations description |
| SIC code | [AI] | AI research | Cross-reference with NAICS |
| Prior non-renewal reason | [O] | Client | Carrier red flag — ask directly; don't assume |
| SOS filing status (active / dissolved) | [AI] | AI / SOS.GA.gov | Pull before every submission |


---

## 2. Location & Premises

| Field | Tag | Source | Notes |
|---|---|---|---|
| Mailing address | [R] | Client | |
| All operating locations | [R] | Client | Each location = separate rated risk — list all |
| Owned vs. leased (per location) | [R] | Client | Drives property coverage structure |
| Building square footage (per location) | [R] | Client | Required for property rating — don't skip |
| Year built (per location) | [R] | Client | Age of construction is a major rate driver |
| Construction type | [R] | Client | Frame / Joisted Masonry / Masonry / Fire Resistive |
| Flood zone designation | [R][AI] | AI / FEMA MSC | Auto-lookup via msc.fema.gov by address — required for all locations |
| Mortgagee / lienholder info | [O] | Client | Required for loss payee endorsement on owned buildings |
| Landlord / lessor info | [O] | Client | Required if leased — may require additional insured |
| Sprinkler system? (Y/N) | [O] | Client | Rate discount — always ask |
| Security / alarm system? (Y/N) | [O] | Client | Theft and GL rate factor |
| Any renovations in past 3 years? | [O] | Client | Building value may be understated — ITV check needed |
| Total insurable building value | [R] | Client | Replacement cost — not market value |
| Total business personal property value | [R] | Client | Contents + equipment inside the building |
| Business income / extra expense needed? | [O] | Client | How long could they survive a shutdown? |

---

## 3. Key People

| Field | Tag | Source | Notes |
|---|---|---|---|
| All owners / officers (name + % ownership + role) | [R] | Client / SOS | Required for all lines — WC exclusion list if applicable |
| Primary contact name | [R] | Client | |
| Primary contact email | [R] | Client | |
| Primary contact phone | [R] | Client | |
| Secondary contact (Gretchen's day-to-day contact) | [O] | Client | Ops manager, bookkeeper, etc. |
| Licenses held (contractor, food handler, professional) | [O] | Client / State | Some carriers require proof |
| SSN (sole proprietors only) | [O] | Client | Some carriers require for mono-line personal link |


---

## 4. Financials & Payroll

| Field | Tag | Source | Notes |
|---|---|---|---|
| Annual gross sales / revenue — current year | [R] | Client | GL and liquor liability primary rating basis |
| Annual gross sales — prior 2 years | [R] | Client | Trend line matters for underwriting appetite |
| Annual total payroll — current year | [R] | Client | WC primary rating basis |
| Annual total payroll — prior 2 years | [O] | Client | WC audit baseline comparison |
| Payroll by WC class code | [R] | Client | Highest-rated class drives WC premium — break out if possible |
| Number of employees — full time | [R] | Client | |
| Number of employees — part time | [R] | Client | |
| Number of employees — seasonal / temporary | [O] | Client | Peak headcount affects WC audit exposure |
| Subcontractor annual spend | [R] | Client | Uninsured subs = your GL and WC exposure |
| Do subcontractors carry their own insurance? | [R] | Client | COIs required — if not, add to payroll basis |
| Cost of goods sold (if selling products) | [O] | Client | Products liability rating basis |
| Estimated largest single job / contract / event | [O] | Client | Umbrella sizing and contract review trigger |
| Seasonal revenue fluctuation | [O] | Client | High/low months — audit exposure risk |

---

## 5. Operations

| Field | Tag | Source | Notes |
|---|---|---|---|
| Full operations description (what / how / where) | [R] | Client / Web | Write this in plain English — used for carrier submissions |
| Work performed outside Georgia? | [O] | Client | Multi-state WC and GL exposure |
| Alcohol served or sold? | [O] | Client | % of revenue — liquor liability trigger above 25% |
| Vehicles used in operations? | [O] | Client | Triggers commercial auto question set |
| Do they sell physical products? | [O] | Client | Products liability exposure — separate rating needed |
| Do they provide professional advice or services? | [O] | Client | E&O / professional liability trigger |
| Do they store customer PII or payment data? | [O] | Client | Cyber liability trigger — yes/no is enough to start |
| Do they perform work at customer locations? | [O] | Client | Off-premises GL exposure |
| Any government / public sector contracts? | [O] | Client | DBE/MBE certified = likely public contract work = surety exposure |
| Any franchise agreements or licensing? | [O] | Client | Franchisor may require specific coverage and limits |


---

## 6. Recent Updates (Review at Every Renewal)

| Field | Tag | Source | Notes |
|---|---|---|---|
| Any ownership changes in past 3 years? | [R] | Client | Affects WC experience mod — must report to carrier |
| Any new locations opened or closed? | [R] | Client | Coverage gap risk if unreported |
| Any new vehicles added or removed? | [R] | Client | Unscheduled vehicles = no coverage |
| Any new employees or contractors added? | [R] | Client | WC payroll and GL exposure change |
| Any building renovations or improvements? | [O] | Client | Insurable value may need updating |
| Any pending claims or open lawsuits? | [R] | Client | Material to all lines — disclose or get non-renewed |
| Any carrier notices received (non-renewal, rate increase)? | [O] | Client | Retention red flag — act 90 days before expiration |
| Any changes to operations, products, or services? | [R] | Client | New exposure may not be covered under existing policy |
| Any new certificates of insurance required? | [O] | Client | New contracts often add AI / WOS requirements |

---

## 7. Existing Coverage

| Field | Tag | Source | Notes |
|---|---|---|---|
| Current carrier(s) — all lines | [R] | Client / NowCerts | |
| Current policy numbers — all lines | [R] | Client / NowCerts | |
| Expiration dates — all lines | [R] | Client / NowCerts | Set renewal tasks 90 days out (commercial) |
| Current premiums — all lines | [R] | Client / Dec pages | Remarketing baseline — know what you're beating |
| 5-year loss runs — all carriers, all lines | [R] | Client / Carrier | Required for every new submission — no exceptions |
| Current limits by line | [R] | Client / Dec pages | Adequacy check — limits may be understated |
| Umbrella / excess currently in place? | [O] | Client | What's the current umbrella limit? |
| Certificate holders on file | [O] | Client | Who gets COIs — ongoing Gretchen service task |
| Additional insured requirements (blanket vs. scheduled) | [O] | Client | Contract review needed if blanket AI required |
| Waiver of subrogation required? | [O] | Client | Contractor clients almost always need this |
| Primary and non-contributory required? | [O] | Client | Large GC and municipality contracts require this |
| Coverage gaps identified | [AI][L] | AI review of dec pages vs. operations | Lamar reviews AI output before client conversation |
| Prior non-renewal or cancellation history | [R] | Client | Ask directly — do not skip |


---

## 8. Commercial Auto (Complete Only If Vehicles Used in Operations)

| Field | Tag | Source | Notes |
|---|---|---|---|
| Vehicle list (year / make / model / VIN / GVW) | [R] | Client | One row per vehicle |
| Owned vs. leased vs. hired | [R] | Client | Each category rates differently |
| Garaging address per vehicle | [R] | Client | Territory is a major auto rate driver |
| Primary use per vehicle (delivery / transport / service) | [R] | Client | |
| Radius of operations | [R] | Client | Local (< 50 mi) / intermediate / long haul |
| Driver list (name / DOB / license # / state) | [R] | Client | MVR pull required before binding |
| Any drivers under 25? | [R] | Client | Surcharge trigger — some carriers decline |
| Any drivers with violations in past 3 years? | [R] | Client | Disclose upfront — don't let the MVR surprise you |
| Hired and non-owned auto exposure? | [O] | Client | Employees using personal vehicles for work? Renting vehicles? |
| DOT number (if applicable) | [O] | Client | Required for vehicles over 10,001 lbs GVW |
| Cargo type (if transporting goods for others) | [O] | Client | Motor truck cargo trigger |

---

## 9. AI Pre-Fill Fields (Research Before Every Client Call)

These fields should be populated by the OpenClaw prospect-researcher or carrier-appetite agent before Gretchen or Lamar touches the file.

| Field | AI Source | Notes |
|---|---|---|
| FEMA flood zone by address | msc.fema.gov lookup | Flag Zone A or AE — flood policy likely required |
| SOS filing status (active / dissolved / admin dissolved) | SOS.GA.gov | If dissolved, stop — do not submit |
| Online reviews and reputation signals | Google / Yelp / BBB | Litigation risk indicator |
| DBE / MBE / WBE certifications | SAM.gov / state portal | Public contract = surety and bonding exposure |
| News / litigation / judgments | Google / CourtListener | Material non-disclosure risk |
| NAICS / SIC code match | AI inference from operations | Cross-reference with GL class code table |
| Industry loss benchmarks | Carrier appetite docs | Helps set client expectations on price |
| Competitor coverage intel | AI / carrier appetite | What similar risks typically carry |
| Prior carrier history (if findable) | Web / CLUE | Context for loss run narrative |

---

## 10. Cross-Sell Triggers (Flag for Lamar Review)

These fields are not intake data — they are signals that OpenClaw agents should flag to `#lamar-alerts` when identified.

| Trigger | Signal | Action |
|---|---|---|
| 5+ employees | EPLI / employment practices exposure | Recommend EPLI quote |
| Sells food or products | Products liability exposure | Confirm products coverage in GL |
| Stores customer PII / payments | Cyber exposure | Offer cyber quote |
| Government contracts | Surety / bonding exposure | Ask about bond requirements |
| Vehicles in operations | Commercial auto gap check | Confirm auto is scheduled |
| No umbrella on file | Limits adequacy risk | Umbrella quote — every commercial client |
| Alcohol > 25% of sales | Liquor liability trigger | Standalone liquor liability |
| Renting or borrowing vehicles | Hired / non-owned auto | Add HNOA endorsement |
| Professional advice given | E&O / professional liability | Recommend E&O quote |
| DBE / MBE certified | Public contract work | Ask about bond and surety needs |

---

## 11. Submission Gate (Required Before Any Carrier Submission)

All fields marked `[R]` in sections 1–7 must be confirmed before submission. OpenClaw agents must enforce this gate.

**Submission blocked if any of the following are missing:**
- [ ] FEIN / EIN
- [ ] Legal business name (exact)
- [ ] 5-year loss runs (all lines)
- [ ] Annual gross sales (current year)
- [ ] Annual payroll (current year)
- [ ] Full operations description
- [ ] All locations listed
- [ ] SOS status confirmed active
- [ ] Any open claims disclosed

**Submission warning (flag to Lamar, do not auto-block):**
- [ ] Prior non-renewal on file
- [ ] Driver under 25 on auto
- [ ] Flood zone A or AE
- [ ] AI confidence < 70% on operations classification
- [ ] Loss ratio > 50% in any single year

---

## Related Vault Documents

- [[RSG Commercial Data Model]] — NAICS, SIC, GL codes, WC codes, risk scoring matrix
- [[AI Underwriting Runbook]] — Step-by-step AI underwriting automation workflow
- [[RSG-Architecture-2026]] — Full system architecture
- [[Account Entity — Complete Field Reference]] — EspoCRM field names and enums
- [[Opportunity Entity — Complete Field Reference]] — Pipeline stage and LOB fields

---
*Generated by Claude / RSG OpenClaw — update this file whenever the intake template changes. Commit to GitHub after every edit.*
