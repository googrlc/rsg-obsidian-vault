---
title: Supabase Readiness — Final (Amy / Copilot Studio)
updated: 2026-08-14
tags: [rsg, supabase, amy, copilot-studio, pgvector, handoff]
status: ready-for-microsoft-session
---

# Supabase Readiness — Final

**Date:** 2026-08-14  
**Project:** `rsg-infrastructure` · ref `wibscqhkvpijzqbhjphg` · us-east-1  
**Status:** **Supabase work complete.** Next session is Microsoft Copilot Studio.

Architecture lock: [[03-Systems/Architecture/Amy-Copilot-Chat-Architecture]]  
Initial recon (pre-build): [[rsg-infrastructure/Supabase-Recon-2026-08-14]]  
Cursor workspace handoff: [agency-knowledge-build](https://github.com/googrlc/agency-knowledge-build) · `HANDOFF.md`

---

## Headline

Supabase is the **intelligence layer** for Amy. All schema, embeddings, RPCs, and Edge Functions are live and tested. **Nothing blocking the Microsoft session.**

| Layer | Status |
|---|---|
| pgvector + HNSW | ✅ 0.8.0 |
| Embeddings | ✅ **4,436 / 4,436** (100%) |
| SQL RPCs | ✅ 8 agent-facing functions |
| Edge Functions | ✅ `batch-embed` v3, `semantic-search` v2 |
| `ai_knowledge_items` | ✅ 121 rows, embedded, in RAG |
| Commission recon | ✅ 70 discrepancies on dry run |
| Governance tables | ✅ schema live (`agent_runs`, `agent_writes`) |

---

## Embeddings (4,436 total)

| Table | Rows | Embedded |
|---|---:|---:|
| `gl_class_codes` | 1,154 | 1,154 |
| `wc_class_codes` | 499 | 499 |
| `naics_codes` | 2,126 | 2,126 |
| `sic_codes` | 445 | 445 |
| `operations_to_codes` | 57 | 57 |
| `knowledge_chunks` | 34 | 34 |
| `ai_knowledge_items` | 121 | 121 |

**`ai_knowledge_items` backfill sources:**

| source_table | rows |
|---|---:|
| `carrier_appetite` | 74 |
| `agency_crm_cases` | 13 |
| `knowledge_chunks` | 34 |

---

## SQL functions (RPCs)

All callable via PostgREST: `POST https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/rpc/{name}`

Headers: `apikey`, `Authorization: Bearer {service_role_key}`, `Content-Type: application/json`

| Function | Purpose | Notes |
|---|---|---|
| `search_carrier_appetite` | Carrier appetite + contacts + class codes | Contacts fallback by `carrier_name` when `carrier_id` null |
| `classify_risk` | Keyword classification (GL/WC/NAICS/SIC/ops) | Tokenized — splits query words, skips filler |
| `run_commission_reconciliation` | Dry run + live discrepancy detection | `lob_matches()` + case-insensitive carrier |
| `create_commission_escalation` | Escalate a reconciliation record | Write target for Commission Agent |
| `get_open_cases` | Open CRM cases + nested tasks/events | |
| `get_client_profile` | Client + policies + open cases/tasks | PK: `nowcerts_insured_guid` |
| `get_medicare_plans` | Medicare plan lookup by county | |
| `match_similar` | Vector similarity (7 tables) | Includes `ai_knowledge_items` |
| `update_embedding` | SECURITY DEFINER vector write | Used by `batch-embed` |
| `lob_matches` | LOB alias helper | 21 rows in `lob_aliases` |

### Commission reconciliation (verified)

Dry run `run_commission_reconciliation(true, 1.00)` → **70 discrepancies**

| Priority | Count |
|---|---:|
| medium | 3 |
| low | 67 |
| high | 0 |

Fixes applied in order:
1. `lob_aliases` + `lob_matches()` — `"Auto"` ↔ `"Commercial Auto"`
2. `upper(trim(carrier_name))` — `"Progressive"` ↔ `"PROGRESSIVE"`

---

## Edge Functions

| Function | Version | JWT | Purpose |
|---|---:|---|---|
| `batch-embed` | 3 | required | Embeds null rows via OpenAI + `update_embedding` RPC |
| `semantic-search` | 2 | required | RAG — embeds query, calls `match_similar` per table |

**Default search order** (`semantic-search` v2):

```
ai_knowledge_items → gl_class_codes → wc_class_codes → naics_codes → sic_codes → operations_to_codes → knowledge_chunks
```

**`batch-embed` TABLE_CONFIG** (7 tables):

```
ai_knowledge_items, gl_class_codes, wc_class_codes, naics_codes, sic_codes, operations_to_codes, knowledge_chunks
```

Endpoint: `POST https://wibscqhkvpijzqbhjphg.supabase.co/functions/v1/semantic-search`

---

## Migrations applied (2026-08-14 session)

| Migration name | What it does |
|---|---|
| `create_update_embedding_rpc` | `update_embedding()` |
| `create_match_similar` | Vector search RPC |
| `create_search_carrier_appetite_rpc` | Appetite search |
| `fix_search_carrier_appetite_order_by` | PG GROUP BY fix |
| `fix_appetite_contacts_fallback` | Contacts by carrier_name |
| `create_classify_risk_rpc` | Classification |
| `fix_classify_risk_tokenization` | Word-split search |
| `create_commission_reconciliation_rpc` | Commission recon |
| `create_commission_escalation_rpc` | Escalations |
| `create_get_open_cases_rpc` | Open cases |
| `fix_get_open_cases_order_by` | PG GROUP BY fix |
| `create_get_client_profile_rpc` | Client profile |
| `create_get_medicare_plans_rpc` | Medicare plans |
| `create_lob_aliases_and_fix_recon` | LOB aliases |
| `fix_commission_carrier_match` | Case-insensitive carrier |
| `create_ai_knowledge_items` | Unified knowledge table + backfill |
| `add_aki_to_match_similar` | RAG includes AKI |

---

## PostgreSQL gotchas (learned this session)

1. **`ORDER BY` inside `jsonb_agg` without subquery** → error `42803: column must appear in GROUP BY`. Fix pattern:

```sql
SELECT jsonb_agg(row_to_json(t)) FROM (
  SELECT ... ORDER BY ... LIMIT n
) t;
```

Applied to: `search_carrier_appetite`, `get_open_cases`, contacts subquery.

2. **Espo field casing rules do NOT apply to Supabase.** Ignore Espo gotchas for this project.

3. **Commission join requires both LOB aliases AND case-insensitive carrier names.**

4. **`sic_codes` uses `sic_description`** (not `description`). **`knowledge_chunks` uses `content`** (not `chunk_text`).

5. **Non-standard PKs:** `canonical_clients.nowcerts_insured_guid`, `canonical_policies.policy_guid`, `carriers.id` (text slugs).

---

## Data gaps (data loading — not schema)

| Gap | Rows | Impact |
|---|---:|---|
| `agency_bill_*` tables | 0 | Agency Bill Agent blocked |
| `appetite_placement_outcomes` | 0 | No placement history |
| `commission_reconciliation` | 0 | Run live recon after human review |
| `commission_escalations` | 0 | Amy creates on escalate |
| `carrier_appetite_class_codes` | 9 | Most appetite rows unmapped |
| `agent_runs` / `agent_writes` | 0 | Wire when Amy goes live |

---

## Microsoft session — next steps

1. Store `service_role_key` in Azure Key Vault
2. Create Amy (orchestrator) in Copilot Studio
3. Create 5 sub-agents (Carrier Appetite, Classification, Commission, CRM/Service, Medicare)
4. Create **8 Power Automate flows** (one per RPC/Edge Function):

| Flow name | Endpoint |
|---|---|
| SearchCarrierAppetite | `/rest/v1/rpc/search_carrier_appetite` |
| ClassifyRisk | `/rest/v1/rpc/classify_risk` |
| SemanticSearch | `/functions/v1/semantic-search` |
| GetOpenCases | `/rest/v1/rpc/get_open_cases` |
| GetClientProfile | `/rest/v1/rpc/get_client_profile` |
| GetMedicarePlans | `/rest/v1/rpc/get_medicare_plans` |
| RunCommissionRecon | `/rest/v1/rpc/run_commission_reconciliation` |
| CreateEscalation | `/rest/v1/rpc/create_commission_escalation` |

5. Add SharePoint knowledge source to Amy
6. Configure governance (DLP, moderation, feedback, transcripts)
7. Connect Application Insights
8. Publish Amy to Microsoft 365 Copilot Chat
9. Test with first prompt

---

## Systems of record (do not confuse)

| System | Role | MCP |
|---|---|---|
| **Zoho CRM** | CRM of record | `user-ZohoMCP` |
| **NowCerts** | Policy truth | `nowcerts` |
| **Supabase** | Intelligence / analytics / RAG | `plugin-supabase-supabase` |
| EspoCRM | **Retired** | Do not use |

---

## Quick test queries

```sql
-- Commission recon (expect 70)
SELECT jsonb_array_length(run_commission_reconciliation(true, 1.00)->'discrepancies');

-- Classification (expect plumbing matches)
SELECT classify_risk('plumbing contractor');

-- AKI embeddings (expect 121/121)
SELECT count(*), count(*) FILTER (WHERE embedding IS NOT NULL) FROM ai_knowledge_items;

-- Total embeddings (expect 4436)
SELECT count(*) FROM gl_class_codes WHERE embedding IS NOT NULL
  + ... + ai_knowledge_items;
```

```bash
# Semantic search (expect ai_knowledge_items hits first)
curl -X POST 'https://wibscqhkvpijzqbhjphg.supabase.co/functions/v1/semantic-search' \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{"query":"Progressive commercial auto appetite Georgia","limit":3,"threshold":0.4}'
```
