---
title: SSH & Claude Code — Mobile Reference
last_updated: 2026-04-04
tags: [ssh, claude-code, elestio, mobile, reference]
---

# SSH & Claude Code — Mobile Reference

> Quick reference for SSHing into RSG's Elestio servers and running Claude Code from your phone. Built for Termius or any mobile SSH app.

---

## 🔑 RSG Server Inventory

| Server | What's on it | Notes |
|---|---|---|
| OpenClaw | AI agents, skills | Primary work server |
| n8n | Automations | Workflow engine |
| EspoCRM | CRM | Avoid SSH unless troubleshooting |

> **All servers are Elestio-hosted.** Get host IPs/ports from your Elestio dashboard → Services.

---

## 📱 Mobile SSH App Setup (Termius)

**Recommended app:** [Termius](https://termius.com) — free tier works fine.

**One-time setup per server:**
1. Termius → **+** → New Host
2. Fill in: Label, Hostname (IP from Elestio), Port (usually `22`)
3. Username: `root` (Elestio default) or the user shown in your dashboard
4. Auth: Password or SSH key (paste your private key under "Keys")
5. Save → tap to connect

**Pro tips:**
- Save each server as a separate host so you one-tap in
- Enable **Keep-Alive** in Termius settings — prevents mobile disconnects
- Use **Snippets** to save your most-used commands

---

## 🔌 Connecting to a Server

```bash
ssh root@<YOUR-ELESTIO-IP> -p <PORT>
```

**OpenClaw example:**
```bash
ssh root@<openclaw-ip> -p 22
```

> Find your exact IPs in **Elestio Dashboard → Your Services → [Service] → SSH Access tab**

---

## 🤖 Running Claude Code via SSH

Once you're in the server shell:

**Start a new Claude Code session:**
```bash
claude
```

**Run Claude Code on a specific folder:**
```bash
claude /home/node/.openclaw
```

**Run a one-shot command (no interactive session):**
```bash
claude -p "Check HEARTBEAT.md and tell me which agents are active"
```

**Check Claude Code version:**
```bash
claude --version
```

**Check if Claude Code is installed:**
```bash
which claude
```

---

## 📋 Session Management (tmux)

**Always use tmux on servers** — keeps your session alive if mobile disconnects.

**Start a named session:**
```bash
tmux new -s work
```

**Detach from session (keeps it running):**
```
Ctrl+B, then D
```

**List running sessions:**
```bash
tmux ls
```

**Reattach to existing session:**
```bash
tmux attach -t work
```

**Kill a session:**
```bash
tmux kill-session -t work
```

> **Mobile tip:** If you lose connection mid-session, SSH back in and `tmux attach -t work` — you're right back where you were.

---

## 🧭 Key Paths on OpenClaw Server

```bash
# OpenClaw skills
/home/node/.openclaw/skills/

# HEARTBEAT.md (agent registry)
/home/node/.openclaw/HEARTBEAT.md

# Check all skills installed
ls /home/node/.openclaw/skills/

# Read HEARTBEAT
cat /home/node/.openclaw/HEARTBEAT.md
```

---

## ⚡ Most-Used Command Cheat Sheet

| What | Command |
|---|---|
| SSH into OpenClaw | `ssh root@<openclaw-ip>` |
| Start tmux session | `tmux new -s work` |
| Reattach tmux | `tmux attach -t work` |
| Start Claude Code | `claude` |
| One-shot Claude prompt | `claude -p "your prompt here"` |
| List OpenClaw skills | `ls /home/node/.openclaw/skills/` |
| Read HEARTBEAT | `cat /home/node/.openclaw/HEARTBEAT.md` |
| Detach from tmux | `Ctrl+B, D` |
| Exit SSH | `exit` |

---

## 🚨 Exit Safely

1. If in Claude Code: type `exit` or press `Ctrl+C`
2. If in tmux: detach with `Ctrl+B, D` (don't close — keeps session alive)
3. If you want to fully close: `tmux kill-session -t work` then `exit`
4. Never just close the Termius tab — orphaned processes can stack up

---

## 🔗 Related Vault Pages

- [[RSG-Architecture-2026]] — Full system architecture
- [[Elestio-Security-Hardening]] — Security notes for Elestio servers
- [[Claude Code Prompt — RSG Infrastructure Setup]] — Initial setup reference
