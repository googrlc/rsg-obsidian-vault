# RSG OpenWebUI Platform SOP
**Last updated:** 2026-06-21
**Platform URL:** https://openwebui-l8ola-u69864.vm.elestio.app

---

## What This Platform Does

OpenWebUI is your AI command center. It routes requests to the right model and tool automatically:

1. You ask a question
2. The **RSG Router** classifies it (CRM query, client email, coverage analysis, etc.)
3. It sends it to the best model for that task
4. CRM questions go straight to Hermes/EspoCRM — you get real data, not hallucinations
5. Everything gets logged (routing decisions, cost, latency)
6. CRM writes pass through n8n validation and post to #systems-check on Slack

**You don't need to pick the right assistant for every question. The router does it for you.**

---

## Part 1: Lamar's Daily Workflow

### Morning Start (2 minutes)

1. Open https://openwebui-l8ola-u69864.vm.elestio.app
2. Select **RSG Router** as your model (top of the model picker)
3. Ask: "What renewals do we have coming up in the next 30 days?"
4. Ask: "Show me the current pipeline summary"
5. Review both responses — these come live from EspoCRM

### Revenue-Generating Tasks

**Check your pipeline:**
- Ask: "What's in my pipeline?" or "Show me opportunities in Negotiation stage"
- The router dispatches to Hermes and returns real EspoCRM pipeline data

**Work a stalled quote:**
- Switch to **Quote Rescue** assistant (has n8n Bridge + Hermes CRM tools)
- Ask it to pull the quote status and suggest next steps
- It can trigger n8n workflows to re-engage the carrier

**Commercial risk analysis:**
- Ask the router: "Compare these two quotes for Acme Corp's commercial auto — what coverage gaps should I flag?"
- The router sends this to DeepSeek-R1 for deep reasoning
- This is the one path where the router may take 20-30 seconds — that's the reasoning model working

**Draft client communications:**
- Ask the router: "Draft an email to [client] about their renewal premium increase"
- The router sends this to Llama 3.3 70B for quality writing
- Or switch to **Client Message Writer** for more control over tone

### When to Use Specific Assistants Instead of the Router

| Task | Use This | Why |
|---|---|---|
| Anything CRM-related (renewals, pipeline, clients) | **RSG Router** | Auto-dispatches to Hermes |
| Stalled quote recovery | **Quote Rescue** | Has n8n Bridge tool for carrier re-engagement |
| Renewal workflow management | **Renewal Manager** | Has n8n Bridge + Hermes tools, renewal-specific skills |
| New business intake parsing | **Intake Builder** | Structured data extraction + CRM prep |
| Dashboard or data queries | **Dashboard Builder** | Has Supabase tool for SQL queries |
| Complex CRM write operations | **CRM Write Operator** | Restricted write path, validation-gated |
| General agency questions | **RSG Router** | Routes to best model automatically |

### Lamar's Golden Rules

1. **Start with the Router.** It handles 90% of what you need without switching assistants.
2. **CRM questions get real data.** The router dispatches renewal/pipeline/client queries to Hermes. You get EspoCRM data, not AI guesses.
3. **OpenAI is fallback only.** Routine work runs on open-source models (Qwen3, Llama 3.3 70B) at pennies per million tokens. You're not burning OpenAI credits on simple lookups.
4. **Everything is logged.** Every routing decision is stored with cost, latency, and model used. You can audit what happened anytime.
5. **CRM writes are validated.** Any write to EspoCRM goes through n8n validation (checks field values, confirmation) and posts an audit message to #systems-check.

---

## Part 2: Gretchen's Daily Workflow

### Morning Start (2 minutes)

1. Open https://openwebui-l8ola-u69864.vm.elestio.app
2. Select **Gretchen Daily Desk** as your model
3. Ask: "What renewals are coming up in the next 30 days for personal lines?"
4. Ask: "Show me any data quality issues in the CRM"
5. Review both — these come live from EspoCRM

### Daily Service Tasks

**Look up a client:**
- Ask: "Find account Acme Corp" or "What's the FEIN for [client]?"
- Hermes returns the real CRM record

**Process a COI (Certificate of Insurance):**
1. Switch to **COI Assistant**
2. Upload the COI image or PDF
3. Ask: "Extract the policy info from this COI and check for coverage gaps"
4. The COI Assistant uses a vision model (Qwen3 VL) to read the document

**Draft client messages:**
1. Switch to **Client Message Writer**
2. Ask: "Draft a text message to [client] reminding them to send their driver license photos"
3. Or: "Write an email to [client] about their auto policy renewal"
4. Review and copy the draft into your email/text

**Check renewal status:**
- Ask Gretchen Daily Desk: "What's the renewal status for [client]?"
- Or: "Show me all personal lines renewals in the next 30 days"
- Hermes returns real renewal data from EspoCRM

**Run a data quality audit:**
- Ask Gretchen Daily Desk: "Run a data quality audit"
- Hermes scans all CRM modules for missing required fields
- Fix any issues directly in EspoCRM

### Gretchen's Assistant Quick Reference

| Task | Assistant | How to Find It |
|---|---|---|
| Daily operations, client lookups, renewals | **Gretchen Daily Desk** | Model picker — your name |
| COI processing (upload images/PDFs) | **COI Assistant** | Model picker |
| Drafting client emails/texts | **Client Message Writer** | Model picker |
| New client onboarding | **Intake Builder** | Model picker |
| Renewal workflow tracking | **Renewal Manager** | Model picker |
| General CRM questions | **Gretchen Daily Desk** or **RSG Router** | Either works |

