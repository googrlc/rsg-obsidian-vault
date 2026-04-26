# OpenClaw Google Calendar Integration
**Claude Code Instructions**
**Date:** March 2026
**Server:** {{OPENCLAW_HOST}}
**n8n:** {{N8N_HOST}}

---

## ARCHITECTURE

Two-mode calendar access for all OpenClaw agents:

```
Mode 1 — Morning Sync (scheduled)
Google Calendar → n8n (6:30am daily) → Supabase calendar_events table
Morning Commander reads Supabase at 7am brief

Mode 2 — On-Demand (webhook)
OpenClaw agent → POST n8n webhook → n8n queries Google Calendar → returns JSON → agent responds
Trigger phrase: "what's on my calendar" / "do I have anything today" / "schedule for [date]"
```

Google OAuth credential already exists in n8n — no new auth needed.

---

## PART 1 — SUPABASE TABLE

### Step 1 — Create calendar_events table

Run in Supabase SQL Editor (project: wibscqhkvpijzqbhjphg):

```sql
CREATE TABLE IF NOT EXISTS calendar_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  google_event_id text UNIQUE,
  title text NOT NULL,
  description text,
  location text,
  start_at timestamptz NOT NULL,
  end_at timestamptz,
  all_day boolean DEFAULT false,
  attendees text[],
  meeting_link text,
  calendar_name text DEFAULT 'primary',
  domain text CHECK (domain IN ('rsg', 'ministry', 'personal', 'other')) DEFAULT 'other',
  espocrm_account_id text,
  espocrm_account_name text,
  needs_prep boolean DEFAULT false,
  synced_at timestamptz DEFAULT now(),
  event_date date GENERATED ALWAYS AS (start_at::date) STORED
);

CREATE INDEX IF NOT EXISTS calendar_events_start_idx ON calendar_events (start_at);
CREATE INDEX IF NOT EXISTS calendar_events_date_idx ON calendar_events (event_date);
CREATE INDEX IF NOT EXISTS calendar_events_google_id_idx ON calendar_events (google_event_id);
```

Confirm table created before proceeding.

---

## PART 2 — N8N WORKFLOW A: MORNING CALENDAR SYNC

### Step 2 — Create n8n workflow via API

Pull n8n API key from 1Password, then create the workflow:

