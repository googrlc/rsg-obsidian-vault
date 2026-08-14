# 03-Systems

Infrastructure documentation, CRM architecture, integration specs, and technical reference.

## Subfolders
- `Architecture/` - System architecture docs (RSG-Architecture-2026, Platform Architecture)
- `CRM/` - CRM field references (live = Zoho CRM; EspoCRM docs are legacy)
- `Agents/` - Hermes, OpenClaw, Dify agent registry and skill files
- `Infrastructure/` - Hosting, SSH, database schemas, security
- `Integrations/` - n8n workflow inventory, API references, sync patterns

## Source of Truth Hierarchy
1. **Zoho CRM** - Pipeline / client relationship truth (live)
2. **NowCerts** - AMS ledger (carrier-facing policy truth)
3. **Supabase** - Normalized sync, analytics, AI layer
4. **n8n** - Automation orchestration
5. **This vault** - Documentation and institutional knowledge

EspoCRM is retired. Treat any Espo field specs or audits in this folder as historical.

## Key Architecture Docs
- [[Architecture/Amy-Copilot-Chat-Architecture]] — locked 2026-08-14: Copilot Chat is Amy's sole interface
- RSG-Architecture-2026.md (Hermes / Slack / n8n ops reference; Espo sections are legacy)
- RSG Workflow Registry
- EspoCRM Codebase Audit (historical — Espo retired)
- Data Dictionary
- [[rsg-infrastructure/Supabase-Recon-2026-08-14]] — live Supabase readiness for Amy
