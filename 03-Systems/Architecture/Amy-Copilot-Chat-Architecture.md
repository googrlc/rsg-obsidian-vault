---
title: Amy — Copilot Chat as the Sole Interface
updated: 2026-08-18
tags: [rsg, architecture, amy, copilot-studio, copilot-chat, supabase]
---

# Amy — Copilot Chat as the Sole Interface

**Decision date:** 2026-08-14  
**Updated:** 2026-08-18 (client service desk)
**Status:** Locked
**Owner:** Lamar Coates

## One-sentence summary

The team opens **Microsoft 365 Copilot Chat**, talks to **Amy**, and Amy routes to specialist agents that query **Supabase** — one conversation, governed inside Microsoft 365, with no app switching.

## What changed

| Before (draft) | Now (locked) |
|---|---|
| Publish agents to Teams + SharePoint + M365 Copilot Chat | Publish agents to **Microsoft 365 Copilot Chat only** |

Everything else stays the same. Supabase is still the intelligence layer. Amy is still the orchestrator. Specialist agents still exist. Governance still lives in Microsoft. The only change is **where users interact with the agents.**

**Do not add:** Teams channel, SharePoint channel, WhatsApp channel, custom website channel.

SharePoint remains a **document store** (carrier appetite PDFs, policy examples, SOPs). It is not an agent channel. Copilot Chat can reference SharePoint through Copilot Studio knowledge sources.

This front door does **not** replace Hermes, Slack, **Zoho CRM**, or NowCerts. Those remain systems of record and ops channels. Copilot Chat is the sole interface for Amy and her specialists.

**CRM of record is Zoho CRM** (MCP: `user-ZohoMCP`). All CRM reads and writes go through Zoho.

## Access model

```
USERS (producers, CSRs, account managers, principals)
    │
    │  Open Microsoft 365 Copilot Chat
    │  (copilot.cloud.microsoft or M365 app)
    ▼
MICROSOFT 365 COPILOT CHAT   ← the only interface
    │
    ▼
AMY (Orchestrator Agent)
    │  Receives all questions
    │  Routes to specialists
    │  Handles CRM/service directly
    │  Drafts communications
    ├── Carrier Appetite Agent
    ├── Classification Agent
    ├── Agency Bill Agent
    ├── Commission Agent
    └── Medicare Agent (sub-agent; publish separately only if a dedicated Medicare team exists)
            │
            ▼
        SUPABASE (Postgres + pgvector)
            │  Structured intelligence
            ▼
        SharePoint / Nextcloud   ← source documents only
            │
            ▼
        Azure Key Vault + App Insights + Power Platform governance
```

## Why Copilot Chat, not Teams

| Factor | Copilot Chat | Teams |
|---|---|---|
| Where agents live | Native home for Copilot Studio agents | Requires Teams app deployment + admin policies |
| Agent discovery | In-conversation agent recommendations | User must know which app to open |
| Agent sharing | Shareable links from Copilot Chat sidebar | Per-user Teams app install |
| License | M365 Copilot $30/user/month includes Chat + agent access | Same license, extra deployment complexity |
| SharePoint grounding | Via Copilot Chat knowledge sources | Separate channel config |
| Admin overhead | Publish once to "Microsoft 365 Copilot" | App manifest, policies, sideloading rules |
| User friction | Zero — it is chat | User must find and pin the Teams app |

## Publishing

| Agent | Channel | Status |
|---|---|---|
| Amy (Orchestrator) | Microsoft 365 Copilot Chat | To publish |
| Carrier Appetite Agent | Sub-agent of Amy (not directly published) | Configured |
| Classification Agent | Sub-agent of Amy (not directly published) | Configured |
| Agency Bill Agent | Sub-agent of Amy (not directly published) | Configured |
| Commission Agent | Sub-agent of Amy (not directly published) | Configured |
| CRM / Service | Handled by Amy directly via **Zoho CRM** (`user-ZohoMCP`) | N/A |
| Medicare Agent | Sub-agent of Amy (not directly published) | Configured |

**Users only see Amy in Copilot Chat.** Specialists are tools Amy calls. That is by design.

### Why not publish specialists directly

1. **Cognitive load.** Seven agents in the sidebar forces the user to pick. That defeats the orchestrator.
2. **Context loss.** Switching agents mid-thread drops conversation context. Amy carries it.
3. **Governance.** One published agent is easier to monitor and update than seven.

**Exception:** Publish Medicare separately only if a dedicated Medicare team never touches P&C.

### Copilot Studio publish steps

