# Vault Migration Map
Created: 2026-05-07
Status: In Progress

This document maps the old (flat) vault structure to the new numbered hierarchy.
Use this as a reference when moving files locally in Obsidian.

## Folder Mapping

| Old Location | New Location | Priority | Notes |
|---|---|---|---|
| `RSG/SOPs/` | `01-Operations/SOPs/` | HIGH | Call intake parser, intake pipeline |
| `RSG/Workflows/` | `01-Operations/Workflows/` | HIGH | n8n workflows, Dify prompts, renewal pipeline |
| `RSG/Templates/` | `01-Operations/Templates/` | MED | Email + doc templates |
| `RSG/Clients/` | `01-Operations/Clients/` | MED | Account notes (data of record in EspoCRM) |
| `Carriers/` | `02-Underwriting/Carriers/` | HIGH | Appetites (CNA, GEICO, Liberty Mutual), commission docs |
| `AI_Knowledge/Carriers/` | `02-Underwriting/Knowledge-Base/Carriers/` | MED | Carrier knowledge base entries |
| `AI_Knowledge/Insurance Education/` | `02-Underwriting/Knowledge-Base/Education/` | MED | Insurance education materials |
| `AI_Knowledge/Lines of Business/` | `02-Underwriting/Knowledge-Base/LOB/` | MED | Lines of business reference |
| `AI_Knowledge/Document Inbox/` | `00-Inbox/` | LOW | Merge with general inbox |
| `RSG Commercial Data model/` | `02-Underwriting/Commercial-Data-Model/` | HIGH | GL, WC, SIC codes (2,000+ files) |
| `CRM Field Reference guide/` | `03-Systems/CRM/Field-Reference/` | HIGH | 10 entity field reference docs |
| `RSG/EspoCRM/` | `03-Systems/CRM/` | HIGH | Build specs, workflow fixes, NowCerts mapping |
| `RSG/Infrastructure/` | `03-Systems/Infrastructure/` | HIGH | Architecture, DB schemas, SSH refs, roadmap |
| `rsg-infrastructure/` | `03-Systems/CRM/` | HIGH | EspoCRM changelog + codebase audit |
| `AI_Knowledge/Skills/` | `03-Systems/Agents/Skills/` | HIGH | 25+ skill files (canonical source) |
| `skills/` | (DELETE - deprecated) | LOW | Replaced by AI_Knowledge/Skills/ |
| `Github/` | `03-Systems/Infrastructure/Github/` | LOW | Repo references |
| `_System/` | `_System/` (stays) | N/A | Meta folder, indexes, architecture docs |
| `_Archive/` | `_Archive/` (stays) | N/A | Retired content |
| `Personal/` (local only) | `05-Personal/` | LOW | Journal, goals, tasks |
| `Ministry/` (local only) | `05-Personal/Ministry/` | LOW | Sermons, assembly notes |
| `Openclaw/` (local only) | `03-Systems/Agents/OpenClaw/` | MED | OpenClaw operational docs |

## Migration Instructions

### Option A: Local Move (Recommended)
Do this in Obsidian so internal links update automatically:

1. Open Obsidian
2. Drag folders from old locations to new locations
3. Obsidian will auto-update `[[wikilinks]]`
4. Commit via Obsidian Git plugin
5. Verify on GitHub

### Option B: Git Move
If doing via command line (links won't auto-update):

```bash
cd /path/to/rsg-obsidian-vault
git mv "RSG/SOPs" "01-Operations/SOPs"
git mv "RSG/Workflows" "01-Operations/Workflows"
git mv "Carriers" "02-Underwriting/Carriers"
# ... etc
git commit -m "vault(migrate): move files to 00-05 structure"
git push
```

Then fix broken links in Obsidian.

### What NOT to Move Yet
- `.obsidian/` - Obsidian config, leave in place
- `_System/` - Already in the right place
- `_Archive/` - Already in the right place
- `.gitignore` - Root level, leave in place
- `VoiceInk_Dictionary.json` - Root level config, consider archiving

## Large Files Warning
The `RSG Commercial Data model/` folder contains 2,000+ CSV files (GL, WC, SIC codes).
Moving this is a bulk operation. Consider doing it last or via git mv.

## Post-Migration Checklist
- [ ] All files moved to 00-05 folders
- [ ] Old empty folders deleted
- [ ] Internal links verified in Obsidian
- [ ] Vault Index updated with final paths
- [ ] GitHub sync confirmed
- [ ] Agent skill file paths updated if needed
- [ ] OpenClaw GitHub mirror tested
