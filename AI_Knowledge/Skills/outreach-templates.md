---
name: outreach-templates
description: >
  8 outreach message templates for RSG sales and retention: cold contractor, cold fleet, follow-up, renewal notice, renewal proposal, win-back, referral request, and LinkedIn connection. Personalize with CRM and carrier data.
---

# Outreach Templates — RSG Sales & Retention

**Usage:** Agent selects the appropriate template, fills variables from EspoCRM + NowCerts + Supabase data, and drafts the message. All messages should sound like Lamar — direct, knowledgeable, no fluff.

## Template 1: Cold Outreach — Contractor

**Use when:** Prospect is a roofing, GC, concrete, excavation, electrical, plumbing, or HVAC company.

**Subject:** Quick question about your {LOB} coverage, {FIRST_NAME}

```
{FIRST_NAME},

I noticed {COMPANY} is doing {INDUSTRY} work in {STATE}. We specialize in insuring contractors like you — GL, workers comp, commercial auto, and tools/equipment.

Most {INDUSTRY} operators I talk to are either overpaying or have coverage gaps they don't know about (especially around subcontractor liability and height exclusions).

Would it be worth 10 minutes to see if we can do better than what you've got? No pressure — I'll give you a straight answer either way.

Lamar Coates
Risk Solutions Group
{PHONE} | {EMAIL}
```

## Template 2: Cold Outreach — Fleet / Trucking

**Use when:** Prospect is a trucking, hauling, or transportation company.

**Subject:** Fleet insurance for {COMPANY} — quick compare?

```
{FIRST_NAME},

I work with fleet operators across {STATE} and wanted to reach out. We've got direct appointments with carriers that specialize in {FLEET_SIZE}-truck operations and understand the DOT compliance side.

If you're coming up on renewal or just want a second set of eyes on your current program, I'd be happy to run a quick comparison — commercial auto, GL, cargo, and workers comp.

Takes about 15 minutes on the phone. Worth a look?

Lamar Coates
Risk Solutions Group
{PHONE} | {EMAIL}
```

## Template 3: Follow-Up (After No Response)

**Use when:** 5-7 days after initial outreach with no reply.

**Subject:** Re: {ORIGINAL_SUBJECT}

```
{FIRST_NAME},

Just circling back — I know you're busy running {COMPANY}.

I put together a quick look at what carriers are actively writing {INDUSTRY} in {STATE} right now. Happy to share what I found if you have 5 minutes this week.

No strings attached — if your current program is solid, I'll tell you that too.

Lamar
```

## Template 4: Renewal Notice (Early Touch)

**Use when:** 45 days (commercial) or 21 days (personal) before expiration.

**Subject:** Your {LOB} policy renewal is coming up — {COMPANY}

```
{FIRST_NAME},

Your {LOB} policy with {CURRENT_CARRIER} expires on {EXP_DATE}. I wanted to get ahead of it so we have time to review options.

A couple of questions before I start:
1. Any changes to your operations since last year? (New vehicles, employees, locations, revenue?)
2. Any claims or issues with {CURRENT_CARRIER} I should know about?

I'll pull the renewal terms and shop 2-3 alternatives so you have a real comparison — not just a blind renewal.

Talk soon,
Lamar Coates
Risk Solutions Group
```

## Template 5: Renewal Proposal (Options Delivery)

**Use when:** 30 days (commercial) or 14 days (personal) before expiration, after quoting.

**Subject:** Your renewal options — {COMPANY} {LOB}

```
{FIRST_NAME},

Here's what I've got for your {LOB} renewal (current policy expires {EXP_DATE}):

OPTION 1: {CARRIER_1} — ${PREMIUM_1}/year
{Key coverage notes, limits, deductible}

OPTION 2: {CARRIER_2} — ${PREMIUM_2}/year
{Key coverage notes, limits, deductible}

OPTION 3: Stay with {CURRENT_CARRIER} — ${RENEWAL_PREMIUM}/year
{What changed from last year}

My recommendation: {RECOMMENDATION and why}

Let me know when you have 10 minutes to walk through these. We need to bind by {BIND_DEADLINE} to avoid a lapse.

Lamar Coates
Risk Solutions Group
```

## Template 6: Win-Back (Lost Client)

**Use when:** Client left 6-10 months ago, approaching their next renewal.

**Subject:** Checking in — {COMPANY}

```
{FIRST_NAME},

It's been about {MONTHS} months since we last worked together on your {LOB} coverage. I hope {NEW_CARRIER} has been treating you well.

With your renewal coming up around {ESTIMATED_EXP}, I wanted to see if it's worth getting a fresh comparison. The market has shifted — some carriers have gotten more aggressive on {INDUSTRY} rates, and I may be able to put together something better.

No hard feelings either way. Just don't want you renewing on autopilot without seeing what's out there.

Lamar
```

## Template 7: Referral Request

**Use when:** After a successful bind or positive client interaction.

**Subject:** Quick favor, {FIRST_NAME}?

```
{FIRST_NAME},

Glad we got your {LOB} coverage locked in. If you know any other {INDUSTRY} operators who might benefit from a second look at their insurance, I'd appreciate the introduction.

I work the same way with everyone — straight answers, real options, no runaround.

Thanks for trusting us with your business.

Lamar Coates
Risk Solutions Group
```

## Template 8: LinkedIn Connection Request

**Use when:** Connecting with a contractor, fleet operator, or business owner on LinkedIn.

**Short version (300 char limit):**
```
{FIRST_NAME}, I insure {INDUSTRY} companies across {STATE}. Saw {COMPANY} and thought we might be a good connection. Always happy to be a resource on the insurance side — no pitch, just here if you need a second opinion.
```

**Follow-up message (after connection accepted):**
```
Thanks for connecting, {FIRST_NAME}. I specialize in {LOB_LIST} for {INDUSTRY} operators. If you're ever shopping coverage or just want a sanity check on what you're paying, I'm an open book. What's the best way to reach you outside of LinkedIn?
```

## Personalization Rules

Before sending any template:
1. **Check EspoCRM** (via crm-manager skill) — pull account, contact, and opportunity data
2. **Check NowCerts** (via nowcerts-skill) — pull current policy details if they're an existing client
3. **Check carrier appetite** (via carrier-appetite skill) — reference specific carriers and rates
4. **Customize** — replace generic industry language with specific details from their business

## Tone Guidelines
- Lamar's voice: direct, confident, no jargon, no hard sell
- Always offer value before asking for anything
- Keep emails under 150 words (except renewal proposals)
- One clear CTA per message
- Never use "just checking in" without adding value
