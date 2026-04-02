# Call Intake Parser — SOP
**Last Updated:** 2026-04-01
**Owner:** Lamar Coates — Risk Solutions Group
**Purpose:** End-to-end workflow for recording a client intake call, parsing it with AI, writing results to EspoCRM, and generating a PDF intake report.

---

## Overview — What This Does

```
Phone Call Recording
        ↓
  Upload transcript (text or audio) to OpenClaw
        ↓
  call-intake-parser skill parses transcript via Claude API
        ↓
  Structured JSON output (all commercial intake fields)
        ↓
  n8n workflow writes Account + Opportunity to EspoCRM
        ↓
  PDF intake report generated and saved to SharePoint/client folder
        ↓
  Slack alert to #lamar-alerts with summary + missing fields
```

---

## Step 1 — Record the Call

**Options (Georgia is one-party consent state):**
- **Allô app** — auto-records VoIP calls, exports transcript
- **iPhone + Otter.ai** — record via Otter during call, export .txt transcript
- **Rev.ai or Whisper** — upload audio file post-call for transcription

**What to say at the start of the call:**
> "I'm going to be taking notes through our conversation today to make sure I capture everything accurately for your file."

---

## Step 2 — Submit Transcript to OpenClaw

Paste or upload the transcript text and trigger the `call-intake-parser` skill with:
> "Parse this intake call transcript for [Client Name] and write to CRM"

The skill will return a structured JSON object and confirm what was written to EspoCRM.

---

## Step 3 — Review Missing Fields

OpenClaw will output a **Missing Fields List** — everything required for submission that wasn't mentioned on the call. These become your follow-up task items in EspoCRM, auto-created by the skill.

---

## Step 4 — PDF Report

The skill auto-generates a PDF intake report saved to `/outputs/intake-reports/`. The PDF includes:
- Client summary card
- All confirmed fields by section
- Missing fields flagged in red
- Cross-sell opportunities flagged
- Submission readiness score
- Next action items

---

## Related Files

- [[Commercial-Client-Intake-Schema]] — master field reference
- OpenClaw skill: `call-intake-parser`
- n8n workflow: `Commercial Intake → EspoCRM` (see workflow registry)
