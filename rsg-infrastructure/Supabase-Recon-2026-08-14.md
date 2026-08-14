---
title: Supabase Recon — rsg-infrastructure (2026-08-14)
updated: 2026-08-14
tags: [rsg, supabase, recon, amy, pgvector]
superseded_by: Supabase-Readiness-Final-2026-08-14
---

# Supabase Recon — rsg-infrastructure

> **Superseded for ops handoff.** Build completed same day. Use [[rsg-infrastructure/Supabase-Readiness-Final-2026-08-14]] for live endpoints, migration list, and Microsoft session checklist. This doc remains the pre-build baseline recon.

**Date:** 2026-08-14
**Project:** `rsg-infrastructure` (`wibscqhkvpijzqbhjphg`)
**Region:** us-east-1 · Postgres 17.6 · status ACTIVE_HEALTHY
**Inactive sibling:** `open-brain` (`ftpfeaizbxfjgvagewrd`) — not used for Amy

Recon for the locked architecture: [[03-Systems/Architecture/Amy-Copilot-Chat-Architecture]]

## Headline

The **schema is ready**. The **data is not**.

CRM of record is **Zoho CRM** (confirmed live 2026-08-14 via `user-ZohoMCP`: Accounts, Contacts, Leads, Deals, Tasks, Cases, plus custom `Policies`, `Renewals`, `Renewal_Events`, `AMS_Write_Queue`). EspoCRM is retired. Supabase still holds analytics, class codes, appetite, commission, and agency-bill tables.

- 206 public tables, ~38,684 rows
- `vector` 0.8.0 installed; `vector(1536)` columns + HNSW indexes exist
- **0 of 4,315 classification embeddings are filled.** Semantic search will fail until embeddings are generated.
- Agency bill tables exist and are **empty**. Amy cannot answer agency-bill exposure until invoices are loaded.
- Classification + Medicare reference data is the strongest part of the book.

## Agent readiness

| Agent | Primary tables | Rows (live) | Verdict |
|---|---|---|---|
| Classification | `gl_class_codes`, `wc_class_codes`, `naics_codes`, `sic_codes`, `operations_to_codes` | 1,154 / 499 / 2,126 / 445 / 57 | **Schema + rows ready. Embeddings empty.** Keyword lookup works; RAG does not. |
| Carrier Appetite | `carrier_appetite`, `carrier_appetite_class_codes`, `appetite_docs`, `appetite_placement_outcomes`, `knowledge_chunks` | 74 / 9 / 2 / 0 / 34 | **Thin.** 74 active appetite rows (24 preferred, 26 standard, 8 non-standard, 16 unlabeled). No placement history. Chunks not embedded. |
| Agency Bill | `agency_bill_invoices`, `agency_bill_receipts`, `agency_bill_remittances`, `agency_bill_exceptions` | 0 / 0 / 0 / 0 | **Blocked.** Schema matches the daily-function fields. No data. |
| Commission | `commission_rules`, `commission_ledger`, `commission_transactions`, `commission_reconciliation`, `commission_escalations`, `commission_statements` | 216 / 123 / 208 / 0 / 0 / 2 | **Partial.** Rules + ledger exist. Reconciliation and escalations are empty. |
| CRM / Service (Amy via Zoho) | Zoho: Accounts, Contacts, Deals, Tasks, Cases, Policies, Renewals. Supabase mirror: `agency_crm_tasks`, `canonical_clients`, `canonical_policies` | Zoho live / Supabase 18 / 364 / 456 | **Usable.** Live CRM is Zoho. Supabase book mirror is populated. |
| Medicare | `medicare_master_plan_index`, `medicare_county_footprints`, `medicare_medical_rx_matrix`, `medicare_supplemental_benefits` | 128 / 357 / 95 / 94 | **Ready for lookup.** `medicare_plans` has 1 row — prefer the master index. |

## pgvector

Installed: `vector` 0.8.0 on `public`.

| Table | Rows | Embeddings filled | Index present |
|---|---|---|---|
| `gl_class_codes` | 1,154 | **0** | `gl_embedding_idx` |
| `wc_class_codes` | 499 | **0** | `wc_embedding_idx` |
| `naics_codes` | 2,126 | **0** | `naics_embedding_idx` |
| `sic_codes` | 445 | **0** | `sic_embedding_idx` |
| `operations_to_codes` | 57 | **0** | `operations_embedding_idx` |
| `code_bundles` | 0 | 0 | `bundle_embedding_idx` |
| `knowledge_chunks` | 34 | **0** | `knowledge_chunks_embedding_idx`, HNSW |

`knowledge_chunks` breakdown: 31 carrier/appetite, 3 carrier/commission. None embedded.

Dimension is **1536** (OpenAI `text-embedding-3-small` / `ada-002` compatible).

## Other notable counts

| Table | Rows | Note |
|---|---|---|
| `carriers` | 159 | Carrier directory |
| `carrier_contacts` | 141 | |
| `renewal_candidates` | 532 | Renewal pool exists |
| `sync_conflicts` | 4,908 | Dirty sync — verify before mutating |
| `inbound_sync_staging` | 4,308 | Staging backlog |
| `agent_runs` / `agent_writes` | 0 / 0 | Observability tables exist, unused |
| Empty non-backup tables | 80 | Includes all agency-bill + placement outcomes |

## RLS advisory

RLS is disabled on 4 tables (3 backup fossils + `nowcerts_picklist_options`). Backup tables should stay locked down. Do not enable RLS blindly without policies — that would block access.

```sql
-- Present only; do not apply until policies are defined
ALTER TABLE public.backup_20260726_cases_prewipe ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.backup_20260726_tasks_prewipe ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.backup_20260727_intake_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nowcerts_picklist_options ENABLE ROW LEVEL SECURITY;
```

## Build order implied by this recon

1. **Generate embeddings** for GL / WC / NAICS / SIC / operations + `knowledge_chunks` (P0 — Classification + Appetite RAG).
2. **Load agency bill** invoices / remittances / exceptions (P0 — Agency Bill Agent is otherwise theater).
3. **Expand appetite** beyond 74 rows; start capturing `appetite_placement_outcomes` (P1).
4. **Wire commission reconciliation + escalations** so the Commission Agent has a write target with live discrepancies (P1).
5. **Ingest more knowledge chunks** from SharePoint/Nextcloud appetite PDFs and embed them (P1).
6. **Start writing `agent_runs` / `agent_writes`** when Amy goes live (P2 — governance).

## Not in this recon

- Copilot Studio agent configs (not in Supabase)
- SharePoint document inventory
- NowCerts / Zoho CRM live reads (separate MCP: `nowcerts`, `user-ZohoMCP`)
- EspoCRM is retired; do not recon it as a live system
