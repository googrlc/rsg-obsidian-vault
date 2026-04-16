# RSG Automation Platform — Master Architecture
**Version:** 1.0 | **Created:** 2026-04-08 | **Owner:** Lamar Coates

---

## Vision
A fully automated intake-to-quote pipeline for both commercial and personal lines.
Client data goes in once. Every downstream agent reads from the same structured record.
No re-entry. No duplicate work. Gretchen runs intake. Lamar sells.

---

## Platform Stages

### Stage 1 — Input Layer
Accept any combination of:
- Chat transcripts / voice-to-text notes
- Carrier declaration pages (PDF)
- Handwritten or typed notes
- Driver info (DL numbers, DOB, MVR)
- Vehicle info (year, make, model, VIN)
- Property addresses

### Stage 2 — Intake & Enrichment Agent
**Built on:** RSG Commercial Assessment (extend, do not rebuild)
**Branches:** Commercial Lines + Personal Lines

Commercial enrichment:
- Extract business info, owner, fleet, employees, revenue, limits
- NAICS + SIC code classification
- Web scrape: business website, live links returned in output
- LinkedIn / D&B enrichment
- Coverage gap identification

Personal lines enrichment (NEW):
- Extract named insured, vehicles, property address
- VIN lookup → vehicle details (year, make, model, trim, specs)
- Auto market value → KBB/Edmunds current retail (Georgia)
- Flag underinsured OR premium waste (vehicle under $6k with full comp/coll)
- Property address → county → GA rebuild cost per sq ft
- Pull sq ft from public property records if not on dec page
- Flag dwelling underinsured if rebuild est. exceeds Coverage A by >15%

### Stage 3 — Data Write Layer
Write structured client record to all three systems:
- EspoCRM: Account + Opportunity + Policy records
- NowCerts/Momentum: Insured record + coverages + vehicles
- Supabase: Structured client JSON (read by all downstream agents)


### Stage 4 — Client Risk Report (HTML)
**Reads from:** Supabase structured client record (Stage 3 output)
**Output:** Hosted HTML page — link texted or emailed to client

Report sections (always in this order):
1. Portfolio snapshot — total spend, # policies, # carriers
2. What your coverage does — plain English, one card per policy
3. What we found — positives first, then gaps by severity
4. How RSG fixes it — action plan written as "we will"
5. CTA — schedule call with Lamar

Post-close variant: regenerate with before/after comparison.
This is the retention tool — client sees their risk score improve.

### Stage 5 — Appetite Check (separate flow — next sprint)
**Status:** Commercial auto exists (Geico dataset). All others to be added.
**Process:**
- Upload carrier UW guidelines as PDFs to Dify dataset
- Chunk and index via Dify UI
- Agent queries dataset before any quote handoff
- Returns GO / CAUTION / NO-GO per LOB per carrier

LOBs to add (in priority order):
1. General Liability / BOP
2. Workers Comp
3. Personal Auto (Progressive, Safeco)
4. Homeowners (Safeco, others)

**This is a standalone ingestion workflow — not part of the main intake pipeline.**
Build as a separate n8n or Dify workflow that accepts a PDF and chunks it into the dataset.

### Stage 6 — Quote Agents (future sprint — browser automation)
**Requires:** Claude in Chrome or Playwright
**Commercial auto:** Geico, National General, Progressive portals
**GL/BOP:** Per appetite result
**Personal auto:** Progressive, Safeco portals
**Homeowners:** Safeco, others per appetite

DO NOT START until Stages 1–5 are stable.
Browser automation is a separate engineering sprint.

---

## This Sprint (Week of April 8)

| Task | Agent | Status |
|---|---|---|
| Extend Commercial Assessment — enhanced web enrichment | Commercial Assessment (Dify workflow) | Build |
| Add personal lines branch to intake | Commercial Assessment (Dify workflow) | Build |
| EspoCRM write — personal lines fields | Commercial Assessment (Dify workflow) | Build |
| Client Risk Report HTML agent | New Dify chatflow | Build |

## Next Sprint

| Task | Notes |
|---|---|
| Appetite guide ingestion workflow | Separate flow — upload PDF → chunk → Dify dataset |
| Add GL/BOP/WC carrier UW guides | Manual upload via Dify UI |
| Add personal lines carrier UW guides | Manual upload via Dify UI |

