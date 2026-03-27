- **Account Classification:** `lob` (multi-enum with 13 LOBs), `xDate`, `estimatedPremium`, `annualPremium`, `renewalDate`, `carrier`, `accountStatus` (with color badges: green/amber/red/gray), `stage` (with color labels)
- **Intel Meta:** `intelRun`, `intelRunDate`, `intelRunBy`, `intelSourcesHit`, `intelConfidence` (High/Medium/Low with color labels)
- **AI Output:** `intelAiSummary`, `intelPainPoints`, `intelCrossSell`, `intelGrowthIndicator`
- **Insights:** `insightSignal`, `insightObjection`, `insightOpener`, `insightRelationship`
- **Company Profile:** `intelLegalName`, `intelDba`, `intelNaics`, `intelSic`, `intelEntityType`, `intelYearsInBusiness`, `intelEmployeeCount`, `intelAnnualRevenueEst`, `intelWebsite`, `intelLinkedinUrl`, `intelBbbRating`, `intelBbbAccredited`, `intelBbbComplaints`
- **Fleet & Risk:** `intelFleetSize`, `intelOperatingRadius`, `intelCargoType`, `intelOwnerOperators`, `intelDotIncidents`, `intelOshaViolations`, `intelUnderwritingFlag`
- **Raw Research:** `intelWebsiteNotes`, `intelNewsNotes`, `intelLinkedinNotes`, `intelBbbNotes`, `intelSignalNews`, `intelSignalLinkedin`
- "Prospect" added to `accountType` options

**Tabbed Detail View (5 tabs):**

1. **Overview** — Account info, classification, internal (collapsed)
2. **Policies** — Policies, renewals, commissions relationship panels
3. **Intelligence** — 7 panels: Run Status, AI Summary, Insights, AI Output, Company Profile, Fleet & Risk Details, Raw Research Notes (collapsed by default)
4. **Activity** — Activity Log, emails, meetings, calls, tasks
5. **Documents** — Documents panel

**Dynamic Logic:** Fleet/risk fields conditionally show/hide based on `lob` values (Commercial Auto, Cargo)

**Custom UI:**

- `intelRun` renders as green/gray dot icon (not true/false text) in list view
- `accountStatus` renders as colored badge (success/warning/danger/default)
- `intelConfidence` renders as colored label
- `stage` renders as colored label

**Run Intel Pack Button:** Appears on Prospect accounts only. Sends POST to n8n webhook (configure `intelPackWebhookUrl` in EspoCRM config).

**ActivityLog:** Added "Intel Run" and "Renewal Outreach" activity types.

**One thing to configure manually:** Set your n8n webhook URL in EspoCRM config. SSH in and run:

```
docker exec app-espocrm-1 php -r "
\$config = include '/var/www/html/data/config.php';
\$config['intelPackWebhookUrl'] = 'YOUR_N8N_WEBHOOK_URL';
file_put_contents('/var/www/html/data/config.php', '<?php return ' . var_export(\$config, true) . ';');
"
```