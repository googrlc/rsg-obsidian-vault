# RSG Obsidian Vault — Index
Last Updated: 2026-03-29

## Source of Truth
Full architecture: [[_System/RSG-Architecture-2026]] — systems, agents, workflows, credentials

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
