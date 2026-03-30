---
title: "EspoCRM Custom Account List View — Deployment Changelog"
updated: 2026-03-30
tags: [rsg, espocrm, changelog, account, custom-view, deployment]
---

# EspoCRM Custom Account List View — Deployment Changelog

**Date:** 2026-03-30
**Server:** `rrespocrm-rsg-u69864.vm.elestio.app`
**EspoCRM Version:** 9.3.4
**Container:** `app-espocrm-1` (Docker, `espocrm/espocrm:latest`)
**Web Root:** `/var/www/html/` inside container

---

## Overview

Deployed a custom 4-tab Account list view that replaces EspoCRM's default Account list. The view segments accounts by type — Commercial Lines, Personal Lines, Prospects, and Inactive — with per-tab stat cards, inline search, sortable columns, and live premium data pulled from the Policy entity.

---

## Files Deployed

| # | Local Source | Server Destination | Purpose |
|---|---|---|---|
| 1 | `~/Desktop/files/Account.json` | `custom/Espo/Custom/Resources/metadata/clientDefs/Account.json` | Registers the custom view class |
| 2 | `~/Desktop/files/list.js` | `client/custom/src/views/account/list.js` | Custom AMD view module (JS logic) |
| 3 | `~/Desktop/files/list.tpl` | `client/custom/res/templates/account/list.tpl` | Handlebars template + embedded CSS |

### Account.json

```json
{
  "views": {
    "list": "custom:views/account/list"
  }
}
```

Tells EspoCRM to use `custom:views/account/list` instead of the default `views/list` when rendering the Account list page.

### list.js — Key Design Decisions

- **Module format:** ES module-style AMD (`exports`/`default`) for EspoCRM 9.x compatibility
- **No parent setup call:** Intentionally skips `Dep.prototype.setup()` — fully replaces the default list behavior
- **Authentication:** Uses `Espo.Ajax.getRequest()` (session cookie auth) — no API keys needed
- **Premium data:** Two-step load per tab — first fetches Accounts, then fetches linked Active/Renewing Policies and sums `premiumAmount` per account into a computed `_totalPremium` field
- **Client-side search/sort:** All filtering and sorting happens in-browser on cached data for instant response

### list.tpl — UI Components

- Page header with "Accounts — Risk Solutions Group" title + "+ New Account" button
- Tab bar with color-coded dots and live record counts
- Stat cards: Account count, Total/Est. Premium, Active count, Needs Attention count
- Search toolbar with result counter
- Sortable data table with clickable rows (navigate to record detail)
- Status badges with color coding (Active=green, Urgent=red, Renewing=blue, At Risk=amber, Inactive=gray)

---

## Tab Definitions

| Tab | Color | Account Filter | Premium Source |
|---|---|---|---|
| **Commercial Lines** | Blue `#2563eb` | `accountType` = "Commercial Lines", `accountStatus` in [Active, Urgent, Renewing, At Risk] | Sum of Active/Renewing `Policy.premiumAmount` |
| **Personal Lines** | Green `#16a34a` | `accountType` = "Personal Lines", `accountStatus` in [Active, Urgent, Renewing, At Risk] | Sum of Active/Renewing `Policy.premiumAmount` |
| **Prospects** | Amber `#b45309` | `accountType` = "Prospect" | `Account.estimatedPremium` (direct field) |
| **Inactive** | Gray `#6b7280` | `accountStatus` = "Inactive" | Sum of Active/Renewing `Policy.premiumAmount` |

### Columns Per Tab

**Commercial Lines:** Account (link), Industry, Premium (currency/sortable), LOB (multi-enum), Status (badge), Assigned
**Personal Lines:** Account (link), Phone, Premium (currency/sortable), Renewal Date, Status (badge), CSR
**Prospects:** Account (link), Industry, Est. Premium (currency/sortable), Stage (badge), Assigned
**Inactive:** Account (link), Type, Last Premium (currency/sortable), Assigned

---

## Bugs Fixed During Deployment

### Bug 1: Blank page — Module format mismatch

| | Detail |
|---|---|
| **Symptom** | Page completely blank when navigating to `#Account` |
| **Root cause** | Original JS used old-style AMD: `define(..., function(Dep) { return Dep.extend({}) })` — incompatible with EspoCRM 9.x loader |
| **Fix** | Switched to ES module-style AMD with `exports`/`default` pattern |
| **Before** | `define('custom:views/account/list', ['views/list'], function (Dep) { return Dep.extend({...}); })` |
| **After** | `define('custom:views/account/list', ['exports', 'views/list'], function (_exports, _list) { ... _exports.default = Dep.extend({...}); })` |

### Bug 2: Blank page — Missing Handlebars helper

