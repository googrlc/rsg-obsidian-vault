# RSG Knowledge Site Blueprint

**Generated:** 2026-08-16 22:50 UTC

## Canonical site

`${SHAREPOINT_SITE_URL}sites/RSG`

## Target folder structure

| Folder | Purpose | Supabase domain |
|--------|---------|---------------|
| 01-Carriers/Appetites | UW guidelines per carrier | carrier / appetite |
| 01-Carriers/Commissions | Rate sheets | carrier / commission |
| 01-Carriers/Contacts | UW contacts, portals | carrier / carrier_detail |
| 02-Lines-of-Business/* | LOB education | lob / lob_reference |
| 03-Operations/SOPs | Call intake, CRM, renewals | agency / sop |
| 03-Operations/Workflows | Process docs | agency / workflow |
| 03-Operations/Roles | Role definitions | agency / sop |
| 04-Client-Service/* | Talk tracks, call scripts, FAQ | agency / client_service |
| 05-Marketing/Brand-Guide | Brand assets | agency / marketing |
| 06-Training/Onboarding | New hire guides | lob / education |
| 07-Compliance/* | Licenses, coverages | agency / compliance |
| 08-CRM-and-Systems | AI configs (do NOT ingest) | — |
| 09-Archive | Migrated originals | — |

## Migration summary

- **37 sites** to migrate content from
- **311 files** cataloged in migration manifest
- **0 sites** safe to delete (Tier 1)
- **30 Loop workspaces** need manual export

## Existing RSG folders → new structure

| Current | New location |
|---------|-------------|
| Current projects | 03-Operations/ |
| Marketing assets | 05-Marketing/ |
| Newsletters | 05-Marketing/ |
| Onboarding | 06-Training/Onboarding/ |
| Presentations | 05-Marketing/Presentations/ |
| Press kit | 05-Marketing/Press-Kit/ |

## Amy (Copilot Studio) config

SharePoint knowledge source: `${SHAREPOINT_SITE_URL}sites/RSG/Documents/`

Include: 01–07. Exclude: 08, 09.

## Supabase ingestion order

1. P0: 01-Carriers/Appetites → carrier_appetite + knowledge_chunks
2. P0: 01-Carriers/Commissions → commission_rules + knowledge_chunks
3. P0: 03-Operations/SOPs → knowledge_chunks
4. P1: 02-Lines-of-Business, 04-Client-Service, 06-Training
5. P2: 05-Marketing, 07-Compliance

Chunk: 400–600 words, split at H2/H3, embed via batch-embed.

## Validation queries

- "What carriers write plumbing contractors in Georgia?"
- "What's our commission rate with [carrier] on commercial auto?"
- "Walk me through the call intake process."
- "When a client calls in, what do I do?"
- "What's our brand color and logo usage?"

## Execution order

1. Lamar approves audit + manifest
2. Create numbered folders on RSG site
3. Migrate SharePoint site files (automated via Graph API)
4. Manual Loop export for denied workspaces
5. Reorganize existing RSG folders
6. Point Amy grounding at RSG/Documents
7. Supabase ingestion P0
8. Delete Tier 1 → Tier 2
