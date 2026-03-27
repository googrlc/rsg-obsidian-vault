
> **Vision:** A unified AI-powered system where every domain of Lamar's life — insurance agency, ministry, finances, and personal calendar — has a dedicated intelligent agent, all connected through a shared knowledge layer.

---

## 🗺️ System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE ENGINE (Layer 0)                   │
│         Supabase Vector DB · Google Workspace · Notion          │
└────────────────────────────┬────────────────────────────────────┘
                             │ feeds all agents
       ┌─────────────────────┼──────────────────────┐
       │                     │                      │
┌──────▼──────┐    ┌─────────▼────────┐   ┌────────▼────────┐
│   RSG AGENCY│    │  PERSONAL OS     │   │  MINISTRY OS    │
│  Agents     │    │  Agents          │   │  Agents         │
└─────────────┘    └──────────────────┘   └─────────────────┘
```

---

## 🤖 Agent Roster (Full Vision)

### RSG Insurance Agency

|Agent|Purpose|Status|
|---|---|---|
|🔍 Prospect Intelligence|Pre-call research → Notion|✅ Built (Manus skill)|
|💰 Commission Agent|Commission calc, split logic, dopamine hits|🟡 Partial (n8n broken)|
|📋 Carrier Appetite Agent|Carrier fit + underwriting guidance|🔴 Not built|
|📚 LOB Education Agent|Line of business Q&A for Gretchen + Lamar|🔴 Not built|
|📣 Marketing Agent|Content, LinkedIn, email sequences|🔴 Not built|
|📊 Financial Agent|Revenue tracking, KPIs, executive dashboard|🔴 Not built|
|⚙️ Operations Agent|Gretchen's service queue, task routing|🟡 Partial (Notion only)|

### Personal OS

|Agent|Purpose|Status|
|---|---|---|
|📅 Calendar Agent|Query next appointments, context-aware prep|🔴 Not built|
|⛪ Ministry Agent|Group overseer tasks, education oversight|🔴 Not built|
|🩺 First Aid Assembly Agent|Assembly oversight reminders + tracking|🔴 Not built|

---

## 🏗️ Build Phases

---

### Phase 0 — Foundation: Knowledge Engine

> **Everything depends on this.** No agents work well without shared, searchable institutional memory.

**Goal:** Build the layer that stores carrier guidelines, underwriting rules, LOB knowledge, ministry docs, and personal context so every agent can retrieve what it needs.

**Components:**

- [ ] Provision Supabase project (already identified as preferred vector DB)
- [ ] Create `knowledge_chunks` table (content, embedding, source, domain, tags, created_at)
- [ ] Create `documents` table (title, source_url, domain, doc_type, last_ingested)
- [ ] Connect Google Workspace → ingestion pipeline (n8n webhook on file add)
- [ ] Build chunker/embedder node in n8n (OpenAI embeddings → Supabase pgvector insert)
- [ ] Build classifier node (tag by domain: agency | ministry | personal)
- [ ] Build semantic search function in Supabase (`match_chunks` RPC)
- [ ] Test retrieval: query "commercial auto appetite Progressive" → returns correct chunk
- [ ] Seed initial corpus: carrier appetite PDFs, underwriting guides, LOB fact sheets

**Dependencies:** Supabase project, OpenAI API key, Google Drive OAuth in n8n

**Obsidian Link:** `[[Knowledge Engine Architecture]]`

---

### Phase 1 — Sales Intelligence Flow

> **Priority 2.** Carrier Appetite Agent + LOB Education Agent plugged into Slack.

**Goal:** Lamar or Gretchen types a question in Slack and gets a market recommendation or coverage explanation back within 60 seconds.

**Components:**

#### 1A — Carrier Appetite Agent

- [ ] Load carrier appetite data into Supabase (PDF ingestion via Phase 0 pipeline)
- [ ] Build n8n workflow: Slack slash command `/carrier [account type]` → semantic search → format response
- [ ] Include: carrier name, appetite fit, key exclusions, underwriting notes
- [ ] Route back to Slack thread (not DM) so Gretchen can see it too
- [ ] Test: `/carrier non-owned auto Dallas TX 5 trucks` → returns Progressive, Canal, next-best alternatives

#### 1B — LOB Education Agent

- [ ] Curate LOB fact sheets: Commercial Auto, GL, Workers Comp, BOP, Umbrella, Life, Medicare
- [ ] Load into Supabase under domain: `lob-education`
- [ ] Build Slack command `/lob [topic]` → retrieve + summarize for Gretchen's use
- [ ] Include: coverage basics, exclusions, common client objections, cross-sell triggers
- [ ] Test: `/lob workers comp audit` → returns clean explanation Gretchen can send to a client

#### 1C — Fix Prospect Intelligence Integration

- [ ] Confirm Manus `prospect-intelligence-pack` skill still writing to Notion Leads Pipeline
- [ ] Add Slack notification when intel pack completes (ping Lamar in #sales)
- [ ] Test end-to-end: new lead added → Intel Pack runs → Notion updated → Slack pinged

**Dependencies:** Phase 0 complete, Slack app with slash commands, n8n Slack node

**Obsidian Link:** `[[Sales Intelligence Flow]]`

---

### Phase 2 — Revenue Operations

> **Priority 3.** Fix what's broken. Then upgrade to a full commission + financial agent.

**Goal:** Every bound policy automatically triggers commission logging, revenue tracking, and executive KPI updates — with zero manual entry.

**Components:**

#### 2A — Fix Broken Commission Automation (URGENT — do this first)

- [ ] Fix won-stage string mismatch: update all FUNCTIONS.md strings to emoji-prefixed values (e.g. `✅ Won - Bound`)
- [ ] Fix 5 empty Set LOB nodes in n8n JSON
- [ ] Fix 4 aggregate sync filter keys with erroneous `=` prefix
- [ ] Add Life Insurance Pipeline to FUNCTIONS.md
- [ ] Fix bidirectional sync bug (hardcode exact select strings to stop accumulating duplicate options)
- [ ] Test: move a test deal to `✅ Won - Bound` → verify commission record created, Slack notified, Gretchen task created

#### 2B — Commission Agent (Upgrade)

- [ ] Move commission rules from n8n hardcode → Supabase `commission_rules` table
- [ ] Build commission calculator function (premium × commission rate × split logic)
- [ ] Build producer math: Lamar vs. referral split, override tiers
- [ ] Add commission ledger view in Notion or Softr dashboard
- [ ] Slack `/commission [client] [premium] [carrier]` → returns estimated commission

#### 2C — Financial Agent (Phase 2 MVP)

- [ ] Build monthly revenue summary (Notion aggregate → n8n → Slack report every 1st of month)
- [ ] Track: new premium written, renewals retained, lost accounts, commission YTD
- [ ] Add close ratio tracking (Leads entered vs. Won)
- [ ] Build simple executive dashboard in Softr (premium, commission, close ratio, retention rate)

**Dependencies:** Phase 0 helpful but not required for 2A fixes; Supabase needed for 2B

**Obsidian Link:** `[[Revenue Operations Architecture]]`

---

### Phase 3 — Task & Service Automation

> **Priority 4.** Gretchen's operational queue — structured, trackable, auditable.

**Goal:** Every service request — COI, endorsement, cancellation, billing question — enters through a consistent intake point, gets routed, validated, and lands in Gretchen's queue as a clean task.

**Components:**

#### 3A — Multi-Source Intake

- [ ] Slack command `/service [request type] [client name]` → creates Notion task
- [ ] Voice Capture Inbox routing: voice notes → transcribed → classified → task created
- [ ] Email intake (forwarded to n8n webhook → parsed → Notion task)
- [ ] Confirm Voice Capture Inbox (Notion ID: `9efbc24bbff847699c30ad156bd7bcbc`) is live

#### 3B — Service Request Agent

- [ ] Build n8n classifier: identify request type (COI | endorsement | cancellation | billing | other)
- [ ] Validate client against NowCerts via API (verify policy exists, status active)
- [ ] Create structured Notion task with: client name, policy #, request type, priority, due date
- [ ] Assign to Gretchen by default; escalate to Lamar if commercial or >$5K exposure

#### 3C — Audit Trail

- [ ] Add status tracking to service tasks: Open → In Progress → Pending Carrier → Closed
- [ ] Build weekly service queue summary → Slack to Lamar every Monday 8am
- [ ] Add SLA tracking: flag tasks open >48h

**Dependencies:** Phase 0 for validation lookups; NowCerts API working

**Obsidian Link:** `[[Task Service Automation]]`

---

### Phase 4 — Personal OS

> **Priority 5.** Calendar context, ministry oversight, assembly coordination.

**Goal:** Lamar has one place to ask questions about his week, his ministry roles, and his assembly responsibilities — and gets back context-aware, structured answers.

**Components:**

#### 4A — Calendar Agent

- [ ] Connect Google Calendar → n8n (OAuth2)
- [ ] Build `/next` command in Slack: returns next 3 appointments with context
- [ ] Build morning briefing v2: 8am Slack message with today's appointments + top 3 priorities
- [ ] For sales appointments: auto-trigger prospect intel check before the call
- [ ] Test: "What do I have tomorrow?" → returns formatted schedule

#### 4B — Ministry Agent

- [ ] Define domains: Group Overseer, Ministry Education Overseer, First Aid Assembly Overseer
- [ ] Build knowledge base for each role (responsibilities, recurring tasks, key contacts)
- [ ] Load ministry calendar events into agent context
- [ ] Build `/ministry` Slack command → returns upcoming responsibilities by role
- [ ] Add recurring task reminders (e.g., weekly education review, monthly assembly check-in)

#### 4C — First Aid Assembly Agent

- [ ] Document assembly oversight responsibilities
- [ ] Build reminder schedule (meeting prep, follow-ups, attendance tracking)
- [ ] Link to calendar agent for upcoming assembly dates
- [ ] Slack notification 24h before assembly responsibilities

**Dependencies:** Google Calendar OAuth2 in n8n, Phase 0 for knowledge storage

**Obsidian Link:** `[[Personal OS Architecture]]`

---

### Phase 5 — Marketing Agent

> **Priority 6.** Content, LinkedIn positioning, and email sequence optimization.

**Goal:** RSG has a consistent content presence that positions Lamar as a commercial insurance expert — without requiring Lamar to write everything from scratch.

**Components:**

- [ ] Define content pillars: fleet risk, contractor coverage, Medicare planning, business insurance myth-busting
- [ ] Build content brief generator: Slack `/content [topic]` → returns LinkedIn post draft
- [ ] Connect to email sequence system (Notion Email Templates DB already built)
- [ ] Build A/B tracking for email sequences (open rate, response rate)
- [ ] Add Manus `{{MANUS_AI_PERSONALIZATION}}` auto-fill for Day 30 renewal emails
- [ ] Monthly content calendar auto-generated in Notion

**Dependencies:** Notion Email Templates DB (already exists), Manus API credentials

**Obsidian Link:** `[[Marketing Agent]]`

---

## 📊 Build Sequence Summary

```
MONTH 1
├── Phase 0: Knowledge Engine (Supabase foundation)
└── Phase 2A: Fix broken commission automation (CRITICAL — revenue is leaking)

