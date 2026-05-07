# RSG Growth Strategy Checklist

Last Updated: 2026-05-07
Owner: Lamar Coates
North Star: **$1M Annual Premium**

---

## Current State Snapshot

| Metric | Value | Notes |
|---|---|---|
| Active Premium | ~$385K | As of Q2 2026 |
| Total Policies | 104 | Across all LOBs |
| Total Clients | 81 | Active accounts |
| Largest LOB | Commercial Auto (~39%) | Key niche advantage |
| Retention Rate | ~55% | CRITICAL - must improve to 80%+ |
| Gap to $1M | ~$615K | Need to 2.6x current book |

---

## Phase 1: Stop the Bleeding (Retention Fix)
Target: Raise retention from ~55% to 80%+

- [ ] **Project 85 - Renewal Enforcement**
  - [ ] Deploy 90/60/30 day renewal touchpoint automation in n8n
  - [ ] Build Hermes renewal risk scoring (flag at-risk accounts)
  - [ ] Create Gretchen daily renewal queue (auto-generated task list)
  - [ ] Establish renewal review SOP (who does what, when)
  - [ ] Track retention rate monthly in Supabase `agency_snapshots`

- [ ] **Anti-Ghosting Protocol**
  - [ ] Hermes monitors for clients going silent (no contact > 60 days)
  - [ ] Auto-trigger re-engagement sequence
  - [ ] Escalation path: Hermes alert -> Slack #the-boss -> Lamar outreach

- [ ] **Service Quality Baseline**
  - [ ] Document response time targets (24hr acknowledgment, 48hr resolution)
  - [ ] Weekly service quality check-in with Gretchen
  - [ ] Client satisfaction pulse (quarterly NPS or simple survey)

---

## Phase 2: Maximize Existing Book (Cross-Sell & Upsell)
Target: +$100K premium from existing clients

- [ ] **Commercial Auto Cross-Sell Campaign**
  - [ ] Identify commercial auto clients missing GL, WC, or umbrella
  - [ ] Build OpenClaw research packs for top 20 cross-sell opportunities
  - [ ] Draft personalized outreach templates
  - [ ] Track conversion rate per campaign wave

- [ ] **Coverage Gap Analysis**
  - [ ] Run book-wide coverage gap report (EspoCRM query)
  - [ ] Prioritize by revenue opportunity (premium gap x close probability)
  - [ ] Assign top 10 gaps to Lamar pipeline this quarter

- [ ] **Account Rounding**
  - [ ] Identify single-policy households/businesses
  - [ ] Bundle opportunities (auto + home, BOP + WC + commercial auto)
  - [ ] Monthly "account rounding" outreach block (2 hours/week)

---

## Phase 3: New Business Engine
Target: +$200K premium from net-new clients

- [ ] **Commercial Auto / Trucking Niche**
  - [ ] Formalize trucking specialization positioning
  - [ ] Build DOT/FMCSA-powered lead research workflow (OpenClaw)
  - [ ] Carrier appetite matrix for commercial auto (Progressive, CNA, etc.)
  - [ ] Target: 5 new commercial auto accounts/month

- [ ] **Lead Pipeline System**
  - [ ] EspoCRM lead-to-opportunity workflow documented
  - [ ] Lead scoring model (industry, fleet size, premium potential)
  - [ ] Weekly pipeline review ritual (30 min, Fridays)
  - [ ] Track: leads in -> quotes out -> policies bound -> premium written

- [ ] **Digital Presence & Inbound**
  - [ ] Agency website refresh (insurtech positioning)
  - [ ] Google Business Profile optimization
  - [ ] Content strategy: 1 post/week on commercial auto risk topics
  - [ ] Referral program for existing clients

---

## Phase 4: Systems & Scale
Target: Infrastructure that supports $1M+ without burning out

- [ ] **Book Health Monitor**
  - [ ] Weekly automated scorecard to #the-boss Slack channel
  - [ ] Metrics: premium, retention, pipeline value, policies bound
  - [ ] Powered by Supabase `agency_snapshots` + Hermes

- [ ] **Sentinel - Commission Auditing**
  - [ ] Automated commission reconciliation vs. expected
  - [ ] Flag missing/short payments
  - [ ] Monthly commission health report

- [ ] **Gretchen Force Multiplier**
  - [ ] Morning task queue automation (plain English, prioritized)
  - [ ] Service request routing and tracking
  - [ ] Renewal prep packet auto-generation

- [ ] **Agent Operational Maturity**
  - [ ] Hermes: anti-ghosting + renewal alerts + KPI reporting
  - [ ] OpenClaw: field research + underwriting support
  - [ ] Dify: client-facing intake and portal
  - [ ] All agents documented with SKILL.md files in vault

---

## Revenue Math

```
Current Book:     $385K
Retention Fix:    +$60K  (saving 15% of what we'd lose)
Cross-Sell:       +$100K (existing client expansion)
New Business:     +$200K (net-new commercial auto focus)
Organic Growth:   +$55K  (rate increases, natural growth)
                  -------
Projected:        $800K  (Year 1 realistic target)

Year 2 push to $1M with compounding retention + pipeline maturity
```

---

## Weekly Ritual Checklist

| Day | Block | Duration | Focus |
|---|---|---|---|
| Monday | Pipeline Review | 30 min | Review EspoCRM opportunities, prioritize week |
| Tue-Thu | Outreach Block | 2 hrs/day | New business calls, cross-sell touches |
| Wednesday | Gretchen Sync | 15 min | Service queue, renewal status, blockers |
| Friday | Book Health | 30 min | Review Hermes scorecard, adjust strategy |

---

## Accountability
- This checklist lives in `04-Strategy/Growth/`
- Monthly review: first Monday of each month
- Hermes flags if no progress logged in 2+ weeks
- Lamar's #1 job: revenue-generating activity, not tech rabbit holes
