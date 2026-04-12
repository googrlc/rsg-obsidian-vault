---
title: RSG n8n Workflow Inventory
tags: [n8n, automation, workflows, inventory, canonical]
created: 2026-04-08
updated: 2026-04-12
status: active
type: inventory
---

# RSG n8n Workflow Inventory

> [!danger] Current Health: 85% Failure Rate
> 4,625 prod executions | 3,930 failed | Avg run time: 5.31s
> Instance: `https://n8n-zpvua-u69864.vm.elestio.app` | Tailscale: `100.73.8.33`
> Backup repo: `googrlc/rsg-n8n` (auto-export every Sunday 2am ET)

---

## Renewal & Retention

| Workflow | ID | Status | Trigger | Notes |
|---|---|---|---|---|
| WF1 — Renewal Auto-Create (EspoCRM) | 0npEnsS6D2hpjBfK | 🔴 BROKEN | Schedule 2x daily (7am + 7pm ET) | Queries policies expiring within 90 days, deduplicates, creates Renewal records. Broken: SLACK_WEBHOOK_URL env var missing + Activity Log 404 |
| WF3 — Renewal Commission Auto-Create (EspoCRM) | zlzLty9lJmtrPWuI | 🟢 Active | Webhook POST `/webhook/wf3-renewal-won` | Fires on stage = "Renewed - Won". Creates commission record + updates Renewal record |
| RSG — Renewal Outreach Automation (EspoCRM) | — | 🟢 Active | Created 20 March | Renewal outreach sequence |
| RSG — Renewal Retention & Commission Report | — | 🟢 Active | Created 23 March | Periodic retention + commission summary |

> [!warning] WF1 Known Failures
> 1. `Build Slack Digest` — `$env.SLACK_WEBHOOK_URL` is undefined
> 2. `Post Activity Log` — 404 error on EspoCRM Activity endpoint
> Fix: Set SLACK_WEBHOOK_URL as n8n environment variable. Verify Activity endpoint URL.

---

## Gmail & Email Automation

| Workflow | ID | Status | Trigger | Notes |
|---|---|---|---|---|
| RSG — Gmail Triage Master | pBt2mygNz2gQ4bsq | 🟢 Live | Gmail poll every 2 min | Gemini Flash pre-screen → Claude Sonnet decision. Routes to 7 branches |
| RSG — OTP Cleanup | A5FlHix8EWRyxuMz | 🟢 Live | Schedule 3x daily (7am, 12pm, 6pm ET) | Deletes OTP/verification emails from inbox, newer than 1 day |
| WF-F — Gmail RSG-Task Label → EspoCRM Task Creator | — | 🔴 Error | Gmail label trigger | Creates EspoCRM tasks from labeled emails. EspoCRM auth issue |
| Task-Workflow D — Task Complete → Client Thank You Email | — | 🔴 Error | EspoCRM webhook | Sends thank you on task completion. Failing every 5 min |

### Gmail Triage — Routing Map

