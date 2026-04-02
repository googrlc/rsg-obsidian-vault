---
name: call-intake-parser
description: >
  Parses commercial client intake call transcripts into structured JSON,
  writes the result to EspoCRM (Account + Opportunity + Tasks), and generates
  a PDF intake report. Trigger ANY TIME Lamar says "parse this intake call",
  "parse this transcript", "write this to CRM", "intake report for [client]",
  or uploads a transcript file after a client call. Also triggers when Gretchen
  submits a completed intake form. Output: structured JSON, EspoCRM records
  created/updated, follow-up tasks for missing fields, PDF report, Slack alert
  to #lamar-alerts. Uses Anthropic (revenue-critical). Depends on: EspoCRM API,
  n8n webhook, Commercial-Client-Intake-Schema.md.
---

# Call Intake Parser

## Purpose
Parse a raw call transcript or intake notes into all fields from the
Commercial Client Intake Schema, write to EspoCRM, flag missing required
fields, identify cross-sell opportunities, and generate a PDF intake report.

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `transcript` | Yes | Raw text of the call transcript or intake notes |
| `client_name` | Yes | Business name — used for CRM lookup/create |
| `call_date` | Yes | Date of call (YYYY-MM-DD) |
| `call_type` | Yes | `new_prospect` / `existing_client` / `renewal_review` |
| `called_by` | No | `lamar` or `gretchen` — defaults to `lamar` |

---

## Step 1 — Parse Transcript via Claude API

Send the transcript to Claude API with the system prompt below.
Model: `claude-sonnet-4-20250514`
Max tokens: 4000
Response format: JSON only — no preamble, no markdown fences.

### System Prompt
```
You are an expert commercial insurance intake analyst for Risk Solutions Group (RSG),
an independent agency in Atlanta, GA specializing in commercial P&C.

Your job is to extract structured client information from a call transcript or intake notes.
Extract ONLY what is explicitly stated or clearly implied. Do NOT invent or assume values.
If a field is not mentioned, set it to null.

Return a single JSON object with this exact structure. No preamble. No markdown. JSON only.

{
  "business_identity": {
    "legal_name": null,
    "dba": null,
    "entity_type": null,
    "fein": null,
    "date_established": null,
    "state_of_formation": null,
    "naics_code": null,
    "sic_code": null,
    "prior_non_renewal": null,
    "sos_status": null
  },
  "location": {
    "mailing_address": null,
    "operating_locations": [],
    "owned_or_leased": null,
    "sq_footage": null,
    "year_built": null,
    "construction_type": null,
    "flood_zone": null,
    "building_value": null,
    "bpp_value": null,
    "sprinkler": null,
    "security_system": null
  },
  "key_people": {
    "owners": [],
    "primary_contact_name": null,
    "primary_contact_email": null,
    "primary_contact_phone": null,
    "licenses": []
  },
  "financials": {
    "annual_revenue_current": null,
    "annual_revenue_prior_1": null,
    "annual_revenue_prior_2": null,
    "annual_payroll_current": null,
    "employees_ft": null,
    "employees_pt": null,
    "employees_seasonal": null,
    "subcontractor_spend": null,
    "subs_insured": null
  },
  "operations": {
    "description": null,
    "multi_state": null,
    "alcohol_pct": null,
    "vehicles_in_ops": null,
    "sells_products": null,
    "professional_advice": null,
    "stores_pii": null,
    "government_contracts": null
  },
  "recent_updates": {
    "ownership_change": null,
    "new_locations": null,
    "new_vehicles": null,
    "pending_claims": null,
    "carrier_notices": null,
    "operations_change": null
  },
  "existing_coverage": {
    "carriers": [],
    "policy_numbers": [],
    "expiration_dates": [],
    "current_premiums": [],
    "loss_runs_received": null,
    "umbrella_in_place": null,
    "umbrella_limit": null,
    "prior_non_renewal_reason": null
  },
  "auto": {
    "vehicles": [],
    "drivers": [],
    "radius": null,
    "dot_number": null,
    "hnoa_exposure": null
  },
  "cross_sell_flags": [],
  "missing_required_fields": [],
  "submission_ready": false,
  "ai_confidence": 0,
  "call_summary": null,
  "next_actions": []
}

For cross_sell_flags, include any of these that apply based on the transcript:
"umbrella_needed", "cyber_exposure", "epli_exposure", "products_liability",
"eo_professional", "liquor_liability", "hnoa_exposure", "surety_bonding",
"commercial_auto_gap", "aflac_cross_sell"

For missing_required_fields, list every [R] field from the intake schema not found in the transcript.

For ai_confidence, return 0-100 based on how complete and clear the transcript is.

For next_actions, return 3-5 specific follow-up items as strings.
```

---

## Step 2 — Write to EspoCRM

After parsing, POST to the n8n webhook:
`POST https://n8n-zpvua-u69864.vm.elestio.app/webhook/commercial-intake`

Payload:
```json
{
  "parsed_data": { ...Claude JSON output... },
  "client_name": "...",
  "call_date": "YYYY-MM-DD",
  "call_type": "new_prospect|existing_client|renewal_review",
  "called_by": "lamar|gretchen",
  "transcript_snippet": "first 500 chars of transcript for reference"
}
```

The n8n workflow handles:
1. Account lookup or create in EspoCRM
2. Opportunity create/update with LOB and stage
3. Task creation for each missing required field
4. Cross-sell opportunity tasks to #lamar-alerts

---

## Step 3 — Generate PDF Report

After CRM write succeeds, trigger PDF generation.
The PDF is built from the parsed JSON and saved as:
`[ClientName]-Intake-[YYYY-MM-DD].pdf`

PDF sections:
1. Client summary card (name, address, contact, entity type)
2. Confirmed fields by section (green checkmarks)
3. Missing required fields (red flags)
4. Cross-sell opportunities
5. Submission readiness score
6. Next action items
7. Call summary paragraph

---

## Step 4 — Slack Alert

Post to `#lamar-alerts`:
```
🗂 NEW INTAKE: [Client Name]
📅 [Call Date] | [Call Type]
✅ Confidence: [X]%
⚠️ Missing required fields: [N]
💰 Cross-sell flags: [list]
📋 Submission ready: YES / NO
View in CRM: [link]
```

---

## Error Handling

- If Claude API returns error → log to `#systems-check`, do not write to CRM
- If EspoCRM write fails → log error, alert `#lamar-alerts`, save JSON to vault
- If confidence < 50 → flag for Lamar review, do not auto-create opportunity
- If `pending_claims: true` → add warning banner to PDF and Slack message

---

## LLM Routing
- Parser: **Anthropic** (revenue-critical — this drives CRM data quality)
- PDF generation: Gemini Flash (not revenue-critical)
