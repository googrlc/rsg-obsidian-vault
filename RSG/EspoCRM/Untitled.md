Here's a breakdown of what I observed and the additional ways you can harden this **EspoCRM (rrespocrm-rsg)** instance on Elestio:

---

**1. Enable Termination Protection (Overview tab)**
Currently showing "Protection deactivated." Toggle this on to prevent the VM from being accidentally powered off or deleted. This is a quick, impactful safeguard.

**2. Restrict Firewall Rules by IP (Security → Firewall)**
All current firewall rules (ports 22, 80, 443, 8686, 18374) are open to "Any IPv4 / Any IPv6 address." You should restrict critical ports to known, trusted IPs:
- **Port 22 (SSH)** — limit to your office/home IP only.
- **Port 8686** — if this is an admin/management port, restrict it to trusted IPs as well.
- **Port 18374** — same principle; restrict if not needed publicly.

**3. Add SSH Key Authentication & Disable Password Login (Security → Manage SSH Keys)**
Use the "Manage SSH Keys" option to add your public SSH key. Then disable password-based SSH login via the Nginx/server config to eliminate brute-force risk.

**4. Configure the Rate Limiter (Security → Rate Limiter)**
The Rate Limiter is available but not shown as configured. Enable it to throttle repeated login attempts and API requests — especially important for a CRM that may be publicly accessible.

**5. Set Up Backups (Backups tab)**
Ensure automated backups are scheduled. In the event of ransomware, compromise, or accidental data loss, having regular off-site backups is a critical recovery layer.

**6. Enable Software Auto-Updates (Overview → Software auto updates)**
The "Software auto updates" setting was visible at the bottom of the Overview tab. Make sure this is enabled so EspoCRM receives security patches promptly.

**7. Use a Custom Domain with SSL (Overview → Custom Domain Names)**
If you're still using the default `.vm.elestio.app` CNAME, consider pointing a custom domain and activating SSL via "Manage SSL Domains." This enables proper certificate management and avoids relying on the shared subdomain.

**8. Tune Alert Thresholds (Alerts tab)**
Alerts are configured but thresholds are quite high (e.g., CPU/Memory at 90%). Lowering these (e.g., CPU to 75%, Memory to 80%) gives you earlier warning of unusual activity that could indicate an attack or compromise.

**9. Review the Audit Trail Regularly**
The left sidebar has an **Audit Trail** section. Set a routine to review it for unexpected actions — admin logins, config changes, or service restarts that you didn't initiate.

**10. Inside EspoCRM itself:**
Beyond the Elestio dashboard, you can also:
- Enable **two-factor authentication (2FA)** for CRM user accounts.
- Review and apply the **principle of least privilege** to CRM user roles.
- Disable or remove unused integrations and API keys.
- Set a strong, unique admin password and rotate it periodically.

The most impactful immediate steps are **IP-restricting your SSH firewall rule** and **enabling termination protection** — both are quick wins directly in this dashboard.