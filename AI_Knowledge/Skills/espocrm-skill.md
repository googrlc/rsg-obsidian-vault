# Skill: EspoCRM — RSG CRM Operations

## Identity
EspoCRM is RSG's CRM, running on-premise on the same Elestio/Tailscale network as OpenClaw. All client records, pipeline stages, leads, and opportunities live here.

## Credentials
- **Base URL:** `https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1`
- **Auth Header:** `X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e`
- **Always include header:** `Content-Type: application/json`

## Core Endpoints

### CONTACTS (Clients)

**Search contacts:**
```
GET /api/v1/Contact?searchParams[name]={NAME}&maxSize=20
X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
```

**Get single contact:**
```
GET /api/v1/Contact/{id}
X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
```

**Create contact:**
```
POST /api/v1/Contact
X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
Content-Type: application/json

{
  "firstName": "",
  "lastName": "",
  "emailAddress": "",
  "phoneNumber": "",
  "accountId": ""
}
```

**Update contact:**
```
PUT /api/v1/Contact/{id}
X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
Content-Type: application/json
```

---

### ACCOUNTS (Commercial Clients / Businesses)

**Search accounts:**
```
GET /api/v1/Account?searchParams[name]={NAME}&maxSize=20
X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
```

**Create account:**
```
POST /api/v1/Account
X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
Content-Type: application/json

{
  "name": "",
  "phoneNumber": "",
  "emailAddress": "",
  "industry": "",
  "type": "Customer"
}
```

---

### OPPORTUNITIES (Pipeline Deals)

**List opportunities by stage:**
```
GET /api/v1/Opportunity?searchParams[stage]={STAGE}&maxSize=50
X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
```

**Common stages:** `Prospecting`, `Qualification`, `Proposal`, `Negotiation`, `Closed Won`, `Closed Lost`

**Create opportunity:**
```
POST /api/v1/Opportunity
X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
Content-Type: application/json

{
  "name": "{CLIENT} - {LOB} Renewal {YEAR}",
  "stage": "Prospecting",
  "closeDate": "{EXPIRATION_DATE}",
  "amount": {PREMIUM},
  "accountId": "{ACCOUNT_ID}",
  "assignedUserId": "{LAMAR_USER_ID}",
  "description": "Source: NowCerts sync | Policy: {POLICY_NUMBER} | Carrier: {CARRIER} | LOB: {LOB}"
}
```

**Update opportunity stage:**
```
PUT /api/v1/Opportunity/{id}
X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
Content-Type: application/json

{
  "stage": "{NEW_STAGE}"
}
```

---

### LEADS

**Create lead:**
```
POST /api/v1/Lead
X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
Content-Type: application/json

{
  "firstName": "",
  "lastName": "",
  "accountName": "",
  "emailAddress": "",
  "phoneNumber": "",
  "status": "New",
  "source": "",
  "description": ""
}
```

**List leads by status:**
```
GET /api/v1/Lead?searchParams[status]={STATUS}&maxSize=50
X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
```

---

### ACTIVITIES (Tasks & Calls)

**Create task:**
```
POST /api/v1/Task
X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e
Content-Type: application/json

{
  "name": "{TASK_DESCRIPTION}",
  "status": "Not Started",
  "priority": "High",
  "dateEnd": "{DUE_DATE}",
  "assignedUserId": "{USER_ID}",
  "parentType": "Contact",
  "parentId": "{CONTACT_ID}",
  "description": ""
}
```

---

## RSG-Specific Business Logic

### NowCerts → EspoCRM Sync Rules
When pulling expiring policies from NowCerts and writing to EspoCRM:
1. Search EspoCRM for existing Account by `insuredName`
2. If account exists → create/update Opportunity linked to that account
3. If account does NOT exist → create Account first, then create Opportunity
4. Set Opportunity `closeDate` = policy `expirationDate`
5. Set Opportunity `amount` = `premiumAmount`
6. Tag description with `[NowCerts Sync]` so manual records are distinguishable

### Duplicate Prevention
Before creating any record:
- Search by name first
- If match found with same LOB and close date within 30 days → update, don't create
- Log action to #systems-check

### Commission Tracking
When Opportunity moves to `Closed Won`:
- Note premium amount
- Calculate estimated commission: Commercial = 10-15%, Personal = 8-12%
- Post to #growth-finance with deal summary

## Error Handling
- 401 → API key invalid, post to #systems-check immediately
- 404 → Record not found, log and continue
- 422 → Validation error, post full error payload to #systems-check
- 500 → EspoCRM down, post alert to #agency-ops, retry in 15 min
