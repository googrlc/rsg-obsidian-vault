# RSG Obsidian Vault - Index
Last Updated: 2026-05-07

## Source of Truth
Full architecture: [[_System/RSG-Architecture-2026]] - systems, agents, workflows, credentials

| Path | Description | Updated |
|---|---|---|
| [[_System/RSG-Dify-Agent-Registry]] | Canonical Dify app IDs, intake workflow deep dive, audit items, portal + deployment runbook | 2026-04-12 |
| [[_System/RSG-n8n-Workflow-Inventory]] | Canonical n8n workflow IDs, health stats, credentials, Gemini/Espo rules, open issues | 2026-04-12 |
| [[03-Systems/CRM/RSG_EspoCRM_Codebase_Audit_2026-04-16]] | Full EspoCRM codebase audit: 52 findings across 7 deep dives, prioritized P0-P3 execution plan | 2026-04-16 |
| [[04-Strategy/Growth/RSG-Growth-Strategy-Checklist]] | Growth strategy checklist: $1M North Star, 4-phase plan, revenue math, weekly rituals | 2026-05-07 |

## Vault Structure (v2 - Numbered Hierarchy)

```
rsg-obsidian-vault/
|-- 00-Inbox/               <- Unsorted captures, quick notes, agent drops
|-- 01-Operations/          <- SOPs, workflows, templates, client operations
|   |-- SOPs/
|   |-- Workflows/
|   |-- Templates/
|   |-- Clients/
|   +-- Renewals/
|-- 02-Underwriting/        <- Carrier knowledge, risk assessment, data models
|   |-- Carriers/
|   |-- Commercial-Data-Model/
|   |-- Knowledge-Base/
|   +-- Intake-Schemas/
|-- 03-Systems/             <- Infrastructure, CRM, architecture, integrations
|   |-- Architecture/
|   |-- CRM/
|   |-- Agents/
|   |-- Infrastructure/
|   +-- Integrations/
|-- 04-Strategy/            <- Growth planning, analytics, revenue targets
|   |-- Growth/
|   |-- Analytics/
|   |-- Initiatives/
|   +-- Market-Research/
|-- 05-Personal/            <- Journal, goals, ministry, personal projects
|   |-- Journal/
|   |-- Goals/
|   |-- Ministry/
|   +-- Projects/
|-- _Archive/               <- Retired content
+-- _System/                <- THIS FOLDER (meta, indexes, architecture)
```

## Migration Status
See [[_System/Migration-Map]] for the full old-to-new folder mapping.
New 00-05 folders initialized 2026-05-07. Migration in progress.

## Tool Access Map

| Tool | Access Method | Read | Write |
|---|---|---|---|
| Littlebird | GitHub MCP (rsg-2026 org) | YES | YES |
| Claude (claude.ai) | Obsidian Local REST API MCP | YES | YES |
| Claude Code | Direct filesystem | YES | YES |
| CoWork | Obsidian Local REST API | YES | YES |
| OpenClaw | GitHub API (git sync) | YES | NO |
| n8n | GitHub API webhook | YES | NO |
| Obsidian app | Direct filesystem | YES | YES |

## GitHub Sync
LIVE - github.com/rsg-2026/rsg-obsidian-vault (main branch)
Previously: github.com/googrlc/rsg-obsidian-vault (redirects still work)

## Key Rules
- Skills canonical source = AI_Knowledge/Skills/ (migrating to 03-Systems/Agents/Skills/)
- OpenClaw reads skills FROM GitHub mirror - keep vault synced
- North Star: $1M annual premium (see 04-Strategy/Growth/)
- Lamar's #1 job: revenue-generating activity
