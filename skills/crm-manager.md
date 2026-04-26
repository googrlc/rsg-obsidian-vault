---
name: crm-manager
description: >
  Universal EspoCRM REST API skill for RSG. Use ANY time the agent needs to create, read,
  update, or search CRM records — accounts, contacts, leads, opportunities, renewals,
  policies, commissions, tasks, calls, or meetings. Triggers: "add account", "create opportunity",
  "update renewal stage", "search for client", "log task", "pipeline status", anything EspoCRM.
---

# CRM Manager — EspoCRM REST API for RSG

**Base URL:** `https://{{ESPOCRM_HOST}}/api/v1`
**Auth:** Header `X-Api-Key: {espocrm.apiKey from agent.json}`
**Content-Type:** `application/json` for POST/PUT/PATCH

---

## API Patterns

### Search / List
```
GET /api/v1/{Entity}?maxSize=20&select=id,name,stage&where[0][type]=equals&where[0][attribute]=stage&where[0][value]=Discovery
```

### Get single record
```
GET /api/v1/{Entity}/{id}
```

### Create record
```
POST /api/v1/{Entity}
Body: { "field": "value", ... }
```

### Update record
```
PUT /api/v1/{Entity}/{id}
Body: { "field": "newValue" }
```

### Delete record
```
DELETE /api/v1/{Entity}/{id}
```

---

## Entities & Key Fields

### Account
Fields: `name`*, `type` (Commercial/Personal Lines), `accountStatus` (Active/Inactive),
`phoneNumber`, `emailAddress`, `billingAddressStreet`, `billingAddressCity`,
`billingAddressState`, `industry`, `numberOfEmployees`, `description`

### Contact
Fields: `firstName`*, `lastName`*, `accountId` (link), `emailAddress`, `phoneNumber`,
`dateOfBirth`, `title`, `description`

### Lead
Fields: `firstName`*, `lastName`*, `accountName`, `emailAddress`, `phoneNumber`,
`status` (New/Assigned/In Process/Converted/Recycled/Dead),
`source`, `description`

### Opportunity
Fields: `name`*, `accountId`* (link), `stage`*, `closeDate`*, `amount`,
`cLineOfBusiness`, `cCarrier`, `cEstimatedPremium`, `cWrittenPremium`,
`cCommissionRate`, `cCommissionLogged` (bool), `cBindDate`, `cEffectiveDate`

**Valid stages (New Business):**
`Discovery` → `Quoting` → `Proposal Presented` → `Negotiation` → `Closed Won` | `Closed Lost`

**Valid stages (Renewal):**
`Renewal Notice Sent` → `Markets Out / Shopping` → `Quoted` → `Presented to Client` → `Bound / Renewed` | `Non-Renewal / Lost`

### Renewal
Fields: `name`*, `accountId`* (link), `policyId` (link), `lineOfBusiness`,
`currentCarrier`, `stage`*, `urgency`, `expirationDate`,
`currentPremium`, `renewalPremium`, `lostReason`, `description`

**Valid stages:**
`Identified` → `Outreach Sent` → `Quote Requested` → `Proposal Sent` → `Negotiating` → `Renewed - Won` | `Lost`

### Policy
Fields: `name`*, `status`* (Active/Expired/Cancelled/Renewing/Renewed),
`carrier`, `lineOfBusiness`, `effectiveDate`, `expirationDate`,
`premiumAmount`, `commissionRate`, `commissionAmount`, `accountId` (link)

### Commission
Fields: `commissionType`*, `status`* (Estimated/Posted/Variance/Reconciled),
`accountId`* (link), `policyId`* (link), `lineOfBusiness`, `carrier`,
`writtenPremium`, `commissionRate`, `estimatedCommission`,
`postedAmount`, `varianceAmount`, `paymentReceivedDate`

### Task
Fields: `name`*, `status` (Inbox/In Progress/Waiting on Client/Waiting on Carrier/Completed/Cancelled),
`assignedUserId`*, `dateEnd`, `priority` (Normal/High/Urgent/Low),
`parentType`, `parentId` (link to Account/Opportunity)

### Call
Fields: `name`*, `status` (Planned/Held/Not Held), `direction` (Outbound/Inbound),
`dateStart`*, `description`, `parentType`, `parentId`

---

## Common API Calls

### Find account by name
```
GET /api/v1/Account?where[0][type]=contains&where[0][attribute]=name&where[0][value]=SMITH&maxSize=5&select=id,name,phoneNumber,accountStatus
```

### Get open opportunities (new business)
```
GET /api/v1/Opportunity?where[0][type]=equals&where[0][attribute]=stage&where[0][value]=Closed Won&maxSize=50&select=id,name,stage,amount,accountName,closeDate,cCommissionLogged
```

### Create opportunity
```
POST /api/v1/Opportunity
{ "name": "ABC Trucking – Commercial Auto", "accountId": "{id}", "stage": "Discovery",
  "closeDate": "2026-06-30", "cLineOfBusiness": "Commercial Auto",
  "cEstimatedPremium": 12000 }
```

### Update renewal stage
```
PUT /api/v1/Renewal/{id}
{ "stage": "Outreach Sent" }
```

### Create task for Gretchen
```
POST /api/v1/Task
{ "name": "Follow up on renewal — ABC Client", "assignedUserId": "{gretchen_user_id}",
  "status": "Inbox", "priority": "High", "dateEnd": "2026-04-05",
  "parentType": "Account", "parentId": "{account_id}" }
```

### Mark opportunity commission logged
```
PUT /api/v1/Opportunity/{id}
{ "cCommissionLogged": true }
```

---

## User IDs (from agent.json)
- Lamar: `assignedUserId` from `agent.json → espocrm.lamarUserId`
- Gretchen: `assignedUserId` from `agent.json → espocrm.gretchenUserId`

## Response Format
All list responses: `{ "list": [...], "total": N }`
All single-record responses: flat object with fields

## Error Handling
- 401 → API key invalid, check agent.json
- 404 → Wrong entity name (case-sensitive) or record not found
- 422 → Missing required field — check `*` fields above
- Always search before creating to avoid duplicates

## Team Routing
- Commercial / new business alerts → #lamar-alerts
- Personal lines tasks → #gretchen-tasks
- System errors → #systems-check
