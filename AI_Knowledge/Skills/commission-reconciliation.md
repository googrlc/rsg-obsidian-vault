---
name: commission-reconciliation
description: >
  Commission reconciliation skill using Supabase commission_ledger and commission_reconciliation tables. Tracks expected vs actual commissions, detects deltas, handles SmartChoice 70/30 split, and flags underpayments for follow-up.
---

# Commission Reconciliation — Find the Missing Money

**Goal:** Make sure RSG gets paid every dollar it's owed. Track expected vs actual commissions, flag discrepancies, and recover underpayments.

## Data Sources

### Supabase (RSG Infrastructure)
- **Base URL:** `https://wibscqhkvpijzqbhjphg.supabase.co/rest/v1`
- **Auth Header:** `Authorization: Bearer {{SUPABASE_SERVICE_ROLE_KEY}}`
- **Always include:** `apikey: {{SUPABASE_SERVICE_ROLE_KEY}}`

### Tables Used

#### `commission_ledger`
Tracks every commission payment RSG expects or receives per policy per statement period.

| Key Column | Type | Purpose |
|---|---|---|
| `policy_number` | text | Policy identifier |
| `carrier_name` | text | Paying carrier |
| `lob` | text | Line of business |
| `client_name` | text | Insured name |
| `mga_name` | text | MGA channel (default: "Direct") |
| `gross_premium` | numeric | Policy premium |
| `expected_commission` | numeric | What RSG should receive |
| `actual_commission` | numeric | What RSG actually received |
| `delta` | numeric (generated) | `actual - expected` (negative = underpaid) |
| `reconciliation_status` | text | `pending` / `matched` / `discrepancy` / `resolved` |
| `revenue_split_percent` | numeric | RSG's share (default 100, SmartChoice = 70) |
| `rsg_net_commission` | numeric | What RSG keeps after MGA split |
| `commission_basis` | text | `as_earned` / `advance` / `hybrid` |
| `advance_amount` | numeric | Upfront advance (if applicable) |
| `earned_to_date` | numeric | Running earned total for advance policies |
| `unearned_balance` | numeric (generated) | `advance - earned` = chargeback exposure |
| `chargeback_expiry_date` | date | Safe from chargeback after this date |
| `audit_adjustable` | boolean | True for WC and audit-basis GL |
| `commission_rule_id` | uuid | FK to commission_rules |

#### `commission_reconciliation`
Flagged discrepancies requiring follow-up.

| Key Column | Type | Purpose |
|---|---|---|
| `ledger_id` | uuid | FK to commission_ledger |
| `policy_number` | text | Policy identifier |
| `carrier_name` | text | Carrier that underpaid/overpaid |
| `delta` | numeric | Discrepancy amount |
| `delta_percent` | numeric | Discrepancy as % of expected |
| `discrepancy_type` | text | Category of issue |
| `priority` | text | `low` / `medium` / `high` / `critical` |
| `status` | text | `open` / `in_progress` / `resolved` / `written_off` |
| `assigned_to` | text | Who's chasing it (default: "Lamar") |
| `resolution_notes` | text | What happened |
| `amount_recovered` | numeric | Money actually recovered |

#### `commission_rules` (reference)
Rate cards — 216 rules. Query: `carrier_name + lob + state + mga_name`, order by `lookup_priority ASC LIMIT 1`.

## Workflow

### Step 1: Ingest Statement Data
When a carrier commission statement arrives:
1. Parse each line item: policy_number, premium, commission_paid
2. For each line, look up the expected rate:
```
GET /rest/v1/commission_rules?carrier_name=eq.{CARRIER}&lob=eq.{LOB}&state=in.({STATE},ALL)&active=is.true&order=lookup_priority.asc&limit=1
```
3. Calculate expected: `gross_premium * nb_percent (or renewal_percent) / 100`
4. Apply split: `rsg_net = actual_commission * revenue_split_percent / 100`

### Step 2: Create/Update Ledger Entries
```
POST /rest/v1/commission_ledger
Content-Type: application/json
Prefer: return=representation

{
  "policy_number": "{POLICY}",
  "carrier_name": "{CARRIER}",
  "lob": "{LOB}",
  "client_name": "{CLIENT}",
  "mga_name": "{MGA}",
  "state": "{STATE}",
  "statement_date": "{DATE}",
  "gross_premium": {PREMIUM},
  "expected_commission": {EXPECTED},
  "actual_commission": {ACTUAL},
  "revenue_split_percent": {SPLIT},
  "rsg_net_commission": {NET},
  "commission_basis": "{BASIS}",
  "commission_rule_id": "{RULE_ID}",
  "policy_year": {YEAR},
  "reconciliation_status": "pending"
}
```

