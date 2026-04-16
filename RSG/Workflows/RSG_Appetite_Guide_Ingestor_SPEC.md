# Agent C — RSG Appetite Guide Ingestor
# n8n Workflow Spec | Version 1.0 | 2026-04-08
#
# AGENT NAME: RSG Appetite Guide Ingestor
# DESCRIPTION: Lamar or Gretchen — use this to add a new carrier underwriting
#   guide to RSG's knowledge base. Upload the PDF and the agent chunks it,
#   labels it by carrier and LOB, and loads it into the Dify dataset so the
#   appetite check agents can find it automatically. Run this once per carrier
#   guide. Takes about 2 minutes.
#
# PLATFORM: n8n workflow (webhook trigger) OR Dify workflow
# RECOMMENDED: Dify workflow — simpler, no server needed

---

## PURPOSE

When a new carrier UW guideline PDF is available, this workflow:
1. Accepts the PDF upload
2. Extracts carrier name and LOB from the document
3. Chunks the document into searchable segments
4. Uploads chunks to Dify dataset with correct metadata tags
5. Confirms upload to Slack #systems-check

This is how RSG's appetite knowledge base grows over time.
Every guide uploaded makes the pre-screen and quote agents smarter.

---

## DIFY WORKFLOW NODES

### Node 1 — Start
Input fields:
- PDF upload (required) — the carrier UW guideline
- carrier_name (text, required) — e.g. "Geico", "Progressive", "Safeco"
- lob (dropdown, required):
    Commercial Auto | General Liability | BOP | Workers Comp |
    Personal Auto | Homeowners | Umbrella | Inland Marine
- state (text, default: GA) — state this guide applies to
- notes (text, optional) — anything Lamar wants to flag about this guide

### Node 2 — Extract & Validate
Prompt: claude-sonnet-4-20250514, temp 0.1
Task: Read the first 3 pages of the uploaded PDF.
Confirm:
- This appears to be a carrier underwriting guideline (yes/no)
- Detected carrier name (compare to input)
- Detected LOB (compare to input)
- Detected state(s) covered
- Any immediate hard knockout rules visible on page 1-3 (list them)
Output: validation JSON

### Node 3 — Chunk Document
Use Dify's built-in document chunking:
- Chunk size: 500 tokens
- Overlap: 50 tokens
- Metadata tags:
    carrier: {{carrier_name}}
    lob: {{lob}}
    state: {{state}}
    doc_type: uw_guideline
    uploaded_date: {{today}}
    uploaded_by: {{operator}}

### Node 4 — Upload to Dify Dataset
Target dataset: 450fb20c-4ce3-47c5-8b69-c09c0bfeaeac
(same dataset as existing Geico commercial auto guide)
Method: Dify Knowledge API
POST /v1/datasets/{dataset_id}/document/create_by_file

### Node 5 — Slack Confirmation
Post to #systems-check:
"✅ Appetite guide uploaded
Carrier: {{carrier_name}}
LOB: {{lob}}
State: {{state}}
Chunks: {{chunk_count}}
Knockout rules found: {{knockout_rules}}
Uploaded by: {{operator}}"

### Node 6 — End
Return confirmation message to operator.

---

## PRIORITY UPLOAD ORDER (next sprint)

| Priority | Carrier | LOB | Notes |
|---|---|---|---|
| 1 | Progressive | Personal Auto | Primary personal auto carrier |
| 2 | Safeco | Homeowners | Primary home carrier |
| 3 | Safeco | Personal Auto | Secondary personal auto |
| 4 | Liberty Mutual | General Liability | Primary commercial relationship |
| 5 | Liberty Mutual | BOP | Primary commercial relationship |
| 6 | Complex Risk | Commercial Auto | Specialty market primary |
| 7 | National General | Commercial Auto | Add to existing Geico dataset |

---

## DIFY DATASET REFERENCE

Dataset ID: 450fb20c-4ce3-47c5-8b69-c09c0bfeaeac
Current contents: Geico Commercial Auto UW Guidelines
After this sprint: all carriers above added

---

## HOW GRETCHEN USES THIS

1. Lamar gets a new carrier UW guide PDF
2. Gretchen opens the Appetite Guide Ingestor in Dify
3. Uploads the PDF, fills in carrier name, LOB, state
4. Hits run — done in 2 minutes
5. Slack confirms it uploaded
6. That carrier now shows up automatically in appetite checks

No technical knowledge required. One form. One click.

---
*Agent C spec — RSG Appetite Guide Ingestor*
*Build this sprint: No. Plan this sprint: Yes. Build next week: Yes.*
