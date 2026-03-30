---
name: crm-manager
description: >
  Universal EspoCRM skill for Risk Solutions Group (RSG). Use this skill ANY time the user wants to add, create, view, search, update, edit, or log anything in the CRM — accounts, contacts, leads, opportunities, policies, renewals, commissions, tasks, calls, or meetings.
---

# CRM Manager — EspoCRM for RSG

**Base URL:** `https://rrespocrm-rsg-u69864.vm.elestio.app`

You are operating EspoCRM on behalf of the user. EspoCRM uses hash-based routing — jump directly to any module or record by constructing the right URL.

## Navigation Cheat Sheet

| What you want | URL pattern |
|---|---|
| Module list view | `{base}/#ModuleName` |
| Create a new record | `{base}/#ModuleName/create` |
| View/edit a specific record | `{base}/#ModuleName/view/{id}` |

**Module names (case-sensitive):** `Account`, `Contact`, `Lead`, `Opportunity`, `Policy`, `Renewal`, `Commission`, `Task`, `Call`, `Meeting`

## Module Field Reference

### Accounts
`Name`*, `Type` (Commercial/Personal Lines), `Account Status` (Active/Inactive), `Phone`, `Email`, `Billing Address`, `Assigned User`, `FEIN`, `Industry`, `Years In Business`, `Number of Employees`, `Description`

### Contacts
`First Name`*, `Last Name`*, `Account` (link), `Email`, `Phone`, `Date of Birth`, `Address`, `Account Title`, `Client Type`, `Household Role`, `CSR Name`, `Description`

### Leads
`First Name`*, `Last Name`*, `Account Name`, `Email`, `Phone`, `Status` (New/Assigned/In Process/Converted/Recycled/Dead), `Source`, `Insurance Interest`, `Priority`, `Currently Insured?`, `Current Carrier`, `Est. Premium`, `AI Summary`

### Opportunities
`Name`*, `Account` (link), `Line of Business`*, `Stage`* (Prospect → Qualified → Needs Analysis → Value Proposition → Proposal → Negotiation → Closed Won/Lost), `Close Date`*, `Est. Premium`, `Written Premium`, `Commission Rate`, `Est. Commission`, `Bind Date`, `Effective Date`

### Policies
`Name`*, `Status`* (Active/Expired/Cancelled/Renewing/Renewed), `Carrier`, `Line of Business`, `Effective Date`, `Expiration Date`, `Premium Amount`, `Commission Rate`, `Commission Amount`, `Account` (link)

### Renewals
`Account`*, `Expiring Policy`* (link), `Line of Business`, `Current Carrier`, `Pipeline Stage` (Identified → Outreach Sent → Quote Requested → Proposal Sent → Negotiating → Won/Lost), `Urgency`, `Expiration Date`, `Current Premium`, `Renewal Premium`, `Lost Reason`, `Renewal Notes`

> Pipeline entry: Commercial at 60 days, Personal Lines at 30 days.

### Commissions
`Commission Type`*, `Status`* (Estimated/Posted/Variance/Reconciled), `Account`* (link), `Policy`* (link), `Line of Business`, `Carrier`, `Written Premium`, `Commission Rate`, `Estimated Commission`, `Posted Amount`, `Variance Amount`, `Payment Received Date`

### Tasks
`Name`*, `Status` (Inbox/In Process/Completed/Deferred/Cancelled), `Task Type`, `Assigned User`*, `Date Due`, `Priority` (Normal/High/Urgent/Low), `Linked Account`

### Calls
`Name`*, `Parent` (link), `Status` (Planned/Held/Not Held), `Direction` (Outbound/Inbound), `Date Start`*, `Description`, `Attendees`

### Meetings
`Name`*, `Parent` (link), `Status`, `Date Start`*, `Date End`*, `Description`, `Attendees`

## Common Workflows

### Add a new account
1. `{base}/#Account/create` → Name, Type, Phone, Email, Status = Active → Save

### Log a call
1. `{base}/#Call/create` → Name, Direction, Date Start, Status = Held, link Parent → Save

### Create a follow-up task
1. `{base}/#Task/create` → Name, Type = Follow Up, Assigned User, Due Date, Priority, link Account → Save

### Move a renewal stage
1. `{base}/#Renewal` → filter by Account → Edit → change Pipeline Stage → Save

### Create an opportunity
1. `{base}/#Opportunity/create` → Name, Account, LOB, Stage, Close Date → Save

## Tips
- Search before creating — avoid duplicates
- Always link records — unlinked tasks and policies get lost
- Keep stages current — drives all pipeline reporting
- Use Description fields — full context for the whole team

## Error Handling
- Record not found → try phone, email, or partial name
- Save fails → check red-highlighted required fields
- 404 page → module names are case-sensitive in URLs

## Team Context
Two-person agency. Lamar = owner/producer, commercial sales. Gretchen = CSR, personal lines + renewals.
- Commercial alerts → Lamar
- Personal lines tasks → Gretchen
