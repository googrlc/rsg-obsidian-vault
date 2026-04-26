# RSG Walled Garden — v2 Build Log
**Date:** March 26, 2026
**Build Session:** Full deployment from scratch
**OpenClaw Version:** 2026.3.25 (hosting platform)
**Status:** LIVE — Gateway healthy, Slack connected, 14 agents deployed

---

## Infrastructure

| Component | Detail |
|---|---|
| **Host** | hosting platform VPS — `{{OPENCLAW_HOST}}` |
| **IP** | 152.53.212.76 (public), 100.109.241.110 (Tailscale) |
| **OS** | Ubuntu 24.04 LTS |
| **Gateway** | OpenClaw 2026.3.25, Docker, port 18789 |
| **Web UI** | `https://{{OPENCLAW_HOST}}/chat?session=main` |
| **SSH** | `ssh root@{{OPENCLAW_HOST}}` |

---

## Tailscale Mesh (All Connected)

| Node | Tailscale IP | Platform | Role |
|---|---|---|---|
| openclaw-larau-u69864 | 100.109.241.110 | Linux | OpenClaw Gateway |
| lamars-mac-mini | 100.82.142.43 | macOS | Local AI (Ollama) |
| n8n-zpvua-u69864 | 100.73.8.33 | Linux | n8n Automation |
| rrespocrm-rsg-u69864 | 100.117.239.109 | Linux | EspoCRM |

---

## Environment Variables (`/opt/app/.env`)

| Key | Status |
|---|---|
| `SOFTWARE_VERSION_TAG` | `latest` |
| `GATEWAY_TOKEN` | Set |
| `ADMIN_PASSWORD` | Set |
| `ANTHROPIC_API_KEY` | Set (`sk-ant-api03-...`) |
| `SLACK_BOT_TOKEN` | Set (`xoxb-9722...`) |
| `SLACK_APP_TOKEN` | Set (`xapp-1-A0AP01DQW6R-10785466...`) |

---

## Model Providers

| Provider | Model | Name | Location |
|---|---|---|---|
| Anthropic | claude-3-5-sonnet-latest | Claude 3.5 Sonnet | Cloud API |
| Ollama | deepseek-r1:8b | The Researcher | Mac Mini (100.82.142.43:11434) |
| Ollama | mxbai-embed-large:latest | The Librarian | Mac Mini (100.82.142.43:11434) |

**groupPolicy valid values:** `"open"` | `"disabled"` | `"allowlist"`

---

## MCP Servers

### Supabase
- **Project:** rsg-infrastructure (`wibscqhkvpijzqbhjphg`)
- **URL:** `https://wibscqhkvpijzqbhjphg.supabase.co`
- **Auth:** Service role key (set in openclaw.json)
- **Command:** `npx -y @supabase/mcp-server-supabase@latest`
- **Lazy-loaded:** Spawns on first query, not at startup

---

## Slack Integration

| Setting | Value |
|---|---|
| Mode | Socket Mode |
| App ID | A0AP01DQW6R |
| Streaming | Partial |
| Group Policy | Allowlist |
| Status | **Connected** |

### Channel Map

| Channel | ID | Primary Agent(s) |
|---|---|---|
| #agency-ops | C0AP4MFKH7U | Revenue Sheriff, Focus Guard |
| #client-service | C0AP4MHCLLS | Operations Foreman, Deal Coach |
| #growth-finance | C0AP89NDTHA | RSG CFO |
| #the-study | C0AP89HLJKE | Shepherding Assistant, Message Prep Scribe |
| #sales-brief | C0AP1BCEURK | Revenue Sheriff |
| #service-brief | C0AP2MML9L6 | Renewal Watchdog |
| #daily-ops-digest | C0ANSEP6SSD | Morning Commander |
| #systems-check | C0AFHN83ZE3 | Automation Triage Nurse |
| #the-task-list | C0AH4KJAYTU | Task Finisher |
| #the-morning-commander | C0ANYMH87HR | Morning Commander (main agent) |

---

## 14 Deployed Agents

All agent configs live in `/opt/app/config/agents/<agent-id>/agent.json`.

| # | Agent ID | Name | Model | Role |
|---|---|---|---|---|
| 01 | revenue-sheriff | Revenue Sheriff | anthropic/claude-3-5-sonnet-latest | ADHD accountability, pipeline pressure |
| 02 | morning-commander | Morning Commander | anthropic/claude-3-5-sonnet-latest | Daily briefing (3 non-negotiables) |
| 03 | operations-foreman | Operations Foreman | anthropic/claude-3-5-sonnet-latest | Lamar ↔ Gretchen delegation |
| 04 | deal-coach | Deal Coach | anthropic/claude-3-5-sonnet-latest | Pre-call prep, objection handling |
| 05 | renewal-watchdog | Renewal Watchdog | anthropic/claude-3-5-sonnet-latest | Renewal pipeline protection |
| 06 | focus-guard | Focus Guard | anthropic/claude-3-5-sonnet-latest | Drift detection, pattern-interrupt |
| 07 | brain-dump-butler | Brain Dump Butler | anthropic/claude-3-5-sonnet-latest | Idea triage (Act/Schedule/Park/Release) |
| 08 | task-finisher | Task Finisher | anthropic/claude-3-5-sonnet-latest | Next physical action extractor |
| 09 | automation-triage-nurse | Automation Triage Nurse | anthropic/claude-3-5-sonnet-latest | Workflow health, build-vs-fix gating |
| 10 | reflection-anchor | Reflection Anchor | anthropic/claude-3-5-sonnet-latest | EOD spiritual processing |
| 11 | message-prep-scribe | Message Prep Scribe | anthropic/claude-3-5-sonnet-latest | Sermon/teaching outlines |
| 12 | rsg-cfo | RSG CFO | anthropic/claude-3-5-sonnet-latest | Commission tracking, cash flow |
| 13 | data-entry-assistant | Data Entry Assistant | anthropic/claude-3-5-sonnet-latest | NowCerts/EspoCRM field guide |
| 14 | shepherding-assistant | Shepherding Assistant | ollama/deepseek-r1:8b | Scriptural research (local model) |

