---
title: Carrier / MGA Knowledge Ingest
updated: 2026-09-01
tags: [rsg, sop, sharepoint, hermes, carrier, mga]
---

# SOP — Ingest carrier / MGA knowledge

**Owner:** Lamar  
**Writer:** hermes-vps job `carrier-knowledge` (not Amy)  
**Truth:** the PDF in SharePoint. Supabase is the map.

Do this every time a guideline, appetite, or rate note should be citable.

## 1. Only ingest a file

The job copies **attachments**, not email bodies.

| Have | Do |
|---|---|
| PDF / Word / spreadsheet | Continue |
| Email with that file attached | File the message into Outlook **Carrier Knowledge** on `lamar@` |
| Guidelines in the email body only | Print → Save as PDF, then upload (step 2) |
| Client policy / ID / application | **Stop.** That is Nextcloud, not this pipeline |

Allowed types: `.pdf` `.doc` `.docx` `.xls` `.xlsx` `.csv` `.txt` `.md` `.png` `.jpg`

## 2. Put the file in the one library

**Library (no extra folder):**  
https://riskintranet.sharepoint.com/sites/coverages/Shared%20Documents

Two doors, same place:

1. **Upload** the file in the browser (or OneDrive-sync that library and drop it in Finder).
2. **Outlook** — move the message into **Carrier Knowledge**. The job names the file `{Subject}__{original}.pdf`.

Do not put carrier/MGA knowledge in Nextcloud.

## 3. Name it so the keys parse (preferred)

`carrier` and `mga` are **distinct**. Empty token = that key is unset. Use `-` or `none` for empty.

| What the doc is | Filename |
|---|---|
| Carrier only | `Progressive__auto__FL__guideline__2026-04-01.pdf` |
| MGA only | `-__CRC__all__XX__guideline__2026-01-15.pdf` |
| Carrier via MGA | `Progressive__CRC__auto__FL__guideline__2026-04-01.pdf` |

Pattern:

- **5 parts:** `Carrier__LOB__ST__doctype__YYYY-MM-DD.ext` → `mga` empty
- **6 parts:** `Carrier__MGA__LOB__ST__doctype__YYYY-MM-DD.ext`

`ST` is a 2-letter state, or `XX` if not state-specific. `LOB` is `all` if it is not one line.

A bad name still ingests. It lands as `carrier=unparsed` and you must fix keys **before** approve (the CRC TAP snapshot was this case).

## 4. Run the writer

Timer is off. After the file is in the library or the mail folder:

- In Cursor / Hermes: “run carrier-knowledge ingest”
- Or: `DRY_RUN=0 ./scripts/run-carrier-knowledge.sh`

Prove: `/carrier-knowledge-verify` → **PASS**.

The job **never** sets current. New rows are `pending`.

## 5. Check the pending row before you approve

Open the SharePoint PDF. Confirm the index matches the document:

| Key | Ask |
|---|---|
| `carrier` | Admitted / writing company? Empty if this is MGA-only. |
| `mga` | MGA name (e.g. `crc`)? Empty if carrier-direct. |
| `doc_type` | guideline, appetite, rate, endorsement, … |
| `lob` / `state` | One line and state, or `all` / `XX` |
| File | Same PDF you meant (hash + link) |

One **current** row per `(carrier, mga, doc_type, lob, state)`. Wrong keys = the next real CRC guideline cannot become current, or Amy cites the wrong party.

## 6. Approve (human gate)

There is no Cliq button yet. Approve in chat: “approve” plus any key corrections.

Approved = `status=approved`, `is_current=true`, `approved_by` you. Amy may cite it only after that.

## Done looks like

- File in Policies & Coverages `Documents`
- One pending (then current) row with the right **carrier** and **mga**
- Re-run of the same file does not create a duplicate (same hash)

## Do not

- Ask Amy to upload or write the index
- Approve `unparsed` / unknown keys
- Use Nextcloud for these files
- Treat a body-only newsletter as ingested
