cat << 'EOF' > ~/.openclaw/RSG_v1_BUILD_LOG.md
# RSG_v1_BUILD_LOG.md
**Date:** March 26, 2026
**Project:** Walled Garden - Risk Solutions Group (RSG)
**Build Version:** 2026.3.24 (cff6dc9)

---

## 🏗️ Core Architecture
- **Orchestrator:** OpenClaw Gateway (Port 18789)
- **Primary Brain:** Anthropic Claude 3.5 Sonnet (Cloud)
- **Specialized Reasoning:** DeepSeek-R1:8B (Local - Mac Mini)
- **Semantic Memory:** mxbai-embed-large:latest (Local - Mac Mini)
- **Hybrid Link:** Elestio VPS ↔ Mac Mini (Tailscale Bridge)

---

## 🧠 Persona & Model Logic
1. **Morning Commander (Claude 3.5):** The executive interface. Hard-wired to Slack channel `C0ANYMH87HR`. 
2. **The Researcher (DeepSeek-R1):** Local reasoning for deep-dive trucking safety data and FMCSA cross-referencing.
3. **The Librarian (mxbai-embed):** Continuous indexing of RSG manuals and prospect history.

---

## 📜 Custom Domain Assets
- **Skill:** `rsg-intel-pack.md` -> Custom sales logic for DOT, OOS rates, and growth signals.
- **Reference:** `edge-cases.md` -> Fallback logic for generic names and FMCSA search collisions.

---

## ⚙️ Verified Configuration (openclaw.json)
```json
{
  "models": {
    "providers": {
      "anthropic": {
        "api": "anthropic-messages",
        "apiKey": "sk-ant-api03-...",
        "baseUrl": "[https://api.anthropic.com](https://api.anthropic.com)",
        "models": [{ "id": "claude-3-5-sonnet-latest", "name": "Claude 3.5 Sonnet" }]
      },
      "ollama": {
        "api": "ollama",
        "baseUrl": "[http://100.82.142.4:11434](http://100.82.142.4:11434)",
        "models": [
          { "id": "deepseek-r1:8b", "name": "The Researcher" },
          { "id": "mxbai-embed-large:latest", "name": "The Librarian" }
        ]
      }
    }
  },
  "channels": { "slack": { "enabled": true } },
  "agents": {
    "main": {
      "name": "Morning Commander",
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-latest",
      "channel": "slack:C0ANYMH87HR",
      "skills": ["slack", "weather", "rsg-intel-pack"],
      "memorySearch": {
        "enabled": true,
        "provider": "ollama",
        "model": "mxbai-embed-large:latest"
      }
    }
  }
}