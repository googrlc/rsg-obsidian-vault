# RSG Unified SSH Config

> **Last updated:** 2026-08-14  
> **Architecture:** Hostinger VPS is the single origin for all services (via Cloudflare Tunnel `rsg-tunnel`).

## Architecture Overview

| Service | Subdomain | Host |
|---|---|---|
| Command Center | `command.risk-solutionsgroup.com` | Hostinger VPS |
| Budibase | `budibase.risk-solutionsgroup.com` | Hostinger VPS |
| Hermes | `hermes.risk-solutionsgroup.com` | Hostinger VPS |
| Homebase | `home.risk-solutionsgroup.com` | Hostinger VPS |
| Carriers | `carriers.risk-solutionsgroup.com` | Hostinger VPS |

## Cloudflare Tunnel

- **Tunnel name:** `rsg-tunnel`
- **Origin IP:** `177.7.38.146` (Hostinger VPS)
- **Edge locations:** ewr08, ewr13, ewr07, ewr05
- **Replica ID:** `1e47a9eb-d254-4d42-8ff4-942486d70865`

## Hostinger VPS Details

| Field | Value |
|---|---|
| Plan | KVM 4 |
| OS | Ubuntu 24.04 LTS |
| Hostname | `srv1624160.hstgr.cloud` |
| IPv4 | `177.7.38.146` |
| Tailscale IP | `100.111.105.90` |
| SSH User | `root` |
| Location | United States - Boston 2 |

## SSH Config File

Drop this into `~/.ssh/config`:

```ssh-config
# ============================================================
#  RSG Unified SSH Config - May 2026
# ============================================================

# --- Global: 1Password SSH Agent ---
Host *
  IdentityAgent "~/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock"
  AddKeysToAgent yes
  IdentitiesOnly yes

# --- GitHub ---
Host github.com
  HostName github.com
  User git

# ============================================================
#  HOSTINGER VPS (KVM 4 / Ubuntu 24.04 / Boston 2)
#  Origin for all services via Cloudflare Tunnel (rsg-tunnel):
#    command.risk-solutionsgroup.com
#    budibase.risk-solutionsgroup.com
#    hermes.risk-solutionsgroup.com
#    home.risk-solutionsgroup.com      (Homebase)
#    carriers.risk-solutionsgroup.com
# ============================================================

Host rsg-vps
  HostName 100.111.105.90
  User root
  # Tailscale - preferred route

Host rsg-vps-direct
  HostName 177.7.38.146
  User root
  # Public IP fallback: srv1624160.hstgr.cloud
```

## 1Password SSH Agent Config

At `~/.config/1Password/ssh/agent.toml`:

```toml
[[ssh-keys]]
vault = "Personal"

[[ssh-keys]]
vault = "Private"

[[ssh-keys]]
vault = "Employee"

[[ssh-keys]]
vault = "ssh_infastructure"
```

> **Note:** The vault name `ssh_infastructure` is intentionally misspelled (missing 'r') - that's how it's named in 1Password.

## Public Keys

### Hostinger VPS

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINHFGoCjXWDF6pABmYfxOmy891/+xizC1bHn53+2Fi5J
```