**Main agent** (webchat + default Slack): Morning Commander (configured in `openclaw.json` → auto-selects `anthropic/claude-opus-4-6`)

---

## Custom Intelligence Assets

### Skill: `rsg-intel-pack.md`
- **Path:** `/opt/app/config/skills/rsg-intel-pack.md`
- **Purpose:** Trucking/commercial auto prospect research — DOT numbers, OOS rates, growth signals, call openers, objection flags
- **Used by:** Revenue Sheriff, Morning Commander

### Reference: `edge-cases.md`
- **Path:** `/opt/app/config/references/edge-cases.md`
- **Purpose:** FMCSA generic name collision resolution — disambiguation logic when company names return multiple matches

---

## Workspace Files (`/opt/app/workspace/`)

| File | Status |
|---|---|
| IDENTITY.md | Filled — "The Walled Garden" |
| USER.md | Filled — Lamar Coates, RSG context |
| SOUL.md | Default OpenClaw (operational) |
| AGENTS.md | Default OpenClaw (operational) |
| TOOLS.md | Default template |
| HEARTBEAT.md | Empty template |
| BOOTSTRAP.md | **Deleted** (onboarding complete) |

---

## Docker Architecture

```
/opt/app/
├── .env                          # API keys, tokens
├── docker-compose.yml            # Service definitions
├── config/                       # → /home/node/.openclaw/ (in container)
│   ├── openclaw.json             # Master config (gateway + mcp)
│   ├── agents/
│   │   ├── main/sessions/        # Main agent session state
│   │   ├── revenue-sheriff/agent.json
│   │   ├── morning-commander/agent.json
│   │   ├── operations-foreman/agent.json
│   │   ├── deal-coach/agent.json
│   │   ├── renewal-watchdog/agent.json
│   │   ├── focus-guard/agent.json
│   │   ├── brain-dump-butler/agent.json
│   │   ├── task-finisher/agent.json
│   │   ├── automation-triage-nurse/agent.json
│   │   ├── reflection-anchor/agent.json
│   │   ├── message-prep-scribe/agent.json
│   │   ├── rsg-cfo/agent.json
│   │   ├── data-entry-assistant/agent.json
│   │   └── shepherding-assistant/agent.json
│   ├── skills/
│   │   └── rsg-intel-pack.md
│   └── references/
│       └── edge-cases.md
└── workspace/                    # → /home/node/.openclaw/workspace/
    ├── IDENTITY.md
    ├── USER.md
    ├── SOUL.md
    ├── AGENTS.md
    ├── TOOLS.md
    └── HEARTBEAT.md
```

---

## Issues Found & Fixed During Build

| Issue | Root Cause | Fix |
|---|---|---|
| hosting platform write rate alert (614 ops/s) | No Anthropic API key → retry loop every 30 min | Set `ANTHROPIC_API_KEY` in .env |
| Ollama unreachable from server | Build doc had IP `100.82.142.4` (typo) | Corrected to `100.82.142.43` |
| Config validation error ("Unrecognized key: main") | `agents` block not valid in openclaw.json | Removed — agents configured via directory structure |
| Version mismatch warning | `meta.lastTouchedVersion: 2026.3.26` > installed `2026.3.25` | Set to `2026.3.25` |
| Slack tokens — app token rotated | Original token from Obsidian was stale | User provided fresh `xapp-1-...` token |
| BOOTSTRAP.md still present | Onboarding never completed on fresh install | Filled IDENTITY.md + USER.md, deleted BOOTSTRAP.md |

---

## Known Limitations / Next Steps

1. **Agent routing not yet wired** — Personas are deployed as configs but OpenClaw's `main` agent handles all traffic. Channel-based routing to specific personas may require OpenClaw's multi-agent routing feature or custom skill logic.
2. **Memory/RAG not tested** — mxbai-embed on Mac Mini is reachable but semantic memory hasn't been exercised yet.
3. **Shepherding Assistant (DeepSeek-R1)** — Uses local Ollama model. Verify response quality and latency through Tailscale bridge.
4. **Heartbeat tasks** — HEARTBEAT.md is empty. Can be configured for periodic checks (email, calendar, renewal pipeline).
5. **Security audit** — Gateway logs: `dangerouslyDisableDeviceAuth=true`. Run `openclaw security audit` when ready to tighten.
6. **Supabase MCP** — Configured but not yet tested end-to-end. First query will trigger `npx` install of the MCP server package.

---

## Quick Reference Commands

```bash
# SSH into the instance
ssh root@{{OPENCLAW_HOST}}

# Check gateway health
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep openclaw

# View live logs
docker logs -f app-openclaw-gateway-1

# Restart gateway
cd /opt/app && docker compose restart openclaw-gateway

# Full stop/start (clears state)
cd /opt/app && docker compose down openclaw-gateway && docker compose up -d openclaw-gateway

# Edit config
nano /opt/app/config/openclaw.json

# Edit an agent
nano /opt/app/config/agents/<agent-id>/agent.json

# Check Tailscale mesh
tailscale status

# Test Ollama connectivity
curl http://100.82.142.43:11434/api/version
```
