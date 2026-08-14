---
title: Supabase → Microsoft Handoff
updated: 2026-08-14
tags: [rsg, supabase, amy, copilot-studio, microsoft, handoff]
status: next-session
---

# SUPABASE → MICROSOFT HANDOFF

**Project:** rsg-infrastructure (wibscqhkvpijzqbhjphg)  
**Supabase session:** Complete  
**Next session:** Microsoft Copilot Studio

GitHub: [agency-knowledge-build/MICROSOFT-HANDOFF.md](https://github.com/googrlc/agency-knowledge-build/blob/main/MICROSOFT-HANDOFF.md)

Architecture lock: [[03-Systems/Architecture/Amy-Copilot-Chat-Architecture]]  
Supabase technical detail: [[rsg-infrastructure/Supabase-Readiness-Final-2026-08-14]]

---

## WHAT WAS BUILT

### Embeddings — 100% complete

| Table | Rows | Embedded | Text Embedded |
|-------|-----:|---------:|-------------|
| gl_class_codes | 1,154 | 1,154 | gl_code + description + search_keywords + typical_businesses + notes |
| wc_class_codes | 499 | 499 | wc_code + description + search_keywords + typical_duties + notes |
| naics_codes | 2,126 | 2,126 | naics_code + naics_title + description + common_ops_keywords + notes |
| sic_codes | 445 | 445 | sic_code + sic_description + subcategory + subcategory_2 + level_3_term |
| operations_to_codes | 57 | 57 | operation_name + keywords + notes |
| knowledge_chunks | 34 | 34 | content + source_title + source_section + carrier_name + lob |
| ai_knowledge_items | 121 | 121 | content + title + lob + carrier_name + insured_name + tags |
| **TOTAL** | **4,436** | **4,436** | |

### SQL RPCs — 8 live and tested

| Function | Test Result | What It Does |
|----------|-------------|-------------|
| `search_carrier_appetite` | 5 rows + contacts fallback | Searches carrier appetite by LOB, state, class codes, carrier name. Falls back to name matching when carrier_id is null. |
| `classify_risk` | Tokenized, matches "plumbing" | Keyword classification. Splits query into words, skips filler words. Searches operations, GL, WC, NAICS, SIC. |
| `run_commission_reconciliation` | **70 discrepancies** found | Compares transactions against rules. Case-insensitive carrier matching + LOB aliases. Dry run and live modes. |
| `create_commission_escalation` | Deployed (empty until live run) | Creates escalation from a reconciliation record. Amy calls this. |
| `get_open_cases` | 12 open cases with tasks + events | Open CRM cases with nested tasks, recent events, overdue flags. |
| `get_client_profile` | Client + policy + cases | Full client view: canonical_clients + canonical_policies + open cases + open tasks. |
| `get_medicare_plans` | 5 plans in Jackson county | Medicare plan lookup by county with nested availability. |
| `match_similar` | 7 tables including ai_knowledge_items | Vector similarity search across all embedded tables. Called by semantic-search Edge Function. |

### Edge Functions — 2 live

| Function | URL | What It Does |
|----------|-----|-------------|
| `batch-embed` | `POST /functions/v1/batch-embed` | Batch embedding generation for any table in TABLE_CONFIG. |
| `semantic-search` | `POST /functions/v1/semantic-search` | Takes a query string, calls OpenAI for embedding, searches all 7 embedded tables via match_similar RPC. |

### Supporting infrastructure

| Component | Status |
|-----------|--------|
| `lob_aliases` table | 21 mappings (Auto ↔ Commercial Auto, GL ↔ General Liability, etc.) |
| `lob_matches()` function | SQL helper for flexible LOB matching |
| `update_embedding()` RPC | Safe vector write from Edge Functions |
| `ai_knowledge_items` table | Created, backfilled from carrier_appetite + agency_crm_cases + knowledge_chunks, embedded |
| `agent_runs` table | Schema live, 0 rows (populates when Amy goes live) |
| `agent_writes` table | Schema live, 0 rows (populates when Amy creates work) |

### Data gaps (not schema — data loading tasks)

| Gap | Rows | Impact | Resolution |
|-----|-----:|--------|------------|
| agency_bill_invoices | 0 | Agency Bill Agent blocked | ETL from NowCerts |
| appetite_placement_outcomes | 0 | No "similar risk placed before" history | Load from cc_submissions or manual entry |
| commission_reconciliation | 0 | Will populate when live recon runs | `SELECT * FROM run_commission_reconciliation(false, 1.00)` after review |
| carrier_appetite | 74 | Thin appetite book | Expand with more carrier data |
| carrier_appetite_class_codes | 9 | Most appetite rows unmapped to class codes | Map remaining 65 rows |
| knowledge_chunks | 34 | Limited RAG grounding | Ingest more SharePoint/Nextcloud PDFs |

---

## ENDPOINTS FOR MICROSOFT SESSION

### SQL RPCs (Power Automate calls these via HTTP POST)

```
Base URL: https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/rpc/{function_name}

Headers (all RPCs):
  apikey: {SUPABASE_SERVICE_ROLE_KEY}
  Authorization: Bearer {SUPABASE_SERVICE_ROLE_KEY}
  Content-Type: application/json
```

| Flow Name (for Copilot Studio) | RPC Function | Body Template |
|-------------------------------|-------------|-------------|
| SearchCarrierAppetite | `search_carrier_appetite` | `{"p_lob": "...", "p_state": "...", "p_gl_code": "...", "p_limit": 20}` |
| ClassifyRisk | `classify_risk` | `{"p_operation_description": "...", "p_state": "..."}` |
| RunCommissionRecon | `run_commission_reconciliation` | `{"p_dry_run": true, "p_min_delta": 1.00}` |
| CreateEscalation | `create_commission_escalation` | `{"p_reconciliation_id": "uuid", "p_created_by": "email", "p_reason_label": "..."}` |
| GetOpenCases | `get_open_cases` | `{"p_user_email": "...", "p_limit": 20}` |
| GetClientProfile | `get_client_profile` | `{"p_insured_name": "..."}` or `{"p_insured_guid": "..."}` |
| GetMedicarePlans | `get_medicare_plans` | `{"p_county_name": "...", "p_plan_type": "...", "p_limit": 50}` |

### Edge Function (Power Automate calls this via HTTP POST)

```
URL: https://wibscqhkvpijzqbhjphg.supabase.co/functions/v1/semantic-search

Headers:
  Authorization: Bearer {SUPABASE_SERVICE_ROLE_KEY}
  Content-Type: application/json

Body: {"query": "...", "tables": ["ai_knowledge_items", "gl_class_codes", ...], "limit": 10, "threshold": 0.5}
```

---

## MICROSOFT SESSION — BUILD ORDER

```
STEP 1: Azure Key Vault
  └─ Store SUPABASE_SERVICE_ROLE_KEY as secret

STEP 2: Create Amy (orchestrator) in Copilot Studio
  └─ Name: Amy
  └─ Description: Master agency assistant for Risk Solutions Group
  └─ Instructions: [full Amy system prompt — routing logic, daily function, rules]
  └─ Enable multi-agent orchestration

STEP 3: Create sub-agents (hidden from users)
  ├─ Carrier Appetite Agent
  ├─ Classification Agent
  ├─ Commission Agent
  ├─ CRM/Service Agent (Amy handles directly, but configure as sub-agent for tool access)
  └─ Medicare Agent

STEP 4: Create 8 Power Automate flows (one per endpoint above)
  └─ Each flow: Copilot Studio trigger → HTTP POST to Supabase → return JSON

STEP 5: Register flows as tools on the appropriate agent
  ├─ SearchCarrierAppetite → Carrier Appetite Agent
  ├─ ClassifyRisk → Classification Agent
  ├─ SemanticSearch → All agents (shared tool)
  ├─ RunCommissionRecon → Commission Agent
  ├─ CreateEscalation → Commission Agent + Amy
  ├─ GetOpenCases → Amy
  ├─ GetClientProfile → Amy
  └─ GetMedicarePlans → Medicare Agent

STEP 6: Add SharePoint knowledge source to Amy
  └─ Select SharePoint site with carrier appetite PDFs, policy examples, SOPs

STEP 7: Configure governance
  ├─ Enable moderation
  ├─ Enable user feedback
  ├─ Enable transcript recording
  ├─ Apply DLP policies
  ├─ Connect Application Insights
  └─ Create Power Platform solution "RSGAIAgents" for ALM

STEP 8: Publish Amy to Microsoft 365 Copilot Chat
  └─ Channels → Microsoft 365 Copilot → Publish
  └─ Do NOT add Teams or SharePoint channels

STEP 9: Test
  └─ "Amy, I have a plumbing contractor in Georgia. What class codes apply and who writes this risk?"
  └─ "Amy, what's on my desk today?"
  └─ "Amy, any commission issues?"
  └─ "Amy, what do we know about Blessed Route Transport?"
  └─ "Amy, what Medicare plans are available in Jackson county?"
```

---

## AMY'S SYSTEM PROMPT (for Copilot Studio)

```
You are Amy, the master agency assistant for Risk Solutions Group.

Your role:
1. Route questions to specialist agents when appropriate
2. Summarize client history and case status
3. Track open work and next actions
4. Draft client/carrier follow-up communications
5. Create tasks and escalations when needed

ROUTING RULES:
- "Who writes [risk] in [state]?" → Carrier Appetite Agent
- "What class codes for [operation]?" → Classification Agent + SemanticSearch
- "What GL/WC codes apply to [business]?" → Classification Agent
- "Any commission issues?" → Commission Agent (RunCommissionRecon)
- "Escalate [reconciliation]" → Commission Agent (CreateEscalation)
- "What's on my desk?" / "What's open?" → GetOpenCases
- "What do we know about [client]?" → GetClientProfile
- "What Medicare plans in [county]?" → Medicare Agent
- "Find similar [risk/operation/case]" → SemanticSearch

ALWAYS:
- Cite the source (table name, record ID)
- Flag when data may be stale
- Suggest next best action
- Offer to create a follow-up task
- Be concise and professional

NEVER:
- Bind coverage or make coverage decisions
- Send communications without human review
- Make up data not in the system
- Mix Medicare data into P&C workflows
- Modify financial records directly

When data is missing or thin, say so explicitly rather than guessing.
```

---

## THE FIRST TEST PROMPT

After publishing, open Copilot Chat and type:

```
Amy, I have a new submission — a plumbing contractor in Georgia, 
$2M revenue, 12 employees. What class codes apply and who writes this risk?
```

**What should happen:**
1. Amy identifies this needs classification + carrier appetite
2. Amy calls Classification Agent → `classify_risk('plumbing contractor')` + `semantic-search` for RAG
3. Classification Agent returns GL 98482/98483, WC 5183/5037, NAICS 238220
4. Amy calls Carrier Appetite Agent → `search_carrier_appetite(p_lob := 'Commercial Auto', p_state := 'GA')`
5. Carrier Appetite Agent returns Progressive, Liberty Mutual, State Auto with contacts
6. Amy combines and responds in one Copilot Chat message

---

Supabase is locked and ready. See you in the Microsoft session.
