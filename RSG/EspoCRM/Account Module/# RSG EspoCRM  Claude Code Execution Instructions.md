# RSG EspoCRM — Claude Code SSH Execution Instructions
# Full server-side configuration via SSH
# Credentials: retrieve from 1Password as needed

===============================================================
CLAUDE CODE — YOUR MISSION
===============================================================

You are configuring the EspoCRM Accounts module for Risk Solutions Group
via SSH. You have full server access. Do everything on disk — no browser,
no API calls for layout changes.

RULES:
1. Find the EspoCRM installation path first — do not assume it.
2. ALWAYS back up any file before editing it.
3. ALWAYS run `php clear_cache.php` from the EspoCRM root after changes.
4. Validate JSON before writing — malformed JSON breaks EspoCRM silently.
5. Report the result of every major step before moving to the next.
6. If a file does not exist where expected, find it — do not create it in the wrong place.

===============================================================
STEP 1 — FIND ESPOCRM AND ORIENT
===============================================================

```bash
# Find EspoCRM installation
find / -name "clear_cache.php" 2>/dev/null | grep -v vendor

# Confirm it's the right one
ls /path/to/espocrm/

# Set working variable (replace with actual path found above)
ESPO=/path/to/espocrm

# Confirm custom directory exists
ls $ESPO/custom/Espo/Custom/Resources/
```

Expected directory structure:
```
$ESPO/custom/Espo/Custom/Resources/
  layouts/
    Account/
      detail.json        ← Overview tab layout
      detailSmall.json   ← Mobile layout
      list.json          ← List view columns
  metadata/
    entityDefs/
      Account.json       ← Field definitions
```

If layouts/Account/ does not exist, create it:
```bash
mkdir -p $ESPO/custom/Espo/Custom/Resources/layouts/Account
mkdir -p $ESPO/custom/Espo/Custom/Resources/metadata/entityDefs
```

===============================================================
STEP 2 — BACKUP EVERYTHING FIRST
===============================================================

```bash
# Create timestamped backup
BACKUP=$ESPO/custom/Espo/Custom/Resources/_backup_$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP

# Backup layouts
cp -r $ESPO/custom/Espo/Custom/Resources/layouts $BACKUP/ 2>/dev/null || echo "No layouts to backup yet"

# Backup metadata
cp -r $ESPO/custom/Espo/Custom/Resources/metadata $BACKUP/ 2>/dev/null || echo "No metadata to backup yet"

# Backup core Account entityDefs (read-only reference)
cp $ESPO/application/Espo/Core/Templates/Metadata/Base/entityDefs.json $BACKUP/core_entityDefs_reference.json 2>/dev/null

echo "Backup complete at: $BACKUP"
```

===============================================================
STEP 3 — READ CURRENT STATE
===============================================================

```bash
# Read current Account field definitions
cat $ESPO/custom/Espo/Custom/Resources/metadata/entityDefs/Account.json 2>/dev/null || echo "File does not exist yet"

# Read core Account entityDefs for reference
cat $ESPO/application/Espo/Entities/Account.php 2>/dev/null | head -50

# Read current detail layout
cat $ESPO/custom/Espo/Custom/Resources/layouts/Account/detail.json 2>/dev/null || echo "No custom layout yet — will use core default"

# Read core default layout for reference
cat $ESPO/application/Espo/Resources/layouts/Account/detail.json 2>/dev/null
```

Report back:
- The full path to EspoCRM
- Whether custom entityDefs/Account.json exists
- Whether custom layouts/Account/detail.json exists
- The current contents of both files if they exist

===============================================================
STEP 4 — CREATE REQUIRED FIELDS
===============================================================

Edit or create: `$ESPO/custom/Espo/Custom/Resources/metadata/entityDefs/Account.json`

Merge these fields into the `fields` object. Do NOT overwrite existing fields —
read the file first, merge, then write back.

Fields to add:

```json
{
  "fields": {
    "type": {
      "type": "enum",
      "options": ["Commercial Lines", "Personal Lines", "Group Benefits", "Prospect"],
      "default": "Prospect",
      "isCustom": true
    },
    "totalActivePremium": {
      "type": "currency",
      "label": "Total Active Premium",
      "readOnly": true,
      "isCustom": true
    },
    "activePolicyCount": {
      "type": "int",
      "label": "Active Policy Count",
      "readOnly": true,
      "min": 0,
      "isCustom": true
    },
    "nextXDate": {
      "type": "date",
      "label": "Next X-Date",
      "readOnly": true,
      "isCustom": true
    },
    "nextXDateLob": {
      "type": "varchar",
      "label": "Next X-Date LOB",
      "readOnly": true,
      "maxLength": 255,
      "isCustom": true
    },
    "intelPackRun": {
      "type": "bool",
      "label": "Intel Pack Run",
      "default": false,
      "isCustom": true
    },
    "intelPackLastRun": {
      "type": "datetime",
      "label": "Intel Pack Last Run",
      "readOnly": true,
      "isCustom": true
    },
    "aiAssessment": {
      "type": "text",
      "label": "AI Assessment",
      "rowsMin": 4,
      "isCustom": true
    }
  }
}
```