### Gretchen's Golden Rules

1. **Start with Gretchen Daily Desk.** It has your service SOPs, communication templates, and CRM tools built in.
2. **Upload documents directly.** For COIs, dec pages, and ID cards — upload the file and ask the assistant to extract info.
3. **Client messages are drafts.** Client Message Writer drafts the message — you review and send it through your normal channels.
4. **CRM data is real.** When you ask about clients, policies, or renewals, you get live EspoCRM data through Hermes.
5. **You can't break anything.** CRM writes go through validation. If something's wrong, the system tells you before it touches EspoCRM.

---

## Part 3: How the Routing Works (Reference)

### The RSG Router

When you select **RSG Router** and ask a question, here's what happens:

1. **Classification** — A small fast model (Qwen3 8B) reads your question and classifies it:
   - `tool_call` → CRM query (renewals, pipeline, clients, tasks) → dispatches to Hermes
   - `routine` → Simple admin/scheduling → Qwen3 8B (fast, cheap)
   - `client_communication` → Drafting emails/messages → Llama 3.3 70B
   - `commercial_reasoning` → Coverage analysis, risk assessment → DeepSeek-R1
   - `vision` → Document/image extraction → Qwen3 VL 32B
   - `general` → General questions, SOPs → Llama 3.3 70B

2. **Routing** — The router sends your question to the selected model
3. **Fallback** — If the selected model fails, it falls back to GPT-4.1 (OpenAI)
4. **Logging** — Every decision is logged to the routing database with cost and latency

### The 11 Assistants

| Assistant | Base Model | Tools | Best For |
|---|---|---|---|
| Lamar Daily Command | GPT-4.1 | Launchpad, Supabase, Hermes CRM | Lamar's command desk |
| Gretchen Daily Desk | GPT-4o | Launchpad, Hermes CRM | Gretchen's service cockpit |
| RSG Assistant | Llama 3.3 70B | None | General internal questions |
| CRM Activity Assistant | Qwen3 32B | Hermes CRM, n8n Bridge | CRM activity tracking |
| CRM Write Operator | Qwen3 32B | Hermes CRM | Restricted CRM writes |
| Quote Rescue | Qwen3 14B | n8n Bridge, Hermes CRM | Stalled quote recovery |
| Renewal Manager | Qwen3 32B | n8n Bridge, Hermes CRM | Renewal workflows |
| Intake Builder | Qwen3 32B | n8n Bridge, Hermes CRM | New business intake |
| COI Assistant | Qwen3 VL 32B | Hermes CRM | COI document processing |
| Client Message Writer | Llama 3.3 70B | None | Drafting client communications |
| Dashboard Builder | Qwen3 32B | Supabase | SQL/dashboard queries |

### CRM Write Validation Flow

When any assistant or the router sends a write command to EspoCRM:

```
Your request
    ↓
n8n validation webhook
    ↓
Checks: is this a write? is it confirmed? are field values valid?
    ↓
If valid → forwarded to Hermes API → EspoCRM
If invalid → rejected with error message
    ↓
Slack audit notification → #systems-check
    ↓
Response returned to you
```

Valid task statuses (enforced by validation): `Inbox`, `In Progress`, `Waiting on Client`, `Waiting on Carrier`, `Completed`, `Cancelled`

---

## Part 4: Troubleshooting

**"The router gave me a generic answer instead of CRM data"**
- This means it misclassified your question. Try rephrasing with specific CRM keywords: "renewals," "pipeline," "client," "account," "policy."
- Or switch to the specific assistant (Renewal Manager, Gretchen Daily Desk) which has Hermes tools attached.

**"The response is taking forever"**
- Commercial reasoning queries (DeepSeek-R1) can take 20-30 seconds. That's normal — it's doing deep analysis.
- If everything is slow, check #systems-check on Slack for any error notifications.

**"I got an error about CRM validation"**
- You tried a CRM write that failed validation. The error message tells you exactly what's wrong (invalid status, missing confirmation, etc.).
- Fix the issue and try again. Nothing was written to EspoCRM.

**"The router says it can't connect to Hermes"**
- The Hermes server may be temporarily unreachable. The router has a fallback that tries Hermes directly if n8n is down.
- If both fail, check with Lamar or check #systems-check for alerts.

**"I don't see an assistant I need"**
- Revenue Focus Coach and Client Onboarding Manager were merged into other assistants (their skills are now part of Lamar Daily Command and Gretchen Daily Desk respectively).
- Use Intake Builder for onboarding tasks.
- Use Lamar Daily Command for revenue focus coaching.

---

## Quick Reference Card

### Lamar's Top 5 Questions for the Router
1. "How many renewals in the next 30 days?"
2. "Show me the pipeline summary"
3. "Draft an email to [client] about [topic]"
4. "Compare these quotes — what coverage gaps should I flag?"
5. "What's the status of [client]'s policy?"

### Gretchen's Top 5 Questions
1. "What personal lines renewals are coming up?"
2. "Find account [client name]"
3. "Run a data quality audit"
4. "Draft a text reminder to [client] about [document needed]"
5. "Show me the renewal status for [client]"

### Login
- URL: https://openwebui-l8ola-u69864.vm.elestio.app
- Email: lamar@risk-solutionsgroup.com
- Password: stored in 1Password (search "OpenWebUI" or "Elestio")
- Signup is disabled — only Lamar and Gretchen have accounts
