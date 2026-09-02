# SharePoint Knowledge Consolidation — Agent Brief

**Owner:** Lamar Coates — Risk Solutions Group  
**Created:** 2026-08-16  
**Status:** Active  
**Purpose:** Audit every SharePoint site, migrate valuable content to the canonical RSG Knowledge Site, and produce a deletion report.

> Do NOT delete anything. Produce reports and a migration plan only. Lamar approves deletions manually.

---

## Credentials & Access

Use injected environment secrets:

- `MS365_TENANT_ID`
- `MS365_CLIENT_ID`
- `MS365_CLIENT_SECRET`
- `SHAREPOINT_SITE_URL` (root: `${SHAREPOINT_SITE_URL}`)

Authenticate via Microsoft Graph client credentials:

```
POST https://login.microsoftonline.com/{MS365_TENANT_ID}/oauth2/v2.0/token
scope: https://graph.microsoft.com/.default
```

List all sites:

```
GET https://graph.microsoft.com/v1.0/sites?search=*&$select=id,displayName,name,webUrl,description,createdDateTime,lastModifiedDateTime&$top=999
```

---

## Canonical Target: RSG Knowledge Site

**Site:** RSG  
**URL:** `${SHAREPOINT_SITE_URL}sites/RSG`  
**Purpose:** Single source of truth for agency knowledge consumed by Amy (Copilot Studio) and Supabase RAG.

### Target folder structure

```
/sites/RSG/Documents/
├── 01-Carriers/
│   ├── Appetites/
│   ├── Commissions/
│   └── Contacts/
├── 02-Lines-of-Business/
│   ├── Commercial-Auto/
│   ├── General-Liability/
│   ├── Workers-Comp/
│   ├── Property/
│   ├── BOP/
│   └── Medicare/
├── 03-Operations/
│   ├── SOPs/
│   ├── Workflows/
│   └── Roles/
├── 04-Client-Service/
│   ├── Intake-Templates/
│   ├── Call-Scripts/
│   └── FAQ/
├── 05-Marketing/
│   ├── Brand-Guide/
│   ├── Presentations/
│   └── Press-Kit/
├── 06-Training/
│   ├── Onboarding/
│   └── Insurance-Education/
├── 07-Compliance/
│   ├── Licenses/
│   └── Policies-Coverages/
├── 08-CRM-and-Systems/
│   ├── CRM-Setup/
│   └── Codes-and-Prompts/
└── 09-Archive/
    └── Migrated-from/
```

### Domain mapping for Supabase ingestion

