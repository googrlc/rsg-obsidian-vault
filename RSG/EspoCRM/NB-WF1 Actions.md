# NB-WF1 — Deal Won Intake & Commission Log
**n8n ID:** UFwZUwlHi1ERwSXP  |  Status: BROKEN — stage string mismatch
**Audited:** March 2026 from actual workflow JSON

---

## What It Actually Does

Polls EspoCRM hourly for Won deals, writes commission to Supabase,
posts Slack alert with action buttons, marks deal commission-logged in EspoCRM.

Critical facts from actual JSON:
- Commission writes to Supabase commission_ledger table — NOT EspoCRM
- Emails are NOT auto-triggered — Slack button fires WF2 manually
- WF2 only runs when Lamar clicks "Send Onboarding Emails" in Slack
- Gmail OAuth2 is NOT configured in WF2 (placeholder still in place)
- OpenClaw handles emails manually from template until Gmail is set up

---

## Node-by-Node Flow

Node 1 — Schedule Trigger (Every Hour)
Starts workflow on hourly schedule.

Node 2 — Query Won Deals (HTTP GET)
GET /api/v1/Opportunity | Auth: X-Api-Key header
BROKEN FILTER: stage = "Won - Bound"
CORRECT VALUE:  stage = "✅ Won - Bound"
Also filters: commissionLogged = false
Selects: id, name, amount, closeDate, accountId, accountName, cLineOfBusiness,
cCarrier, cEstimatedPremium, cWrittenPremium, cCommissionLogged, cClientEmail,
cBindDate, cCommissionRate

Node 3 — Extract Deals (Code)
Loops response. Skips already-logged deals. Maps to clean deal object.
Returns _empty flag if nothing found.

Node 4 — Has Deals? (IF)
True: continue. False: stop entirely.

Node 5 — Loop Each Deal (Split in Batches)
One deal at a time through remaining nodes.

Node 6 — Prepare Commission Data (Code)
Maps LOB to category (Commercial Lines, Personal Lines, Life, Medicare, etc.)
Builds commission row: opportunityId, clientName, lob, carrier,
annual_premium, commission_rate (default 10%), lamar_split (1.0), bound_date, notes.

Node 7 — Create Commission Entry (POST to Supabase)
POST wibscqhkvpijzqbhjphg.supabase.co/rest/v1/commission_ledger
Auth: Supabase credential ID orQ76IQmpakFh3sm
Header: Prefer = return=representation (gets back new row ID)
onError: continueRegularOutput

Node 8 — Store Commission Page ID (Code)
Extracts Supabase commission record ID. Passes as commissionPageId.

Node 9 — Build Slack Message (Code)
Block Kit payload to channel C0AFYMES6DU (hardcoded — verify channel)
Shows: client, LOB, carrier, premium, effective date.
Button 1 "Send Onboarding Emails": webhook rsg-onboarding-trigger?dealId={id}
Button 2 "View Deal": EspoCRM record link.
Sets commissionCreated flag.

Node 10 — Commission OK? (IF)
True: mark logged + post Slack. False: skip to next deal.

Node 11 — Mark Commission Logged (PATCH EspoCRM)
PATCH /api/v1/Opportunity/{dealId} | Body: { cCommissionLogged: true }
Auth: X-Api-Key | onError: continueRegularOutput

Node 12 — Slack: Commission Logged (POST)
Posts Block Kit from Node 9. Auth: Slack credential rTNF4McInN9GXdlG.
Loops back to Node 5 for next deal.

---

## THE FIX — Node 2 Filter Value

CURRENT (broken):  stage = "Won - Bound"
CORRECT:           stage = "✅ Won - Bound"

Verify first on a known Won deal:
GET /api/v1/Opportunity?select=id,stage&maxSize=5&where[0][type]=equals&where[0][attribute]=stage&where[0][value]=Won

---

## Dependencies

EspoCRM stage string — must match exactly — FIX NEEDED
EspoCRM API Key — e5df7c321b47427d24046bab814dbb58 — OK
Supabase credential — ID orQ76IQmpakFh3sm — verify active
commission_ledger table — Supabase project wibscqhkvpijzqbhjphg — verify exists
Slack API credential — ID rTNF4McInN9GXdlG — OK
Slack channel — C0AFYMES6DU — verify correct
Gmail OAuth2 for WF2 — REPLACE_WITH_GMAIL_CREDENTIAL_ID — NOT CONFIGURED

---

## Email Strategy — OpenClaw Bridge

Gmail OAuth2 not set up. Until it is:
1. WF1 fires Slack alert with deal details
2. Do NOT click "Send Onboarding Emails" — emails won't send
3. Ask OpenClaw for the Day 0 email template for the client
4. Send manually from Gmail
5. When Gmail OAuth2 is configured: re-enable WF2 nodes and button goes live

---

## Downstream

NB-WF2 (Day 0 and Day 1 emails) — Slack button triggers webhook rsg-onboarding-trigger
NB-WF3 (Day 7-60 nurture) — called by WF2 after Day 1 email sends
