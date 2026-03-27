# WF2 & WF3 — Replace Gmail Sends with Slack Template Drops
# Claude Code Instructions
# Date: March 2026

## MISSION

Update NB-WF2 and NB-WF3 to remove Gmail auto-send nodes.
Replace each send node with a Slack message that drops the pre-filled
email template so Gretchen can copy/paste and send manually from Gmail.

Gretchen's details:
- Email: Gretchen@rsksolutionsgroup.net
- Phone: 404-609-0722
- Slack: search for her by email to get user ID

Gmail OAuth2 is NOT configured. Do not attempt to fix it.
Human sends email. n8n drops the template. That is the full scope.

---

## STEP 1 — GET GRETCHEN'S SLACK USER ID

```bash
curl -s "https://slack.com/api/users.lookupByEmail?email=Gretchen@rsksolutionsgroup.net" \
  -H "Authorization: Bearer $(op read 'op://RSG/Slack Bot Token/credential')" \
  | python3 -c "import json,sys; r=json.load(sys.stdin); print('Gretchen ID:', r.get('user',{}).get('id'))"
```

Save the user ID — it will be used as the DM channel for template drops.
If lookup fails, search by name:
```bash
curl -s "https://slack.com/api/users.list" \
  -H "Authorization: Bearer $(op read 'op://RSG/Slack Bot Token/credential')" \
  | python3 -c "
import json,sys
r=json.load(sys.stdin)
for u in r.get('members',[]):
    if 'gretchen' in u.get('name','').lower() or 'gretchen' in u.get('real_name','').lower():
        print(u['id'], u['real_name'], u.get('profile',{}).get('email',''))
"
```

---

## STEP 2 — PULL LIVE WORKFLOW JSONS

```bash
# Pull WF2
curl -s "https://n8n-zpvua-u69864.vm.elestio.app/api/v1/workflows/qbMMleTF4xQDJNGo" \
  -H "X-N8N-API-KEY: $(op read 'op://RSG/n8n API Key/credential')" \
  | python3 -m json.tool > /tmp/wf2_live.json

# Pull WF3
curl -s "https://n8n-zpvua-u69864.vm.elestio.app/api/v1/workflows/J9lZZBwUA2888qkP" \
  -H "X-N8N-API-KEY: $(op read 'op://RSG/n8n API Key/credential')" \
  | python3 -m json.tool > /tmp/wf3_live.json

# List all nodes in each
echo "=== WF2 NODES ===" && python3 -c "
import json
with open('/tmp/wf2_live.json') as f: wf=json.load(f)
for n in wf['nodes']: print(n['id'],'|',n['name'],'|',n['type'].split('.')[-1])
"

echo "=== WF3 NODES ===" && python3 -c "
import json
with open('/tmp/wf3_live.json') as f: wf=json.load(f)
for n in wf['nodes']: print(n['id'],'|',n['name'],'|',n['type'].split('.')[-1])
"
```

Report all node IDs and names before proceeding.

---

## STEP 3 — UNDERSTAND THE REPLACEMENT LOGIC

For each Gmail send node in WF2 and WF3, replace the node with an
HTTP Request node that posts to the Slack webhook URL with the
pre-filled email template.

The email content is already built by the Code node before each send.
The replacement node just reads $json.emailSubject and $json.emailBody
and posts them to Slack as a formatted message for Gretchen.

Slack message format for each template drop:
- Header: which day email this is (Day 0, Day 1, Day 7, Day 30, Day 60)
- To: client email address
- Subject line (copy this)
- Body (copy this)
- Instructions: "Copy subject and body → paste into Gmail → send from Gretchen@rsksolutionsgroup.net"

---

## STEP 4 — BUILD THE REPLACEMENT NODE TEMPLATE

Use this as the base for every Gmail replacement node.
Replace GRETCHEN_USER_ID with the ID found in Step 1.
Replace DAY_LABEL with the appropriate day (Day 0, Day 1, Day 7, etc).

