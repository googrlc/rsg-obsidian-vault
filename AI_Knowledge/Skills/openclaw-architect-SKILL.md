# OpenClaw Architect — SKILL.md (Updated 2026-03-31)

The purpose of this skill is to help Lamar build, modify, and maintain RSG's OpenClaw agent
architecture with precision — asking the right clarifying questions before writing any
markdown, and keeping the Obsidian vault + GitHub repo clean and in sync as the single
source of truth.

---

## RSG Identity & Soul Context

**Who Lamar is:** Faith-driven leader, Firefighter-Architect, ADHD operator running a
2-person agency with million-dollar vision. Everything serves two missions:
1. Generate revenue (new business, renewals, proposals, prospecting)
2. Free up Lamar's selling time (help Gretchen work smarter, build systems that prevent fires)

**Current agency state (2026-03-31):**
- Active Premium: ~$385K | Policies: 104 | Clients: 81
- Retention Rate: 54.92% → Target: 75%+ ⚠️ CRITICAL — this is the #1 problem
- Gate 1: $425K premium / 60% retention (next milestone)

**Revenue Alarm:** Before recommending any new technical work, ask:
"Does this make Lamar money, protect existing revenue, or free up Gretchen?"
If no to all three — flag it as a distraction.

---

## RSG OpenClaw Context

**OpenClaw host:** Elestio instance
**Live workspace:** `/opt/app/workspace/` (HEARTBEAT.md, SOUL.md, AGENTS.md, IDENTITY.md, TOOLS.md, USER.md, MEMORY.md)
**Live skills path:** `/opt/app/config/skills/` (flat .md files — OpenClaw reads from here)
**Secondary skills path:** `/home/node/.openclaw/skills/[name]/SKILL.md` (backup/reference)
**SSH:** `ssh root@openclaw-larau-u69864.vm.elestio.app` (ed25519 keys via 1Password SSH agent)
**Vault path:** `/Users/lamarcoates/Documents/GitHub/rsg-obsidian-vault`
**GitHub repo:** `github.com/googrlc/rsg-obsidian-vault`
**Skills in vault:** `AI_Knowledge/Skills/` (canonical documentation)
**Workflow Registry:** `_System/RSG Workflow Registry.md` (agent count, status, IDs)
**Architecture doc:** `_System/RSG-Architecture-2026.md` (canonical system doc)

**CRITICAL — Two HEARTBEAT.md locations (both must be updated):**
1. `/opt/app/workspace/HEARTBEAT.md` — the live file OpenClaw reads
2. `AI_Knowledge/Skills/HEARTBEAT.md` — the vault version (commit to GitHub)

**Key Slack channels:**
- `#the-boss` (C0ANQUENX4P) — boss-level summaries, revenue alerts, Lamar's command center
- `#gretchen-tasks` — personal lines service tasks (plain English, NO jargon)
- `#service-brief` (C0AP2MML9L6) — renewal alerts, operations digest
- `#systems-check` (C0AFHN83ZE3) — system health, errors, workflow failures
- `#growth-finance` (C0AP89NDTHA) — revenue reporting, commission tracking
- `#the-morning-commander` (C0ANYMH87HR) — daily briefing
- `#lamar-alerts` — commercial client/policy alerts requiring Lamar's attention
- `#agency-ops` (C0AP4MFKH7U) — focus/ADHD accountability
- `#the-task-list` (C0AH4KJAYTU) — task digests
- `#growth-finance` (C0AP89NDTHA) — revenue, commission

**LLM routing:**
- Anthropic (Claude): Revenue-critical only — Revenue Sheriff, Renewal Watchdog, Deal Coach, Book Health Monitor, Retention Risk Scout
- Gemini (`google/gemini-2.0-flash-001`): All other agents — default for new agents

---

## Current Agent Roster (18 agents as of 2026-03-31)

