---
name: book-health-monitor
description: >
  Weekly agency book health scorecard for RSG. Pulls live data from NowCerts,
  EspoCRM, and Supabase to generate a single boss-level snapshot of premium,
  retention, pipeline, renewals, and Gate progress. Posts to #the-boss.
  Triggers on "book health", "book check", "how's the book", "agency scorecard",
  "weekly scorecard", or on the Monday 10am ET auto-schedule.
  Revenue-critical — uses Anthropic. Always compare to prior Supabase snapshot.
Last Updated: 2026-03-31
---

# Book Health Monitor

## Purpose
Generate a weekly Book Health Scorecard and post to **#the-boss (C0ANQUENX4P)**.
Lamar should never have to wonder how the agency is doing. This agent answers that
question every Monday before the week kicks off — and on demand any time he asks.

---

## Trigger Phrases
- "book health"
- "book check"
- "how's the book"
- "agency scorecard"
- "weekly scorecard"

**Scheduled:** Every Monday 10:00 AM ET

---

## Data Sources

| Source | What We Pull |
|--------|-------------|
| NowCerts | Active premium, policy count, client count, retention rate, expiring policies |
| EspoCRM | Open opportunity pipeline value + stage breakdown |
| Supabase (agency_snapshots) | Prior snapshot for week-over-week delta |

---

## Scorecard Output Format

```
📋 *RSG BOOK HEALTH — {day} {date}*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *THE BOOK*
• Premium: *${active_premium}* (↑/↓ $X WoW)
• Policies: *{policy_count}* (↑/↓ X WoW) | Clients: *{client_count}*

🔄 *RETENTION*
• Rate: *{retention_rate}%* → Target: 75% | Gap: X pts
• Status: [🔴 CRITICAL <55% | ⚠️ BELOW TARGET <60% | 🟡 IMPROVING <65% | 🟢 ON TRACK <75% | ✅ HIT 75%+]
• WoW: ↑/↓ X.XX pts

💰 *PIPELINE*
• Open Value: *${pipeline_value}* across {deal_count} deals
• Top stages: {stage_summary}

⚠️ *RENEWAL RADAR*
• 🔴 ≤14 days: X policies ($X at risk)
• 🟡 15–30 days: X policies ($X)
• 📋 31–60 days: X policies ($X)
• 📋 61–90 days: X policies ($X)

🎯 *GATE 1 PROGRESS* ($425K / 60% retention)
• {gate_status}

[🚨 CRITICAL RENEWALS block — only if ≤14 day policies exist]
```

---

## Gate 1 Logic

- **Target:** $425,000 premium AND 60% retention
- Both cleared → `🎉 GATE 1 UNLOCKED`
- Retention only → `✅ Retention cleared — need $X more premium`
- Premium only → `✅ Premium cleared — need X.X pts more retention`
- Neither → `🔒 XX% premium / XX% retention`

---

## Agent Config

| Setting | Value |
|---------|-------|
| LLM | Anthropic (revenue-critical) |
| Output | #the-boss (C0ANQUENX4P) |
| Schedule | Monday 10:00 AM ET |
| On-demand | Yes |
| Gretchen-facing | No |
| Skills | nowcerts-skill, crm-manager, commission-reconciliation |

---

## Related
- [[HEARTBEAT]] — scheduled task registration
- [[nowcerts-skill]] — NowCerts API integration
- [[crm-manager]] — EspoCRM pipeline pull
- [[commission-reconciliation]] — Supabase agency_snapshots