```bash
# Validate JSON before writing
echo 'YOUR_JSON_HERE' | python3 -m json.tool > /dev/null && echo "✅ JSON valid" || echo "❌ JSON invalid — do not write"

# Write the merged file
cat > $ESPO/custom/Espo/Custom/Resources/metadata/entityDefs/Account.json << 'EOF'
MERGED_JSON_HERE
EOF

# Clear cache
php $ESPO/clear_cache.php

echo "Fields written and cache cleared."
```

===============================================================
STEP 5 — CONFIGURE OVERVIEW LAYOUT (detail.json)
===============================================================

Write this as: `$ESPO/custom/Espo/Custom/Resources/layouts/Account/detail.json`

This replaces the Overview tab layout. Fields listed here appear on the account record.
Fields NOT listed here are hidden (but their data is preserved).

```json
[
  {
    "rows": [
      [{"name": "name"}, {"name": "type"}],
      [{"name": "accountStatus"}, {"name": "assignedUser"}],
      [{"name": "phoneNumber"}, {"name": "emailAddress"}],
      [{"name": "billingAddress", "fullWidth": true}]
    ]
  },
  {
    "label": "Key Metrics",
    "rows": [
      [{"name": "totalActivePremium"}, {"name": "activePolicyCount"}],
      [{"name": "nextXDate"}, {"name": "nextXDateLob"}]
    ]
  }
]
```

```bash
# Validate
echo 'LAYOUT_JSON' | python3 -m json.tool > /dev/null && echo "✅ Valid" || echo "❌ Invalid"

# Write
cat > $ESPO/custom/Espo/Custom/Resources/layouts/Account/detail.json << 'EOF'
LAYOUT_JSON_HERE
EOF

php $ESPO/clear_cache.php
echo "Overview layout written."
```

===============================================================
STEP 6 — CONFIGURE DETAILS TAB LAYOUT
===============================================================

Write this as: `$ESPO/custom/Espo/Custom/Resources/layouts/Account/detailConvert.json`

Note: EspoCRM stores additional tab layouts separately. Check what layout
file controls the Details tab in your version:

```bash
# Check what layout files exist for Account
ls $ESPO/application/Espo/Resources/layouts/Account/
ls $ESPO/custom/Espo/Custom/Resources/layouts/Account/
```

The Details tab layout to write:

```json
[
  {
    "label": "Account Details",
    "rows": [
      [{"name": "fein"}, {"name": "industry"}],
      [{"name": "yearsInBusiness"}, {"name": "numberOfEmployees"}],
      [{"name": "dateOfBirth"}, {"name": "gender"}],
      [{"name": "maritalStatus"}, false],
      [{"name": "description", "fullWidth": true}]
    ]
  },
  {
    "label": "Internal",
    "rows": [
      [{"name": "momentumClientId"}, {"name": "momentumLastSync"}],
      [{"name": "googleDriveFolderUrl", "fullWidth": true}]
    ]
  },
  {
    "label": "AI Intel Pack",
    "rows": [
      [{"name": "intelPackRun"}, {"name": "intelPackLastRun"}],
      [{"name": "aiAssessment", "fullWidth": true}]
    ]
  }
]
```

===============================================================
STEP 7 — CONFIGURE DYNAMIC LOGIC
===============================================================

Dynamic Logic is stored inside the detail layout file as a `dynamicLogic`
key at the top level. Merge this into detail.json:

```json
{
  "dynamicLogic": {
    "fields": {
      "fein": {
        "visible": {
          "conditionGroup": [{
            "type": "equals",
            "attribute": "type",
            "value": "Commercial Lines"
          }]
        }
      },
      "industry": {
        "visible": {
          "conditionGroup": [{
            "type": "or",
            "value": [
              {"type": "equals", "attribute": "type", "value": "Commercial Lines"},
              {"type": "equals", "attribute": "type", "value": "Group Benefits"}
            ]
          }]
        }
      },
      "numberOfEmployees": {
        "visible": {
          "conditionGroup": [{
            "type": "or",
            "value": [
              {"type": "equals", "attribute": "type", "value": "Commercial Lines"},
              {"type": "equals", "attribute": "type", "value": "Group Benefits"}
            ]
          }]
        }
      },
      "yearsInBusiness": {
        "visible": {
          "conditionGroup": [{
            "type": "equals",
            "attribute": "type",
            "value": "Commercial Lines"
          }]
        }
      },
      "dateOfBirth": {
        "visible": {
          "conditionGroup": [{
            "type": "equals",
            "attribute": "type",
            "value": "Personal Lines"
          }]
        }
      },
      "gender": {
        "visible": {
          "conditionGroup": [{
            "type": "equals",
            "attribute": "type",
            "value": "Personal Lines"
          }]
        }
      },
      "maritalStatus": {
        "visible": {
          "conditionGroup": [{
            "type": "equals",
            "attribute": "type",
            "value": "Personal Lines"
          }]
        }
      }
    }
  }
}
```

Merge this `dynamicLogic` key into the existing detail.json — do not replace
the entire file, just add the key alongside the existing layout array.

===============================================================
STEP 8 — CLEAR CACHE AND VERIFY
===============================================================

