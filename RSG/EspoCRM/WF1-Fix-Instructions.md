# NB-WF1 Fix — Claude Code Instructions
**Task:** Fix stage string mismatch in NB-WF1 (Deal Won Intake & Commission Log)
**n8n ID:** UFwZUwlHi1ERwSXP
**Date:** March 2026

---

## YOUR MISSION

Fix one broken filter value in n8n workflow UFwZUwlHi1ERwSXP.
Pull credentials from 1Password. Do not skip verification steps.

---

## STEP 1 — VERIFY THE EXACT STAGE STRING ON A LIVE RECORD

Before changing anything, confirm what EspoCRM actually stores.

```bash
curl -s "https://{{ESPOCRM_HOST}}/api/v1/Opportunity?\
where[0][type]=isNotNull&where[0][attribute]=stage&\
select=id,name,stage&maxSize=10" \
  -H "X-Api-Key: $(op read 'op://RSG/EspoCRM API Key/credential')" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
for r in data.get('list', []):
    print(repr(r.get('stage', '')), '|', r.get('name',''))
"
```

Report back all unique stage values you see before touching anything.
Look specifically for the Won stage — it may contain an emoji prefix.

---

## STEP 2 — PULL THE LIVE WORKFLOW JSON

```bash
curl -s "https://{{N8N_HOST}}/api/v1/workflows/UFwZUwlHi1ERwSXP" \
  -H "X-N8N-API-KEY: $(op read 'op://RSG/n8n API Key/credential')" \
  | python3 -m json.tool > /tmp/wf1_live.json

echo "Nodes in workflow:"
python3 -c "
import json
with open('/tmp/wf1_live.json') as f:
    wf = json.load(f)
for n in wf.get('nodes', []):
    print(n.get('id',''), '|', n.get('name',''))
"
```

Then find the broken node:
```bash
python3 -c "
import json
with open('/tmp/wf1_live.json') as f:
    wf = json.load(f)
for n in wf.get('nodes', []):
    params = json.dumps(n.get('parameters', {}))
    if 'Won' in params:
        print('FOUND IT:', n.get('name'))
        print('Parameters:', params[:500])
"
```

Report back the exact current value of the stage filter before patching.

---

## STEP 3 — APPLY THE FIX

Replace the stage filter value with the exact string confirmed in Step 1.
Expected fix: change "Won - Bound" to "✅ Won - Bound" (with emoji).
Use whatever exact value you found in Step 1 — do not assume.

```bash
python3 << 'EOF'
import json, copy

with open('/tmp/wf1_live.json') as f:
    wf = json.load(f)

fixed = False
for node in wf.get('nodes', []):
    params = node.get('parameters', {})
    qp = params.get('queryParameters', {}).get('parameters', [])
    for param in qp:
        if param.get('name') == 'where[0][value]' and 'Won' in str(param.get('value', '')):
            print(f"BEFORE: {repr(param['value'])}")
            param['value'] = '✅ Won - Bound'
            print(f"AFTER:  {repr(param['value'])}")
            fixed = True

if fixed:
    with open('/tmp/wf1_fixed.json', 'w') as f:
        json.dump(wf, f, indent=2)
    print("✅ Fixed JSON saved to /tmp/wf1_fixed.json")
else:
    print("❌ Could not find the stage filter — report back what you found")
EOF
```

---

## STEP 4 — VALIDATE BEFORE PUSHING

```bash
# Confirm the fix looks right
python3 -c "
import json
with open('/tmp/wf1_fixed.json') as f:
    wf = json.load(f)
for n in wf.get('nodes', []):
    params = json.dumps(n.get('parameters', {}))
    if 'Won' in params:
        print('Node:', n.get('name'))
        for p in n.get('parameters',{}).get('queryParameters',{}).get('parameters',[]):
            if 'Won' in str(p.get('value','')):
                print('Stage filter value:', repr(p['value']))
"
```

Confirm output shows the corrected emoji string before continuing.

---

## STEP 5 — PUSH THE FIX TO n8n

