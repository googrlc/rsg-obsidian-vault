# RSG Document Inbox — How to Add Anything to the Knowledge Base
Last Updated: March 2026

---

## The Simple Rule

Drop it in the right folder. The pipeline handles the rest.

---

## WHERE TO DROP FILES BY TYPE

### Commission Guides / Carrier Schedules
Drop in: AI_Knowledge/Carriers/{carrier_name}/
Example: AI_Knowledge/Carriers/next_ins/guides/commission_guide_2026.pdf
Goes to: Supabase commission_rules table + knowledge_chunks (domain=carrier)

### Carrier Appetite Guides / Underwriting Guidelines  
Drop in: AI_Knowledge/Carriers/{carrier_name}/
Goes to: Supabase carrier_appetite table + knowledge_chunks (domain=carrier)

### Insurance Education / CE Material
Drop in: AI_Knowledge/Insurance Education/{topic}/
Goes to: Supabase knowledge_chunks (domain=lob)

### Declarations Pages / Policy Documents (client)
Drop in: AI_Knowledge/Document Inbox/
Goes to: Supabase commercial_documents + risk_assessments

### Internal SOPs / Procedures
Drop in: RSG/SOPs/
Goes to: Supabase knowledge_chunks (domain=agency)

### Sermon Notes / Ministry Content
Drop in: Ministry/Sermons/ or Ministry/Teaching/
Goes to: Supabase knowledge_chunks (domain=ministry)

---

## SUPABASE TABLE MAP

| Table | What Goes In | Who Writes It |
|---|---|---|
| knowledge_chunks | Chunked text from any document + vector embedding | n8n ingestion workflow |
| documents | Document metadata (title, type, source, domain) | n8n ingestion workflow |
| commercial_documents | Parsed client policy docs (dec pages, quotes) | n8n ingestion workflow |
| commission_rules | Parsed commission rates by carrier + LOB | n8n or manual |
| carrier_appetite | Carrier appetite by LOB + state | n8n or manual |
| email_templates | Email sequence templates | Manual via Supabase UI |

---

## HOW CHUNKING WORKS

1. File lands in the drop folder
2. n8n Document Inbox workflow picks it up (runs every hour — NOT YET BUILT, see below)
3. Text extracted (PDF → text, DOCX → text, MD → text)
4. Split into 500-token chunks with 50-token overlap
5. Each chunk embedded via Claude/OpenAI embedding API
6. Written to Supabase: documents table (metadata) + knowledge_chunks (chunks + vectors)
7. File moved to: AI_Knowledge/Document Inbox/processed/

Failed files move to: AI_Knowledge/Document Inbox/failed/

---

## MANUAL PROCESS (Until Ingestion Workflow is Built)

For commission guides specifically:

1. Open Supabase → Table Editor → commission_rules
2. Add row:
   - lob: (Commercial Auto, GL, WC, etc.)
   - carrier: carrier name
   - commission_rate: decimal (0.12 = 12%)
   - lamar_split: 1.0 (unless referral split applies)
   - notes: source document name
   - active: true

For carrier appetite:
1. Open Supabase → Table Editor → carrier_appetite
2. Add row with: carrier_name, lob, appetite_level, states_approved, exclusions

---

## INGESTION WORKFLOW — STATUS

Document Inbox n8n workflow: NOT YET BUILT
Priority: Medium — manual entry works for now
When built it will: watch the Document Inbox folder via Google Drive or local path,
parse each file type, chunk, embed, write to Supabase, move to processed/

---

## WHAT OPENCLAW CAN QUERY

Once chunks are in Supabase knowledge_chunks, OpenClaw agents can query via:
POST https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/rpc/match_knowledge_chunks
Body: { query_embedding: [...], match_threshold: 0.7, match_count: 5, domain: 'carrier' }

This powers:
- Deal Coach pre-call intel (carrier appetite lookups)
- Revenue Sheriff commission calculations  
- Data Entry Assistant policy entry guidance