```json
{
  "name": "📋 Slack: Drop DAY_LABEL Template for Gretchen",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.2,
  "parameters": {
    "method": "POST",
    "url": "={{ $env.SLACK_WEBHOOK_URL }}",
    "sendBody": true,
    "specifyBody": "json",
    "jsonBody": "={{ JSON.stringify({\n  channel: 'GRETCHEN_USER_ID',\n  text: '📧 DAY_LABEL Email Template — ' + $json.clientName,\n  blocks: [\n    {\n      type: 'header',\n      text: { type: 'plain_text', text: '📧 DAY_LABEL Email — ' + ($json.clientName || 'Client') }\n    },\n    {\n      type: 'section',\n      text: { type: 'mrkdwn', text: '*Send from:* Gretchen@rsksolutionsgroup.net\\n*Send to:* ' + ($json.emailTo || $json.clientEmail || 'check EspoCRM') }\n    },\n    {\n      type: 'section',\n      text: { type: 'mrkdwn', text: '*Subject:*\\n```' + ($json.emailSubject || '') + '```' }\n    },\n    {\n      type: 'section',\n      text: { type: 'mrkdwn', text: '*Body:*\\n```' + ($json.emailBody || '') + '```' }\n    },\n    {\n      type: 'context',\n      elements: [{ type: 'mrkdwn', text: '_Copy subject and body → paste into Gmail → send from Gretchen@rsksolutionsgroup.net · 404-609-0722_' }]\n    }\n  ]\n}) }}",
    "options": {}
  },
  "onError": "continueRegularOutput"
}
```

---

## STEP 5 — APPLY REPLACEMENTS IN WF2

WF2 has 2 Gmail send nodes to replace:
1. "📨 Send Day 0 Email" (id: seq-101)
2. "📨 Send Day 1 Email" (id: seq-202)

```python
import json, copy

with open('/tmp/wf2_live.json') as f:
    wf = json.load(f)

GRETCHEN_ID = 'PASTE_ID_FROM_STEP_1'
WEBHOOK = '={{ $env.SLACK_WEBHOOK_URL }}'

def slack_template_node(node_id, name, day_label):
    return {
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [0, 0],  # position will be preserved from original
        "parameters": {
            "method": "POST",
            "url": WEBHOOK,
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": f"""={{ JSON.stringify({{
  channel: '{GRETCHEN_ID}',
  text: '📧 {day_label} Email Template — ' + ($json.clientName || 'Client'),
  blocks: [
    {{ type: 'header', text: {{ type: 'plain_text', text: '📧 {day_label} Email — ' + ($json.clientName || 'Client') }} }},
    {{ type: 'section', text: {{ type: 'mrkdwn', text: '*Send from:* Gretchen@rsksolutionsgroup.net\\n*Send to:* ' + ($json.emailTo || $json.clientEmail || 'check EspoCRM') }} }},
    {{ type: 'section', text: {{ type: 'mrkdwn', text: '*Subject:*\\n```' + ($json.emailSubject || '') + '```' }} }},
    {{ type: 'section', text: {{ type: 'mrkdwn', text: '*Body:*\\n```' + ($json.emailBody || '') + '```' }} }},
    {{ type: 'context', elements: [{{ type: 'mrkdwn', text: '_Copy → paste into Gmail → send from Gretchen@rsksolutionsgroup.net · 404-609-0722_' }}] }}
  ]
}}) }}""",
            "options": {}
        },
        "onError": "continueRegularOutput"
    }

# Replace nodes, preserving position
for i, node in enumerate(wf['nodes']):
    if node['id'] == 'seq-101':
        pos = node.get('position', [0, 0])
        replacement = slack_template_node('seq-101', '📋 Slack: Drop Day 0 Template', 'Day 0')
        replacement['position'] = pos
        wf['nodes'][i] = replacement
        print('Replaced Day 0 send node')
    elif node['id'] == 'seq-202':
        pos = node.get('position', [0, 0])
        replacement = slack_template_node('seq-202', '📋 Slack: Drop Day 1 Template', 'Day 1')
        replacement['position'] = pos
        wf['nodes'][i] = replacement
        print('Replaced Day 1 send node')

with open('/tmp/wf2_fixed.json', 'w') as f:
    json.dump(wf, f, indent=2)
print('WF2 fixed JSON saved')
```

Run as: `python3 /tmp/fix_wf2.py` (save the above to that file first)

---

## STEP 6 — APPLY REPLACEMENTS IN WF3

WF3 has 3 Gmail send nodes to replace:
- "📨 Send Day 7 Email"
- "📨 Send Day 30 Email"
- "📨 Send Day 60 Email"

Also: disable the Manus AI nodes (Day 30 Manus call will error — env var not set).
Set the "🤖 Call Manus AI" node to skip by routing around it.