| | Detail |
|---|---|
| **Symptom** | Template fails silently, no tabs render |
| **Root cause** | Template used `{{#ifEquals @key ../activeTab}}` — EspoCRM does not register an `ifEquals` Handlebars helper |
| **Fix** | Pre-compute `active` boolean per tab in the `data()` method; use standard `{{#if active}}` in template |

### Bug 3: Access Denied — Wrong authentication method

| | Detail |
|---|---|
| **Symptom** | API calls return "Access denied" |
| **Root cause** | Original code used `$.ajax` with `X-Api-Key` header reading from `localStorage` (empty) |
| **Fix** | Replaced with `Espo.Ajax.getRequest('Account', params)` which uses EspoCRM's built-in session cookie authentication |

### Bug 4: API error — maxSize exceeded

| | Detail |
|---|---|
| **Symptom** | API returns "Max size should not exceed 200" |
| **Root cause** | `maxSize: 500` in API params; EspoCRM enforces a hard cap of 200 |
| **Fix** | Changed to `maxSize: 200` |

### Bug 5: Premium showing $0 — Wrong data source

| | Detail |
|---|---|
| **Symptom** | Total Premium stat card and per-row Premium column always show $0 |
| **Root cause** | Code read `annualPremium` from Account entity — field was null for all 92 accounts. Premium data lives on the **Policy** entity (338 policies, $391K active premium). |
| **Fix** | After loading accounts, makes a second `Espo.Ajax.getRequest('Policy', ...)` call filtering by `accountId` (in) + `status` in [Active, Renewing], sums `premiumAmount` per account into computed `_totalPremium` field |

---

## Deployment Method

```bash
# 1. SCP files from Mac to server /tmp
scp ~/Desktop/files/Account.json root@rrespocrm-rsg-u69864.vm.elestio.app:/tmp/
scp ~/Desktop/files/list.js root@rrespocrm-rsg-u69864.vm.elestio.app:/tmp/
scp ~/Desktop/files/list.tpl root@rrespocrm-rsg-u69864.vm.elestio.app:/tmp/

# 2. Create directories + copy into Docker container
docker exec app-espocrm-1 mkdir -p /var/www/html/custom/Espo/Custom/Resources/metadata/clientDefs
docker exec app-espocrm-1 mkdir -p /var/www/html/client/custom/src/views/account
docker exec app-espocrm-1 mkdir -p /var/www/html/client/custom/res/templates/account

docker cp /tmp/Account.json app-espocrm-1:/var/www/html/custom/Espo/Custom/Resources/metadata/clientDefs/Account.json
docker cp /tmp/list.js app-espocrm-1:/var/www/html/client/custom/src/views/account/list.js
docker cp /tmp/list.tpl app-espocrm-1:/var/www/html/client/custom/res/templates/account/list.tpl

# 3. Fix ownership + permissions
docker exec app-espocrm-1 chown www-data:www-data /var/www/html/custom/Espo/Custom/Resources/metadata/clientDefs/Account.json
docker exec app-espocrm-1 chown www-data:www-data /var/www/html/client/custom/src/views/account/list.js
docker exec app-espocrm-1 chown www-data:www-data /var/www/html/client/custom/res/templates/account/list.tpl
docker exec app-espocrm-1 chmod 644 /var/www/html/client/custom/src/views/account/list.js
docker exec app-espocrm-1 chmod 644 /var/www/html/client/custom/res/templates/account/list.tpl

# 4. Clear cache + rebuild
docker exec app-espocrm-1 php /var/www/html/command.php clear-cache
docker exec app-espocrm-1 php /var/www/html/command.php rebuild
```

**Post-deploy:** Admin → Rebuild from EspoCRM UI + hard browser refresh (Cmd+Shift+R)

---

## Known Limitations

1. **200 record cap per tab** — EspoCRM API hard limit. Accounts beyond 200 won't appear. Pagination not yet implemented.
2. **200 policy cap per tab** — If an account set has >200 active policies, some premiums may be undercounted.
3. **Account.annualPremium not populated** — The field exists on the Account entity but has no data. Premium is computed live from Policy records.
4. **Prospects tab** uses `estimatedPremium` from Account (not Policy), so it only shows values if that field is manually populated.

---

## Rollback

To revert to the default Account list view, remove the custom clientDefs:

```bash
docker exec app-espocrm-1 rm /var/www/html/custom/Espo/Custom/Resources/metadata/clientDefs/Account.json
docker exec app-espocrm-1 php /var/www/html/command.php clear-cache
docker exec app-espocrm-1 php /var/www/html/command.php rebuild
```

The `list.js` and `list.tpl` files can remain — they won't load without the clientDefs registration.