```bash
# Full cache clear
php $ESPO/clear_cache.php

# Confirm files are in place
echo "=== entityDefs ===" && cat $ESPO/custom/Espo/Custom/Resources/metadata/entityDefs/Account.json | python3 -m json.tool | head -30
echo "=== detail layout ===" && cat $ESPO/custom/Espo/Custom/Resources/layouts/Account/detail.json | python3 -m json.tool | head -30

# Check file permissions — EspoCRM needs to read these
ls -la $ESPO/custom/Espo/Custom/Resources/layouts/Account/
ls -la $ESPO/custom/Espo/Custom/Resources/metadata/entityDefs/
```

Fix permissions if needed:
```bash
chown -R www-data:www-data $ESPO/custom/
chmod -R 755 $ESPO/custom/
```

===============================================================
STEP 9 — n8n ROLLUP WORKFLOW
===============================================================

Save this JSON file and import into n8n manually:
Go to n8n → Workflows → Import from File → select rsg_rollup_workflow.json

```bash
cat > ~/rsg_rollup_workflow.json << 'EOF'
{
  "name": "RSG Account Rollup Fields",
  "active": false,
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": { "interval": [{ "field": "hours", "hoursInterval": 6 }] }
      },
      "position": [240, 300]
    },
    {
      "name": "Get All Accounts",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "GET",
        "url": "={{ $env.ESPOCRM_URL }}/api/v1/Account?maxSize=500&select=id,name",
        "authentication": "genericCredentialType",
        "genericAuthType": "basicAuth"
      },
      "position": [460, 300]
    },
    {
      "name": "Split Accounts",
      "type": "n8n-nodes-base.splitInBatches",
      "parameters": { "batchSize": 1 },
      "position": [680, 300]
    },
    {
      "name": "Get Active Policies",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "GET",
        "url": "={{ $env.ESPOCRM_URL }}/api/v1/Policy?where[0][type]=equals&where[0][attribute]=accountId&where[0][value]={{ $json.id }}&where[1][type]=equals&where[1][attribute]=status&where[1][value]=Active&select=id,lob,premiumAmount,expirationDate",
        "authentication": "genericCredentialType",
        "genericAuthType": "basicAuth"
      },
      "position": [900, 300]
    },
    {
      "name": "Calculate Rollup",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "const policies = items[0]?.json?.list || [];\nconst accountId = $('Split Accounts').first().json.id;\nif (!policies.length) {\n  return [{ json: { accountId, totalActivePremium: 0, activePolicyCount: 0, nextXDate: null, nextXDateLob: null } }];\n}\nconst total = policies.reduce((s, p) => s + (parseFloat(p.premiumAmount) || 0), 0);\nconst sorted = policies.filter(p => p.expirationDate).sort((a,b) => new Date(a.expirationDate) - new Date(b.expirationDate));\nconst soonest = sorted[0];\nreturn [{ json: { accountId, totalActivePremium: Math.round(total*100)/100, activePolicyCount: policies.length, nextXDate: soonest?.expirationDate || null, nextXDateLob: soonest?.lob || null } }];"
      },
      "position": [1120, 300]
    },
    {
      "name": "Write to Account",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "PATCH",
        "url": "={{ $env.ESPOCRM_URL }}/api/v1/Account/{{ $json.accountId }}",
        "authentication": "genericCredentialType",
        "genericAuthType": "basicAuth",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            { "name": "totalActivePremium", "value": "={{ $json.totalActivePremium }}" },
            { "name": "activePolicyCount", "value": "={{ $json.activePolicyCount }}" },
            { "name": "nextXDate", "value": "={{ $json.nextXDate }}" },
            { "name": "nextXDateLob", "value": "={{ $json.nextXDateLob }}" }
          ]
        }
      },
      "position": [1340, 300]
    }
  ],
  "connections": {
    "Schedule Trigger": { "main": [[{ "node": "Get All Accounts", "type": "main", "index": 0 }]] },
    "Get All Accounts": { "main": [[{ "node": "Split Accounts", "type": "main", "index": 0 }]] },
    "Split Accounts": { "main": [[{ "node": "Get Active Policies", "type": "main", "index": 0 }]] },
    "Get Active Policies": { "main": [[{ "node": "Calculate Rollup", "type": "main", "index": 0 }]] },
    "Calculate Rollup": { "main": [[{ "node": "Write to Account", "type": "main", "index": 0 }]] }
  }
}
EOF

echo "✅ n8n workflow JSON saved to ~/rsg_rollup_workflow.json"
echo "Import into n8n: Workflows → Import from File"
```

===============================================================
COMPLETION REPORT — REQUIRED
===============================================================

When all steps are done, report back with:

1. Full EspoCRM path found on server
2. List of files created/modified with their full paths
3. Output of final cache clear
4. Any errors encountered and how they were resolved
5. Confirmation that JSON validation passed for all files
6. Contents of final detail.json (first 30 lines)
7. Note: Lamar needs to manually verify in browser that
   A1 Auto Speciality Overview looks correct after this runs



===============================================================
STEP 10 — PERSONAL LINES ACCOUNT LAYOUT
===============================================================

Personal Lines accounts are structurally different from Commercial:
- The account IS the contact — no separate Contacts panel needed
- No FEIN, Industry, Years in Business, Number of Employees
- Need DOB, Gender, Marital Status on the Details tab
- Overview is streamlined — name, contact info, key metrics only
- List view shows columns relevant to both account types

