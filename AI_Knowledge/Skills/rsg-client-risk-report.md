---
name: rsg-client-risk-report
description: >
  Client-facing risk profile generator. Reads dec pages (PDF or manual entry) or a completed RSG pre-screen assessment and produces a hosted HTML report. Leads with what the client has and what it means in plain English, then flags gaps, then presents RSG's action plan. Also runs web lookups for personal auto market value and Georgia home rebuild cost estimates.
platform: Dify (Chatflow)
model: claude-sonnet-4-20250514
tools: Web Search, PDF Upload
used_by: Lamar Coates, Gretchen Coates
output: Client-facing HTML report (hosted link or Assembly iframe)
status: spec-ready
created: 2026-04-08
related_agents: Quote Pre-Screen (n8n uY9G3kTxTchOZ5UG + Dify dataset 450fb20c)
---

# RSG Client Risk Report Agent

## Purpose

Turns raw insurance policy data into a personalized, client-readable risk profile.
Used after a new account is written OR as a pre-close tool to show prospects what RSG found and how we fix it.
Post-close, re-run with new policy data to produce a before/after risk improvement view.

---

## Input Modes

### Scenario A — Raw dec pages
PDF upload or manual entry of carrier declaration pages.
Agent extracts all data and runs full analysis.

### Scenario B — Completed RSG assessment
PDF output from the Quote Pre-Screen agent.
Agent reads the completed assessment and translates it into client-facing language.
No re-analysis. Translation only.

### Scenario C — Mixed
Both dec pages and partial assessment present.
Agent uses assessment where available, fills gaps from dec pages.

---

## Manual Entry Format (Gretchen / Lamar)


```
CLIENT: [Full name or business name]
DATE: [Today's date]

POLICY 1:
- Type: [Personal Auto / Homeowners / BOP / Commercial Auto / Workers Comp / Umbrella]
- Carrier: [Name]
- Premium: [$ amount] [annual / 6-month]
- Vehicles (if auto): [Year Make Model Trim]
- Address (if home/property): [Full address including county]
- Limits: [All limits — BI, PD, dwelling, liability, etc.]
- Deductibles: [All deductibles]
- Endorsements: [Any add-ons or scheduled items]

POLICY 2: [repeat]

NOTES: [Anything specific to flag or highlight]
```

---

## Web Lookups (runs automatically when applicable)

### Personal Auto — Market Value
- Trigger: any personal auto policy present
- Search: `[year] [make] [model] [trim] retail value Georgia [current year]`
- Sources: KBB, Edmunds, CarGurus
- Flags UNDERINSURED (market > insured value) or PREMIUM WASTE (low-value vehicle with full comp/coll)
- Flag threshold for premium waste: vehicle retail under $6,000

### Home Rebuild Cost — Georgia Only
- Trigger: any homeowners policy present
- Search: `residential construction cost per square foot [county] Georgia [current year]`
- Sources: RSMeans, HomeAdvisor, local contractor data
- Calculates: sq ft × cost/sq ft = estimated rebuild
- Compares to Coverage A (dwelling limit)
- Flags UNDERINSURED if rebuild estimate exceeds Coverage A by more than 15%
- If sq ft not on dec page: searches public records for property address

---

## Report Structure (always this order)

1. **Portfolio snapshot** — total spend, # policies, # carriers
2. **What your coverage actually does** — one card per policy, plain English, key limits shown
3. **What we found** — positives first (green), then gaps ordered high → medium → low severity
4. **How we're going to fix it** — RSG action plan written as "we will" not "you should"
5. **CTA** — schedule a call with Lamar


---

## Gap Analysis Rules

### Liability — Personal
| Condition | Severity |
|---|---|
| Personal auto at GA state min ($25k/$50k) | Critical |
| No personal umbrella (homeowner + business owner) | High |

### Liability — Commercial
| Condition | Severity |
|---|---|
| Commercial auto under $500k | High |
| Commercial auto under $1M | Medium |
| No commercial umbrella over GL + commercial auto | High |
| GL per-occurrence < commercial auto limit | Medium |

### Property
| Condition | Severity |
|---|---|
| Dwelling underinsured vs rebuild estimate | High |
| No water backup/sewer coverage | Medium |
| No service line coverage | Low |

### Coverage Gaps
| Condition | Severity |
|---|---|
| WC missing for businesses with employees | Critical |
| Liquor liability missing for food/beverage | Critical |
| No hired/non-owned auto for employee drivers | Medium |

---

## Dify Configuration

| Setting | Value |
|---|---|
| Model | claude-sonnet-4-20250514 |
| Temperature | 0.3 |
| Max tokens | 8000 |
| Tools | Web Search (enabled) |
| File upload | PDF, max 5 files |
| Memory | Off (each report is a fresh session) |

**Opening message (shown to operator, not client):**
> RSG Risk Report Agent ready. Upload PDF dec pages or a completed assessment, or type in policy details using the standard format. I'll extract the data, run market value and rebuild cost checks, and produce a client-ready HTML report.

**Output rule:** Final output is a single complete HTML document — nothing else. If data is missing, output a bulleted list of what's missing before producing any HTML.

---

## Post-Close: Risk Improvement View

Re-run the agent after new policies are bound. Pass both original and new policy data with this header:

```
REPORT TYPE: POST-CLOSE COMPARISON
Original policies: [old data]
New policies: [new confirmations]
```

Agent generates the same report with a before/after column on all gap items.
Positive findings section becomes the hero — leads with everything that improved.
This is the **retention tool** — client sees their risk score improve and ties it to RSG.

---

## Relationship to Other RSG Agents

| Agent | Relationship |
|---|---|
| Quote Pre-Screen (n8n uY9G3kTxTchOZ5UG) | Upstream — its output PDF feeds this agent in Scenario B |
| Prospect Researcher | Separate — pre-call intel only, no overlap |
| Renewal Watchdog | Downstream — post-close report supports renewal retention story |

---

## Full Spec
See: `RSG/Workflows/rsg-client-risk-report-dify-spec.md` for complete system prompt and HTML template.
