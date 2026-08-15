# Skill: NowCerts / Momentum API

## Identity
NowCerts (also branded as Momentum/InMotionNow) is RSG's system of record for all insurance policies. All policy data lives here. Always mint a fresh token per session — tokens expire in ~60 minutes.

## Credentials
- **Login endpoint:** `POST https://api.nowcerts.com/api/AgencyLogin`
- **Username:** `lamar@risk-solutionsgroup.com`
- **Password:** `{{NOWCERTS_PASSWORD}}` ← stored in 1Password
- **Agency ID:** `09d93486-1536-48d7-9096-59f1f62b6f51`
- **Agency Name:** Risk Solutions Group

## Step 1: Always Mint a Fresh Token First

```
POST https://api.nowcerts.com/api/token
Content-Type: application/x-www-form-urlencoded

grant_type=password&username=lamar@risk-solutionsgroup.com&password={{NOWCERTS_PASSWORD}}&client_id=ngAuthApp
```

Extract `access_token` from response. Use as `Bearer {access_token}` in all subsequent calls.

## Step 2: Key API Endpoints

### Get Expiring Policies (Renewal Watchdog)
```
GET https://api.nowcerts.com/api/InsuredDetailList?agencyId=09d93486-1536-48d7-9096-59f1f62b6f51&$orderby=expirationDate&$top=100&$skip=0
Authorization: Bearer {access_token}
```

### Get All Active Insureds
```
GET https://api.nowcerts.com/api/InsuredDetailList?agencyId=09d93486-1536-48d7-9096-59f1f62b6f51&$top=100&$skip=0
Authorization: Bearer {access_token}
```

### Search Insured by Name
```
GET https://api.nowcerts.com/api/InsuredDetailList?agencyId=09d93486-1536-48d7-9096-59f1f62b6f51&$filter=contains(commercialName,'SEARCH_TERM')
Authorization: Bearer {access_token}
```

## Key Insured Fields to Extract
- `databaseId` — NowCerts GUID (use as foreign key in Zoho CRM)
- `commercialName` — business name (use for commercial accounts)
- `firstName` + `lastName` — personal name (use for personal lines clients)
- `expirationDate` — policy expiration (ISO format)
- `premium` — annual premium
- `carrierName` — insurance carrier
- `lineOfBusiness` — LOB
- `policyStatus` — Active / Cancelled / Expired

## Name Resolution Logic
- If `commercialName` is populated → use it as account name
- If `commercialName` is blank → use `firstName + ' ' + lastName`
- Zoho CRM stores names as First Last — NowCerts personal names may be Last, First — always normalize before matching

## Renewal Urgency Tiers (RSG Standard)
- **🔴 CRITICAL:** expiring in 0–14 days
- **🟡 URGENT:** expiring in 15–30 days
- **🟢 WATCH:** expiring in 31–60 days
- **📋 PIPELINE:** expiring in 61–90 days

## LOB Routing (which Zoho CRM pipeline to update)
- Commercial Auto → `Commercial_Auto_Renewals`
- General Liability → `Commercial_PC_Renewals`
- Workers Comp → `Commercial_PC_Renewals`
- Personal Auto → `Personal_Lines_Renewals`
- Homeowners → `Personal_Lines_Renewals`
- Life / Health → `Life_Health_Renewals`

## Error Handling
- If token mint fails → post error to #systems-check, stop execution
- If policy fetch returns empty → verify agencyId, post warning to #systems-check
- If 401 → token expired mid-run, re-mint and retry once
- Never silently fail — always post status to relevant Slack channel