```python
import json

with open('/tmp/wf3_live.json') as f:
    wf = json.load(f)

GRETCHEN_ID = 'PASTE_ID_FROM_STEP_1'
WEBHOOK = '={{ $env.SLACK_WEBHOOK_URL }}'

send_replacements = {
    'Send Day 7': 'Day 7',
    'Send Day 30': 'Day 30',
    'Send Day 60': 'Day 60'
}

for i, node in enumerate(wf['nodes']):
    name = node.get('name', '')
    for key, label in send_replacements.items():
        if key in name and node.get('type','').endswith('gmail'):
            pos = node.get('position', [0, 0])
            wf['nodes'][i] = {
                "id": node['id'],
                "name": f"📋 Slack: Drop {label} Template",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": pos,
                "parameters": {
                    "method": "POST",
                    "url": WEBHOOK,
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": f"""={{ JSON.stringify({{
  channel: '{GRETCHEN_ID}',
  text: '📧 {label} Email Template — ' + ($json.clientName || 'Client'),
  blocks: [
    {{ type: 'header', text: {{ type: 'plain_text', text: '📧 {label} Email — ' + ($json.clientName || 'Client') }} }},
    {{ type: 'section', text: {{ type: 'mrkdwn', text: '*Send from:* Gretchen@rsksolutionsgroup.net\\n*Send to:* ' + ($json.emailTo || $json.clientEmail || 'check EspoCRM') }} }},
    {{ type: 'section', text: {{ type: 'mrkdwn', text: '*Subject:*\\n```' + ($json.emailSubject || '') + '```' }} }},
    {{ type: 'section', text: {{ type: 'mrkdwn', text: '*Body:*\\n```' + ($json.emailBody || '') + '```' }} }},
    {{ type: 'context', elements: [{{ type: 'mrkdwn', text: '_Copy → paste into Gmail → send from Gretchen@rsksolutionsgroup.net · 404-609-0722_' }}] }}
  ]
}}) }}""",
                    "options": {}
                },
                "onError": "continueRegularOutput"
            }
            print(f'Replaced {label} send node')

# Replace Manus AI node with Claude API call
for i, node in enumerate(wf['nodes']):
    if 'Manus' in node.get('name','') and 'Call' in node.get('name',''):
        pos = node.get('position', [0, 0])
        wf['nodes'][i] = {
            "id": node['id'],
            "name": "Claude: Generate Day 30 Personalization",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": pos,
            "parameters": {
                "method": "POST",
                "url": "https://api.anthropic.com/v1/messages",
                "sendHeaders": True,
                "headerParameters": {"parameters": [
                    {"name": "x-api-key", "value": "={{ $env.ANTHROPIC_API_KEY }}"},
                    {"name": "anthropic-version", "value": "2023-06-01"},
                    {"name": "content-type", "value": "application/json"}
                ]},
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({ model: 'claude-sonnet-4-20250514', max_tokens: 300, messages: [{ role: 'user', content: 'Write a warm 2-3 sentence 30-day check-in paragraph for RSG client ' + ($json.clientName||'the client') + ' with ' + ($json.pipeline?.lob||'insurance') + ' coverage via ' + ($json.carrier||'their carrier') + '. Mention RSG can help with additional coverage. No greeting or sign-off. Just the paragraph.' }] }) }}",
                "options": {}
            },
            "onError": "continueRegularOutput"
        }
        print('Manus node replaced with Claude API call')

with open('/tmp/wf3_fixed.json', 'w') as f:
    json.dump(wf, f, indent=2)
print('WF3 fixed JSON saved')
```

---

## STEP 7 — VALIDATE BOTH FIXED FILES

```bash
# Check WF2 — confirm no gmail nodes remain
python3 -c "
import json
with open('/tmp/wf2_fixed.json') as f: wf=json.load(f)
for n in wf['nodes']:
    t = n.get('type','')
    print('OK' if 'gmail' not in t else 'STILL HAS GMAIL', '|', n['name'], '|', t.split('.')[-1])
"

# Check WF3 — confirm no gmail nodes remain
python3 -c "
import json
with open('/tmp/wf3_fixed.json') as f: wf=json.load(f)
for n in wf['nodes']:
    t = n.get('type','')
    print('OK' if 'gmail' not in t else 'STILL HAS GMAIL', '|', n['name'], '|', t.split('.')[-1])
"
```

No gmail nodes should remain. All send nodes should show httpRequest type.

---

## STEP 8 — PUSH BOTH WORKFLOWS

