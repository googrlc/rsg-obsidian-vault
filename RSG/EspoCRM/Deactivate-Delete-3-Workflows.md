# Deactivate & Delete 3 Redundant n8n Workflows
# Claude Code Instructions | March 2026

## MISSION
Deactivate and delete 3 redundant n8n workflows that have been replaced by OpenClaw agents.
Pull n8n API key from 1Password.

RULES:
- Deactivate first, then delete — never delete an active workflow
- Confirm each step before proceeding to next
- Report back with final status

---

## THE 3 WORKFLOWS TO REMOVE

| ID | Name | Replaced By |
|---|---|---|
| 8w54qlueIikaBw7c | WF-E — Escalation Watchdog | Renewal Watchdog + Focus Guard (OpenClaw) |
| 3KJRFIwkTtCFexU3 | RSG Afternoon Pulse (3pm ET) | Morning Commander (OpenClaw) |
| X88iqwjGkbOwQ3Dc | Personal OS — Task Reminder Engine | Task Finisher + Focus Guard (OpenClaw) |

---

## STEP 1 — CONFIRM WORKFLOWS EXIST AND ARE ACTIVE

```bash
N8N_KEY=$(op read 'op://RSG/n8n API Key/credential')

for ID in "8w54qlueIikaBw7c" "3KJRFIwkTtCFexU3" "X88iqwjGkbOwQ3Dc"; do
  curl -s "https://n8n-zpvua-u69864.vm.elestio.app/api/v1/workflows/$ID" \
    -H "X-N8N-API-KEY: $N8N_KEY" \
    | python3 -c "import json,sys; r=json.load(sys.stdin); print(f'ID: {r.get(\"id\")} | Name: {r.get(\"name\")} | Active: {r.get(\"active\")}')"
done
```

Report all 3 back before touching anything.

---

## STEP 2 — DEACTIVATE ALL 3

```bash
N8N_KEY=$(op read 'op://RSG/n8n API Key/credential')

for ID in "8w54qlueIikaBw7c" "3KJRFIwkTtCFexU3" "X88iqwjGkbOwQ3Dc"; do
  echo "Deactivating $ID..."
  curl -s -X POST \
    "https://n8n-zpvua-u69864.vm.elestio.app/api/v1/workflows/$ID/deactivate" \
    -H "X-N8N-API-KEY: $N8N_KEY" \
    | python3 -c "import json,sys; r=json.load(sys.stdin); print(f'  {r.get(\"name\")} | active: {r.get(\"active\")}')"
done
```

Confirm active = false for all 3 before proceeding to delete.

---

## STEP 3 — DELETE ALL 3

```bash
N8N_KEY=$(op read 'op://RSG/n8n API Key/credential')

for ID in "8w54qlueIikaBw7c" "3KJRFIwkTtCFexU3" "X88iqwjGkbOwQ3Dc"; do
  echo "Deleting $ID..."
  RESULT=$(curl -s -X DELETE \
    "https://n8n-zpvua-u69864.vm.elestio.app/api/v1/workflows/$ID" \
    -H "X-N8N-API-KEY: $N8N_KEY")
  echo "  Result: $RESULT"
done
```

---

## STEP 4 — VERIFY GONE

```bash
N8N_KEY=$(op read 'op://RSG/n8n API Key/credential')

for ID in "8w54qlueIikaBw7c" "3KJRFIwkTtCFexU3" "X88iqwjGkbOwQ3Dc"; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    "https://n8n-zpvua-u69864.vm.elestio.app/api/v1/workflows/$ID" \
    -H "X-N8N-API-KEY: $N8N_KEY")
  echo "$ID → HTTP $STATUS (404 = deleted successfully)"
done
```

All 3 should return 404.

---

## COMPLETION REPORT

Report:
1. Pre-deletion status of all 3 (name + active state)
2. Deactivation result for each
3. Deletion result for each
4. Final verification — all 3 return 404