MONTH 2
├── Phase 1A: Carrier Appetite Agent
├── Phase 1B: LOB Education Agent
└── Phase 2B: Commission Agent upgrade

MONTH 3
├── Phase 1C: Prospect Intelligence fixes
├── Phase 2C: Financial Agent MVP
└── Phase 3A–B: Service Automation

MONTH 4
├── Phase 3C: Audit Trail
└── Phase 4A–B: Personal Calendar + Ministry Agent

MONTH 5+
├── Phase 4C: First Aid Assembly Agent
└── Phase 5: Marketing Agent
```

---

## 🚧 Known Blockers (Resolve Before Building)

|Blocker|Affects|Resolution|
|---|---|---|
|Gmail OAuth2 credentials not set|Renewal email sequences|Add in n8n credentials|
|Notion Header Auth credential ID missing|Multiple n8n workflows|Document and configure|
|Manus API env vars not set|Day 30 personalization|Add to Manus Secrets Vault|
|8 broken n8n automations|Revenue Ops, Onboarding|Fix before building new|
|Won-stage string mismatch|Commission automation|Fix FUNCTIONS.md + n8n JSON|
|NowCerts token expiry (~60 min)|All NowCerts API calls|Fresh token mint per run (already documented)|

---

## 🔑 Key Credentials & IDs Reference

|Item|Location|
|---|---|
|Voice Capture Inbox DB|Notion: `9efbc24bbff847699c30ad156bd7bcbc`|
|NowCerts credentials|Manus Secrets Vault|
|Supabase project|`fekxkldrucwiorxriohx`|
|LOB Template Registry|Notion (documented in pipeline architecture)|

---

## 📁 Related Notes

- `[[RSG Supporting Architecture Diagrams]]`
- `[[RSG New Business Pipeline SOP]]`
- `[[FUNCTIONS.md — Commission & Onboarding Automation]]`
- `[[n8n Workflow Registry]]`
- `[[Knowledge Engine Architecture]]`
- `[[Manus Skill Registry]]`

---

_Last updated: March 2026 | Owner: Lamar | Status: Planning_