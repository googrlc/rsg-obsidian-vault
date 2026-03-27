# EspoCRM Custom Fields Setup
*Applied by Claude Code — 2026-03-22*

## Opportunity Custom Fields

### Already Existed (skipped — N8N workflows already reference these)
| Field | Type | Notes |
|-------|------|-------|
| lineOfBusiness | enum (25 options) | Replaces planned `cLob` — superset of requested options |
| carrier | varchar (255) | Replaces planned `cCarrier` |
| writtenPremium | currency | Replaces planned `cPremium` (also has `estimatedPremium`) |
| emailSequenceStarted | bool | Replaces planned `cEmailSequenceStarted` |
| commissionLogged | bool | Replaces planned `cCommissionLogged` |

### Newly Added
| Field | Type | Status |
|-------|------|--------|
| cClientEmail | email | Added |
| cRenewalDate | date | Added |

## Case Status Values Added
Full status list now available:
- New
- Assigned
- Pending
- Day 0 Sent
- Day 1 Sent
- Day 7 Sent
- Day 14 Sent
- Day 30 Sent
- Day 60 Sent
- Sequence Complete
- Opted Out
- Closed
- Rejected
- Duplicate

## N8N Workflow Audit
All 16 workflows were exported and searched — none reference `c`-prefixed field names. All already use the correct existing field names (`lineOfBusiness`, `carrier`, `emailSequenceStarted`, `commissionLogged`, `writtenPremium`).

## Cache Cleared
Yes — `clear-cache` and `rebuild` run via Docker exec on 2026-03-22

## Verification
All fields and statuses confirmed present via EspoCRM Metadata API.
