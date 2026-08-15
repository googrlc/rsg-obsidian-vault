# SSH & Claude Code — Mobile Reference
*Last updated: 2026-04-04*

---

## Quick Access — Cloud Servers

RSG servers run on Elestio, DigitalOcean, and Hostinger. SSH format:

```
ssh [user]@[hostname] -p [port]
```

| Server | Hostname | Notes |
|--------|----------|-------|
| Elestio VMs | `vm.elestio.app` (see Elestio dashboard) | Nextcloud + LiteLLM live here |
| hermes-vps | See [[rsg-infrastructure/Hermes-VPS-DigitalOcean]] | Hermes agent (DigitalOcean) |
| rsg-vps | `100.111.105.90` (Tailscale) | Hostinger VPS — see [[rsg-infrastructure/SSH-Config]] |

> 📌 **Find exact SSH details:** Elestio Dashboard → Your Service → SSH/SFTP tab

---

## SSH Key Setup (one-time)

```bash
# Generate key if you don't have one
ssh-keygen -t ed25519 -C "lamar-mobile"

# Copy public key to server
ssh-copy-id -i ~/.ssh/id_ed25519.pub [user]@[host]
```

On **Termius** (iOS/Android): Settings → Keychain → Import or generate key there.

---

## Running Claude Code via SSH

```bash
# SSH into an Elestio server
ssh [user]@[elestio-host]

# Start Claude Code (interactive)
claude

# Start with a specific prompt
claude "summarize my pipeline"

# Run non-interactively (good for scripts)
claude -p "your prompt here" --output-format text
```

---

## Key Commands — Claude Code

| What | Command |
|------|---------|
| Start session | `claude` |
| Resume last session | `claude --resume` |
| List recent sessions | `claude --list` |
| Resume specific session | `claude --resume [session-id]` |
| Run one-shot (no chat) | `claude -p "prompt"` |
| Exit cleanly | `Ctrl+C` or type `/exit` |

---

## Tmux — Keep Sessions Alive (Recommended)

SSH drops = lost session. Use tmux so your Claude session survives disconnects.

```bash
# Start a named session
tmux new -s rsg

# Detach (leave running)
Ctrl+B then D

# Re-attach after reconnecting
tmux attach -t rsg

# List sessions
tmux ls

# Kill a session
tmux kill-session -t rsg
```

---

## Mobile SSH Apps

**Termius** (recommended — iOS & Android)
- Saves hosts, keys, and has a decent keyboard
- Set up your Elestio/DigitalOcean hosts once, one tap to connect
- Enable "Keep Alive" to reduce drops

**Blink Shell** (iOS power users)
- mosh support = much more stable on cellular
- Worth it if you SSH often from your phone

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Connection refused | Check port number in the Elestio dashboard |
| Permission denied | SSH key not added to server — use password first, then `ssh-copy-id` |
| Session dropped | Use tmux (see above) or switch to mosh |
| `claude` not found | `which claude` — may need full path or `source ~/.bashrc` |

---

## Pro Tips

- Always use **tmux** on the server — never raw SSH for long sessions
- Use **Termius snippets** to save common commands (ssh + tmux attach in one tap)
- On cellular: enable mosh if your SSH app supports it — way more stable than TCP