## Future Sprint

| Task | Notes |
|---|---|
| Commercial auto quote agent | Browser automation — Geico, Natl General, Progressive |
| Personal auto quote agent | Browser automation — Progressive, Safeco |
| GL quote agent | TBD per appetite results |


---

## Agent Inventory

| Agent | Platform | Status | Purpose |
|---|---|---|---|
| RSG Commercial Assessment | Dify (workflow) | Extend this sprint | Intake + enrichment + EspoCRM write |
| RSG Quote Pre-Screen | Dify (agent-chat) | Keep as-is | Geico commercial auto GO/CAUTION/NO-GO |
| RSG Client Risk Report | Dify (chatflow) | Build this sprint | Client-facing HTML risk profile |
| Appetite Guide Ingestor | n8n or Dify | Next sprint | Chunk UW PDFs into Dify dataset |
| Commercial Auto Quote Agent | TBD (browser automation) | Future | Enter quote data into carrier portals |
| Personal Lines Quote Agent | TBD (browser automation) | Future | Enter quote data into Progressive/Safeco |

---

## Data Flow Summary

```
INPUT (transcripts, dec pages, notes, VINs, DL numbers)
  ↓
COMMERCIAL ASSESSMENT AGENT (extended)
  — extract + classify + web enrich + personal lines branch
  ↓
WRITE TO: EspoCRM + NowCerts + Supabase (structured JSON)
  ↓
CLIENT RISK REPORT AGENT
  — reads Supabase record
  — produces HTML report → hosted link → sent to client
  ↓
[NEXT SPRINT] APPETITE CHECK
  — LOB routing → carrier UW dataset query → GO/CAUTION/NO-GO
  ↓
[FUTURE] QUOTE AGENTS
  — browser automation → carrier portals → quote returned
```

---

## Key Decisions Locked

- Commercial Assessment extended, not rebuilt
- Quote Pre-Screen kept as-is — personal lines UW docs added to existing dataset
- Risk Report is a separate agent reading from Supabase — not re-extracting from PDFs
- Appetite guides are a separate ingestion workflow — not blocking current sprint
- Quote agents (browser automation) are a future sprint — not in scope now
- Georgia only for rebuild cost estimates until further notice
- Auto market value flags both directions: underinsured AND premium waste

---

*Master architecture doc — update this before starting any new build sprint.*
*Last updated: 2026-04-08*

## Sprint Status Update — 2026-04-08

### This Sprint — COMPLETED ✅
| Task | Status | Notes |
|---|---|---|
| Extend Commercial Assessment — personal lines branch | ✅ Done | 17 nodes, 19 edges |
| VIN + auto market value web lookup | ✅ Done | Bing search → LLM flags |
| Property records + GA rebuild cost | ✅ Done | Bing search → LLM flags |
| Enhanced web enrichment with live URLs | ✅ Done | Parse Web Research Results node |
| EspoCRM write | ✅ Done | Account + Opportunity nodes intact |
| Supabase client_assessments table | ✅ Done | Project wibscqhkvpijzqbhjphg |
| Supabase write node | ✅ Done | Full JSON posted post-report |
| Client Risk Report spec | ✅ Done | Vault: RSG/Workflows/RSG_Client_Risk_Report_SPEC.md |
| Appetite Guide Ingestor spec | ✅ Done | Vault: RSG/Workflows/RSG_Appetite_Guide_Ingestor_SPEC.md |

### One Manual Step Remaining
⚠️ Add SUPABASE_SERVICE_KEY to Dify app 81bfd19b environment variables

### Next Sprint — Week of April 14
| Task | Owner | Notes |
|---|---|---|
| Build RSG Client Risk Report in Dify | Claude Code | Spec ready in vault |
| Test Intake agent with real client data | Gretchen | Use Centeno dec pages as first test |
| Build Appetite Guide Ingestor workflow | Claude Code | Spec ready in vault |
| Upload personal lines UW guides to dataset | Lamar | Progressive, Safeco first |
| Upload GL/BOP/WC carrier guides | Lamar | Liberty Mutual first |