```bash
N8N_KEY=$(op read 'op://RSG/n8n API Key/credential')

curl -s -X POST "https://{{N8N_HOST}}/api/v1/workflows" \
  -H "X-N8N-API-KEY: $N8N_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "RSG — Google Calendar Morning Sync",
    "active": false,
    "nodes": [
      {
        "id": "cal-trigger",
        "name": "Schedule — 6:30am Daily",
        "type": "n8n-nodes-base.scheduleTrigger",
        "typeVersion": 1.2,
        "position": [0, 0],
        "parameters": {
          "rule": {
            "interval": [{ "field": "cronExpression", "expression": "30 6 * * 1-5" }]
          }
        }
      },
      {
        "id": "cal-fetch",
        "name": "Get Google Calendar Events",
        "type": "n8n-nodes-base.googleCalendar",
        "typeVersion": 1,
        "position": [220, 0],
        "parameters": {
          "operation": "getAll",
          "calendar": "primary",
          "returnAll": false,
          "limit": 50,
          "options": {
            "timeMin": "={{ $now.startOf(\"day\").toISO() }}",
            "timeMax": "={{ $now.plus({days: 2}).endOf(\"day\").toISO() }}",
            "singleEvents": true,
            "orderBy": "startTime"
          }
        },
        "credentials": { "googleCalendarOAuth2Api": { "id": "REPLACE_WITH_GOOGLE_CREDENTIAL_ID", "name": "Google Calendar" } }
      },
      {
        "id": "cal-transform",
        "name": "Transform Events",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [440, 0],
        "parameters": {
          "jsCode": "const events = $input.all();\nconst rows = events.map(e => {\n  const ev = e.json;\n  const start = ev.start?.dateTime || ev.start?.date;\n  const end = ev.end?.dateTime || ev.end?.date;\n  const allDay = !ev.start?.dateTime;\n  const attendees = (ev.attendees || []).map(a => a.email).filter(Boolean);\n  const meetingLink = ev.hangoutLink || ev.conferenceData?.entryPoints?.[0]?.uri || null;\n  \n  // Auto-classify domain\n  const title = (ev.summary || '').toLowerCase();\n  let domain = 'other';\n  if (title.includes('church') || title.includes('assembly') || title.includes('ministry') || title.includes('sermon') || title.includes('speaking')) domain = 'ministry';\n  else if (title.includes('rsg') || title.includes('client') || title.includes('prospect') || title.includes('renewal') || title.includes('quote') || title.includes('insurance')) domain = 'rsg';\n  \n  return {\n    google_event_id: ev.id,\n    title: ev.summary || 'No Title',\n    description: ev.description || null,\n    location: ev.location || null,\n    start_at: start,\n    end_at: end,\n    all_day: allDay,\n    attendees: attendees.length ? attendees : null,\n    meeting_link: meetingLink,\n    calendar_name: 'primary',\n    domain: domain,\n    needs_prep: domain === 'rsg',\n    synced_at: new Date().toISOString()\n  };\n});\n\nreturn rows.map(r => ({ json: r }));"
        }
      },
      {
        "id": "cal-upsert",
        "name": "Upsert to Supabase",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [660, 0],
        "parameters": {
          "method": "POST",
          "url": "https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/calendar_events",
          "sendHeaders": true,
          "headerParameters": { "parameters": [
            { "name": "apikey", "value": "={{ $env.SUPABASE_SERVICE_ROLE_KEY }}" },
            { "name": "Authorization", "value": "=Bearer {{ $env.SUPABASE_SERVICE_ROLE_KEY }}" },
            { "name": "Content-Type", "value": "application/json" },
            { "name": "Prefer", "value": "resolution=merge-duplicates,return=minimal" }
          ]},
          "sendBody": true,
          "specifyBody": "json",
          "jsonBody": "={{ JSON.stringify($json) }}",
          "options": {}
        }
      },
      {
        "id": "cal-slack",
        "name": "Slack: Sync Complete",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [880, 0],
        "parameters": {
          "method": "POST",
          "url": "={{ $env.SLACK_WEBHOOK_URL }}",
          "sendBody": true,
          "specifyBody": "json",
          "jsonBody": "={{ JSON.stringify({ channel: 'C0AFHN83ZE3', text: '📅 Calendar synced — ' + $input.all().length + ' events loaded for today/tomorrow' }) }}",
          "options": {}
        }
      }
    ],
    "connections": {
      "Schedule — 6:30am Daily": { "main": [[{ "node": "Get Google Calendar Events", "type": "main", "index": 0 }]] },
      "Get Google Calendar Events": { "main": [[{ "node": "Transform Events", "type": "main", "index": 0 }]] },
      "Transform Events": { "main": [[{ "node": "Upsert to Supabase", "type": "main", "index": 0 }]] },
      "Upsert to Supabase": { "main": [[{ "node": "Slack: Sync Complete", "type": "main", "index": 0 }]] }
    }
  }' | python3 -c "import json,sys; r=json.load(sys.stdin); print('Created WF ID:', r.get('id'), '| Name:', r.get('name'))"
```

**IMPORTANT:** Before activating, update the Google Calendar node:
1. Find your Google Calendar credential ID in n8n (Settings → Credentials)
2. Replace `REPLACE_WITH_GOOGLE_CREDENTIAL_ID` with the actual ID
3. Also add `SUPABASE_SERVICE_ROLE_KEY` to n8n environment variables if not already set

---

## PART 3 — N8N WORKFLOW B: ON-DEMAND WEBHOOK

### Step 3 — Create on-demand calendar webhook workflow

