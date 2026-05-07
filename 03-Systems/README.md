# 03-Systems

Infrastructure documentation, CRM architecture, integration specs, and technical reference.

## Subfolders
- `Architecture/` - System architecture docs (RSG-Architecture-2026, Platform Architecture)
- `CRM/` - EspoCRM field references, codebase audits, deployment changelogs
- `Agents/` - Hermes, OpenClaw, Dify agent registry and skill files
- `Infrastructure/` - Hosting, SSH, database schemas, security
- `Integrations/` - n8n workflow inventory, API references, sync patterns

## Source of Truth Hierarchy
1. **EspoCRM** - Client/policy data of record
2. **NowCerts** - AMS ledger (carrier-facing)
3. **Supabase** - Normalized sync, analytics, AI layer
4. **n8n** - Automation orchestration
5. **This vault** - Documentation and institutional knowledge

## Key Architecture Docs
- RSG-Architecture-2026.md (master reference)
- RSG Workflow Registry
- EspoCRM Codebase Audit
- Data Dictionary
