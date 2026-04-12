---
title: RSG Dify Agent Registry
tags: [dify, agents, workflows, registry, canonical]
created: 2026-04-08
updated: 2026-04-12
status: active
type: registry
---

# RSG Dify Agent Registry

> [!important] Source of Truth
> This file tracks all Dify apps in `admin's Workspace` on the RSG Dify instance.
> Instance: `https://dify-zglao-u69864.vm.elestio.app` | Tailscale: `100.122.238.64`
> Admin credentials stored in 1Password RSG vault.

---

## App Registry

| App Name | App ID | Mode | Status | Used By | Purpose |
|---|---|---|---|---|---|
| RSG Client Intake & Assessment | 81bfd19b-5cee-4726-915e-bddc92d3556d | Workflow | 🟡 Audit fixes pending | Lamar + Gretchen | Intake dec pages/notes → extract → enrich → EspoCRM + Supabase → assessment report |
| RSG Quote Pre-Screen | 0f8ed022-5006-4085-9874-5929f9319cbf | Agent-chat | 🟢 Live | Lamar + Gretchen | Geico commercial auto GO / CAUTION / NO-GO verdict |
| RSG Commercial Assessment | 1a3a6d8d-8feb-4dbb-a509-e41b7ec20830 | Chatflow | 🟢 Live | Lamar | CL commercial assessment |
| Personalized Memory Assistant | 7558d0aa-a4c9-43dd-9b88-4ffb6ffd3167 | Chatflow | 🟢 Live | Internal | General AI memory assistant |
| RSG Client Risk Report | TBD — build next sprint | Chatflow | 🟡 Spec ready | Lamar + Gretchen | Client-facing HTML risk profile from assessment output |
| RSG Appetite Guide Ingestor | TBD — next sprint | Workflow | 🟡 Spec ready | Lamar | Upload carrier UW PDF → chunk → index into knowledge base |

---

## RSG Client Intake & Assessment — Deep Dive

**App ID:** `81bfd19b-5cee-4726-915e-bddc92d3556d`

**Draft Workflow ID:** `ac8eb261-ba20-4147-9429-9d3126f1588c`

**Published Workflow ID:** `33b4b6c6-ff90-48b5-a3d4-c6bc90d8982c`

**API Token:** stored in 1Password (`app-UtQB7dnEXr8xyNnZUXci4THV`)

**Nodes:** 19+ | **Edges:** 21+

**Supabase table:** `client_assessments` (project `wibscqhkvpijzqbhjphg`)

### Workflow Inputs (Start Node)

| Field | Type | Required | Notes |
|---|---|---|---|
| transcription_notes | text | No | Call notes from Gretchen |
| files | Array[File] | No | Upload dec pages / images |
| client_type | enum | Yes | "Personal Lines" or "Commercial Lines" |
| additional_notes | text | No | Any extra context |

### Commercial Lines (CL) Node Flow

```text
Start
→ Detect Client Type (IF: client_type = Commercial Lines)
→ Extract Business Info (claude-sonnet-4-20250514)
→ Build CL Search Query
→ Tavily Search (Web)
→ Scrape Business Website (WebScraper)
→ Parse Web Research Results (claude-sonnet-4-20250514)
→ Classify & Enrich (claude-sonnet-4-20250514)
→ Supabase Carrier Appetite Lookup (HTTP GET)
→ EspoCRM — Create Account (HTTP POST)
→ EspoCRM — Create Opportunity (HTTP POST)
→ Generate Assessment Report / report_node (claude-sonnet-4-20250514)
→ cl_json_extract_node (claude-haiku-4-5-20251001)
→ cl_portal_prep_node (Code)
→ cl_save_report_node (HTTP POST → Supabase client_reports)
→ End
```

### Personal Lines (PL) Node Flow