```bash
N8N_KEY=$(op read 'op://RSG/n8n API Key/credential')

curl -s -X POST "https://{{N8N_HOST}}/api/v1/workflows" \
  -H "X-N8N-API-KEY: $N8N_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "RSG — Google Calendar On-Demand Query",
    "active": false,
    "nodes": [
      {
        "id": "webhook-in",
        "name": "Webhook",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 2,
        "position": [0, 0],
        "parameters": {
          "path": "rsg-calendar-query",
          "responseMode": "responseNode",
          "options": {}
        }
      },
      {
        "id": "parse-request",
        "name": "Parse Request",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [220, 0],
        "parameters": {
          "jsCode": "const body = $input.first().json.body || {};\nconst query = body.query || 'today';\nconst now = new Date();\n\nlet timeMin, timeMax, label;\n\nif (query === 'today' || query === 'now') {\n  timeMin = new Date(now.getFullYear(), now.getMonth(), now.getDate()).toISOString();\n  timeMax = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59).toISOString();\n  label = 'today';\n} else if (query === 'tomorrow') {\n  const tom = new Date(now); tom.setDate(tom.getDate() + 1);\n  timeMin = new Date(tom.getFullYear(), tom.getMonth(), tom.getDate()).toISOString();\n  timeMax = new Date(tom.getFullYear(), tom.getMonth(), tom.getDate(), 23, 59, 59).toISOString();\n  label = 'tomorrow';\n} else if (query === 'week') {\n  timeMin = now.toISOString();\n  const weekEnd = new Date(now); weekEnd.setDate(weekEnd.getDate() + 7);\n  timeMax = weekEnd.toISOString();\n  label = 'next 7 days';\n} else {\n  // Try to parse a date string\n  const parsed = new Date(query);\n  if (!isNaN(parsed)) {\n    timeMin = new Date(parsed.getFullYear(), parsed.getMonth(), parsed.getDate()).toISOString();\n    timeMax = new Date(parsed.getFullYear(), parsed.getMonth(), parsed.getDate(), 23, 59, 59).toISOString();\n    label = query;\n  } else {\n    timeMin = new Date(now.getFullYear(), now.getMonth(), now.getDate()).toISOString();\n    timeMax = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59).toISOString();\n    label = 'today';\n  }\n}\n\nreturn [{ json: { timeMin, timeMax, label } }];"
        }
      },
      {
        "id": "gcal-query",
        "name": "Query Google Calendar",
        "type": "n8n-nodes-base.googleCalendar",
        "typeVersion": 1,
        "position": [440, 0],
        "parameters": {
          "operation": "getAll",
          "calendar": "primary",
          "returnAll": false,
          "limit": 20,
          "options": {
            "timeMin": "={{ $json.timeMin }}",
            "timeMax": "={{ $json.timeMax }}",
            "singleEvents": true,
            "orderBy": "startTime"
          }
        },
        "credentials": { "googleCalendarOAuth2Api": { "id": "REPLACE_WITH_GOOGLE_CREDENTIAL_ID", "name": "Google Calendar" } }
      },
      {
        "id": "format-response",
        "name": "Format Response",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [660, 0],
        "parameters": {
          "jsCode": "const events = $input.all();\nconst label = $('Parse Request').first().json.label;\n\nif (!events.length) {\n  return [{ json: { success: true, label, count: 0, events: [], summary: `No events found for ${label}.` } }];\n}\n\nconst formatted = events.map(e => {\n  const ev = e.json;\n  const start = ev.start?.dateTime || ev.start?.date;\n  const end = ev.end?.dateTime || ev.end?.date;\n  const startTime = ev.start?.dateTime ? new Date(start).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', timeZone: 'America/New_York' }) : 'All Day';\n  const endTime = ev.end?.dateTime ? new Date(end).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', timeZone: 'America/New_York' }) : '';\n  const timeStr = endTime ? `${startTime} - ${endTime}` : startTime;\n  return {\n    title: ev.summary || 'No Title',\n    time: timeStr,\n    location: ev.location || null,\n    meeting_link: ev.hangoutLink || null,\n    attendees: (ev.attendees || []).map(a => a.email),\n    description: ev.description || null\n  };\n});\n\nreturn [{ json: { success: true, label, count: formatted.length, events: formatted, summary: `${formatted.length} event(s) for ${label}` } }];"
        }
      },
      {
        "id": "respond",
        "name": "Respond to Webhook",
        "type": "n8n-nodes-base.respondToWebhook",
        "typeVersion": 1,
        "position": [880, 0],
        "parameters": {
          "respondWith": "json",
          "responseBody": "={{ JSON.stringify($json) }}"
        }
      }
    ],
    "connections": {
      "Webhook": { "main": [[{ "node": "Parse Request", "type": "main", "index": 0 }]] },
      "Parse Request": { "main": [[{ "node": "Query Google Calendar", "type": "main", "index": 0 }]] },
      "Query Google Calendar": { "main": [[{ "node": "Format Response", "type": "main", "index": 0 }]] },
      "Format Response": { "main": [[{ "node": "Respond to Webhook", "type": "main", "index": 0 }]] }
    }
  }' | python3 -c "import json,sys; r=json.load(sys.stdin); print('Created WF ID:', r.get('id'), '| Name:', r.get('name'))"
```

Report both workflow IDs back before continuing.

---

## PART 4 — WIRE OPENCLAW TO CALENDAR

### Step 4 — Get Google Calendar credential ID from n8n

```bash
N8N_KEY=$(op read 'op://RSG/n8n API Key/credential')

curl -s "https://{{N8N_HOST}}/api/v1/credentials" \
  -H "X-N8N-API-KEY: $N8N_KEY" \
  | python3 -c "
import json, sys
r = json.load(sys.stdin)
for c in r.get('data', []):
    if 'google' in c.get('type','').lower() or 'google' in c.get('name','').lower():
        print('ID:', c['id'], '| Name:', c['name'], '| Type:', c['type'])
"
```