All field-level hiding is handled via Dynamic Logic in Step 7.
This step covers the missing pieces: Contacts panel suppression,
list view config, field existence verification, and browser checklist.

--- 10A: HIDE CONTACTS PANEL FOR PERSONAL LINES ---

The Contacts relationship panel on the Overview tab must be hidden
when Account Type = Personal Lines.

Merge the `panels` key into the existing `dynamicLogic` object in detail.json.
Do NOT replace the fields conditions — append panels alongside them.

```json
{
  "dynamicLogic": {
    "fields": {
      "... existing field conditions stay here ..."
    },
    "panels": {
      "contacts": {
        "visible": {
          "conditionGroup": [{
            "type": "or",
            "value": [
              {"type": "equals", "attribute": "type", "value": "Commercial Lines"},
              {"type": "equals", "attribute": "type", "value": "Group Benefits"}
            ]
          }]
        }
      }
    }
  }
}
```

```bash
# After editing, validate and clear cache
cat $ESPO/custom/Espo/Custom/Resources/layouts/Account/detail.json | python3 -m json.tool > /dev/null && echo "✅ Valid" || echo "❌ Invalid — do not proceed"
php $ESPO/clear_cache.php
```

--- 10B: PERSONAL LINES LIST VIEW COLUMNS ---

Configure a single list view that works for both Commercial and Personal
accounts. Write this as:
$ESPO/custom/Espo/Custom/Resources/layouts/Account/list.json

```bash
cat > $ESPO/custom/Espo/Custom/Resources/layouts/Account/list.json << 'EOF'
[
  {"name": "name", "link": true},
  {"name": "type"},
  {"name": "accountStatus"},
  {"name": "phoneNumber"},
  {"name": "assignedUser"},
  {"name": "totalActivePremium"},
  {"name": "nextXDate"},
  {"name": "nextXDateLob"},
  {"name": "activePolicyCount"}
]
EOF

php $ESPO/clear_cache.php
echo "✅ List view written."
```

--- 10C: VERIFY PERSONAL LINES FIELDS EXIST ---

Check that DOB, Gender, and Marital Status exist in entityDefs:

```bash
cat $ESPO/custom/Espo/Custom/Resources/metadata/entityDefs/Account.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
fields = data.get('fields', {})
required = ['dateOfBirth', 'gender', 'maritalStatus']
for f in required:
    status = '✅' if f in fields else '❌ MISSING — must add'
    print(f'{status}  {f}')
"
```

If any are missing, merge these into entityDefs/Account.json:

```json
{
  "fields": {
    "dateOfBirth": {
      "type": "date",
      "label": "Date of Birth",
      "isCustom": true
    },
    "gender": {
      "type": "enum",
      "label": "Gender",
      "options": ["Male", "Female", "Non-binary", "Prefer not to say"],
      "isCustom": true
    },
    "maritalStatus": {
      "type": "enum",
      "label": "Marital Status",
      "options": ["Single", "Married", "Domestic Partner", "Widowed", "Divorced"],
      "isCustom": true
    }
  }
}
```

Merge into existing file, validate JSON, write back, clear cache.

--- 10D: FIELDS THAT MUST NEVER APPEAR ON PERSONAL LINES ---

These are already suppressed via Dynamic Logic in Step 7 and 10A.
Confirm all of the following are covered:

- fein → hidden via Dynamic Logic (Step 7)
- industry → hidden via Dynamic Logic (Step 7)
- yearsInBusiness → hidden via Dynamic Logic (Step 7)
- numberOfEmployees → hidden via Dynamic Logic (Step 7)
- contacts panel → hidden via Dynamic Logic (Step 10A)

No additional layout file changes needed. Verify Dynamic Logic is
firing correctly in the browser verification step below.

--- 10E: BROWSER VERIFICATION CHECKLIST — PERSONAL LINES ---

After all steps complete, open a Personal Lines account in EspoCRM
and confirm ALL of the following:

OVERVIEW TAB:
[ ] Name, Account Type (= Personal Lines), Status, Score, Assigned User visible
[ ] Phone, Email, Billing Address visible
[ ] Total Active Premium, Policy Count, Next X-Date, Next X-Date LOB visible
[ ] Contacts panel is HIDDEN (critical — Personal Lines has no separate contact)
[ ] FEIN, Industry, Years in Business are HIDDEN

DETAILS TAB:
[ ] Date of Birth visible
[ ] Gender visible
[ ] Marital Status visible
[ ] FEIN, Industry, Years in Business are HIDDEN
[ ] Description, Momentum fields, AI Intel section all visible

POLICIES TAB:
[ ] Linked policies panel visible
[ ] Renewals panel visible

LIST VIEW (Accounts list):
[ ] 9 columns visible for all account types
[ ] Account Type column correctly shows "Personal Lines"
[ ] No broken/empty column headers

===============================================================
IF ANYTHING BREAKS
===============================================================

```bash
# Restore from backup
cp -r $BACKUP/layouts $ESPO/custom/Espo/Custom/Resources/
cp -r $BACKUP/metadata $ESPO/custom/Espo/Custom/Resources/
php $ESPO/clear_cache.php
echo "Restored from backup"
```