```bash
# Deactivate WF2
curl -s -X POST "https://n8n-zpvua-u69864.vm.elestio.app/api/v1/workflows/qbMMleTF4xQDJNGo/deactivate" \
  -H "X-N8N-API-KEY: $(op read 'op://RSG/n8n API Key/credential')" \
  | python3 -c "import json,sys; print('Active:', json.load(sys.stdin).get('active'))"

# Push WF2
curl -s -X PUT "https://n8n-zpvua-u69864.vm.elestio.app/api/v1/workflows/qbMMleTF4xQDJNGo" \
  -H "X-N8N-API-KEY: $(op read 'op://RSG/n8n API Key/credential')" \
  -H "Content-Type: application/json" \
  -d @/tmp/wf2_fixed.json \
  | python3 -c "import json,sys; r=json.load(sys.stdin); print('WF2 updated:', r.get('id'))"

# Reactivate WF2
curl -s -X POST "https://n8n-zpvua-u69864.vm.elestio.app/api/v1/workflows/qbMMleTF4xQDJNGo/activate" \
  -H "X-N8N-API-KEY: $(op read 'op://RSG/n8n API Key/credential')" \
  | python3 -c "import json,sys; print('WF2 active:', json.load(sys.stdin).get('active'))"

# Deactivate WF3
curl -s -X POST "https://n8n-zpvua-u69864.vm.elestio.app/api/v1/workflows/J9lZZBwUA2888qkP/deactivate" \
  -H "X-N8N-API-KEY: $(op read 'op://RSG/n8n API Key/credential')" \
  | python3 -c "import json,sys; print('Active:', json.load(sys.stdin).get('active'))"

# Push WF3
curl -s -X PUT "https://n8n-zpvua-u69864.vm.elestio.app/api/v1/workflows/J9lZZBwUA2888qkP" \
  -H "X-N8N-API-KEY: $(op read 'op://RSG/n8n API Key/credential')" \
  -H "Content-Type: application/json" \
  -d @/tmp/wf3_fixed.json \
  | python3 -c "import json,sys; r=json.load(sys.stdin); print('WF3 updated:', r.get('id'))"

# Reactivate WF3
curl -s -X POST "https://n8n-zpvua-u69864.vm.elestio.app/api/v1/workflows/J9lZZBwUA2888qkP/activate" \
  -H "X-N8N-API-KEY: $(op read 'op://RSG/n8n API Key/credential')" \
  | python3 -c "import json,sys; print('WF3 active:', json.load(sys.stdin).get('active'))"
```

---

## COMPLETION REPORT

Report back with:
1. Gretchen's Slack user ID
2. WF2 — list of nodes replaced (names + old type → new type)
3. WF3 — list of nodes replaced (names + old type → new type)
4. WF3 Manus node — confirm neutralized
5. Both workflows active status after push
6. Any nodes that could NOT be replaced and why

---

## STEP 6B — UPDATE BUILD DAY 30 EMAIL NODE (Claude Response Format)

After replacing the Manus node with Claude, the "Build Day 30 Email" node
needs to read from Claude's response format instead of Manus format.

Claude returns: `{ content: [{ type: "text", text: "..." }] }`
Manus returned: `{ aiBody: "..." }` or `{ completion: "..." }`

Find the "Build Day 30 Email" node in wf3 and update its jsCode:

```python
for i, node in enumerate(wf['nodes']):
    if 'Day 30 Email' in node.get('name','') and 'Build' in node.get('name',''):
        code = node.get('parameters',{}).get('jsCode','')
        # Replace Manus response parsing with Claude response parsing
        updated = code.replace(
            "const manusResponse = $input.item.json;",
            "const manusResponse = $input.item.json;\nconst claudeText = manusResponse?.content?.[0]?.text || '';"
        )
        # Also update wherever aiBody or manusRaw is referenced
        updated = updated.replace("manusResponse?.aiBody", "claudeText")
        updated = updated.replace("manusResponse?.completion", "claudeText")
        updated = updated.replace("$json.manusRaw", "claudeText")
        updated = updated.replace("manusRaw", "claudeText")
        wf['nodes'][i]['parameters']['jsCode'] = updated
        print('Build Day 30 Email updated to read Claude response')
```

Save wf3 after this update:
```bash
with open('/tmp/wf3_fixed.json', 'w') as f:
    json.dump(wf, f, indent=2)
print('WF3 fixed JSON saved with Claude + response parsing updates')
```
