---
name: call-intake-parser
description: >
  RSG's commercial client intake parser. Triggers when Lamar or Gretchen says
  anything like: "parse this intake call", "run intake for [client]", "process
  this transcript", "intake [client name]", "I just got off a call with [client]",
  "log this call for [client]", "run the intake parser", "parse this call for me",
  or pastes a block of call notes/transcript text.

  On trigger: extracts all commercial intake fields from the transcript, writes
  a lean Account + Opportunity stub to EspoCRM, generates a PDF + Excel intake
  report saved to ~/Documents/rsg-intake-parser/output/, and fires a Slack
  summary to #lamar-alerts.

  Gretchen trigger phrases: "I finished a call with [client]", "here are my
  notes from [client]", "can you log this call", "intake notes for [client]".

  ALWAYS ask for client name and call date if not provided. NEVER skip the
  transcript — paste it in or provide a file path.

  Dependencies: Python service at ~/Documents/rsg-intake-parser/, EspoCRM API,
  Anthropic API, Slack. Uses Anthropic (revenue-critical).
---

# Call Intake Parser — OpenClaw Skill

## What This Does
Takes a raw call transcript or intake notes → parses into structured data →
writes lean CRM stub → generates PDF + Excel intake report → Slack alert.

Detail lives in the reports. CRM gets name, stage, opportunity, one task.

---

## Trigger Detection

Fire this skill when the user says ANY of:
- "parse this intake call / transcript / notes"
- "run intake for [name]"  
- "I just got off a call with [name]"
- "log this call / these notes"
- "intake [client name]"
- "process this call"
- Pastes a block of text that looks like call notes or a transcript

---

## Step 1 — Collect Required Info

Before running, confirm you have:

| Field | How to get it |
|---|---|
| `client_name` | Ask if not in message |
| `call_date` | Ask if not in message — default today |
| `call_type` | Infer or ask: `new_prospect` / `existing_client` / `renewal_review` |
| `transcript` | Must be pasted in chat OR a file path provided |

If transcript is missing, say:
> "Paste your call notes or transcript here and I'll run the intake."

If client name is missing, say:
> "What's the client's business name?"

---

## Step 2 — Run the Parser

Once you have all inputs, run the command below.

### If transcript is pasted in chat:
Save it to a temp file first, then run:

```bash
# Save transcript to temp file
TRANSCRIPT_FILE="/tmp/intake_$(date +%Y%m%d_%H%M%S).txt"
cat > "$TRANSCRIPT_FILE" << 'TRANSCRIPT_EOF'
[PASTE TRANSCRIPT HERE]
TRANSCRIPT_EOF

# Run intake parser
cd ~/Documents/rsg-intake-parser && \
python3 main.py \
  --transcript "$TRANSCRIPT_FILE" \
  --client "[CLIENT_NAME]" \
  --date "[YYYY-MM-DD]" \
  --type [new_prospect|existing_client|renewal_review]
```

### If transcript is a file path:
```bash
cd ~/Documents/rsg-intake-parser && \
python3 main.py \
  --transcript "[FILE_PATH]" \
  --client "[CLIENT_NAME]" \
  --date "[YYYY-MM-DD]" \
  --type [new_prospect|existing_client|renewal_review]
```

### Dry-run (parse + PDF only, skip CRM + Slack):
```bash
cd ~/Documents/rsg-intake-parser && \
python3 main.py \
  --transcript "[FILE_PATH]" \
  --client "[CLIENT_NAME]" \
  --date "[YYYY-MM-DD]" \
  --type new_prospect \
  --dry-run
```

---

## Step 3 — Confirm Output to User

After the command runs successfully, report back:

```
✅ Intake complete for [CLIENT NAME]

📊 AI Confidence: [X]%
⚠️  Missing fields: [N] — listed in task + reports
💰 Cross-sell flags: [list or "none"]
📋 Submission ready: YES / NO

📄 PDF: ~/Documents/rsg-intake-parser/output/[filename].pdf
📊 Excel: ~/Documents/rsg-intake-parser/output/[filename].xlsx
🔗 CRM: https://{{ESPOCRM_HOST}}/#Account/view/[account_id]

Slack alert sent to #lamar-alerts.
```

If confidence < 50%, add:
> "⚠️ Low confidence — review the intake sheet before submitting to carriers."

If pending_claims is flagged, add:
> "🚨 Pending claims detected — disclose to all carriers before submission."

---

## Step 4 — Open Reports (optional)

If Lamar asks to open or review the reports:
```bash
open ~/Documents/rsg-intake-parser/output/[CLIENT]-Intake-[DATE].pdf
open ~/Documents/rsg-intake-parser/output/[CLIENT]-Intake-[DATE].xlsx
```

---

## Error Handling

| Error | Response |
|---|---|
| Missing client name | Ask for it before running |
| Missing transcript | Ask user to paste or provide file path |
| API key error | Check .env — may need key refresh from 1Password |
| CRM write fails | Reports still generate — note CRM as manual follow-up |
| Low confidence (<50%) | Run but flag loudly — do not auto-submit |

---

## Gretchen Usage (Plain English)

Gretchen doesn't need to know the command. She says:
> "I finished a call with ABC Landscaping. Here are my notes: [paste notes]"

OpenClaw responds:
> "Got it — running intake for ABC Landscaping. What's today's date and is this a new prospect or existing client?"

Then runs automatically once confirmed.

---

## Quick Reference — Call Types

| Situation | `--type` value |
|---|---|
| New prospect, first call | `new_prospect` |
| Existing client, renewal or service call | `existing_client` |
| Renewal review specifically | `renewal_review` |

---

## Output Files

All outputs saved to: `~/Documents/rsg-intake-parser/output/`

Naming: `[Client-Name]-Intake-[YYYY-MM-DD].pdf` and `.xlsx`

---

## LLM: Anthropic (revenue-critical)
## Slack: #lamar-alerts
## CRM: EspoCRM Account + Opportunity + 1 Task
