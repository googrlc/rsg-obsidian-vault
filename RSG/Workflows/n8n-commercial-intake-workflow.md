# n8n Workflow: Commercial Intake → EspoCRM
**Workflow Name:** `Commercial Intake → EspoCRM`
**Trigger:** Webhook POST from OpenClaw call-intake-parser skill
**Webhook path:** `/webhook/commercial-intake`
**Last Updated:** 2026-04-01

---

## Workflow Map

```
[Webhook] → [Validate Payload] → [Lookup Account in EspoCRM]
                                          ↓
                              [Account exists?]
                             YES ↓          NO ↓
                        [Update Account]  [Create Account]
                                    ↓
                        [Lookup Opportunity]
                                    ↓
                        [Opp exists?]
                       YES ↓         NO ↓
                  [Update Opp]    [Create Opp]
                             ↓
                  [Create Tasks — Missing Fields]
                             ↓
                  [Create Tasks — Cross-Sell Flags]
                             ↓
                  [Trigger PDF Generation webhook]
                             ↓
                  [Post to Slack #lamar-alerts]
                             ↓
                  [Return success JSON to OpenClaw]
```

---

## Node 1 — Webhook Trigger

- **Type:** Webhook
- **Method:** POST
- **Path:** `/commercial-intake`
- **Auth:** Header `X-OpenClaw-Key` (store in n8n credentials)
- **Response mode:** Last node

**Expected payload fields:**
```
parsed_data (object)
client_name (string)
call_date (string YYYY-MM-DD)
call_type (string)
called_by (string)
transcript_snippet (string)
```

---

## Node 2 — Validate Payload

- **Type:** Code (JavaScript)
- **Purpose:** Reject incomplete payloads before touching CRM

```javascript
const data = $input.first().json;
const required = ['parsed_data', 'client_name', 'call_date', 'call_type'];
const missing = required.filter(f => !data[f]);
if (missing.length > 0) {
  throw new Error(`Missing required fields: ${missing.join(', ')}`);
}
// Normalize client name
data.client_name_clean = data.client_name.trim().toUpperCase();
return [{ json: data }];
```

---

## Node 3 — Lookup Account in EspoCRM

- **Type:** HTTP Request
- **Method:** GET
- **URL:** `https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1/Account`
- **Headers:** `X-Api-Key: {{$credentials.espocrm_api_key}}`
- **Query params:**
  - `where[0][type]`: `contains`
  - `where[0][attribute]`: `name`
  - `where[0][value]`: `{{$json.client_name_clean}}`
  - `maxSize`: `5`


---

## Node 4 — IF: Account Exists?

- **Type:** IF
- **Condition:** `{{$json.total}}` > 0
- **True branch:** Update Account (Node 5a)
- **False branch:** Create Account (Node 5b)

---

## Node 5a — Update Account

- **Type:** HTTP Request
- **Method:** PATCH
- **URL:** `https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1/Account/{{$json.list[0].id}}`
- **Headers:** `X-Api-Key: {{$credentials.espocrm_api_key}}`
- **Body (JSON):**
```json
{
  "website": "{{$json.parsed_data.business_identity.fein}}",
  "billingAddressStreet": "{{$json.parsed_data.location.mailing_address}}",
  "numberOfEmployees": "{{$json.parsed_data.financials.employees_ft}}",
  "annualRevenue": "{{$json.parsed_data.financials.annual_revenue_current}}",
  "description": "{{$json.parsed_data.operations.description}}",
  "type": "Customer"
}
```

---

## Node 5b — Create Account

- **Type:** HTTP Request
- **Method:** POST
- **URL:** `https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1/Account`
- **Headers:** `X-Api-Key: {{$credentials.espocrm_api_key}}`
- **Body (JSON):**
```json
{
  "name": "{{$json.client_name_clean}}",
  "type": "{{$json.call_type === 'new_prospect' ? 'Prospect' : 'Customer'}}",
  "industry": "{{$json.parsed_data.business_identity.naics_code}}",
  "billingAddressStreet": "{{$json.parsed_data.location.mailing_address}}",
  "numberOfEmployees": "{{$json.parsed_data.financials.employees_ft}}",
  "annualRevenue": "{{$json.parsed_data.financials.annual_revenue_current}}",
  "description": "{{$json.parsed_data.operations.description}}",
  "assignedUserId": "{{$credentials.lamar_user_id}}"
}
```

---

## Node 6 — Create Opportunity

- **Type:** HTTP Request
- **Method:** POST
- **URL:** `https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1/Opportunity`
- **Body (JSON):**
```json
{
  "name": "{{$json.client_name_clean}} — Commercial Intake {{$json.call_date}}",
  "accountId": "{{$json.account_id}}",
  "stage": "Intake / Qualifying",
  "closeDate": "{{DateTime.now().plus({days: 30}).toISODate()}}",
  "description": "Intake call parsed by OpenClaw. Confidence: {{$json.parsed_data.ai_confidence}}%. Missing fields: {{$json.parsed_data.missing_required_fields.length}}",
  "assignedUserId": "{{$credentials.lamar_user_id}}"
}
```