===============================================================
STEP 11 — POPULATE ROLLUP FIELDS (n8n)
===============================================================

The four rollup fields (totalActivePremium, activePolicyCount, nextXDate,
nextXDateLob) are empty placeholders until the n8n workflow runs.

--- 11A: IMPORT THE WORKFLOW ---

1. Open your n8n instance
2. Go to Workflows → Import from File
3. Select ~/rsg_rollup_workflow.json
4. The workflow will import as INACTIVE — do not activate yet

--- 11B: SET CREDENTIALS IN n8n ---

1. In n8n, go to Credentials → New Credential
2. Type: HTTP Basic Auth
3. Name: EspoCRM Basic Auth
4. Username: your EspoCRM admin username
5. Password: your EspoCRM admin password
6. Save

Then in the imported workflow:
- Open each HTTP Request node
- Set Authentication to the credential you just created
- Confirm ESPOCRM_URL variable is set to your EspoCRM base URL
  (e.g. https://crm.yourdomain.com — no trailing slash)

--- 11C: RUN MANUALLY ONCE TO POPULATE ALL ACCOUNTS ---

1. Open the workflow
2. Click "Execute Workflow" (manual run)
3. Watch the execution — each account will be processed one at a time
4. When complete, open A1 Auto Speciality in EspoCRM
5. Confirm Total Active Premium, Policy Count, Next X-Date, Next X-Date LOB
   all show real values

--- 11D: ACTIVATE FOR SCHEDULED RUNS ---

1. Toggle the workflow to ACTIVE
2. It will now run every 6 hours automatically
3. Check n8n executions log after first scheduled run to confirm no errors

VERIFY:
[ ] A1 Auto Speciality shows totalActivePremium with a dollar value
[ ] activePolicyCount shows correct number of active policies
[ ] nextXDate shows the soonest expiring policy date
[ ] nextXDateLob shows the LOB of that policy

===============================================================
STEP 12 — WIN PERCENTAGE BY STAGE
===============================================================

Win % by stage tells you where deals are converting and where they are dying.
For RSG this is most useful on the Commercial P&C and Group Benefits pipelines.

--- 12A: NATIVE ESPOCRM REPORTS (no code required) ---

EspoCRM has a built-in Reports module that handles this natively.

Navigate to: Reports → Create Report → Matrix Report

REPORT 1: Win Rate by Stage (Opportunities)
- Entity: Opportunities
- Group By (rows): Stage
- Group By (columns): Status (Won / Lost / Open)
- Value: COUNT
- Name: "Win Rate by Stage"
- Save and add to dashboard

This gives you a table:
  Stage         | Won | Lost | Open
  Prospecting   |  3  |  2   |  8
  Qualified     |  5  |  1   |  4
  Proposal      |  4  |  3   |  2

Win % per stage = Won / (Won + Lost) x 100
EspoCRM can calculate this automatically if you add a formula column.

REPORT 2: Pipeline by LOB (New Business)
- Entity: Opportunities
- Group By: Type (LOB)
- Values: COUNT, SUM of Amount
- Filter: Status = Open
- Name: "Open Pipeline by LOB"

REPORT 3: Conversion Funnel — Commercial P&C
- Entity: Opportunities
- Group By: Stage
- Filter: Type = Commercial P&C
- Value: COUNT
- Name: "Commercial P&C Funnel"

--- 12B: n8n WIN RATE CALCULATOR (advanced — adds % field) ---

If you want win % written directly onto records or pushed to Slack weekly,
add this workflow to n8n:

Trigger: Schedule (every Monday 7am)
Node 1: HTTP GET — fetch all Opportunities from EspoCRM
  URL: $ESPOCRM_URL/api/v1/Opportunity?maxSize=1000&select=id,stage,status
Node 2: Code node — group by stage, calculate win %
  const opps = items.map(i => i.json);
  const stages = {};
  opps.forEach(o => {
    if (!stages[o.stage]) stages[o.stage] = { won: 0, lost: 0, open: 0 };
    if (o.status === 'Won') stages[o.stage].won++;
    else if (o.status === 'Lost') stages[o.stage].lost++;
    else stages[o.stage].open++;
  });
  const results = Object.entries(stages).map(([stage, counts]) => {
    const closed = counts.won + counts.lost;
    const winPct = closed > 0 ? Math.round((counts.won / closed) * 100) : null;
    return { stage, ...counts, winPct };
  });
  return results.map(r => ({ json: r }));
Node 3: Slack message — format and post to #rsg-pipeline
  Example: "Commercial P&C — Qualified stage: 71% win rate (5W / 7 closed)"

===============================================================
STEP 13 — ESPOCRM DASHBOARDS
===============================================================

EspoCRM dashboards are fully native — no plugins needed.
Navigate to: Home → Dashboards (top nav) → Add Dashlet

--- 13A: LAMAR'S SALES DASHBOARD ---

Create a dashboard named "RSG Sales Overview"
Add these dashlets:

DASHLET 1: Total Active Premium
- Type: Report Chart
- Report: Create a new Report → Accounts → SUM of totalActivePremium
- Display as: Single metric / KPI card
- Label: "Total Active Premium"

DASHLET 2: Policies Expiring in 30 Days
- Type: List
- Entity: Policies
- Filter: expirationDate <= today+30 AND status = Active
- Columns: Account Name, LOB, Carrier, Expiration Date
- Sort: Expiration Date ascending
- Label: "Expiring in 30 Days"

DASHLET 3: Policies Expiring in 60 Days
- Same as above but filter: expirationDate <= today+60
- Label: "Expiring in 31-60 Days"

DASHLET 4: Open Pipeline by LOB
- Type: Report Chart
- Report: Open Pipeline by LOB (created in Step 12A)
- Display as: Bar chart

DASHLET 5: Win Rate by Stage
- Type: Report
- Report: Win Rate by Stage (created in Step 12A)
- Display as: Table

DASHLET 6: Recent Activity
- Type: Activities
- Shows: Calls, Emails, Meetings logged today
- Assigned to: Lamar

--- 13B: GRETCHEN'S RENEWALS DASHBOARD ---

Create a dashboard named "Renewals — Personal Lines"
Add these dashlets:

DASHLET 1: Personal Lines Renewals Due (30 days)
- Type: List
- Entity: Renewals
- Filter: expirationDate <= today+30 AND LOB IN [Auto, Homeowners, Renters]
- Columns: Client Name, LOB, Carrier, Expiration Date, Stage, Urgency
- Sort: Expiration Date ascending

DASHLET 2: Renewals by Stage
- Type: Report
- Entity: Renewals
- Group By: Stage
- Value: COUNT
- Display as: Pie or bar chart

DASHLET 3: Accounts Missing Renewal Contact
- Type: List
- Entity: Renewals
- Filter: Stage = "Not Started" AND expirationDate <= today+60
- Columns: Client Name, Assigned User, LOB, Expiration Date
- Label: "Not Yet Contacted — Due in 60 Days"

DASHLET 4: Commissions This Month
- Type: Report
- Entity: Commissions
- Filter: createdAt >= first day of current month
- Value: SUM of commission amount
- Display as: KPI metric

--- 13C: DASHBOARD LAYOUT TIPS ---

- Dashboards are per-user — Lamar and Gretchen each get their own
- Drag dashlets to resize and reorder
- Set refresh interval on time-sensitive dashlets (e.g. expiring policies: 1 hour)
- Pin the most-used dashboard as default via the star icon

--- 13D: VERIFY DASHBOARDS ---

[ ] Lamar's dashboard loads and shows 6 dashlets with real data
[ ] Gretchen's dashboard shows renewal list sorted by urgency
[ ] "Expiring in 30 Days" list correctly filters active policies
[ ] Win Rate by Stage report shows data from Opportunities
[ ] Total Active Premium KPI shows dollar value (requires n8n rollup from Step 11)

===============================================================
STEP 14 — CLAUDE CODE: REVIEW & BUILD n8n ROLLUP WORKFLOW
===============================================================

You are Claude Code. Your job is to connect to the RSG n8n instance,
review all existing workflows, and either update the rollup workflow
if it already exists or create it fresh if it does not.

Credentials: retrieve from 1Password as needed.
n8n instance: retrieve URL from 1Password.

RULES:
1. Read before you write. Pull all existing workflows first.
2. Never delete an existing workflow — deactivate only if replacing.
3. Validate all JSON before posting to the API.
4. Report every step result before moving to the next.
5. If an existing workflow partially matches, update it — don't duplicate.

--- 14A: CONNECT TO n8n API ---

n8n has a REST API. Authenticate with an API key.

```bash
# Retrieve n8n API key from 1Password
# Then test connectivity
curl -s -H "X-N8N-API-KEY: YOUR_API_KEY" \
  https://YOUR_N8N_URL/api/v1/workflows?limit=50 | python3 -m json.tool | head -60
```

If the API key auth fails, try basic auth:
```bash
curl -s -u "admin:PASSWORD" \
  https://YOUR_N8N_URL/api/v1/workflows?limit=50 | python3 -m json.tool | head -60
```

--- 14B: AUDIT ALL EXISTING WORKFLOWS ---

Pull the full workflow list and report back:

```bash
# Get all workflows — names, IDs, active status
curl -s -H "X-N8N-API-KEY: YOUR_API_KEY" \
  "https://YOUR_N8N_URL/api/v1/workflows?limit=100" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
workflows = data.get('data', [])
print(f'Total workflows: {len(workflows)}')
print()
for w in workflows:
    status = '🟢 ACTIVE' if w.get('active') else '⚫ INACTIVE'
    print(f\"{status} | ID: {w['id']} | {w['name']}\")
"
```

Report back the FULL list before touching anything.

Then read the details of any workflow whose name contains:
- rollup, account, policy, premium, expir, renewal, sync, espo

```bash
# Read a specific workflow by ID
curl -s -H "X-N8N-API-KEY: YOUR_API_KEY" \
  "https://YOUR_N8N_URL/api/v1/workflows/WORKFLOW_ID" \
  | python3 -m json.tool > workflow_WORKFLOW_ID.json

cat workflow_WORKFLOW_ID.json | python3 -c "
import json, sys
w = json.load(sys.stdin)
print('Name:', w['name'])
print('Active:', w['active'])
print('Node count:', len(w.get('nodes', [])))
print()
for node in w.get('nodes', []):
    print(f\"  Node: {node['name']} | Type: {node['type']}\")
"
```

--- 14C: DECISION LOGIC (UPDATED FROM AUDIT) ---

AUDIT CONFIRMED: No rollup workflow exists. Decision: CREATE new.

Corrections from audit — apply to all nodes:
1. Auth: Use X-Api-Key header, NOT Basic Auth
   Header name: X-Api-Key
   Value: retrieve from 1Password (key name: EspoCRM API Key)
2. EspoCRM URL: hardcode to https://rrespocrm-rsg-u69864.vm.elestio.app
   Do NOT use $vars.ESPOCRM_URL — it does not exist in this instance
3. Slack: use $env.SLACK_WEBHOOK_URL to #systems-check (matches existing pattern)
4. Create as INACTIVE — manual test run first, activate after confirming success

--- 14D: CORRECTED ROLLUP WORKFLOW SPEC ---

```json
{
  "name": "RSG — Account Rollup Fields",
  "active": false,
  "settings": {
    "saveDataSuccessExecution": "none",
    "saveDataErrorExecution": "all",
    "executionTimeout": 300
  },
  "nodes": [
    {
      "id": "node-schedule",
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.1,
      "position": [200, 300],
      "parameters": {
        "rule": {
          "interval": [{ "field": "hours", "hoursInterval": 6 }]
        }
      }
    },
    {
      "id": "node-get-accounts",
      "name": "Get All Accounts",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [420, 300],
      "parameters": {
        "method": "GET",
        "url": "https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1/Account",
        "sendQuery": true,
        "queryParameters": {
          "parameters": [
            { "name": "maxSize", "value": "500" },
            { "name": "select", "value": "id,name,type" }
          ]
        },
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            { "name": "X-Api-Key", "value": "e5df7c321b47427d24046bab814dbb58" }
          ]
        }
      }
    },
    {
      "id": "node-extract-list",
      "name": "Extract Account List",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [640, 300],
      "parameters": {
        "jsCode": "const list = $input.first().json.list || [];\nreturn list.map(account => ({ json: account }));"
      }
    },
    {
      "id": "node-get-policies",
      "name": "Get Active Policies",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [860, 300],
      "parameters": {
        "method": "GET",
        "url": "https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1/Policy",
        "sendQuery": true,
        "queryParameters": {
          "parameters": [
            { "name": "where[0][type]", "value": "equals" },
            { "name": "where[0][attribute]", "value": "accountId" },
            { "name": "where[0][value]", "value": "={{ $json.id }}" },
            { "name": "where[1][type]", "value": "equals" },
            { "name": "where[1][attribute]", "value": "status" },
            { "name": "where[1][value]", "value": "Active" },
            { "name": "select", "value": "id,name,lob,premiumAmount,expirationDate,status" },
            { "name": "maxSize", "value": "50" }
          ]
        },
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            { "name": "X-Api-Key", "value": "e5df7c321b47427d24046bab814dbb58" }
          ]
        }
      }
    },
    {
      "id": "node-calculate",
      "name": "Calculate Rollup Values",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1080, 300],
      "parameters": {
        "jsCode": "const accountId = $('Extract Account List').first().json.id;\nconst policies = $input.first().json.list || [];\n\nif (!policies.length) {\n  return [{ json: {\n    accountId,\n    totalActivePremium: 0,\n    activePolicyCount: 0,\n    nextXDate: null,\n    nextXDateLob: null\n  }}];\n}\n\nconst total = policies.reduce((sum, p) => {\n  return sum + (parseFloat(p.premiumAmount) || 0);\n}, 0);\n\nconst withDates = policies.filter(p => p.expirationDate);\nwithDates.sort((a, b) => new Date(a.expirationDate) - new Date(b.expirationDate));\nconst soonest = withDates[0];\n\nreturn [{ json: {\n  accountId,\n  totalActivePremium: Math.round(total * 100) / 100,\n  activePolicyCount: policies.length,\n  nextXDate: soonest ? soonest.expirationDate : null,\n  nextXDateLob: soonest ? (soonest.lob || null) : null\n}}];"
      }
    },
    {
      "id": "node-write-back",
      "name": "Write Rollup to Account",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [1300, 300],
      "parameters": {
        "method": "PATCH",
        "url": "=https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1/Account/{{ $json.accountId }}",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            { "name": "X-Api-Key", "value": "e5df7c321b47427d24046bab814dbb58" },
            { "name": "Content-Type", "value": "application/json" }
          ]
        },
        "sendBody": true,
        "contentType": "json",
        "body": "={{ JSON.stringify({\n  totalActivePremium: $json.totalActivePremium,\n  activePolicyCount: $json.activePolicyCount,\n  nextXDate: $json.nextXDate,\n  nextXDateLob: $json.nextXDateLob\n}) }}"
      }
    },
    {
      "id": "node-slack-success",
      "name": "Slack Success Digest",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [1520, 300],
      "parameters": {
        "method": "POST",
        "url": "={{ $env.SLACK_WEBHOOK_URL }}",
        "sendBody": true,
        "contentType": "json",
        "body": "={\"text\": \"✅ RSG Account Rollup complete — all accounts updated.\"}"
      }
    },
    {
      "id": "node-slack-error",
      "name": "Slack Error Alert",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [1300, 500],
      "parameters": {
        "method": "POST",
        "url": "={{ $env.SLACK_WEBHOOK_URL }}",
        "sendBody": true,
        "contentType": "json",
        "body": "={\"text\": \"🚨 RSG Account Rollup FAILED\\nCheck n8n executions for details.\"}"
      }
    }
  ],
  "connections": {
    "Schedule Trigger": {
      "main": [[{ "node": "Get All Accounts", "type": "main", "index": 0 }]]
    },
    "Get All Accounts": {
      "main": [[{ "node": "Extract Account List", "type": "main", "index": 0 }]]
    },
    "Extract Account List": {
      "main": [[{ "node": "Get Active Policies", "type": "main", "index": 0 }]]
    },
    "Get Active Policies": {
      "main": [[{ "node": "Calculate Rollup Values", "type": "main", "index": 0 }]]
    },
    "Calculate Rollup Values": {
      "main": [[{ "node": "Write Rollup to Account", "type": "main", "index": 0 }]]
    },
    "Write Rollup to Account": {
      "main": [[{ "node": "Slack Success Digest", "type": "main", "index": 0 }]]
    }
  }
}
```

--- 14E: CREATE OR UPDATE VIA API ---

TO CREATE (if no existing workflow found):
```bash
curl -s -X POST \
  -H "X-N8N-API-KEY: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d @rsg_rollup_workflow.json \
  "https://YOUR_N8N_URL/api/v1/workflows" \
  | python3 -c "
import json, sys
r = json.load(sys.stdin)
print('Created workflow ID:', r.get('id'))
print('Name:', r.get('name'))
print('Active:', r.get('active'))
"
```

TO UPDATE (if existing workflow found — replace WORKFLOW_ID):
```bash
curl -s -X PUT \
  -H "X-N8N-API-KEY: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d @rsg_rollup_workflow.json \
  "https://YOUR_N8N_URL/api/v1/workflows/WORKFLOW_ID" \
  | python3 -c "
import json, sys
r = json.load(sys.stdin)
print('Updated workflow ID:', r.get('id'))
print('Name:', r.get('name'))
"
```

--- 14F: SET ESPOCRM CREDENTIALS IN n8n ---

The workflow uses basicAuth. Credentials must exist in n8n before activation.

Check if EspoCRM credentials already exist:
```bash
curl -s -H "X-N8N-API-KEY: YOUR_API_KEY" \
  "https://YOUR_N8N_URL/api/v1/credentials" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
creds = data.get('data', [])
for c in creds:
    print(f\"ID: {c['id']} | Name: {c['name']} | Type: {c['type']}\")
"
```

If no EspoCRM Basic Auth credential exists, create one:
```bash
curl -s -X POST \
  -H "X-N8N-API-KEY: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "EspoCRM Basic Auth",
    "type": "httpBasicAuth",
    "data": {
      "user": "YOUR_ESPOCRM_USERNAME",
      "password": "YOUR_ESPOCRM_PASSWORD"
    }
  }' \
  "https://YOUR_N8N_URL/api/v1/credentials" \
  | python3 -c "import json,sys; r=json.load(sys.stdin); print('Credential ID:', r.get('id'))"
```

Save the returned credential ID — you will need it to link to the workflow nodes.

--- 14G: RUN WORKFLOW MANUALLY ONCE ---

After creating/updating, trigger a manual execution to populate all accounts:

```bash
# Execute workflow manually
curl -s -X POST \
  -H "X-N8N-API-KEY: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  "https://YOUR_N8N_URL/api/v1/workflows/WORKFLOW_ID/run" \
  | python3 -c "
import json, sys
r = json.load(sys.stdin)
print('Execution ID:', r.get('executionId'))
print('Status:', r.get('status', 'started'))
"
```

Wait 2-3 minutes, then check execution result:
```bash
curl -s -H "X-N8N-API-KEY: YOUR_API_KEY" \
  "https://YOUR_N8N_URL/api/v1/executions/EXECUTION_ID" \
  | python3 -c "
import json, sys
r = json.load(sys.stdin)
print('Status:', r.get('status'))
print('Finished:', r.get('finished'))
print('Mode:', r.get('mode'))
"
```

--- 14H: ACTIVATE WORKFLOW ---

Only activate AFTER confirming the manual run completed successfully:
```bash
curl -s -X POST \
  -H "X-N8N-API-KEY: YOUR_API_KEY" \
  "https://YOUR_N8N_URL/api/v1/workflows/WORKFLOW_ID/activate" \
  | python3 -c "import json,sys; r=json.load(sys.stdin); print('Active:', r.get('active'))"
```

--- 14I: COMPLETION REPORT ---

Report back to Lamar with:
1. Full list of all n8n workflows found (names, IDs, active status)
2. Whether rollup workflow was CREATED or UPDATED (and which existing one)
3. Workflow ID of the final rollup workflow
4. Credential ID used for EspoCRM auth
5. Manual execution result (success/fail, how many accounts processed)
6. Whether workflow is now ACTIVE on 6-hour schedule
7. Sample output: paste the rollup values written to A1 Auto Speciality