| Agent | Trigger | LLM | Output |
|-------|---------|-----|--------|
| Revenue Sheriff | Daily schedule | Anthropic | #the-boss |
| Renewal Watchdog | Daily schedule | Anthropic | #lamar-alerts, #gretchen-tasks |
| Deal Coach | On-demand | Anthropic | #the-boss |
| Morning Commander | Weekdays 7am | Gemini | #the-morning-commander |
| Personal Assistant | On-demand | Gemini | #the-boss |
| RSG CFO | On-demand + Friday 4pm | Gemini | #growth-finance |
| Operations Foreman | On-demand | Gemini | #service-brief |
| Data Entry Assistant | On-demand | Gemini | #gretchen-tasks |
| Automation Triage Nurse | On-demand | Gemini | #systems-check |
| Focus Guard | On-demand | Gemini | #agency-ops |
| Brain Dump Butler | On-demand | Gemini | #the-task-list |
| Task Finisher | On-demand | Gemini | #the-task-list |
| Reflection Anchor | On-demand | Gemini | #personal |
| Message Prep Scribe | On-demand | Gemini | #the-study |
| Shepherding Assistant | On-demand | DeepSeek-R1 | #the-study |
| Book Health Monitor | Monday 10am ET + on-demand | Anthropic | #the-boss |
| Retention Risk Scout | Wednesday 9am ET + on-demand | Anthropic | #the-boss + #service-brief |
| Gretchen Daily Queue | Weekdays 8:30am ET + on-demand | Gemini | #gretchen-tasks |

---

## Deployed Skills (19 skills as of 2026-03-31)

crm-manager, nowcerts-skill, prospect-researcher, renewal-prep, carrier-appetite,
outreach-templates, commission-reconciliation, linkedin-prospecting, email-triage,
vin-lookup, property-lookup, medication-formulary, medicare-plan-advisor,
google-calendar, prospect-intelligence-pack, book-health-monitor,
retention-risk-scout, gretchen-daily-queue, rsg-intel-pack

---

## Workflow

### Step 1 — Revenue Test First

Before writing a single line of YAML, ask:
> "Does this make Lamar money, protect existing revenue, or free up Gretchen?"

If no → flag as distraction and stop. If yes → proceed.

### Step 2 — Clarify Before Writing

**Never write or commit markdown until clarifying questions are answered.**

#### If creating/updating a SKILL:
1. **Name:** Short identifier (e.g., `retention-risk-scout`)
2. **Trigger:** Exact phrases that should fire this skill
3. **Purpose:** One sentence
4. **Inputs:** What data does it need?
5. **Output:** What does it produce?
6. **Routing:** Slack channel(s)?
7. **LLM:** Gemini (default) or Anthropic (revenue-critical only)?
8. **Gretchen-facing?** If yes — plain English mandatory, zero jargon
9. **Dependencies:** NowCerts, EspoCRM, Supabase, external APIs?

#### If creating/updating an AGENT:
1. **Agent name** in HEARTBEAT.md
2. **Role** in one sentence
3. **Trigger:** Schedule, event, or on-demand?
4. **Skills used**
5. **Slack output:** Which channel(s)? @mentions?
6. **LLM:** Gemini or Anthropic?

---

### Step 3 — Draft the Skill File

Skill files live at `/opt/app/config/skills/skill-name.md` (flat, no subdirectory).

```yaml
---
name: skill-name
description: >
  One-paragraph description. Include WHEN to trigger (specific phrases).
  Mention if Gretchen-facing. Note key integrations.
  Be "pushy" — err toward triggering when in doubt.
---
```

Body: Step-by-step with ALL API calls inline (full URLs, auth headers, request bodies).
**Do NOT reference external skill files in the body.**

---

### Step 4 — Draft the HEARTBEAT Block

HEARTBEAT trigger blocks must be **100% self-contained**.
Never say "Read skill-name.md" — the agent reads the HEARTBEAT and executes directly.

```
## TRIGGER: "phrase 1" / "phrase 2" / "phrase 3"
**Skill:** skill-name.md
**Output channel:** #channel-name (CHANNEL_ID)
**Schedule:** [if applicable]

Confirm start: "emoji Agent running → action incoming"

Step 1 — [Complete self-contained instruction with full API call inline]
Step 2 — ...

Uses [Gemini/Anthropic]. [Gretchen-facing: plain English only / Boss-level only]
```

---

### Step 5 — Deploy to OpenClaw Server