```bash
# Deactivate first (safer to update inactive workflows)
curl -s -X POST \
  "https://{{N8N_HOST}}/api/v1/workflows/UFwZUwlHi1ERwSXP/deactivate" \
  -H "X-N8N-API-KEY: $(op read 'op://RSG/n8n API Key/credential')" \
  | python3 -c "import json,sys; r=json.load(sys.stdin); print('Active:', r.get('active'))"

# Push the fixed workflow
curl -s -X PUT \
  "https://{{N8N_HOST}}/api/v1/workflows/UFwZUwlHi1ERwSXP" \
  -H "X-N8N-API-KEY: $(op read 'op://RSG/n8n API Key/credential')" \
  -H "Content-Type: application/json" \
  -d @/tmp/wf1_fixed.json \
  | python3 -c "
import json, sys
r = json.load(sys.stdin)
print('Workflow ID:', r.get('id'))
print('Name:', r.get('name'))
print('Active:', r.get('active'))
print('Updated OK' if r.get('id') else 'ERROR — check response')
"

# Reactivate
curl -s -X POST \
  "https://{{N8N_HOST}}/api/v1/workflows/UFwZUwlHi1ERwSXP/activate" \
  -H "X-N8N-API-KEY: $(op read 'op://RSG/n8n API Key/credential')" \
  | python3 -c "import json,sys; r=json.load(sys.stdin); print('Active:', r.get('active'))"
```

---

## STEP 6 — VERIFY THE FIX IS LIVE

```bash
# Pull the workflow back and confirm the stage value
curl -s "https://{{N8N_HOST}}/api/v1/workflows/UFwZUwlHi1ERwSXP" \
  -H "X-N8N-API-KEY: $(op read 'op://RSG/n8n API Key/credential')" \
  | python3 -c "
import json, sys
wf = json.load(sys.stdin)
for n in wf.get('nodes', []):
    for p in n.get('parameters',{}).get('queryParameters',{}).get('parameters',[]):
        if 'Won' in str(p.get('value','')):
            print('CONFIRMED stage filter:', repr(p['value']))
            print('Workflow active:', wf.get('active'))
"
```

---

## STEP 7 — TEST TRIGGER WITH A REAL RECORD (IF AVAILABLE)

If there are any Won deals in EspoCRM that have NOT been commission-logged yet:

```bash
# Find unlogged Won deals
curl -s "https://{{ESPOCRM_HOST}}/api/v1/Opportunity?\
where[0][type]=equals&where[0][attribute]=stage&where[0][value]=✅ Won - Bound&\
where[1][type]=equals&where[1][attribute]=cCommissionLogged&where[1][value]=false&\
select=id,name,stage,cCommissionLogged&maxSize=5" \
  -H "X-Api-Key: $(op read 'op://RSG/EspoCRM API Key/credential')" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
records = data.get('list', [])
print(f'Unlogged Won deals found: {len(records)}')
for r in records:
    print(f\"  {r['name']} | stage: {repr(r.get('stage'))} | logged: {r.get('cCommissionLogged')}\")
"
```

If unlogged Won deals exist, trigger a manual execution:
```bash
curl -s -X POST \
  "https://{{N8N_HOST}}/api/v1/workflows/UFwZUwlHi1ERwSXP/run" \
  -H "X-N8N-API-KEY: $(op read 'op://RSG/n8n API Key/credential')" \
  -H "Content-Type: application/json" \
  | python3 -c "import json,sys; r=json.load(sys.stdin); print('Execution ID:', r.get('executionId'))"
```

Wait 2 minutes then check execution result and Supabase for new commission records.

---

## COMPLETION REPORT

Report back to Lamar with:
1. Exact stage string found on live EspoCRM records (Step 1)
2. Exact value changed (before and after)
3. Workflow active status after push (Step 5)
4. Confirmed live stage filter value (Step 6)
5. Number of unlogged Won deals found (Step 7)
6. Manual execution result if triggered
7. Any errors encountered
