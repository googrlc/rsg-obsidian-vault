# RSG Intake Pipeline

## Overview
Daily automated document processor for Risk Solutions Group.
Watches `/Users/lamarcoates/Documents/RSG/00 Inbox` for new files,
parses them with Claude AI, and routes extracted data to Supabase + EspoCRM.

## Folder Structure
```
00 Inbox/           ← Drop files here
  processed/        ← Auto-moved after successful parse
  failed/           ← Auto-moved if parse fails
  intake.log        ← Daily run log
```

## Supported Document Types
| Type | What gets extracted | Destination |
|---|---|---|
| Dec Page (PDF) | Client, carrier, LOB, premium, policy#, eff/exp dates | Supabase risk_assessments + EspoCRM Account |
| ACORD Application | Business info, exposures, vehicles, payroll | Triggers full assessment |
| Commission Statement | Carrier, policy#, premium, commission amount | Supabase commission_ledger |
| Call Transcript | Client name, pain points, coverage discussed, next steps | EspoCRM Note + Lead update |
| Loss Run | Claim history, total incurred, loss ratio | Risk assessment red flags |
| COI | Certificate holder, coverage limits, expiry | EspoCRM Account note |

## Schedule
Runs daily at 9:00 AM via launchd (macOS cron alternative)
Manual run: `python3 /Users/lamarcoates/Documents/Obsidian\ Vault/RSG\ Intake\ Pipeline/rsg-intake-pipeline.py`

## Setup
1. Install dependencies: `pip3 install anthropic requests pymupdf --break-system-packages`
2. Set env vars in `~/.zshenv`:
   - `ANTHROPIC_API_KEY`
   - `SLACK_BOT_TOKEN`
3. Install launchd job: `cp com.rsg.intake.plist ~/Library/LaunchAgents/ && launchctl load ~/Library/LaunchAgents/com.rsg.intake.plist`

## Files
- `rsg-intake-pipeline.py` — main script
- `com.rsg.intake.plist` — macOS launchd scheduler
- `README.md` — this file
