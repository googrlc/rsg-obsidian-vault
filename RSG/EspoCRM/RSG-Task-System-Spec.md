# RSG Task Command System — Architecture & Build Spec
**Date:** March 2026
**Status:** Design complete — ready to build

---

## The Problem

Tasks come in from everywhere (Slack, Claude chat, email, phone) and disappear.
No single list. No reminders with context. No disposition tracking.
OpenClaw agents don't know what's on the list.

---

## The Solution: One Hub, Multiple Entry Points

**Single source of truth:** EspoCRM Tasks entity
**Command channel:** #the-boss (Lamar) + #the-task-list (work list view)
**Both Lamar and OpenClaw read and write from the same EspoCRM task list**

---

## Task Creation — All Paths Lead to EspoCRM

### Path 1 — From #the-boss (primary)
Lamar posts anything task-like in #the-boss.
Personal Assistant detects it and creates an EspoCRM task automatically.
Trigger phrases: "create a task", "remind me", "don't let me forget",
"dispatch to Gretchen", "follow up on", or any imperative sentence.
Personal Assistant replies with: "Task created: [name] — due [date] — assigned to [person]"

### Path 2 — From Claude.ai chat (this conversation)
When Lamar says "create a task" or I identify an action item,
I post to #the-boss with the task formatted for Personal Assistant to pick up.
This keeps the creation path consistent — everything goes through #the-boss first.

### Path 3 — From Gmail (existing)
WF-F already handles this: label email "RSG-Task" → EspoCRM task created.
No changes needed.

### Path 4 — From any Slack channel
Lamar or Gretchen types "create task: [description]" anywhere.
Personal Assistant monitors mentions or keyword triggers.
Creates EspoCRM task and confirms in the channel.

---

## Task Fields in EspoCRM

| Field | Value | Notes |
|---|---|---|
| name | Task description | Required |
| status | Not Started / In Progress / Deferred / Complete | |
| priority | High / Medium / Low | |
| assignedUserId | Lamar or Gretchen | |
| dateStart | Today | |
| dateDue | Due date | Default: today + 1 day if not specified |
| accountId | Linked account | Optional — link to client if relevant |
| description | Full context + source | Where it came from, what triggered it |
| cTaskSource | Slack / Claude / Gmail / Phone | Custom field — track origin |
| cDisposition | Open / Done / Parked / Deferred / Delegated | Custom field |

---

## Disposition Language

Lamar responds in Slack with one word to disposition a task:

| Lamar says | What happens |
|---|---|
| "done" | Status → Complete. Moved to done view. |
| "park" | Status → Deferred. Note added: "Parked by Lamar" |
| "defer [date]" | Status → Deferred. Due date updated. |
| "delegate" | Reassigned to Gretchen. She gets a DM. |
| "drop" | Status → Complete with note: "Dropped — no longer relevant" |

Personal Assistant handles all of these from #the-boss.

---

## Reminder Logic — n8n Workflow

**Workflow name:** RSG — Task Reminder Engine
**Replaces:** Personal OS — Task Reminder Engine (WF17 — deactivate that one)

Schedule: Every morning at 8am ET and 3pm ET

Morning run (8am): Post to #the-task-list
- All High priority tasks due today or overdue
- Any tasks assigned to Gretchen not started in 24hrs

Afternoon run (3pm): Post to #the-boss only
- Tasks that were due today and still Not Started
- Any tasks open for 3+ days with no status change

Each reminder includes:
- Task name
- How long it's been open
- Who it's assigned to
- Account it's linked to (if any)
- Suggested next action (Claude generates this)

Escalation: If a task is 5+ days old and still Not Started → post to #the-boss
with urgent flag and ask Lamar to disposition it.

---

## OpenClaw Agent Updates Needed

### Personal Assistant — update system prompt
Add these instructions:
1. Monitor #the-boss for task-like language
2. Create EspoCRM task via API when detected
3. Listen for disposition responses (done/park/defer/delegate/drop)
4. Update EspoCRM accordingly
5. Post confirmation back to #the-boss

### Task Finisher — update system prompt
Add these instructions:
1. When called, pull open tasks from EspoCRM for the assigned user
2. Group by priority
3. For each task, generate the next physical action (one sentence)
4. Post formatted list to #the-task-list

---

## n8n Workflows to Build / Modify

| Workflow | Action | Notes |
|---|---|---|
| RSG — Task Reminder Engine (NEW) | Build | Replaces WF17 |
| Personal OS — Task Reminder Engine (WF17) | Deactivate | Replaced above |
| WF-F — Gmail Task Creator | Keep as-is | Already works |

---

## EspoCRM Custom Fields to Add

Add these to the Task entity before building the n8n workflow:
- cTaskSource (Enum: Slack, Claude, Gmail, Phone, Manual)
- cDisposition (Enum: Open, Done, Parked, Deferred, Delegated)

---

## Build Order

1. Add cTaskSource and cDisposition fields to EspoCRM Task entity (SSH)
2. Update Personal Assistant agent prompt in OpenClaw to handle task creation and disposition
3. Update Task Finisher agent prompt in OpenClaw
4. Build RSG Task Reminder Engine n8n workflow
5. Deactivate WF17 (Personal OS Task Reminder Engine)
6. Test: Lamar posts a task in #the-boss → confirm it lands in EspoCRM
7. Test: Lamar posts "done" → confirm EspoCRM updates