### Step 3: Detect Discrepancies
After inserting, query for mismatches:
```
GET /rest/v1/commission_ledger?reconciliation_status=eq.pending&select=*&order=statement_date.desc
```

**Tolerance rules:**
- Delta within +/- $1.00 → auto-set `reconciliation_status = 'matched'`
- Delta between $1-$50 → flag as `discrepancy`, priority `low`
- Delta between $50-$200 → flag as `discrepancy`, priority `medium`
- Delta > $200 → flag as `discrepancy`, priority `high`
- Delta > $500 → flag as `discrepancy`, priority `critical`

### Step 4: Create Reconciliation Records
For each discrepancy:
```
POST /rest/v1/commission_reconciliation
{
  "ledger_id": "{LEDGER_ID}",
  "policy_number": "{POLICY}",
  "carrier_name": "{CARRIER}",
  "client_name": "{CLIENT}",
  "statement_date": "{DATE}",
  "expected_commission": {EXPECTED},
  "actual_commission": {ACTUAL},
  "delta": {DELTA},
  "delta_percent": {DELTA_PCT},
  "discrepancy_type": "{TYPE}",
  "priority": "{PRIORITY}",
  "status": "open",
  "assigned_to": "Lamar"
}
```

**Discrepancy types:**
- `underpayment` — carrier paid less than expected
- `overpayment` — carrier paid more (verify before spending)
- `missing_payment` — expected commission, received $0
- `rate_mismatch` — rate applied doesn't match commission_rules
- `split_error` — MGA split calculated incorrectly
- `audit_adjustment` — WC/GL audit changed the premium basis

### Step 5: SmartChoice 70/30 Split Handling
For all SmartChoice policies (`mga_name = 'SmartChoice'`):
- `revenue_split_percent = 70`
- `rsg_net_commission = actual_commission * 0.70`
- SmartChoice retains 30%
- Verify SmartChoice statement matches: their 30% + RSG's 70% = carrier total
- If mismatch → flag as `split_error`

## Queries for Reporting

**Open discrepancies (money owed to RSG):**
```
GET /rest/v1/commission_reconciliation?status=eq.open&delta=lt.0&order=priority.desc,delta.asc&select=*
```

**Monthly commission summary:**
```
GET /rest/v1/commission_ledger?statement_date=gte.{MONTH_START}&statement_date=lt.{MONTH_END}&select=carrier_name,sum(actual_commission),sum(expected_commission),sum(rsg_net_commission)
```

**Chargeback exposure (unearned balance):**
```
GET /rest/v1/commission_ledger?unearned_balance=gt.0&select=policy_number,client_name,carrier_name,unearned_balance,chargeback_expiry_date&order=unearned_balance.desc
```

**Audit-adjustable policies (WC/GL pending audit):**
```
GET /rest/v1/commission_ledger?audit_adjustable=is.true&audit_status=is.null&select=*
```

## Output Format — Commission Flash

Post to **#growth-finance (C0AP89NDTHA)**:
```
💰 COMMISSION RECONCILIATION — {DATE}

STATEMENT: {CARRIER} — {STATEMENT_DATE}
Policies processed: {COUNT}
Expected total: ${EXPECTED}
Actual received: ${ACTUAL}
Delta: ${DELTA} {🟢 matched | 🔴 underpaid | 🟡 overpaid}

DISCREPANCIES FOUND:
🔴 {policy} — {client} | Expected: ${exp} | Got: ${act} | Delta: -${delta}
   Type: {discrepancy_type} | Priority: {priority}

OPEN ITEMS (cumulative):
Total open discrepancies: {count}
Total $ owed to RSG: ${sum_of_negative_deltas}
Oldest open item: {date} — {carrier} — ${amount}

CHARGEBACK EXPOSURE:
Total unearned balance: ${sum}
Highest risk: {policy} — ${unearned} (expires {date})
```

## Error Handling
- Commission rule not found for carrier/LOB → flag as `rate_mismatch`, use 0% as expected
- Duplicate ledger entry (same policy + statement_date) → update existing, don't create new
- Supabase connection failure → retry once, then alert #systems-check