Use the ID returned to replace `REPLACE_WITH_GOOGLE_CREDENTIAL_ID` in both workflows:

```bash
N8N_KEY=$(op read 'op://RSG/n8n API Key/credential')
GCAL_CRED_ID="PASTE_ID_HERE"

# Update sync workflow (replace WF_SYNC_ID with ID from Step 2)
curl -s "https://{{N8N_HOST}}/api/v1/workflows/WF_SYNC_ID" \
  -H "X-N8N-API-KEY: $N8N_KEY" | python3 -c "
import json, sys
wf = json.load(sys.stdin)
for node in wf['nodes']:
    if node.get('type') == 'n8n-nodes-base.googleCalendar':
        node['credentials']['googleCalendarOAuth2Api']['id'] = '$GCAL_CRED_ID'
        print('Updated credential in:', node['name'])
with open('/tmp/wf_sync_cred.json', 'w') as f: json.dump(wf, f)
"

curl -s -X PUT "https://{{N8N_HOST}}/api/v1/workflows/WF_SYNC_ID" \
  -H "X-N8N-API-KEY: $N8N_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/wf_sync_cred.json \
  | python3 -c "import json,sys; r=json.load(sys.stdin); print('Sync WF updated:', r.get('id'))"

# Repeat for on-demand workflow (replace WF_ONDEMAND_ID)
curl -s "https://{{N8N_HOST}}/api/v1/workflows/WF_ONDEMAND_ID" \
  -H "X-N8N-API-KEY: $N8N_KEY" | python3 -c "
import json, sys
wf = json.load(sys.stdin)
for node in wf['nodes']:
    if node.get('type') == 'n8n-nodes-base.googleCalendar':
        node['credentials']['googleCalendarOAuth2Api']['id'] = '$GCAL_CRED_ID'
        print('Updated credential in:', node['name'])
with open('/tmp/wf_ondemand_cred.json', 'w') as f: json.dump(wf, f)
"

curl -s -X PUT "https://{{N8N_HOST}}/api/v1/workflows/WF_ONDEMAND_ID" \
  -H "X-N8N-API-KEY: $N8N_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/wf_ondemand_cred.json \
  | python3 -c "import json,sys; r=json.load(sys.stdin); print('On-demand WF updated:', r.get('id'))"
```

---

## PART 5 — ADD CALENDAR SKILL TO OPENCLAW

### Step 5 — Create calendar skill file on OpenClaw server

```bash
ssh root@{{OPENCLAW_HOST}} << 'EOF'
cat > /opt/app/config/skills/google-calendar.md << 'SKILL'
# Skill: Google Calendar

## Identity
This skill gives you access to Lamar's Google Calendar via two n8n endpoints.

## Endpoints

### On-Demand Query (real-time)
POST https://{{N8N_HOST}}/webhook/rsg-calendar-query
Body: { "query": "today" | "tomorrow" | "week" | "YYYY-MM-DD" }
Returns: { success, label, count, events[], summary }

### Supabase Read (synced data — faster)
GET https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/calendar_events
Headers: apikey + Authorization: Bearer {SUPABASE_SERVICE_ROLE_KEY}
Filter today: ?event_date=eq.{TODAY}&order=start_at.asc
Filter range: ?start_at=gte.{START}&start_at=lte.{END}&order=start_at.asc

## When to Use Which
- Morning brief → Supabase (already synced at 6:30am, fast)
- "What's on my calendar right now" → webhook (real-time)
- Any query after 6:30am for same day → Supabase is fine
- Future dates beyond tomorrow → webhook

## Response Format
Each event includes: title, time (ET), location, meeting_link, attendees[], description

## Business Logic
- Events with domain='rsg' → flag as needing prep, offer "prep me for [title]"
- Events with meeting_link → include the link in the response
- Back-to-back meetings → flag the gap so Lamar can prepare
- If event title matches an EspoCRM account name → surface the connection

## Trigger Phrases
"what's on my calendar", "do I have anything today", "schedule for [date]",
"what time is my [meeting]", "am I free [time]", "block [time] for [task]"
SKILL

echo "✅ google-calendar.md skill created"
ls /opt/app/config/skills/
EOF
```

### Step 6 — Update HEARTBEAT.md to register the skill

