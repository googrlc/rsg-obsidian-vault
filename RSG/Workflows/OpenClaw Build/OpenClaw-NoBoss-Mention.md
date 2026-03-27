# OpenClaw — Remove @mention Requirement from #the-boss
# Claude Code Instructions | March 2026

## MISSION
Update Personal Assistant agent config in OpenClaw so every message
posted to #the-boss (C0ANQUENX4P) triggers a response — no @mention needed.

Credentials: pull from 1Password as needed.
Server: openclaw-larau-u69864.vm.elestio.app

RULES:
1. Read every file before editing it — never write blind
2. Backup any file before changing it
3. Restart the gateway after changes and confirm it comes back healthy
4. Report full current config before touching anything

---

## STEP 1 — READ CURRENT CONFIG

```bash
ssh root@openclaw-larau-u69864.vm.elestio.app << 'EOF'

echo "=== openclaw.json ===" && cat /opt/app/config/openclaw.json

echo ""
echo "=== Personal Assistant agent.json ===" && \
  find /opt/app/config/agents -name "agent.json" | xargs grep -l -i "personal\|assistant\|main" | \
  while read f; do echo "FILE: $f"; cat "$f"; echo ""; done

echo ""
echo "=== All agent directories ===" && ls /opt/app/config/agents/

EOF
```

Report back the full contents of openclaw.json and all agent.json files before proceeding.

---

## STEP 2 — UNDERSTAND OPENCLAW EVENT HANDLING

OpenClaw uses Slack Socket Mode. Review how it handles events:

```bash
ssh root@openclaw-larau-u69864.vm.elestio.app << 'EOF'
# Check OpenClaw version and any event config docs
cat /opt/app/config/openclaw.json | python3 -m json.tool

# Look for any event subscription or channel config
grep -r "message\|mention\|event\|channel\|C0ANQUENX4P\|the-boss" \
  /opt/app/config/ 2>/dev/null | grep -v ".git"

# Check OpenClaw docs or readme if available
find /opt/app -name "README*" -o -name "*.md" 2>/dev/null | head -5 | xargs cat 2>/dev/null | head -100
EOF
```

---

## STEP 3 — IMPLEMENT OPTION A

Based on what you find in Step 2, implement the correct approach.

### If OpenClaw supports channel-level triggers in agent.json:
Add the channel to the agent's trigger config so it responds to all messages
in C0ANQUENX4P without requiring a mention.

### If OpenClaw uses openclaw.json for channel routing:
Add an entry that routes all messages from C0ANQUENX4P to Personal Assistant.

### If OpenClaw uses a groupPolicy or channels block:
Update it to include C0ANQUENX4P as a dedicated channel for Personal Assistant
where all messages (not just mentions) are processed.

### Typical OpenClaw channel config pattern to look for and update:
```json
{
  "channels": {
    "C0ANQUENX4P": {
      "agent": "personal-assistant",
      "listenToAllMessages": true,
      "requireMention": false
    }
  }
}
```

Or in agent.json:
```json
{
  "dedicatedChannels": ["C0ANQUENX4P"],
  "requireMention": false
}
```

Find the correct field names from the actual config and apply accordingly.

---

## STEP 4 — BACKUP AND APPLY

```bash
ssh root@openclaw-larau-u69864.vm.elestio.app << 'EOF'
# Backup first
cp /opt/app/config/openclaw.json /opt/app/config/openclaw.json.bak.$(date +%Y%m%d_%H%M%S)
echo "Backup created"

# Apply your edit here using the correct field names found in Step 2
# Edit the file with the appropriate changes
EOF
```

---

## STEP 5 — RESTART GATEWAY AND VERIFY

```bash
ssh root@openclaw-larau-u69864.vm.elestio.app << 'EOF'
cd /opt/app

# Restart
docker compose restart openclaw-gateway

# Wait for health
sleep 8

# Confirm running
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep openclaw

# Tail logs to confirm Slack connected and no errors
docker logs --tail 30 app-openclaw-gateway-1
EOF
```

---

## COMPLETION REPORT

Report back:
1. What event handling mechanism OpenClaw uses (mentions vs channel triggers)
2. Exact field names used to configure the change
3. Before and after of the changed config section
4. Gateway restart status and health confirmation
5. Log output confirming Slack Socket Mode reconnected
6. Confirmation that the change is live