```text
Start
→ Detect Client Type (ELIF: client_type = Personal Lines)
→ Extract Personal Lines Info (claude-sonnet-4-20250514)
→ Build PL Search Query
→ Tavily Search — Vehicles (Web)
→ Vehicle Research & Market Value (claude-sonnet-4-20250514)
→ Tavily Search — Property Records (Web)
→ Extract Property URL (claude-haiku-4-5-20251001)
→ Scrape Property Records Page (WebScraper)
→ Property Research & Rebuild Cost (claude-sonnet-4-20250514)
→ Generate PL Assessment Report / pl_report_node (claude-sonnet-4-20250514)
→ pl_json_extract_node (claude-haiku-4-5-20251001)
→ pl_portal_prep_node (Code)
→ pl_save_report_node (HTTP POST → Supabase client_reports)
→ End
```

### Key Node IDs

| Node Name | Node ID |
|---|---|
| supabase_appetite_node | supabase_appetite_node |
| espocrm_account_node | espocrm_account_node |
| espocrm_opportunity_node | espocrm_opportunity_node |
| Tavily (CL) | 1775687016841 |
| Tavily (PL vehicles) | 1775687042744 |
| Tavily (PL property) | 1775686926901 |
| pl_save_report_node | pl_save_report_node |
| cl_save_report_node | cl_save_report_node |

### Environment Variables (Set in Dify UI)

| Var Name | Used In | Notes |
|---|---|---|
| SUPABASE_api_key | All Supabase nodes | Anon key |
| SUPABASE_SERVICE_KEY | client_assessments write node | Service role key |
| ESPOCRM_API_KEY | EspoCRM account + opportunity nodes | Base64(key:) |

> [!danger] Open Audit Items (Apr 12 2026)
> 1. HIGH: `espocrm_account_node` — field `type` must be `accountType`
> 2. HIGH: `espocrm_opportunity_node` — field `type` must be `lineOfBusiness`
> 3. HIGH: `espocrm_opportunity_node` — stage value "Prospect" is invalid
> 4. CRITICAL: `espocrm_opportunity_node` — `accountId` missing (orphan risk)
> 5. MEDIUM: 3 Supabase nodes — hardcoded anon key, replace with `{{ENV.SUPABASE_ANON_KEY}}`
> 6. LOW: `pl_save_report_node`, `cl_save_report_node` — missing `espocrm_account_id`

---

## Client Portal Infrastructure

**Edge Function:** `client-portal`

**URL Pattern:** `https://wibscqhkvpijzqbhjphg.supabase.co/functions/v1/client-portal?id={report_id}`

**Supabase Table:** `client_reports`

**Columns:** `id` · `client_name` · `client_type` · `report_type` · `report_data (JSONB)` · `prospect_html` · `client_html` · `portal_url` · `status` · `espocrm_account_id`

**Two-Phase Model:**

| Phase | Trigger | Content |
|---|---|---|
| Prospect Report | End of intake workflow | Current coverage + gaps + recommendations |
| Client Report | Post-bind update | What improved, what stayed, 12-month roadmap |

---

## Model Usage Guide

| Model | Use Case | Nodes |
|---|---|---|
| claude-sonnet-4-20250514 | Complex extraction, assessment reports, enrichment | report_node, pl_report_node, Extract Business Info, Classify & Enrich |
| claude-haiku-4-5-20251001 | JSON extraction, URL parsing, lightweight transforms | json_extract nodes, extract_property_url_node |

---

## Deployment Runbook

> [!note] DSL Format
> Always use `.dsl` extension (YAML content). Never `.yml`.

```bash
# 1. Fix DSL locally
# 2. Validate YAML
# 3. Push to GitHub
cd ~/rsg-dify
git add -A
git commit -m "fix/feat: <description>"
git push origin main

# 4. SSH to Dify server
ssh dify-ts   # ~/.ssh/claudecode_dify | 100.122.238.64

# 5. Pull latest on server
cd ~/rsg-dify && git pull origin main

# 6. Get console auth token
curl -s -X POST http://localhost/console/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"DIFY_ADMIN_EMAIL","password":"DIFY_ADMIN_PASSWORD","remember_me":true}'

# 7. Import DSL (use access_token from step 6)
# For existing app use: POST /console/api/apps/{app_id}/import
```

## Related Notes

- [[RSG Agency Full Schema Setup]]
- [[n8n Workflow Inventory]]
- [[RSG Client Risk Report SPEC]]
- [[RSG Appetite Guide Ingestor SPEC]]
