---
title: Client Service Desk — Outlook to Zoho Creator
updated: 2026-08-19
tags: [rsg, architecture, amy, zoho, creator, service-request, outlook]
---

# Client Service Desk

**Decision date:** 2026-08-18  
**Updated:** 2026-08-19 (live Zoho create + retrieve)  
**Status:** Locked for client work. Admin/ops is a later planner.  
**Owner:** Lamar Coates

## One-sentence summary

From Outlook, Amy turns a client email into a Zoho Task or a Service Request (Case plus the steps to finish it). She writes **and reads live Zoho CRM** — not the Supabase case mirror. The pipeline is Cases.`Service_Request_Status`. Gretchen and Lamar zoom into a Zoho Creator workstation. NowCerts gets an additive monthly backup.

## What this is (and is not)

| In | Out |
|---|---|
| COI, endorsement, ID cards, policy billing, claim, cancellation, coverage change | Admin/ops (Wix, subscriptions, internal portals) |
| Adhoc from the open Outlook email, confirm before write | Auto-scan of the whole inbox (v1) |
| Zoho CRM as system of record | Creator as a second database |
| Monthly additive AMS notes/tasks | Live NowCerts writes on intake |

Amy stays published to **Microsoft 365 Copilot only**. The Outlook Copilot pane is that same channel — not a new Teams or SharePoint agent. Creator is a Zoho workbench, not an Amy channel.

This replaces n8n **WF-F** (Gmail `RSG-Task` → EspoCRM). Espo stays retired. Deactivate WF-F.

## Layers

```
Outlook email
    → Amy (preview → confirm)
    → live Zoho Note + Task  OR  Case + child Tasks
    → Cases Kanban (Service_Request_Status)
    → Creator Client Service Desk (work the queue)
    → monthly AMS_Write_Queue → NowCerts (additive)

Amy retrieve
    → Zoho MCP Data Insights / Data Operations
    → the same live Cases and Tasks
```

**Hard rule:** Creator reads and writes CRM Cases, Tasks, Account, and Policy. It does not store its own service-request records.

## Service Request = Case + steps

A Service Request is never a single task. Templates live in Supabase (`get_service_request_templates`): `coi`, `endorsement`, `id_cards`, `billing`, `claim`, `cancellation`. Amy may edit the step list to fit the email. Zero steps is invalid.

Personal-lines service → Gretchen. Claim, commercial, bind, cancellation → Lamar.

## Build spec

Canonical session docs (repo): [CLIENT-SERVICE-HANDOFF.md](https://github.com/googrlc/agency-knowledge-build/blob/main/CLIENT-SERVICE-HANDOFF.md) and `AMY-INSTRUCTIONS.md` (Zoho MCP wiring + paste-ready Amy prompt).

Gretchen-facing: [[RSG/SOPs/Client-Service-Request-Desk]]

Related: [[03-Systems/Architecture/Amy-Copilot-Chat-Architecture]]
