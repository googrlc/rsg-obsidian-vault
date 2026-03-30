---
name: obsidian-knowledge-ingestor
description: >
  Chunks and inserts Obsidian vault markdown files into the RSG Supabase knowledge_chunks table for AI retrieval. Use this skill when Lamar says "ingest", "chunk and insert", "sync to Supabase", "update the knowledge base", or references a specific Obsidian folder like Carriers, Appetites, Commissions, or AI_Knowledge. Handles commission schedules, carrier appetite notes, carrier details, and any other markdown knowledge files. Automatically maps folder paths to the correct domain and doc_type tags.
---

# Obsidian Knowledge Ingestor

Reads markdown files from a specified Obsidian folder, chunks them intelligently, and upserts them into `knowledge_chunks` in Supabase (`rsg-infrastructure`).

---

## Vault Root

```
/Users/lamarcoates/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault
```

## Target Folders & Domain Mapping

| Obsidian Folder | domain | doc_type | Notes |
|---|---|---|---|
| `Carriers/Appetites/` | `carrier` | `appetite` | Carrier appetite notes per carrier |
| `Carriers/Commisions/` | `carrier` | `commission` | Commission schedules (PDF text extracted first) |
| `Carriers/` (root .md files) | `carrier` | `carrier_detail` | General carrier reference notes |
| `AI_Knowledge/Skills/` | `agency` | `skill` | Agent skill files |
| `AI_Knowledge/Lines of Business/` | `lob` | `lob_reference` | LOB education/reference |
| `AI_Knowledge/Insurance Education/` | `lob` | `education` | Insurance education content |
| `RSG/SOPs/` | `agency` | `sop` | Standard operating procedures |
| `Ministry/` | `ministry` | `ministry` | Ministry content |
| `Personal/` | `personal` | `personal` | Personal notes/goals |

---

## Step-by-Step Process

### Step 1 — Identify files to ingest

Use Desktop Commander list_directory on the target folder. Collect all `.md` files. Skip: `.DS_Store`, `README.md`, image files, `.json`, `.sh`, `.skill`.

For PDFs in `Carriers/Commisions/` — use Desktop Commander read_file to extract text content first.

### Step 2 — Read each file

Use Desktop Commander read_file on each `.md` file path (absolute path).

### Step 3 — Chunk the content

Split each file into chunks of **400–600 words** max. Rules:

- Prefer splitting at `##` or `###` headers — each section becomes its own chunk
- If a section exceeds 600 words, split at paragraph breaks
- Always include the file title and section header at the top of each chunk for context
- Minimum chunk size: 50 words (skip smaller chunks)

**Chunk format:**
```
[FILE: {filename}] [SECTION: {header or "Main"}]

{content}
```

### Step 4 — Build metadata

For each chunk:
- `source_url` = relative vault path (e.g. `Carriers/Appetites/CNA.md`)
- `source_title` = filename without extension (e.g. `CNA`)
- `domain` = from folder mapping table above
- `doc_type` = from folder mapping table above
- `tags` = extract from filename + content: carrier name, LOB keywords, state if mentioned

### Step 5 — Upsert to Supabase

Use Supabase execute_sql to insert chunks. Use ON CONFLICT DO UPDATE on `(source_url, source_title, content)` hash to avoid duplicates.

**Batch insert SQL pattern (insert up to 10 chunks per call):**

```sql
INSERT INTO knowledge_chunks (content, source_url, source_title, domain, doc_type, tags, created_at, updated_at)
VALUES
  ('chunk text here', 'Carriers/Appetites/CNA.md', 'CNA', 'carrier', 'appetite', ARRAY['CNA','Workers Comp','General Liability'], now(), now()),
  ('next chunk...', ...)
ON CONFLICT (source_url, source_title)
DO UPDATE SET
  content = EXCLUDED.content,
  tags = EXCLUDED.tags,
  updated_at = now();
```

> Note: If ON CONFLICT clause fails due to missing unique constraint, use plain INSERT and skip duplicates with a WHERE NOT EXISTS check.

### Step 6 — Report results

After ingestion, report:
```
✅ Obsidian Ingest Complete
Folder: {folder}
Files processed: {N}
Chunks inserted: {N}
Chunks skipped (too small): {N}
Errors: {list any files that failed}
```

---

## Priority Folders for RSG Revenue Impact

Run these first — they directly feed agent intelligence:

1. `Carriers/Appetites/` — feeds Prospect Researcher + Renewal agents
2. `Carriers/Commisions/` — feeds Commission Reconciliation agent
3. `AI_Knowledge/Skills/` — feeds all OpenClaw agents
4. `AI_Knowledge/Lines of Business/` — feeds underwriting + quoting context

---

## Common Trigger Phrases

| What Lamar says | What to do |
|---|---|
| "ingest the carriers folder" | Process `Carriers/` recursively |
| "sync appetites to Supabase" | Process `Carriers/Appetites/` only |
| "update commission knowledge" | Process `Carriers/Commisions/` only |
| "ingest everything" | Process all mapped folders in priority order |
| "re-sync [filename]" | Re-process that single file, overwrite existing chunks |

---

## Error Handling

- File not found → log and skip, continue with remaining files
- File too large (>10,000 words) → chunk aggressively at every `##` header, max 20 chunks per file
- PDF extraction fails → note in report, flag for manual review
- Supabase insert fails → log the chunk content and error, continue with next chunk
- Empty file → skip silently

---

## Dependency

Requires `SUPABASE_SERVICE_KEY` in agent environment. Uses project `wibscqhkvpijzqbhjphg`.
Full table schema in `supabase-data-layer` skill.
