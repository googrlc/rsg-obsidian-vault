---
name: linkedin-prospecting
description: >
  LinkedIn prospecting skill targeting contractors and fleet operators. 3-touch outreach sequence, daily activity targets (5-10 connects, 5 messages), and EspoCRM lead logging.
---

# LinkedIn Prospecting — Contractor & Fleet Targeting

**Goal:** Generate warm leads from LinkedIn by connecting with contractors and fleet operators in RSG's target markets. Every connection gets logged to EspoCRM.

## Target Profiles

### Primary: Contractors
- **Titles:** Owner, President, VP Operations, Safety Director, Office Manager
- **Industries:** Roofing, General Contracting, Concrete, Excavation/Grading, Electrical, Plumbing/HVAC, Landscaping, Hauling
- **Geography:** GA, AL, FL, SC, TN (RSG's active states)
- **Company size:** 5-100 employees (sweet spot for commercial package)

### Secondary: Fleet Operators
- **Titles:** Owner, Fleet Manager, Safety Director, Operations Manager
- **Industries:** Trucking, Transportation, Hauling, Last-Mile Delivery, Auto Dealers
- **Geography:** Same states
- **Fleet size:** 3-50 vehicles

### Signals to Watch For
- Recently started a business (new LLC filings — cross-ref with Market Radar)
- Growing headcount (hiring posts)
- New equipment or vehicle posts
- Complaints about insurance costs or claims
- License/permit posts

## Daily Activity Targets

| Activity | Target | Notes |
|---|---|---|
| Profile views | 20-30 | Browse target profiles to trigger "who viewed" |
| Connection requests | 5-10 | With personalized note (Template 8 from outreach-templates) |
| Messages to connections | 5 | Follow-up on accepted connections |
| Content engagement | 5-10 | Like/comment on target prospects' posts |

## 3-Touch Outreach Sequence

### Touch 1: Connection Request (Day 0)
Use Template 8 (LinkedIn) from `AI_Knowledge/Skills/outreach-templates.md`:
```
{FIRST_NAME}, I insure {INDUSTRY} companies across {STATE}. Saw {COMPANY} and thought we might be a good connection. Always happy to be a resource on the insurance side — no pitch, just here if you need a second opinion.
```

**After sending:** Log to EspoCRM as Lead:
```
POST /api/v1/Lead
{
  "firstName": "{FIRST}",
  "lastName": "{LAST}",
  "accountName": "{COMPANY}",
  "status": "New",
  "source": "LinkedIn",
  "description": "LinkedIn connection request sent {DATE}. Industry: {INDUSTRY}. Title: {TITLE}."
}
```

### Touch 2: Value Message (Day 2-3, after connection accepted)
```
Thanks for connecting, {FIRST_NAME}. I specialize in {LOB_LIST} for {INDUSTRY} operators.

Quick question — are you up for renewal in the next few months? The market for {INDUSTRY} coverage has shifted recently, and I've been finding better rates for companies your size.

Either way, I'm an open book if you ever need a second opinion on your insurance program.
```

**After sending:** Update EspoCRM Lead status to `Assigned`.

### Touch 3: Specific Value / Ask (Day 7-10)
Personalize based on what you've learned:
```
{FIRST_NAME}, I was looking at the {INDUSTRY} market in {CITY/STATE} and thought of you.

{One of these hooks:}
- "I just got a carrier to sharpen their pencil on {LOB} for {INDUSTRY} — rates are down 10-15% from last year."
- "I noticed {COMPANY} is growing — congrats. When you add trucks/employees/subs, your coverage needs to keep up. Happy to do a quick gap check."
- "A {INDUSTRY} client of mine just saved $X by restructuring their GL/WC program. Want me to take a look at yours?"

Worth a 10-minute call this week?
```

**After sending:** Update EspoCRM Lead status to `In Process`.

### If No Response After Touch 3
- Wait 30 days
- Engage with their content (like/comment) for 1-2 weeks
- Try one more direct message with fresh value
- If still no response → update Lead status to `Recycled`, set task to re-engage in 90 days

### If They Reply
- Move Lead to `In Process` immediately
- If they share renewal date → create EspoCRM Opportunity with close date
- If they want a quote → run prospect-researcher skill, then hand off to quoting workflow
- Post to **#the-boss**: "🎯 LinkedIn lead engaged: {NAME} at {COMPANY} — {next step}"

## EspoCRM Lead Logging

Every LinkedIn prospect gets a Lead record. Read `AI_Knowledge/Skills/crm-manager.md` for API details.

**Required fields:**
- `firstName`, `lastName`
- `accountName` (company)
- `source`: always `"LinkedIn"`
- `status`: track through `New` → `Assigned` → `In Process` → `Converted` (or `Dead`)
- `description`: include LinkedIn profile URL, industry, touch history

**Convert to Opportunity when:**
- Prospect confirms a renewal date
- Prospect requests a quote
- Prospect agrees to a call

## Weekly LinkedIn Report

Post to **#the-boss** every Friday:
```
📊 LINKEDIN PROSPECTING — Week of {DATE}

Connections sent: {count}
Connections accepted: {count} ({accept_rate}%)
Messages sent: {count}
Replies received: {count} ({reply_rate}%)
Leads created in CRM: {count}
Calls scheduled: {count}

TOP PROSPECTS:
• {Name} — {Company} — {Industry} — {Status}
• {Name} — {Company} — {Industry} — {Status}

NEXT WEEK FOCUS:
- {industry/geography to target}
- {follow-ups due}
```

## Content Strategy (Engagement Bait)
Suggest posts for Lamar to publish that attract contractor/fleet audiences:
- "3 coverage gaps I see in every roofing contractor's policy"
- "Your trucking insurance is probably wrong — here's how to check"
- "What your GL class code actually means for your premium"
- "Why your sub's COI isn't protecting you"

## Error Handling
- EspoCRM down → queue leads in a local note, bulk-create when back up
- Duplicate lead detected → update existing Lead with new touch info, don't create duplicate
- LinkedIn rate limits → reduce daily activity, focus on quality over quantity
