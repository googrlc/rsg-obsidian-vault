# Obsidian Git + GitHub Sync Setup
# So Claude, OpenClaw, and n8n all read/write the same vault
# March 2026

---

## STEP 1 — Create a Private GitHub Repo (Lamar does this manually)

1. Go to github.com → New repository
2. Name: rsg-obsidian-vault
3. Set to PRIVATE — vault contains credentials and client data
4. Do NOT initialize with README (vault already has files)
5. Copy the repo URL: https://github.com/googrlc/rsg-obsidian-vault.git

---

## STEP 2 — Install Obsidian Git Plugin (Lamar does this in Obsidian)

1. Open Obsidian → Settings → Community Plugins
2. Search "Obsidian Git" → Install → Enable
3. Go to Obsidian Git settings:
   - Auto pull interval: 10 minutes
   - Auto push after commit: ON
   - Commit message: "vault: auto-sync {{date}}"
   - Pull on startup: ON

---

## STEP 3 — Init Git and Push Vault (Claude Code does this)

Paste this into Claude Code:

"Initialize git in /Users/lamarcoates/Documents/Obsidian Vault,
connect it to GitHub repo rsg-obsidian-vault (URL from Step 1),
create a .gitignore that excludes .obsidian/workspace.json and
any files containing raw credentials, do the first commit and push.
Pull GitHub token from 1Password."

---

## STEP 4 — Create GitHub Fine-Grained Token for OpenClaw + n8n

1. Go to GitHub → Settings → Developer Settings → Personal Access Tokens → Fine-grained
2. Create token named: rsg-vault-readwrite
3. Repository access: Only rsg-obsidian-vault
4. Permissions: Contents (Read and Write), Metadata (Read)
5. Save token to 1Password as: GitHub Vault Token

---

## STEP 5 — Add Token to OpenClaw Environment

SSH into {{OPENCLAW_HOST}}

Add to /opt/app/.env:
GITHUB_VAULT_TOKEN=your_token_here
GITHUB_VAULT_REPO=googrlc/rsg-obsidian-vault
GITHUB_VAULT_BRANCH=main

Restart gateway after.

---

## STEP 6 — Add Token to n8n Environment

In n8n → Settings → Variables:
GITHUB_VAULT_TOKEN = same token
GITHUB_VAULT_REPO = googrlc/rsg-obsidian-vault

---

## HOW OPENCLAW READS/WRITES VAULT FILES

Read a file:
GET https://api.github.com/repos/{REPO}/contents/{path}
Headers: Authorization: Bearer {GITHUB_VAULT_TOKEN}
Response: content field is base64 encoded

Write a file:
PUT https://api.github.com/repos/{REPO}/contents/{path}
Headers: Authorization: Bearer {GITHUB_VAULT_TOKEN}
Body: { message: "commit message", content: base64(newContent), sha: existingSha }

OpenClaw agents can be instructed to read/write vault files using these API calls.
The Personal Assistant already knows to write tasks and notes — once this is set up,
it can also write to vault files for persistent memory.

---

## .gitignore FOR VAULT

Create this file at vault root before first push:

.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/plugins/obsidian-git/data.json
*.DS_Store
.trash/