1. Build Amy and each specialist in Copilot Studio.
2. For Amy: Channels → **Microsoft 365 Copilot** → Publish.
3. Enable **multi-agent orchestration** on Amy.
4. Add specialists as **sub-agents**.
5. Tell the team: "Open Copilot Chat and talk to Amy."

Copilot Chat can still suggest a specialist via in-conversation agent recommendations (Build 2025). Prefer Amy as the default so routing stays internal.

## CRM of record

**Zoho CRM is live.** MCP: `user-ZohoMCP`. Confirmed 2026-08-14 — 39 visible modules including standard Leads / Contacts / Accounts / Deals / Tasks / Cases plus RSG custom modules: `Policies`, `Renewals`, `Renewal_Events`, `AMS_Write_Queue`.

Amy's CRM/service answers and task writes go through Zoho.

**Client service (locked 2026-08-18):** Outlook email → Amy (confirm first) → Zoho Case + step Tasks (or a standalone Task) → Cases Kanban → **Zoho Creator Client Service Desk**. Creator is a workbench, not a second CRM. NowCerts is a monthly additive backup. Agency client work only. See [[03-Systems/Architecture/Client-Service-Desk]] and [CLIENT-SERVICE-HANDOFF.md](https://github.com/googrlc/agency-knowledge-build/blob/main/CLIENT-SERVICE-HANDOFF.md).

## Daily function (target UX)

Amy handles morning desk, mid-day placement ("who writes GL for plumbing in Georgia?"), commission discrepancies, and agency-bill exposure — all in one Copilot Chat thread. Writes go to `agency_crm_tasks`, `commission_escalations`, and related Supabase tables. See [[rsg-infrastructure/Supabase-Recon-2026-08-14]] for live table readiness.

## Governance (Copilot Chat specific)

| Control | Configuration |
|---|---|
| Who can use agents | Microsoft 365 Copilot license ($30/user/month) |
| Agent visibility | Only Amy appears; specialists are hidden sub-agents |
| Transcript recording | Copilot Studio → Security & governance → Enable transcripts |
| DLP | Microsoft Purview — block sensitive labeled output |
| Moderation | Copilot Studio → Generative AI → Enable moderation |
| User feedback | Copilot Studio → Generative AI → Enable feedback (thumbs in Chat) |
| Application Insights | Azure → connect to Copilot Studio |
| Power Platform solution | `RSGAIAgents` for version control and env migration |
| Secrets | Azure Key Vault for Supabase keys and OpenAI keys |

## Prerequisites

| Requirement | Notes |
|---|---|
| Microsoft 365 Copilot license | Required per user who talks to Amy via Copilot Chat |
| Copilot Studio license or pay-as-you-go | Required to build and publish |
| Azure subscription | Key Vault + Application Insights |
| SharePoint site | Document storage — **not** an agent channel |
| Supabase project `rsg-infrastructure` (`wibscqhkvpijzqbhjphg`) | Existing insurance schema |
| OpenAI API key | Embeddings |

**Not required:** Teams licenses, Teams admin policies, Teams app deployment, SharePoint agent channel.

## Locked decisions

- Copilot Chat is the sole user interface for Amy.
- Specialists are sub-agents, not separately published (Medicare exception as above).
- Supabase is the intelligence layer. SharePoint/Nextcloud hold source documents only.
- Do not deploy Teams or SharePoint as agent channels.
- Hermes / Slack / **Zoho CRM** / NowCerts remain systems of record; this does not replace them.
- **CRM of record is Zoho CRM.** EspoCRM is retired — historical vault docs that mention Espo are legacy, not live.
- Client service intake is Outlook + Amy → Zoho Cases/Tasks. The workstation is Zoho Creator reading those CRM records. Admin/ops is a separate planner.

## Supabase status (2026-08-14)

**Complete.** 4,436 embeddings, 8 RPCs, 2 Edge Functions, `ai_knowledge_items` live. Ready for Copilot Studio.

**Next session:** [[03-Systems/Architecture/Supabase-Microsoft-Handoff-2026-08-14]] — build order, endpoints, Amy system prompt, first test prompt.

→ [[rsg-infrastructure/Supabase-Readiness-Final-2026-08-14]]  
→ GitHub: [agency-knowledge-build/MICROSOFT-HANDOFF.md](https://github.com/googrlc/agency-knowledge-build/blob/main/MICROSOFT-HANDOFF.md)

## Related

- **Final readiness (use this):** [[rsg-infrastructure/Supabase-Readiness-Final-2026-08-14]]
- Pre-build recon: [[rsg-infrastructure/Supabase-Recon-2026-08-14]]
- Platform ops architecture (Hermes, Slack): [[_System/RSG-Architecture-2026]]
