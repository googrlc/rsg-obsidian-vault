# RSG Obsidian Vault — Index
Last Updated: 2026-04-22

## Source of Truth
Full architecture: [[_System/RSG-Architecture-2026]] — systems, agents, workflows, credentials

| Path | Description | Updated |
|---|---|---|
| [[_System/RSG-Dify-Agent-Registry]] | Canonical Dify app IDs, intake workflow deep dive, audit items, portal + deployment runbook | 2026-04-12 |
| [[_System/RSG-n8n-Workflow-Inventory]] | Canonical n8n workflow IDs, health stats, credentials, Gemini/Espo rules, open issues | 2026-04-12 |
| [[rsg-infrastructure/RSG_EspoCRM_Codebase_Audit_2026-04-16]] | Full EspoCRM codebase audit: 52 findings across 7 deep dives, prioritized P0-P3 execution plan | 2026-04-16 |
| [[AI_Knowledge/Skills/OpenClaw-Build-Context]] | Canonical build memory for OpenClaw hosting platform deployment, Bedrock role setup, model choices, and active decisions | 2026-04-22 |

## Vault Structure

```
Obsidian Vault/
├── 00-Inbox/               ← Unsorted captures
├── AI_Knowledge/           ← Insurance knowledge base
│   ├── Skills/             ← Agent skill files (canonical source)
│   ├── Carriers/
│   ├── Insurance Education/
│   ├── Lines of Business/
│   └── Document Inbox/
├── Carriers/               ← Carrier appetite + commission docs
├── RSG/                    ← Agency operations
│   ├── Infrastructure/     ← System docs, DB schemas, security
│   ├── Workflows/          ← n8n + OpenClaw build docs
│   ├── EspoCRM/            ← CRM build specs + workflow fixes
│   ├── SOPs/               ← Standard operating procedures
│   ├── Templates/          ← Email + document templates
│   └── Clients/            ← Account notes (client data lives in EspoCRM)
├── RSG Commercial Data model/ ← GL/WC/SIC class codes (2,000+ files)
├── Skills/                 ← (deprecated — use AI_Knowledge/Skills/)
├── Github/                 ← Repo references
├── Ministry/               ← Sermons, Assembly, Teaching
├── Personal/               ← Journal, Tasks, Goals
├── _Archive/               ← Retired content
└── _System/                ← THIS FOLDER
    ├── RSG Vault Index.md          ← This file
    ├── RSG-Architecture-2026.md    ← Full system architecture
    ├── RSG Workflow Registry.md    ← n8n + OpenClaw workflow status
    ├── data dictionary.txt
    └── Credentials/
```

## Tool Access Map

| Tool | Access Method | Read | Write |
|---|---|---|---|
| Claude (claude.ai) | Obsidian Local REST API MCP | YES | YES |
| Claude Code | Direct filesystem | YES | YES |
| CoWork | Obsidian Local REST API | YES | YES |
| OpenClaw | GitHub API (git sync) | YES | NO |
| n8n | GitHub API webhook | YES | NO |
| Obsidian app | Direct filesystem | YES | YES |

## GitHub Sync
LIVE — github.com/googrlc/rsg-obsidian-vault (main branch, auto-sync via Obsidian Git plugin)

## Key Rule
Skills canonical source = AI_Knowledge/Skills/
OpenClaw reads skills FROM GitHub mirror — keep vault synced
