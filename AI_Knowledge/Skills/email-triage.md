---
name: email-triage
description: >
  Email triage skill with 5 priority categories. Routes emails to Lamar (Now/Today) or Gretchen (personal lines/service), drafts responses, applies Gmail labels, and archives low-value messages.
---

# Email Triage — 5-Category Routing

**Goal:** Zero inbox noise. Every email categorized, routed, and either responded to or queued within minutes.

## Priority Categories

| Priority | Label | Who | Response Time | Examples |
|---|---|---|---|---|
| 🔴 **Lamar Now** | `RSG/Lamar-Now` | Lamar | < 1 hour | Carrier underwriting questions, bind requests, claims reported, referral from producer |
| 🟡 **Lamar Today** | `RSG/Lamar-Today` | Lamar | Same day | Quote requests, renewal discussions, prospect follow-ups, carrier updates |
| 🟢 **Gretchen** | `RSG/Gretchen` | Gretchen | Same day | Personal lines service, endorsements, COI requests, payment questions, ID cards |
| ⚪ **Low Priority** | `RSG/Low-Priority` | Either | This week | Marketing emails from carriers, training webinars, industry newsletters, non-urgent vendor emails |
| 🗑️ **Archive** | — | Nobody | Never | Spam, promotional, unsubscribe-worthy, duplicate notifications |

## Routing Rules

### 🔴 Lamar Now
- Subject contains: "bind", "claim", "urgent", "ASAP", "underwriting question"
- From a carrier underwriter or MGA
- Contains a referral or warm introduction
- Money on the table — quote ready to bind, commission dispute, payment issue
- Renewal expiring in < 14 days

### 🟡 Lamar Today
- New quote request (not yet urgent)
- Carrier appetite or rate change announcements
- Prospect replied to outreach
- Renewal 15-60 days out
- EspoCRM opportunity-related correspondence

### 🟢 Gretchen
- Personal lines anything: home, auto, renters, umbrella
- Service requests: endorsements, add vehicle, address change, COI
- Payment questions or billing issues
- ID card requests
- Client asking about their policy details (not sales)
- From known personal lines clients

### ⚪ Low Priority
- Carrier marketing / new product announcements
- CE/training webinar invitations
- Industry newsletters (IA Magazine, Insurance Journal, etc.)
- Vendor sales pitches (not insurance prospects)
- System notifications (NowCerts alerts, EspoCRM notifications)

### 🗑️ Archive
- Pure spam / promotional
- Newsletters the agency didn't subscribe to
- Duplicate system notifications
- Social media notifications
- Subscription renewal reminders for non-critical tools

## Draft Response Templates

### For Quote Requests (Lamar Today)
```
{FIRST_NAME},

Thanks for reaching out. I'd be happy to put together some options for you.

To get started, I'll need:
- Current policy dec page (if you have one)
- {LOB-specific items: fleet schedule / payroll by class code / property schedule}
- Any claims in the last 3 years

I can usually turn quotes around in 24-48 hours once I have the above. What's the best number to reach you?

Lamar Coates
Risk Solutions Group
```

### For COI Requests (Gretchen)
```
Hi {FIRST_NAME},

We'll get that certificate out to you. Can you confirm:
- Certificate holder name and address
- Any specific requirements (additional insured, waiver of subrogation, primary/non-contributory)?
- Deadline?

We'll have it over as soon as we have the details.

Best,
Gretchen — Risk Solutions Group
```

### For Bind Requests (Lamar Now)
```
{FIRST_NAME},

Got it — binding this now. I'll send confirmation and the binder once it's processed.

A few things I'll need to finalize:
- {Any missing info}
- Payment method preference (pay-in-full or monthly)
- Effective date confirmation: {DATE}

Lamar Coates
Risk Solutions Group
```

### For Claims Reported (Lamar Now)
```
{FIRST_NAME},

I'm sorry to hear about this. Let me get this reported to {CARRIER} right away.

I'll need:
- Date and time of the incident
- Brief description of what happened
- Any injuries or third-party involvement
- Photos if available

I'll file the claim and get you a claim number and adjuster contact ASAP.

Lamar Coates
Risk Solutions Group
```

## Gmail Label Structure

Create these labels if they don't exist:
```
RSG/
  Lamar-Now
  Lamar-Today
  Gretchen
  Low-Priority
  Clients/
    {Client Name}
  Carriers/
    {Carrier Name}
```

## Workflow

### Step 1: Read Incoming Email
Use Gmail MCP tools to fetch unread messages:
- Check sender against EspoCRM contacts (via crm-manager skill)
- Check subject line against routing rules
- Check body content for keywords

### Step 2: Categorize
Apply the appropriate Gmail label based on routing rules above.

### Step 3: Draft Response (if applicable)
For 🔴 and 🟡 emails:
- Draft a response using the appropriate template
- Pull relevant data from EspoCRM (account, policies, opportunities)
- Save as Gmail draft — Lamar reviews and sends

For 🟢 emails:
- Draft response for Gretchen
- Post summary to **#client-service (C0AP4MHCLLS)**

### Step 4: Log Activity
For any client-related email:
- Log a note or update in EspoCRM on the relevant Account/Contact
- If it relates to an open Opportunity or Renewal, update the record

### Step 5: Archive
For 🗑️ emails:
- Archive immediately
- If sender is a repeat offender → suggest unsubscribe

## Daily Email Digest

Post to **#the-boss (C0ANQUENX4P)** at 8 AM:
```
📧 EMAIL TRIAGE — {DATE}

🔴 LAMAR NOW ({count}):
• {Subject} — from {Sender} — {1-line summary}

🟡 LAMAR TODAY ({count}):
• {Subject} — from {Sender} — {1-line summary}

🟢 GRETCHEN ({count}):
• {Subject} — from {Sender} — {1-line summary}

⚪ LOW PRIORITY ({count}): Labeled and queued
🗑️ ARCHIVED ({count}): Nothing to see here

DRAFTS READY FOR REVIEW: {count}
```

## Error Handling
- Gmail API failure → retry once, then alert #systems-check
- Unknown sender (not in EspoCRM) → default to 🟡 Lamar Today, suggest creating a Lead
- Ambiguous routing (could be Lamar or Gretchen) → default to 🟡 Lamar Today with note