```bash
ssh root@{{OPENCLAW_HOST}} << 'EOF'
# Check current HEARTBEAT.md
cat /opt/app/workspace/HEARTBEAT.md | head -50
EOF
```

Then add `google-calendar` to the skills registry section in HEARTBEAT.md.

### Step 7 — Update Morning Commander to use calendar

```bash
ssh root@{{OPENCLAW_HOST}} << 'EOF'
python3 << 'PYEOF'
import json

path = '/opt/app/config/agents/morning-commander/agent.json'
with open(path) as f:
    agent = json.load(f)

calendar_block = """

## Calendar (Google Calendar via Supabase sync)
At the start of every morning brief, query calendar_events in Supabase for today and tomorrow.
Supabase URL: https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/calendar_events
Filter: event_date=eq.{TODAY_DATE}&order=start_at.asc
Auth: apikey header + Authorization: Bearer {SUPABASE_SERVICE_ROLE_KEY}

Include a "📅 Today's Schedule" section in the brief:
- List all events with time (ET) and location/link
- Flag any event with domain='rsg' as needing prep → "Say 'prep me for [title]' for a pre-call brief"
- If no events: "Calendar is clear today"
- Always show tomorrow's first event as a heads-up"""

system = agent.get('system', '')
if 'calendar' not in system.lower():
    agent['system'] = system + calendar_block
    with open(path, 'w') as f:
        json.dump(agent, f, indent=2)
    print('✅ Morning Commander updated with calendar instructions')
else:
    print('Calendar instructions already present — skipping')
PYEOF
EOF
```

---

## PART 6 — ACTIVATE AND TEST

### Step 8 — Activate both workflows

```bash
N8N_KEY=$(op read 'op://RSG/n8n API Key/credential')

# Activate sync workflow
curl -s -X POST "https://{{N8N_HOST}}/api/v1/workflows/WF_SYNC_ID/activate" \
  -H "X-N8N-API-KEY: $N8N_KEY" \
  | python3 -c "import json,sys; r=json.load(sys.stdin); print('Sync active:', r.get('active'))"

# Activate on-demand webhook
curl -s -X POST "https://{{N8N_HOST}}/api/v1/workflows/WF_ONDEMAND_ID/activate" \
  -H "X-N8N-API-KEY: $N8N_KEY" \
  | python3 -c "import json,sys; r=json.load(sys.stdin); print('On-demand active:', r.get('active'))"
```

### Step 9 — Test on-demand webhook

```bash
curl -s -X POST \
  "https://{{N8N_HOST}}/webhook/rsg-calendar-query" \
  -H "Content-Type: application/json" \
  -d '{"query": "today"}' \
  | python3 -m json.tool
```

Expected: JSON with today's events list.

### Step 10 — Run sync workflow manually to seed Supabase

```bash
N8N_KEY=$(op read 'op://RSG/n8n API Key/credential')

curl -s -X POST \
  "https://{{N8N_HOST}}/api/v1/workflows/WF_SYNC_ID/run" \
  -H "X-N8N-API-KEY: $N8N_KEY" \
  -H "Content-Type: application/json" \
  | python3 -c "import json,sys; r=json.load(sys.stdin); print('Execution ID:', r.get('executionId'))"
```

Then verify Supabase has rows:
```bash
curl -s "https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1/calendar_events?select=title,start_at,domain&order=start_at.asc&limit=10" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  | python3 -m json.tool
```

### Step 11 — Restart OpenClaw and test from Slack

```bash
ssh root@{{OPENCLAW_HOST}} \
  "cd /opt/app && docker compose restart openclaw-gateway && sleep 8 && docker ps | grep openclaw"
```

Then in Slack #the-boss:
```
what's on my calendar today?
```

Expected: Morning Commander queries Supabase and returns today's schedule.

---

## COMPLETION REPORT

Report back:
1. Supabase table created — confirm row count after seed
2. Sync workflow ID + active status
3. On-demand webhook ID + URL
4. Google Calendar credential ID used
5. On-demand test result (Step 9)
6. Supabase seed result (Step 10) — how many events loaded
7. OpenClaw restart status
8. Slack test result
9. Any errors

---

## SUMMARY — WHAT GETS BUILT

| Component | What It Does |
|---|---|
| `calendar_events` Supabase table | Stores synced calendar data |
| n8n Sync Workflow (6:30am) | Pulls Google Calendar → Supabase daily |
| n8n On-Demand Webhook | Real-time calendar queries from OpenClaw |
| `google-calendar.md` skill | Tells agents how to query calendar |
| Morning Commander update | Includes schedule in every daily brief |