```bash
# Deploy skill file
scp skill-name.md root@openclaw-larau-u69864.vm.elestio.app:/opt/app/config/skills/skill-name.md

# Backup to node skills dir
ssh root@openclaw-larau-u69864.vm.elestio.app \
  "mkdir -p /home/node/.openclaw/skills/skill-name && \
   cp /opt/app/config/skills/skill-name.md /home/node/.openclaw/skills/skill-name/SKILL.md"

# Append HEARTBEAT block to live workspace
ssh root@openclaw-larau-u69864.vm.elestio.app \
  "cat >> /opt/app/workspace/HEARTBEAT.md << 'EOF'
[HEARTBEAT block]
EOF"

# Verify
ssh root@openclaw-larau-u69864.vm.elestio.app \
  "ls /opt/app/config/skills/skill-name.md && grep -c 'trigger phrase' /opt/app/workspace/HEARTBEAT.md"
```

---

### Step 6 — Vault Sync & Git Commit

```bash
# Copy skill doc to vault
cp skill-name.md /Users/lamarcoates/Documents/GitHub/rsg-obsidian-vault/AI_Knowledge/Skills/

# Append to vault HEARTBEAT
cat >> /Users/lamarcoates/Documents/GitHub/rsg-obsidian-vault/AI_Knowledge/Skills/HEARTBEAT.md << 'EOF'
[HEARTBEAT block]
EOF

# Update Workflow Registry (increment count, add row to agent table)

cd /Users/lamarcoates/Documents/GitHub/rsg-obsidian-vault
git stash   # if uncommitted changes exist
git pull --rebase origin main
git stash pop
git add AI_Knowledge/Skills/skill-name.md AI_Knowledge/Skills/HEARTBEAT.md "_System/RSG Workflow Registry.md"
git commit -m "feat: add [Agent Name] agent

- [what it does]
- [trigger + schedule]
- [output channels]"
git push origin main
```

---

### Step 7 — Test in Slack

Send trigger phrase to `#the-boss`. Expect:
1. Confirmation message within ~5 sec: "emoji Agent running → action incoming"
2. Full output in designated channel within 15–30 sec

If agent errors → check `#systems-check`, verify HEARTBEAT block is self-contained.

---

## Quality Checklist

Before finalizing any OpenClaw change:

- [ ] Revenue test passed (makes money / protects revenue / frees Gretchen)
- [ ] Skill deployed to `/opt/app/config/skills/`
- [ ] HEARTBEAT block is 100% self-contained (no "Read skill-file" lines)
- [ ] Both HEARTBEAT.md files updated (live server + vault)
- [ ] Workflow Registry agent count updated
- [ ] Vault committed and pushed to GitHub
- [ ] Slack routing correct
- [ ] LLM selection intentional (Anthropic = revenue-critical; Gemini = everything else)
- [ ] Gretchen-facing outputs: plain English, no jargon, no field names, action verbs
- [ ] Trigger tested in #the-boss

---

## Common Fixes

### Skill not triggering
1. Confirm trigger phrase in `/opt/app/workspace/HEARTBEAT.md`
2. Confirm skill exists at `/opt/app/config/skills/skill-name.md`
3. Remove any "Read skill-name.md" lines from HEARTBEAT block
4. Re-test in #the-boss

### Agent errors on run
1. Check `#systems-check` for error details
2. Verify all API endpoints and auth are inline in HEARTBEAT block
3. NowCerts token expires ~60 min — always mint fresh per run
4. EspoCRM header: `X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e`

### Vault merge conflicts
```bash
cd /Users/lamarcoates/Documents/GitHub/rsg-obsidian-vault
git stash && git pull --rebase origin main && git stash pop
# Resolve: keep upstream, append new content at end of file
git add [conflicted file] && git commit -m "fix: resolve merge conflict" && git push
```

---

## Credentials Reference (inline use in HEARTBEAT only — never commit to vault)

NowCerts token: POST https://api.nowcerts.com/api/token
  Body: grant_type=password&username=lamar@risk-solutionsgroup.com&password=dcp1vwv*RCF9fpz*dfh&client_id=ngAuthApp
  Agency ID: 09d93486-1536-48d7-9096-59f1f62b6f51

EspoCRM: X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
  Base: https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1

Supabase project: wibscqhkvpijzqbhjphg (us-east-1)
  Base: https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1
  Keys: read from agent.json in OpenClaw workspace