| Category | EspoCRM Task | Todoist | Slack | Other |
|---|---|---|---|---|
| RENEWAL | Create (Priority=High) | RSG—My Tasks (urgent) | #the-boss | — |
| CLIENT_SERVICE | Create | None (Gretchen's) | #rsg-gretchen | — |
| CARRIER_REQUEST | Create (Priority=Normal) | RSG—My Tasks (high) | #the-boss | — |
| MEETING_REQUEST | Create (Priority=High) | RSG—My Tasks (urgent) | #the-boss (interactive buttons) | — |
| PERSONAL | None | Personal project | None | Supabase personal_tasks |
| CARRIER_FYI | None | None | None | Gmail label + archive |
| JUNK | None | None | None | Gmail delete |

### Todoist Project IDs

| Project | ID |
|---|---|
| Inbox | 6fxMwxJmmPPgfPGP |
| 🏢 RSG—My Tasks | 6gJxf8MQvVcwmfVf |
| 📧 Personal | 6gJxfRffv2hf2g7w |

---

## Calendar Workflows

| Workflow | ID | Status | Trigger |
|---|---|---|---|
| RSG — Google Calendar Morning Sync | — | 🟢 Active | Schedule (7am ET daily) |
| RSG — Google Calendar On-Demand Query | — | 🟢 Active | Webhook (on-demand) |
| RSG — Meeting Approval Callback | oySUjI7SAcdO2XDv | 🟢 Live | Webhook POST `/webhook/meeting-approval` |

> [!warning] Meeting Approval Callback - Pending Config
> Slack app interactivity URL must be set to:
> `https://n8n-zpvua-u69864.vm.elestio.app/webhook/meeting-approval`
> Without this, the "Add to Calendar" button in Slack meeting alerts will not work.

---

## Commissions & New Business

| Workflow | ID | Status | Trigger | Notes |
|---|---|---|---|---|
| WF2 — NB Commission Auto-Create (EspoCRM) | — | 🟢 Published | EspoCRM webhook | New business commission creation |
| NB-Workflow 1 — Deal Won Intake & Commission Log | 2XZNvkYJvseyACLj | 🟢 Active | — | Deal won intake processing |

---

## NowCerts ↔ EspoCRM Sync (10 Workflows)

All rebuilt Apr 11, 2026. Stored in `googrlc/rsg-n8n/workflows/`.

| File | Direction | Entity |
|---|---|---|
| 01-nc-to-espo-accounts.json | NowCerts → EspoCRM | Accounts |
| 02-espo-to-nc-accounts.json | EspoCRM → NowCerts | Accounts |
| 03-nc-to-espo-policies.json | NowCerts → EspoCRM | Policies |
| 04-espo-to-nc-policies.json | EspoCRM → NowCerts | Policies |
| 05-nc-to-espo-contacts.json | NowCerts → EspoCRM | Contacts |
| 06-espo-to-nc-contacts.json | EspoCRM → NowCerts | Contacts |
| 07-nc-to-espo-tasks.json | NowCerts → EspoCRM | Tasks |
| 08-espo-to-nc-tasks.json | EspoCRM → NowCerts | Tasks |
| 09-nc-to-espo-cases.json | NowCerts → EspoCRM | Cases |
| 10-espo-to-nc-cases.json | EspoCRM → NowCerts | Cases |

---

## System & Utility

| Workflow | ID | Status | Notes |
|---|---|---|---|
| RSG — Global Error Workflow (EspoCRM) | lWeQqSjVGaDEqTsS | 🟢 Active | Catches all workflow errors → Slack #systems-check alert |
| RSG — X-Date Nurture Loop | YDzMjoooRDFjXD0U | 🟡 Inactive | Daily 7am ET, fetches Leads (Nurture status) + Closed Lost Opps, creates EspoCRM tasks |

---

## Credential Reference

| Service | Credential ID | Type |
|---|---|---|
| Gmail | 3tNPdo42yNxdUEr4 | gmailOAuth2 |
| Google Calendar | gxYGjDYGvKxCvv5O | googleCalendarOAuth2Api |
| Gemini (Flash) | cKbetIsqPmgrl3DI | googlePalmApi (use gemini-2.5-flash) |
| Anthropic/Claude | Y3Od9JXqvfLMKI9G | anthropicApi |
| EspoCRM | 90zG2fzO7i0KhGwi | httpHeaderAuth (X-Api-Key) |
| Slack | rTNF4McInN9GXdlG | slackApi |
| Supabase | orQ76IQmpakFh3sm | supabaseApi |
| Todoist | pMnJVnQfFWDQPMMi | todoistApi |

### Slack Channel IDs

| Channel | ID |
|---|---|
| #the-boss (Lamar) | C0ANQUENX4P |
| #rsg-gretchen | C0AMWAZBBJP |
| #systems-check | C0ANSEP6SSD |

### EspoCRM Key IDs

| Key | Value |
|---|---|
| Lamar Coates User ID | 69bdad92458da2204 |
| EspoCRM API Key | stored in 1Password RSG vault |

---

## Gemini Flash Config (Critical)

> [!warning] Gemini Model Gotchas
> - Use model: `gemini-2.5-flash` (1.5-flash is deprecated)
> - Must include `thinkingConfig: { thinkingBudget: 0 }` inside `generationConfig`
> - Must set `responseMimeType: 'application/json'` for structured output
> - Without these settings, output will be truncated and JSON parsing will fail

---

## n8n EspoCRM API Rules (Critical)

> [!danger] GET vs POST Auth — Never Mix These Up
> - **GET requests:** Use `X-Api-Key` header ONLY. Never add `Content-Type`.
> - **POST/PUT requests:** Use `contentType: json` + `httpHeaderAuth` credential.
> - Credential type: `genericCredentialType` → `genericAuthType: httpHeaderAuth`
> - Credential ID: `90zG2fzO7i0KhGwi`

---

## Open Issues & Action Items

| # | Workflow | Issue | Fix |
|---|---|---|---|
| 1 | WF1 Renewal Auto-Create | SLACK_WEBHOOK_URL env var undefined | Add to n8n environment variables |
| 2 | WF1 Renewal Auto-Create | Post Activity Log → 404 | Verify /api/v1/Activity endpoint URL |
| 3 | WF-F Gmail → EspoCRM Task | Error every 5 min | Check EspoCRM auth credential |
| 4 | Task-Workflow D | Error every 5 min | Investigate; may be credential expired |
| 5 | RSG — Meeting Approval | "Add to Calendar" Slack button not wired | Set Slack app interactivity URL |
| 6 | X-Date Nurture Loop | Inactive — not running | Decision needed: activate or archive? |
| 7 | Gmail Triage — Personal branch | Supabase personal_tasks missing service key | Add SUPABASE_SERVICE_KEY to env vars |

---

## Related Notes

- [[RSG Agency Full Schema Setup]]
- [[RSG-Dify-Agent-Registry]]
- [[NowCerts EspoCRM Sync SOPs]]
