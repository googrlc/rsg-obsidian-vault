---
title: Hostinger production n8n — SSH, Tailscale, Docker ops
updated: 2026-05-12
tags: [rsg, n8n, hostinger, tailscale, docker, infrastructure]
---

# Hostinger production n8n — SSH, Tailscale, Docker

Canonical runbook for the **Hostinger** VPS that runs production **n8n** (and related RSG services). Workflow-specific IDs and inventory live in [[_System/RSG-n8n-Workflow-Inventory]].

## Access

### SSH (public hostname)

```bash
ssh root@srv1624160.hstgr.cloud
```

### SSH via Tailscale (preferred when tailnet is active)

Use the Tailscale **machine name** (shorter, no public DNS dependency):

```bash
ssh root@srv1624160
```

**Tailscale IP for this host:** `100.100.222.115` (use if you need IP-based access on the tailnet).

### Credentials (1Password — names only)

- SSH private key is stored in the **`rsg_infrastructure`** or **`ssh_infrastructure`** vault.
- Look for items titled **Hostinger SSH** or **hostinger server**.

Do not paste keys or passwords into notes; rotate in 1Password if exposure is suspected.

## n8n HTTPS (cross-reference)

Public n8n URL (also referenced from `rsg-espocrm` README):

https://n8n-n8fq.srv1624160.hstgr.cloud

## Docker — production n8n container

| Item | Value |
|------|--------|
| Container name | `n8n-n8fq-n8n-1` |

### Follow logs

```bash
docker logs -f n8n-n8fq-n8n-1
```

### Import a workflow (CLI inside container)

```bash
docker exec n8n-n8fq-n8n-1 n8n import:workflow --input=/path/to/your/workflow.json
```

Mount or copy the JSON into the container filesystem as needed so `/path/to/your/workflow.json` exists **inside** the container, or adjust the path to match your volume layout.

## Co-located services (same host)

This VPS also runs (non-exhaustive; treat as shared capacity and security boundary):

- OpenClaw  
- Hermes  
- Open WebUI  
- Homepage (command center)

Legacy Tailscale scratch note (links here for Hostinger ops): [[RSG/Workflows/OpenClaw Build/N8N-Tailscale]].

## Troubleshooting

1. **Connection refused on port 22**  
   - Prefer reaching the host over **Tailscale** (`ssh root@srv1624160` or the Tailscale IP) in case public SSH or routing is down or filtered.

2. **Still cannot connect**  
   - Check **Tailscale daemon** and machine status on the host (via Hostinger **hPanel** console / recovery access if SSH is completely unavailable).

3. **n8n UI or web issues**  
   - Confirm container health: `docker ps`, then `docker logs` as above; verify DNS and TLS at the HTTPS URL.

---

*Single canonical ops note for this server’s n8n stack; do not duplicate long SSH/Docker sections in other notes — link here instead.*
