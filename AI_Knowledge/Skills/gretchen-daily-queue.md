---
name: gretchen-daily-queue
description: >
  Generates a plain-English daily task queue for Gretchen (Personal Lines
  Specialist) and posts to #gretchen-tasks every weekday at 8:30am ET.
  Also triggered on "gretchen queue", "gretchen tasks", "what does gretchen have today",
  "gretchen's list", or "queue for gretchen".
  Gretchen-facing: zero jargon, zero insurance-speak, plain action steps only.
  Uses Gemini. Frees Lamar from being Gretchen's task dispatcher.
---

# Gretchen Daily Queue

## Purpose
Gretchen should start every day knowing exactly what to do — in what order —
without having to ask Lamar. This agent replaces the daily "what should I work
on?" conversation and gives Gretchen a clear, prioritized action list every morning.

No jargon. No EspoCRM navigation instructions. Just: here's what to do today.

---

## Trigger Phrases
- "gretchen queue"
- "gretchen tasks"
- "what does gretchen have today"
- "gretchen's list"
- "queue for gretchen"

**Scheduled:** Weekdays 8:30 AM ET (before Gretchen's workday starts)

---

## Step 1 — Pull Gretchen's Open Tasks from EspoCRM

GET https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1/Task
  ?where[0][type]=notEquals&where[0][attribute]=status&where[0][value]=Completed
  &where[1][type]=notEquals&where[1][attribute]=status&where[1][value]=Cancelled
  &select=name,status,priority,dateDue,description,parentName,parentType,createdAt
  &maxSize=50
X-Api-Key: 3d34836b07bb327db8d8fa6b63430c4e

Filter to tasks where assignedUserName contains "Gretchen" OR tasks in the
personal lines category (flag tasks with LOB = personal auto, homeowners,
renters, life, or any tasks routed to #gretchen-tasks channel).

---

## Step 2 — Pull Expiring Personal Lines Policies (Gretchen's Domain)

GET https://api.nowcerts.com/api/InsuredDetailList?agencyId=09d93486-1536-48d7-9096-59f1f62b6f51&active=True
Authorization: Bearer {nowcerts_token}

Filter policies where:
- LOB = Personal Auto, Homeowners, Renters, Life, Health, Medicare
- expirationDate within 30 days

These are Gretchen's renewal follow-ups if not already in EspoCRM tasks.

---

## Step 3 — Prioritize and Sort

Sort tasks into 3 buckets:

**🔴 DO FIRST — Due today or overdue**
- Tasks with dateDue <= today
- Personal lines policies expiring ≤7 days with no renewal task

**🟡 DO TODAY — Due this week**
- Tasks due within 5 business days
- Personal lines policies expiring 8–14 days

**📋 ON DECK — Coming up**
- Tasks due 6–14 days out
- Personal lines policies expiring 15–30 days

---

## Step 4 — Translate to Plain English

For each task, rewrite the name/description in plain English. Rules:
- NO insurance jargon (no "bind", "endorsement", "declarations page", "COI" — spell it out)
- NO EspoCRM field names
- NO carrier codes
- Start every task with an action verb: Call, Email, Send, Follow up, Check, Get
- Include the client's first name if available
- Include a phone number or email if in the task description

**Translation examples:**
- "Process endorsement for Smith account" → "Update coverage change for Smith — call carrier to confirm"
- "COI needed - ABC Corp" → "Send proof of insurance certificate to ABC Corp"
- "F/U renewal XYZ" → "Follow up on renewal quote for XYZ — did they get the quote?"
- "Bind PA Smith" → "Confirm personal auto policy is active for Smith — call carrier to bind"
- "Dec page needed" → "Get the policy summary document and email it to the client"

---

## Step 5 — Post to #gretchen-tasks

**Post to:** #gretchen-tasks (find channel ID via Slack API if needed)

Format:
```
👋 Good morning Gretchen! Here's your list for {day}, {date}:

🔴 *DO FIRST ({count} items)*
1. {Plain English task} — {client name if known}
2. {Plain English task} — {client name if known}

🟡 *DO TODAY ({count} items)*
3. {Plain English task}
4. {Plain English task}

📋 *ON DECK — heads up for later this week ({count} items)*
5. {Plain English task} — exp {date}

📊 *Quick numbers:*
• {N} tasks total | {N} overdue | {N} renewals coming up
```

If nothing urgent:
```
👋 Good morning Gretchen! Light day today — here's what's on deck:
[list]
```

If nothing at all:
```
👋 Good morning Gretchen! Queue is clear — no open tasks right now.
Check with Lamar if you need something to work on.
```

---

## Step 6 — Notify Lamar (summary only, to #the-boss)

Post a ONE-LINE summary to #the-boss (C0ANQUENX4P):
```
📋 Gretchen's queue posted: {N} tasks ({N} urgent) → #gretchen-tasks
```

Only post to #the-boss if there are urgent/overdue items. If queue is light, skip the #the-boss ping entirely.

---

## Error Handling

| Error | Action |
|-------|--------|
| EspoCRM unreachable | Post to #gretchen-tasks: "Good morning Gretchen! The task system is down this morning — please check with Lamar for today's priorities." Post error to #systems-check. |
| NowCerts auth fails | Post task list from EspoCRM only; note "Renewal reminder data unavailable today" |
| No tasks found | Post the "queue is clear" message — never leave Gretchen without a response |

---

## Notes
- LLM: **Gemini** (operational, not revenue-critical)
- Primary output: **#gretchen-tasks** (Gretchen-facing — plain English mandatory)
- Secondary output: **#the-boss** (one-line summary only, only if urgent items exist)
- Schedule: **Weekdays 8:30 AM ET**
- NEVER use insurance jargon in Gretchen-facing output
- NEVER include EspoCRM navigation steps
- NEVER show task IDs, system codes, or field names
- Goal: Gretchen starts work knowing exactly what to do without asking Lamar
