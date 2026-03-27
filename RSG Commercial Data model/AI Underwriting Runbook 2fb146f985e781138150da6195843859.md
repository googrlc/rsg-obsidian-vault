# AI Underwriting Runbook

<aside>
📘 Operational runbook for the AI underwriting automation. Follow this exactly.

</aside>

---

# Workflow Overview

Document Upload → Trigger Check → AI Analysis → Notion Write-back → Human Review → Sales Pipeline

---

# Step 1: Trigger Conditions

The automation fires when ALL of these are true:

- A new document is linked to a Prospect (Documents & Transcripts → Prospect relation populated)
- The Prospect Status = "Intake" or "Analyzing"
- The document has parsed text (Parsed Text is not empty)

<aside>
🛑 If ANY condition fails, the automation does NOT run. No manual override.

</aside>

---

# Step 2: Build Input Payload

The automation (n8n, Make, or custom script) must:

1. Query the Prospect record from Notion API
2. Query all linked Documents & Transcripts for that Prospect
3. Build the JSON payload matching the Input Contract
4. Send to ChatGPT API (or Claude API) with the system prompt

Reference: See "AI Underwriting System Prompt" page for exact contracts.

---

# Step 3: Process AI Response

Parse the JSON response. If "error" key exists, log and stop.

## Write Risk Assessment

1. Create page in Risk Assessments database
2. Set Assessment Name = "[Prospect Name] - [Date]"
3. Link Prospect via relation
4. Set Assessment Date = today
5. Set Primary NAICS, Secondary NAICS, SIC from response
6. Link Operations Identified via relation (match by Operation Name)
7. Link GL Codes and WC Codes via relations
8. Set Coverage Requirements, Key Endorsements, Red Flags, Favorable Factors, Missing Items as multi-select values
9. Write underwriting_summary to "Underwriting Summary"
10. Write evidence_map as formatted JSON to "AI Evidence Map"
11. Set AI Confidence from response
12. Set Review Status = "Needs Review"

## Update Prospect

1. Set Status = "Analyzing"
2. Set Primary NAICS from response
3. Set Last AI Run = today
4. Set AI Confidence from response
5. Set Key Red Flags from response red_flags

## Create Sales Opportunity (conditional)

<aside>
⚠️ ONLY if sales_opportunity.create = true

</aside>

1. Create page in Sales Pipeline
2. Set Prospect (title) = prospect name
3. Link Prospect via "Prospect Link" relation
4. Link Risk Assessment via "Risk Assessment" relation
5. Set Stage = "🔬 Being Quoted"
6. Set Line of Business from response (map to Notion select values)

If sales_opportunity.create = false: Add reason to Prospect Notes. Do NOT create a deal.

---

# Step 4: Human Review Gate

<aside>
🛑 Sales CANNOT advance a deal past "🔬 Being Quoted" until:

</aside>

- Missing Items rollup is empty (all items resolved)
- Review Status on Risk Assessment = "Approved"
- "Ready to Quote?" formula shows true

The "Ready to Quote?" formula enforces this automatically. If it shows false, the deal is not ready.

---

# Step 5: Error Handling

- If AI returns {"error": ...}: Log to Prospect Notes, set Status = "Needs Review"
- If API call fails: Retry once after 30 seconds. If still failing, alert admin.
- If AI confidence < 50: Create the assessment but set Review Status = "Needs Follow-up"
- Never retry more than twice. Escalate to human.

---

# API Endpoints Reference

All Notion API calls use: https://api.notion.com/v1/

- Create page: POST /pages
- Update page: PATCH /pages/{page_id}
- Query database: POST /databases/{database_id}/query
- ChatGPT API: POST https://api.openai.com/v1/chat/completions
- Model: gpt-4o (or claude-opus-4-5-20251101 for Claude)