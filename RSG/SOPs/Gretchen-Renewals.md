---
title: Gretchen — Personal Lines Renewals (step by step)
updated: 2026-09-01
tags: [rsg, sop, gretchen, renewals, zoho, cliq, momentum]
---

# Gretchen — Personal Lines Renewals

Your job on renewals: **get the client’s facts, send the review email when it looks right, and keep the file moving.** Lamar approves anything that writes back to Momentum (NowCerts). You do not tap those buttons.

This is the first SOP in your set. Next ones (files, service requests, morning Momentum) will follow the same shape.

## What you use

| Tool | What it is for |
|---|---|
| **Zoho Cliq → #renewals** | Morning ping + buttons on each renewal |
| **Zoho CRM → Tasks** | Your to-do list (including the daily Momentum check) |
| **Zoho CRM → Deals** | The renewal file (brief, notes, email draft) |
| **Momentum** | Carrier downloads and rater imports — clear these first |

You do **not** need Hermes, Nextcloud admin, or AMS “approve write” buttons.

---

## Every weekday — do this first (10 minutes)

Hermes posts a **morning book update** in `#renewals` around 8:00 AM and creates a CRM task for you.

1. Open **Momentum** and sign in.
2. Left sidebar → **Carrier Downloads** — process every pending item until the badge is clear.
3. Left sidebar → **Rater Imports & eDocs** — process every pending item until the badge is clear.
4. Open **Zoho CRM → Tasks**. Find today’s task (subject like *Daily Momentum queue check*). Mark it **Completed** only when both queues are actually empty.

If Momentum is down, note that on the task and tell Lamar. Do not mark it done.

---

## Then work renewals — one client at a time

Overnight, Hermes writes a **brief** on each upcoming renewal and pings `#renewals`. Personal lines are yours. Commercial is Lamar unless he asks you to help.

### Step 1 — Open the list

1. Open Cliq channel **#renewals**.
2. You can also type in the **RSG Renewals** bot: `Today Renewals` or `Past Due`.
3. Start with **Past Due**, then anything due this week.

### Step 2 — Open the CRM file

On the card, open the **Deal** (or search the client in Zoho CRM → Deals).

You will see two tasks on that Deal:

| Task | Meaning | Who finishes it |
|---|---|---|
| **Task 1 — RENEWAL BRIEF** | Brief is written; you review facts and send (or fix) the client email | You (after the email is really sent) |
| **Task 2 — RENEWAL PREMIUM UPDATE** | New premium / quote is in | You, when the number is real — not guessed |

Do not mark Task 1 complete just because you read the brief.

### Step 3 — Read before you touch anything

On the Deal, read:

1. The **brief / PDF** (what we think is on the policy).
2. **Recent notes** (did we already email them?).
3. **Documents** — what we still need (ID, photos, application, etc.).

If the brief looks wrong (wrong cars, wrong address, wrong people), **stop**. Put a one-line note on the Deal and ping Lamar in `#renewals`. Do not send the email.

### Step 4 — Get what is missing

Call or email the client only for facts we do not have. Keep it simple:

- Confirm the people and the property / cars on the policy.
- Ask for any document the brief says we still need.
- Write what they said as a **Note on the Deal** the same day. Do not keep it only in your head or inbox.

When a client sends a file: open the **Document Registry** record for that item (the full record, not the tiny related-list create). Upload on **File**. Hermes files it into the client folder twice a day (12:30 PM and 8:30 PM). You do not need to log into Nextcloud for that.

### Step 5 — The client email (your send button)

The email is **not** sent until you approve it.

1. In `#renewals`, on that renewal, tap **Show Email Draft** (or the bot: email drafts).
2. Read **To**, **From** (should be `gretchen@risksolutionsgroup.net`), **Subject**, and the body.
3. Check: right client, right policy, no invented coverage, no “we already bound this” language unless it is true.
4. If it is wrong: tap **Reject**. Fix the facts (or ask Lamar). Do not send a bad draft.
5. If it is right: tap **Approve & Send**. That sends from CRM and stamps the Deal that it went out.

Only then mark **Task 1** completed.

### Step 6 — When the new price is in

When the carrier quote / renewal premium is real (from Momentum or the carrier, not from memory):

1. Put the number on the Deal (premium fields / a note with the source).
2. Complete **Task 2 — RENEWAL PREMIUM UPDATE**.

Completing Task 2 pings `#renewals` again. That is expected.

### Step 7 — Leave AMS writes to Lamar

You will see buttons like **Approve AMS**, **Reject AMS**, **Requeue AMS**.

- **Do not press Approve AMS.** That writes the policy in Momentum. Lamar does that after he is happy with the file.
- If a card is stuck on “needs approval,” ping Lamar with the client name. Do not retry it yourself.

---

## How you know you are done with one client

All of these are true:

- [ ] Missing facts / docs are requested **or** already on the Deal
- [ ] Review email actually sent (Approve & Send), or Lamar said skip
- [ ] Task 1 completed only after the email (or skip) happened
- [ ] Task 2 completed only after a real premium is on the file
- [ ] You did not tap Approve AMS

If Hermes or a card says “done” but Task 1 is still open or the email never went — it is **not** done. Finish the checklist.

---

## If something looks broken

| What you see | What to do |
|---|---|
| No morning book update / no Momentum task | Tell Lamar. Still clear Carrier Downloads if you can. |
| Brief for a client you do not recognize | Ping Lamar before emailing. |
| Approve & Send errors | Copy the error, do not keep tapping. Lamar. |
| Client says they never got the email | Check the Deal note for `EMAIL_SENT`. If missing, it did not send. |

---

## What this SOP is not

- Not commercial accounts (unless Lamar assigns one).
- Not writing policies in Momentum.
- Not building quotes from scratch in a rater (unless that is already your usual desk work on that file).
- Not the client **service request** desk (certificates, ID cards, claims) — that is a different SOP: [[RSG/SOPs/Client-Service-Request-Desk]].
