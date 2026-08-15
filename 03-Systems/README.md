# 03-Systems

Infrastructure documentation, CRM architecture, integration specs, and technical reference.

## Subfolders
- `Architecture/` - System architecture docs (RSG-Architecture-2026, Platform Architecture)
- `CRM/` - CRM field references (live = Zoho CRM)
- `Agents/` - Hermes and Claude agent registry and skill files
- `Infrastructure/` - Hosting, SSH, database schemas, security
- `Integrations/` - API references, sync patterns

## Source of Truth Hierarchy
1. **Zoho CRM** - Pipeline / client relationship truth (live)
2. **NowCerts** - AMS ledger (carrier-facing policy truth)
3. **Supabase** - Normalized sync, analytics, AI layer
4. **This vault** - Documentation and institutional knowledge

## Key Architecture Docs
- [[Architecture/Amy-Copilot-Chat-Architecture]] — locked 2026-08-14: Copilot Chat is Amy's sole interface
- RSG-Architecture-2026.md (Hermes / Slack ops reference)
- Data Dictionary
- [[rsg-infrastructure/Supabase-Recon-2026-08-14]] — live Supabase readiness for Amy
