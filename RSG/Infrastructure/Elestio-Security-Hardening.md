# hosting platform Security Hardening — RSG

Applies to all 3 hosting platform VMs: OpenClaw, n8n, EspoCRM

## Immediate Actions

1. **Enable Termination Protection** (Overview tab) — prevents accidental VM deletion
2. **Restrict Firewall by IP** — Port 22 SSH and Port 8686 admin → limit to known IPs only
3. **Add SSH Key Auth + disable password login** via Manage SSH Keys
4. **Configure Rate Limiter** — throttle repeated login/API attempts
5. **Verify Backups** — automated backups scheduled on all 3 VMs
6. **Enable Software Auto-Updates** (Overview → Software auto updates)
7. **Custom Domain + SSL** — point custom domain, activate SSL via Manage SSL Domains
8. **Lower Alert Thresholds** — CPU to 75%, Memory to 80% (default 90% is too late)
9. **Review Audit Trail** regularly for unexpected admin logins or config changes

## Inside EspoCRM
- Enable 2FA for all user accounts
- Principle of least privilege on user roles
- Disable unused integrations and API keys
- Rotate admin password regularly