---

## Node 7 — Create Tasks for Missing Required Fields

- **Type:** Split In Batches → HTTP Request loop
- **Input:** `$json.parsed_data.missing_required_fields` array
- **Per item — POST to** `/api/v1/Task`:
```json
{
  "name": "MISSING: {{$item}} — {{$json.client_name_clean}}",
  "status": "Inbox",
  "priority": "High",
  "parentType": "Opportunity",
  "parentId": "{{$json.opportunity_id}}",
  "assignedUserId": "{{$credentials.lamar_user_id}}",
  "dateEnd": "{{DateTime.now().plus({days: 3}).toISODate()}}"
}
```

---

## Node 8 — Create Cross-Sell Tasks

- **Type:** Split In Batches → HTTP Request loop
- **Input:** `$json.parsed_data.cross_sell_flags` array
- **Per item — POST to** `/api/v1/Task`:
```json
{
  "name": "CROSS-SELL OPPORTUNITY: {{$item}} — {{$json.client_name_clean}}",
  "status": "Inbox",
  "priority": "Normal",
  "parentType": "Account",
  "parentId": "{{$json.account_id}}",
  "assignedUserId": "{{$credentials.lamar_user_id}}",
  "dateEnd": "{{DateTime.now().plus({days: 14}).toISODate()}}"
}
```


---

## Node 9 — Trigger PDF Generation

- **Type:** HTTP Request
- **Method:** POST
- **URL:** `https://n8n-zpvua-u69864.vm.elestio.app/webhook/generate-intake-pdf`
- **Body:**
```json
{
  "parsed_data": "{{$json.parsed_data}}",
  "client_name": "{{$json.client_name_clean}}",
  "call_date": "{{$json.call_date}}",
  "account_id": "{{$json.account_id}}",
  "opportunity_id": "{{$json.opportunity_id}}"
}
```

---

## Node 10 — Slack Alert to #lamar-alerts

- **Type:** Slack (Send Message)
- **Channel:** `C0ANQUENX4P` (#lamar-alerts)
- **Message:**
```
🗂 *NEW INTAKE PARSED: {{$json.client_name_clean}}*
📅 Call date: {{$json.call_date}} | Type: {{$json.call_type}}
✅ AI Confidence: {{$json.parsed_data.ai_confidence}}%
⚠️ Missing required fields: {{$json.parsed_data.missing_required_fields.length}}
💰 Cross-sell flags: {{$json.parsed_data.cross_sell_flags.join(', ') || 'none'}}
📋 Submission ready: {{$json.parsed_data.submission_ready ? '✅ YES' : '❌ NO'}}
📝 Summary: {{$json.parsed_data.call_summary}}
🔗 CRM: https://rrespocrm-rsg-u69864.vm.elestio.app/#Account/view/{{$json.account_id}}
```

---

## Node 11 — Return Success Response

- **Type:** Respond to Webhook
- **Body:**
```json
{
  "status": "success",
  "account_id": "{{$json.account_id}}",
  "opportunity_id": "{{$json.opportunity_id}}",
  "missing_fields_count": "{{$json.parsed_data.missing_required_fields.length}}",
  "pdf_triggered": true,
  "slack_sent": true
}
```

---

## Error Handling Nodes

Add error handler branches at:
- Node 3 (lookup fails) → log to `#systems-check`
- Node 5b (create fails) → alert `#lamar-alerts`, return error
- Node 6 (opp create fails) → alert `#lamar-alerts`, return error
- Node 9 (PDF fails) → continue without PDF, note in Slack message

---

## Credentials Needed in n8n

| Credential Name | Value Source |
|---|---|
| `espocrm_api_key` | 1Password: `op://RSG/EspoCRM API Key/credential` |
| `lamar_user_id` | EspoCRM user ID for Lamar (check Admin > Users) |
| `slack_bot_token` | 1Password: `op://RSG/Slack Bot Token/credential` |
| `openclaw_webhook_key` | Set in n8n + OpenClaw skill config |

---

## Deployment Steps

1. Import this workflow spec into n8n at `https://n8n-zpvua-u69864.vm.elestio.app`
2. Add all credentials listed above
3. Activate the webhook — note the production URL
4. Update `call-intake-parser` SKILL.md with confirmed webhook URL
5. Test with a sample transcript from this vault: `_System/test-transcripts/`
6. Confirm Account + Opportunity appear in EspoCRM
7. Confirm Slack message fires to `#lamar-alerts`
8. Update `_System/RSG-Architecture-2026.md` with workflow entry
