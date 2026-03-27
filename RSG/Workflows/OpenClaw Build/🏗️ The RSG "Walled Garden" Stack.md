
|**Component**|**Specification**|**Role**|
|---|---|---|
|**Orchestrator**|OpenClaw 2026.3.24 (Build cff6dc9)|The "Lobster" CLI and Gateway|
|**Cloud Brain**|Anthropic Claude 3.5 Sonnet|Executive reasoning and Slack interaction|
|**Local Reasoning**|DeepSeek-R1:8B (Mac Mini)|Specialized "Deep Thinking" for research|
|**Local Memory**|mxbai-embed-large:latest (Mac Mini)|"The Librarian" (Semantic Search/RAG)|
|**Primary Channel**|Slack (`C0ANYMH87HR`)|The #the-morning-commander command center|

---

## 🧠 The Neural Logic (Model Assignments)

The system is split into three distinct "Personas" to maximize accuracy while minimizing API costs:

1. **The Commander (Claude 3.5):** Handles the final output in Slack. It follows the RSG manual to produce professional, 3-4 sentence summaries and verbatim call openers.
    
2. **The Researcher (DeepSeek-R1):** Runs on your Mac Mini. It sifts through messy trucking data (DOT numbers, OOS rates) to find patterns that a standard AI might miss.
    
3. **The Librarian (mxbai-embed):** The "Memory" engine. It indexes your custom skills and previous Slack threads so the bot "remembers" your specific preferences and client history.
    

---

## 📜 Custom Intelligence Assets

These are the physical files stored on the Elestio server that provide the "Domain Knowledge" for your agency.

### 1. **Skill: `rsg-intel-pack.md`**

- **Path:** `~/.openclaw/skills/rsg-intel.md`
    
- **Logic:** Dictates the "Revenue Sheriff" persona. Specifically looks for DOT numbers, Out-of-Service (OOS) rates, and "Growth Signals."
    
- **Format:** Forces the bot to provide a structured "Call Opener" and "Objection Flag" for every prospect.
    

### 2. **Reference: `edge-cases.md`**

- **Path:** `~/.openclaw/references/edge-cases.md`
    
- **Logic:** A fallback manual for when a company name is generic or the FMCSA database returns multiple matches.
    

---

## ⚙️ The Master Configuration (`openclaw.json`)

This is the "Source of Truth" that fixed the recent "Unrecognized Key" and "Model Mismatch" errors.

JSON

```
{
  "meta": { "lastTouchedVersion": "2026.3.24" },
  "models": {
    "providers": {
      "anthropic": {
        "api": "anthropic-messages",
        "apiKey": "sk-ant-api03-rCTk...",
        "baseUrl": "https://api.anthropic.com",
        "models": [{ "id": "claude-3-5-sonnet-latest", "name": "Claude 3.5 Sonnet" }]
      },
      "ollama": {
        "api": "ollama",
        "baseUrl": "http://100.82.142.4:11434",
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
      "instructions": "You are the Morning Commander for RSG. Use the rsg-intel-pack for prospect research in channel #the-morning-commander.",
      "memorySearch": {
        "enabled": true,
        "provider": "ollama",
        "model": "mxbai-embed-large:latest"
      }
    }
  }
}
```

---

## ✅ Current Status: "Production Ready"

- **Gateway:** Active on Port 18789.
    
- **Slack Connection:** Verified (OK).
    
- **Hybrid Bridge:** Elestio ↔ Mac Mini (via Tailscale) is active.
    
- **Persona:** The **Morning Commander** is now hard-wired to your Slack channel and armed with your custom sales logic.
    

**Would you like me to archive this build spec into a file on your server called `RSG_v1_BUILD_LOG.md` so you have a permanent record of this setup?**