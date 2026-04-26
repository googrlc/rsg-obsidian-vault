#!/bin/bash
# RSG OpenClaw Deploy Script
# Run this from your local machine
# Usage: bash deploy-openclaw.sh

SERVER="root@{{OPENCLAW_HOST}}"

echo "🚀 Deploying RSG OpenClaw updates..."

# 1. Upload skills
echo "📚 Uploading skills..."
scp nowcerts-skill.md $SERVER:/opt/app/config/skills/nowcerts-skill.md
scp espocrm-skill.md $SERVER:/opt/app/config/skills/espocrm-skill.md

# 2. Upload HEARTBEAT
echo "💓 Uploading HEARTBEAT..."
scp HEARTBEAT.md $SERVER:/opt/app/workspace/HEARTBEAT.md

# 3. Upload agent configs
echo "🤖 Uploading agent configs..."
scp renewal-watchdog-agent.json $SERVER:/opt/app/config/agents/renewal-watchdog/agent.json
scp morning-commander-agent.json $SERVER:/opt/app/config/agents/morning-commander/agent.json

# 4. Add NOWCERTS_PASSWORD to .env
echo ""
echo "⚠️  MANUAL STEP REQUIRED:"
echo "SSH into the server and add your NowCerts password to .env:"
echo ""
echo "  ssh $SERVER"
echo "  echo 'NOWCERTS_PASSWORD=YOUR_PASSWORD_HERE' >> /opt/app/.env"
echo ""

# 5. Restart gateway to pick up changes
echo "🔄 Restarting OpenClaw gateway..."
ssh $SERVER "cd /opt/app && docker compose restart openclaw-gateway"

echo ""
echo "✅ Deploy complete. Check #systems-check in Slack for health status."
echo "✅ Morning Commander will fire tomorrow at 7am ET."
echo "✅ Renewal Watchdog will fire at 8am and 2pm daily."