| SharePoint folder | domain | doc_type |
|---|---|---|
| 01-Carriers/Appetites | carrier | appetite |
| 01-Carriers/Commissions | carrier | commission |
| 01-Carriers/Contacts | carrier | carrier_detail |
| 02-Lines-of-Business/* | lob | lob_reference |
| 03-Operations/SOPs | agency | sop |
| 03-Operations/Workflows | agency | workflow |
| 04-Client-Service/* | agency | client_service |
| 05-Marketing/* | agency | marketing |
| 06-Training/* | lob | education |
| 07-Compliance/* | agency | compliance |
| 08-CRM-and-Systems/* | agency | system |

---

## Known Site Inventory (42 sites — verify and expand)

### Keep & migrate content from

| Site | URL path | Action |
|------|----------|--------|
| Risk Solutions Group Intranet | `/` (root) | Audit libraries. Migrate useful docs to RSG. Keep root as portal shell. |
| Operations and Roles | `/sites/homepage` | Migrate SOPs, roles, workflows → `03-Operations/` |
| Policies & Coverages | `/sites/coverages` | Migrate → `07-Compliance/Policies-Coverages/` |
| Brand Guide | `/sites/BrandGuide` | Migrate → `05-Marketing/Brand-Guide/` |
| Agencyfinance | `/sites/agencyfinance` | Audit. Migrate finance SOPs if any. |
| RSG | `/sites/RSG` | **Canonical target.** Reorganize into structure above. |

### System sites — do not delete

| Site | Reason |
|------|--------|
| Apps (`/sites/appcatalog`) | SharePoint app catalog |
| Team Site (`/sites/contentTypeHub`) | Content type hub |
| PointPublishing Hub | System portal |
| Community | System portal |

### Loop / content storage — migrate then delete

| Workspace | Likely destination | Priority |
|-----------|-------------------|----------|
| Carriers | `01-Carriers/` | P0 |
| Agency Licenses and Insurance | `07-Compliance/Licenses/` | P0 |
| Codes And Prompts | `08-CRM-and-Systems/Codes-and-Prompts/` | P1 |
| CRM Setup | `08-CRM-and-Systems/CRM-Setup/` | P1 |
| When a client calls in | `04-Client-Service/Call-Scripts/` | P0 |
| UW questions | `01-Carriers/Appetites/` or `02-Lines-of-Business/` | P0 |
| Workflows | `03-Operations/Workflows/` | P0 |
| Current Operations Manager Tasks | `03-Operations/` | P1 |
| Roles and responsibilites | `03-Operations/Roles/` | P0 |
| Kim Onboarding Guide | `06-Training/Onboarding/` | P0 |
| Medicare Rollout | `02-Lines-of-Business/Medicare/` | P1 |
| Ideas (×5) | Delete unless active project | P3 |
| Getting Started (×3) | Delete — template defaults | P3 |
| Designer (×2) | Delete — Copilot artifacts | P3 |
| My workspace (×2) | Delete — personal workspaces | P3 |

---

## Phase 1: Deep Dive Audit

For every site, record:

1. Site name and URL
2. Site type (SharePoint site / Loop workspace / Portal / System)
3. Created date and last modified date
4. Total document libraries and file count
5. Total size (bytes)
6. Last activity (most recent file modified date)
7. Content summary
8. Duplicate check
9. Recommendation: KEEP | MIGRATE | ARCHIVE | DELETE
10. Migration target (if MIGRATE)
11. Risk level: LOW / MEDIUM / HIGH

### Graph API calls

```
GET /sites/{site-id}/drives
GET /drives/{drive-id}/root/children
GET /sites/{site-id}/lists
```

---

## Phase 2: Migration Plan

For each site marked MIGRATE:

1. List every file: name, path, size, modified date, file type
2. Map each file to target RSG folder
3. Flag duplicates
4. Flag stale content (not modified in 18+ months)
5. Flag sensitive content (PII, policy numbers, financials) → `09-Archive/` with restricted permissions

### Migration rules

- Rename on conflict: `{source-site}_{original-filename}`
- Preserve metadata in `_migration-manifest.json` at each target folder
- Do not migrate empty folders, default Loop templates, personal workspaces
- Convert Loop pages to PDF or DOCX before migrating
- **Do not execute migration** — plan and manifest only

---

## Phase 3: Deletion Report

### Tier 1 — Safe to delete (after migration confirmed)

- Ideas (×5)
- Getting Started (×3)
- Designer (×2)
- My workspace (×2)

### Tier 2 — Delete after content migrated

- All Loop workspaces with content migrated to RSG
- FAQ subsites (after merge into `04-Client-Service/FAQ/`)
- Stale meeting notes (>12 months old)

### Tier 3 — Evaluate with Lamar

- Agencyfinance
- Intranet Notes
- Root intranet libraries (Talk Tracks, WidgetBoard_Assets)

### Never delete

- `/sites/RSG`
- `/sites/appcatalog`
- `/sites/contentTypeHub`
- Portal sites on lamarcoates1.sharepoint.com

---

## Phase 4: AI Knowledge Base Direction

### A. Copilot Studio (Amy) — SharePoint knowledge source

Point Amy's SharePoint grounding at:

```
${SHAREPOINT_SITE_URL}sites/RSG/Documents/
```

Include: 01-Carriers, 02-Lines-of-Business, 03-Operations, 04-Client-Service, 06-Training, 07-Compliance  
Exclude: 08-CRM-and-Systems, 09-Archive

### B. Supabase RAG — knowledge_chunks

Project: `wibscqhkvpijzqbhjphg` (rsg-infrastructure)

| Priority | Source folder | Target table | Agent |
|----------|--------------|--------------|-------|
| P0 | 01-Carriers/Appetites | carrier_appetite + knowledge_chunks | Carrier Appetite Agent |
| P0 | 01-Carriers/Commissions | commission_rules + knowledge_chunks | Commission Agent |
| P0 | 03-Operations/SOPs | knowledge_chunks (domain=agency) | Amy |
| P1 | 02-Lines-of-Business | knowledge_chunks (domain=lob) | Classification Agent |
| P1 | 04-Client-Service | knowledge_chunks (domain=agency) | Amy |
| P1 | 06-Training | knowledge_chunks (domain=lob) | All agents |
| P2 | 05-Marketing | knowledge_chunks (domain=agency) | Amy |
| P2 | 07-Compliance | knowledge_chunks (domain=agency) | Amy |
| SKIP | 08-CRM-and-Systems | Do not ingest | Internal reference |
| SKIP | 09-Archive | Do not ingest | Historical only |

Chunking rules: 400–600 words, split at H2/H3, prefix `[FILE: name] [SECTION: header]`, embed via batch-embed Edge Function.

### C. Validation test queries

1. "What carriers write plumbing contractors in Georgia?"
2. "What's our commission rate with [carrier] on commercial auto?"
3. "Walk me through the call intake process."
4. "What coverage does a restaurant need?"
5. "When a client calls in, what do I do?"
6. "What's our brand color and logo usage?"

---

## Deliverables

| File | Description |
|------|-------------|
| `RSG/Reports/sharepoint-audit-report.md` | Full site inventory with audit columns |
| `RSG/Reports/migration-manifest.csv` | Every file mapped to RSG target folder |
| `RSG/Reports/deletion-recommendations.md` | Tiered deletion list with rationale |
| `RSG/Reports/rsg-knowledge-site-blueprint.md` | Folder structure, Amy config, ingestion order |

---

## Constraints

- Read-only audit. Do NOT delete, move, or modify files.
- Do NOT publish or reconfigure Copilot Studio.
- Flag client PII or policy documents outside expected locations.
- Cross-reference Supabase: 34 knowledge_chunks, 74 carrier_appetite rows, 121 ai_knowledge_items.

## Success criteria

Lamar can:

1. See exactly what's in every SharePoint site
2. Approve a migration plan with zero guesswork
3. Approve a deletion list with confidence tiers
4. Hand the blueprint to the next agent to execute migration + Supabase ingestion
