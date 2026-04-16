---
title: RSG EspoCRM Codebase Audit — Consolidated Findings
updated: 2026-04-16
tags: [rsg, espocrm, audit, technical-debt, crm]
---

# RSG EspoCRM Codebase Audit — Consolidated Findings

**Repo:** `/Users/lamarcoates/Documents/GitHub/rsg-espocrm`
**Audit date:** 2026-04-16
**Scope:** 7 parallel deep dives covering Opportunity end-to-end, Account cascading saves, all PHP hooks, Renewal + Commission entities, n8n + webhook automation chain, layout audit for all entities, Task module, and cross-entity field pollution.
**Total distinct issues identified:** 52

---

## Executive Summary

The RSG EspoCRM has three classes of problems, in decreasing severity:

1. **Active bugs** — code that runs and produces wrong data today (null-days bug, duplicate tasks, zero-value rejection, unauthenticated webhook, committed API key).
2. **Architectural drift** — multiple systems writing the same fields with different logic; fields that live on the wrong entity; automations documented in changelogs but never implemented.
3. **UI + field bloat** — ~200 fields on Account alone, roughly half misplaced, duplicated, orphaned, or referencing missing client views.

Account entity is the epicenter of pollution. Task + ActivityLog is the epicenter of race conditions. Policy + PolicyAccountSync is the epicenter of null-handling bugs. Webhook chain is the epicenter of security gaps.

---

## Severity Legend

- **P0 / CRITICAL** — producing wrong production data or security risk; fix immediately.
- **P1 / HIGH** — logic conflict, guaranteed user-facing failure, or data integrity gap.
- **P2 / MEDIUM** — orphaned automation, dead code paths, race conditions that fire under specific conditions.
- **P3 / LOW** — UI noise, duplicate fields, dead columns, minor inconsistencies.

---

## P0 — CRITICAL (fix this week)

### P0.1 — Committed live API key in `api-deploy.sh`
- **File:** `api-deploy.sh`
- **Issue:** Hardcoded production `API_KEY="e5df7c32..."`
- **Risk:** Key is in git history; anyone with repo access has prod access.
- **Fix:** Rotate key immediately. Move to env var or secrets manager. Add `api-deploy.sh` pattern to `.gitignore` or use a `.env.local`.

### P0.2 — Null-days bug flags valid policies as "EXPIRED CRITICAL"
- **File:** `custom/Espo/Custom/Classes/Policy/PolicyAccountSync.php`
- **Issue:** `$daysRemaining <= 0` evaluates true when `$daysRemaining` is `null` (policy has no `expirationDate`). Policy gets `statusLabel = 'EXPIRED'`, `urgencyIcon = '!!'`.
- **Fix:** Add explicit null guard before numeric comparison.
```php
if ($daysRemaining === null) {
    $statusLabel = 'UNKNOWN';
    $urgencyIcon = '?';
} elseif ($daysRemaining <= 0) {
    ...
}
```

### P0.3 — Intel Pack webhook has no authentication
- **File:** `custom/Espo/Custom/Controllers/Account.php` → `postActionRunIntelPack`
- **Issue:** Posts account data to `intelPackWebhookUrl` with no HMAC, no signature, no shared secret.
- **Risk:** Anyone who learns the URL can submit forged account enrichment data.
- **Fix:** HMAC SHA-256 signature header with shared secret; validate on n8n side.

### P0.4 — `WonBoundValidation` rejects legitimate $0 `writtenPremium`
- **File:** `custom/Espo/Custom/Hooks/Opportunity/WonBoundValidation.php`
- **Issue:** `!$entity->get("writtenPremium")` treats `0` as missing. `0` is a valid written premium (e.g., monoline courtesy bind, zero-fee review policy).
- **Fix:** `$entity->get('writtenPremium') === null || $entity->get('writtenPremium') === ''`

### P0.5 — Opportunity `name` field required but missing from detail layout
- **Files:** `entityDefs/Opportunity.json` (required: true), `layouts/Opportunity/detail.json` (no name field)
- **Issue:** Users cannot fill a required field via the UI. Saves from UI fail.
- **Fix:** Add `name` to detail layout OR implement `beforeSaveScript` auto-generation from `account.name + lineOfBusiness + estimatedEffectiveDate`.

### P0.6 — Opportunity `lineOfBusiness` required + locked trap
- **Files:** `entityDefs/Opportunity.json` (required: true), `clientDefs/Opportunity.json` (readOnly when `id` exists)
- **Issue:** Legacy records with empty `lineOfBusiness` cannot be updated. Field is required to save, readOnly to edit.
- **Fix:** Relax readOnly condition: `isNotEmpty(id) AND isNotEmpty(lineOfBusiness)`.

---

## P1 — HIGH (fix this sprint)

### P1.1 — `Stalled` bool filter references nonexistent stage (A1)
- **File:** `custom/Espo/Custom/Classes/Select/Opportunity/BoolFilters/Stalled.php`
- Filter uses `stage === "Stalled"`, but "Stalled" isn't in the stage enum. Returns zero results forever.
- **Fix:** Implement as "Opportunities stuck in any stage > 14 days" via `modifiedAt`, or add Stalled stage to enum.

### P1.2 — Probability formula drift (A2)
- **File:** `entityDefs/Opportunity.json`
- `probabilityMap` lists 12 stages, `formula.beforeSaveScript` only covers 6. Renewal stages never update `probability`.
- **Fix:** Extend formula to cover all stages OR remove stored `probability` and derive it in UI only.

### P1.3 — `lostReason` not required for `Non-Renewal / Lost` (A3)
- **File:** `clientDefs/Opportunity.json`
- `lostReason` required only for `Closed Lost`, not for the renewal pipeline's lost state.
- **Fix:** Add `Non-Renewal / Lost` to the `lostReason` required conditions.

### P1.4 — Bind fields not enforced for `Bound / Renewed` (A4)
- **File:** `clientDefs/Opportunity.json`
- `writtenPremium`, `policyNumber`, etc. only required for `Closed Won`, not `Bound / Renewed`.
- **Fix:** Mirror the bind field requirements for the renewal stage.

### P1.5 — Duplicate-task race on ActivityLog save (F2)
- **File:** `custom/Espo/Custom/Hooks/ActivityLog/CreateServiceTask.php`
- Triage + rescue both fire on one ActivityLog. Each dedupes only against its own `automationKey`. A cancellation log with `followUpTask` set creates **two tasks**.
- **Fix:** Single dedup guard: if any open task exists for this `sourceActivityLogId`, rescue wins; triage aborts.

### P1.6 — Renewal + playbook tasks bypass all webhooks (F3)
- **Files:** `ServiceWebhookDispatcher.php`, `ServiceActivityLogger.php`
- `isServiceTask` whitelist excludes `Renewal`, `New Business`, `Commission`. Status changes on these task types never fire n8n webhooks or ActivityLog events. `Waiting on Carrier` also unmapped.
- **Fix:** Either document as intentional, or extend whitelist + map new status → event types.

### P1.7 — `ServiceWebhookDispatcher` swallows all errors (C5)
- **File:** `custom/Espo/Custom/Classes/Task/ServiceWebhookDispatcher.php`
- `curl_exec` result ignored. No HTTP status check. No logging on failure.
- **Risk:** Silent integration failure. n8n never receives events. No alert.
- **Fix:** Capture `curl_getinfo`, log non-2xx responses to the Espo log, optionally fail the Task save or queue for retry.

### P1.8 — Account scoring schema drift (B5 / E4)
- **File:** `custom/Espo/Custom/Jobs/RecalculateAccountScores.php`
- Writes raw SQL to `account.account_score` and `account.score_breakdown`. Columns are **not defined** in `entityDefs/Account.json`. Conflicts with `scoreTotal` + `scoreTier` system maintained by `AccountHealthManager`.
- **Fix:** Pick one scoring system. Delete the other. Currently you have two parallel scores disagreeing.

### P1.9 — `AccountHealthManager` vs `PolicyAccountSync` race on renewal fields (B1 / B2)
- **Files:** `Classes/Account/AccountHealthManager.php` + `Classes/Policy/PolicyAccountSync.php`
- Both write `nextRenewalDate`, `nextRenewalLob`, `nextRenewalCarrier`, `daysToRenewal`. Order of save hooks determines which wins.
- **Fix:** Designate `PolicyAccountSync` as sole writer. Remove these writes from `AccountHealthManager`.

### P1.10 — `DeriveProfile` wipes user-entered `description` (C4)
- **File:** `custom/Espo/Custom/Hooks/Contact/DeriveProfile.php`
- Every Contact save overwrites `description` with a generated summary, deleting any notes the user typed.
- **Fix:** Write to a separate field like `derivedProfile` or `profileSummary`, never `description`.

### P1.11 — Commission `listSmall.json` references nonexistent fields (D1)
- **File:** `layouts/Commission/listSmall.json`
- Shows `expectedAmount` and `reconciliationStatus`; neither in entity defs.
- **Fix:** Replace with `estimatedCommission`, `postedAmount`, `status`.

### P1.12 — Commission filter classes reference nonexistent fields (C3)
- **Files:** `Classes/Select/Commission/PrimaryFilters/*.php`, `BoolFilters/*.php`
- Four filter classes reference `businessType`, `sourceType` which don't exist on Commission.
- **Fix:** Remove or repoint to valid fields.

### P1.13 — Lead conversion does not create Opportunity (A22 / E1)
- **File:** `custom/Espo/Custom/Hooks/Lead/SyncConvertedRecords.php`
- CHANGELOG claims Lead→Opportunity creation on conversion. Hook creates Contact + Account only.
- **Fix:** Either implement the Opportunity create logic OR update changelog to match reality.

### P1.14 — `Task` `priority` never set by automation (F4)
- All 4 task creators set `urgency` but not `priority`. Layouts + list sort use `priority`.
- **Fix:** Map `priority` from `urgency` in every creator (urgent→High, high→High, normal→Normal, low→Low).

### P1.15 — Missing client views referenced everywhere (F5 + layouts audit)
- `clientDefs/Task.json` → `custom:views/task/record/detail-view` (missing)
- `clientDefs/Account.json` → `custom:views/account/record/panels/account-score`, `record-info` (missing)
- `clientDefs/Opportunity.json` → many custom views missing
- Same class of bug across Contact, Policy, Commission clientDefs
- **Fix:** Either create the JS files or remove the overrides.

---

## P2 — MEDIUM (fix this quarter)

### P2.1 — Duplicate Account premium/count fields (FP1)
Collapse these pairs:
- `activePolicyCount` ↔ `policyCountActive` — both written to same value
- `totalActivePremium` ↔ `totalAnnualPremium` — only first is maintained by code; second is orphan
- `nextXDate*` ↔ `nextRenewal*` — keep `nextRenewal*`

### P2.2 — Two competing Account intel field sets (FP2)
Native ↔ intel duplicates:
- `websiteUrl` / `intelWebsite`
- `linkedinUrl` / `intelLinkedinUrl`
- `sicCode` / `intelSic`
- `yearsInBusiness` / `intelYearsInBusiness`
- `numberOfEmployees` / `intelEmployeeCount`
- `annualRevenue` / `intelAnnualRevenueEst`

Pick one canonical writer per field.

### P2.3 — Gap flags never populated (FP5 subset)
- `gapUmbrella`, `gapLife`, `gapMedicareEligible`, `gapFinalExpense`, etc. are read by `AccountHealthManager.countGapFlags()` but **never written** by any PHP. Tooltip claims n8n maintains them — no such n8n job exists.
- `gapCount` is always 0.
- **Fix:** Either compute gaps in PHP from Policy rows OR wire n8n OR delete the gap system.

### P2.4 — Task `assignedUser` can be null silently (F6)
- `resolveOwnership` chains activity→policy→account owner. If all null, task has no assignee.
- **Fix:** Team-queue fallback (service team role or default system user).

### P2.5 — Playbook bulk-create amplification (F7)
- Account `afterSave` → `SyncCrossSellPlaybooks` runs on every save. Importing 100 accounts = up to 500 tasks.
- **Fix:** Guard on field-change detection or add an import-mode flag.

### P2.6 — Lead Qualification Handoff + X-Date Nurture Loop missing (E1)
- `CHANGELOG-2026-04-02.md` documents these automations. No PHP, no n8n workflow implements them.
- **Fix:** Implement or strike from changelog.

### P2.7 — n8n service lifecycle workflow is inactive + has placeholder creds (E3)
- **File:** `n8n/crm-service-lifecycle-notifications.json`
- `"active": false`, SMTP cred is `REPLACE_SMTP_CREDENTIAL_ID`, webhooks have no auth options.
- **Fix:** Complete credential wiring OR delete the workflow.

### P2.8 — Opportunity `probability` exposed but overwritten by formula (A12)
- `defaultSidePanel.json` shows `probability`, formula overwrites on save. Users edit, save, it reverts.
- **Fix:** Make `probability` readOnly in UI, OR remove from panel.

### P2.9 — Opportunity `amount` auto-set to 0 when `estimatedPremium` null (A12)
- Confusing for users — blank input becomes $0 deal.
- **Fix:** Leave null if source is null.

### P2.10 — Opportunity `account` link not required (A10)
- Orphan opportunities possible.
- **Fix:** `required: true` on `account` link.

### P2.11 — Opportunity `closeDate` missing from detail layout (A10)
- Referenced by reports, hidden from UI.

### P2.12 — `kanbanOrder` omits renewal stages (A5)
- Renewal opportunities don't sort on kanban properly.

### P2.13 — Stage-bar prevents pipeline switching (A6)
- `client/custom/src/views/opportunity/fields/stage-bar.js` locks new-business vs renewal pipelines. Cannot rebrand a stale new-business opp as a renewal without DB surgery.

### P2.14 — `PolicyAccountSync` overwrites `name` on every save (C2)
- User-entered policy names get wiped by derived format on each save.

### P2.15 — Hardcoded `carrierPortalUrl` in `PolicyAccountSync` (C7)
- Should come from per-carrier config.

### P2.16 — Inconsistent default commission rate (C6)
- `PolicyAccountSync` uses `0.10`. Other writers use different defaults. Commission entity should hold authoritative rate.

### P2.17 — `export-espocrm.sh` hardcoded wrong repo path
- Uses `/Users/lamarcoates/espocrm-workspace`; actual repo is `/Users/lamarcoates/Documents/GitHub/rsg-espocrm`.

### P2.18 — `linkedAccount` vs `parent` drift on Task (F8)
- Manual UI edits can desync; resolvers prefer `linkedAccount`, so wrong parent hides task from health manager.

---

## P3 — LOW (field bloat, dead code, UI polish)

### P3.1 — Account policy-level fields (~80-120 fields) (FP3)
Full `policyAuto*`, `policyHome*`, `policyUmbrella*`, `policyLife*`, `policyMedicare*` blocks on Account. Not in any active layout. Zero PHP writers. Candidate for bulk deletion.

### P3.2 — Account household/contact-level fields (FP4)
`primary*`, `spouse*`, `dependents*`, `dateOfBirth`, `gender`, `maritalStatus`, `property*`, `vehicle*`, `driver*` on Account. Unreferenced `detailHousehold.json` exists. Migrate to Contact.

### P3.3 — Account orphan AI fields (FP5)
`aiAssessment`, `keyFindings`, `coverageGaps`, `riskScore`, `intelPackRun`, `intelPackLastRun`, `assessmentDate`. On layout, no PHP writer. Depends on unauthenticated Intel Pack webhook (P0.3).

### P3.4 — Account outreach orphan fields (FP5)
`lastContactDate`, `lastContactType`, `lastContactBy`, `lastContactOutcome`, `npsScore`, `npsDate`, `referralsGiven`, `outreachAttemptsCurrent`. No PHP writes.

### P3.5 — Account renewal workflow fields
`renewalOutreachStage`, `renewalQuote*`, `renewalDecision*`, `premiumChange*`. Should live on Renewal, not Account.

### P3.6 — Account `accountScore` + `scoreBreakdown` fields
Separate from `scoreTotal` + `scoreTier`. Written by raw SQL job (P1.8). No UI panel (broken view reference). Delete.

### P3.7 — Opportunity dead/orphan fields
- `aggregatePageId` — DEAD, i18n says "deprecated"
- `policyStubId`, `policyStubStatus` — ORPHAN
- `cClientEmail`, `cRenewalDate` — duplicate of standard fields
- `lossRunsRequested`, `commissionLogged`, `chk*` onboarding flags — ORPHAN

### P3.8 — Contact policy-level fields
Medicare + Life fields belong on Policy; keep on Contact as derived snapshot only.

### P3.9 — Commission `lineOfBusiness` enum incomplete (D3)
Missing LOB values present on Policy + Renewal. Data integrity risk on save.

### P3.10 — Commission `name` required but not in layout (D6)

### P3.11 — `Task.momentumTaskId`, `momentumLastSynced` (F9)
No code path. Either external NowCerts sync exists outside repo, or orphans.

### P3.12 — Commission task type present but never automated
`taskType: "Commission"` enum value with no custom automation path.

### P3.13 — Duplicate / backup metadata folders
`_backup_20260327_174612` duplicates entire metadata tree. Pure repo hygiene.

### P3.14 — Unused layouts on disk
`layouts/Account/detailHousehold.json`, `detailCommercial.json` — not referenced in clientDefs.

---

## Unified Execution Plan

### Phase 0 — Security + data-integrity (1 day)
Nothing else matters if prod keys leak or policies are mass-labeled EXPIRED.
1. **P0.1** — Rotate API key, move to env var, purge from deploy script.
2. **P0.2** — Null-days guard in `PolicyAccountSync::applyDerivedFields`.
3. **P0.3** — HMAC auth on Intel Pack webhook (shared secret + SHA-256 signature).
4. **P0.4** — `writtenPremium === null` check in `WonBoundValidation`.
5. **P2.17** — Fix `export-espocrm.sh` repo path.

### Phase 1 — Opportunity save path (0.5 day)
Unblocks the original bug report.
6. **P0.5** — Add `name` to Opportunity detail layout or auto-generate.
7. **P0.6** — Relax `lineOfBusiness` readOnly trap.
8. **P1.1** — Fix `Stalled.php` filter.
9. **P1.2, P1.3, P1.4** — Probability formula + lostReason + bind fields enforcement for renewal pipeline.
10. **P2.8, P2.9, P2.10, P2.11** — Probability readOnly, amount null-preserve, account required, closeDate in layout.

### Phase 2 — Task + webhook chain hardening (1 day)
11. **P1.5** — Single dedup guard in `CreateServiceTask`.
12. **P1.6** — Extend `isServiceTask` whitelist OR document.
13. **P1.7** — Log webhook errors, capture curl_getinfo.
14. **P1.14** — Map `priority` from `urgency` in all 4 task creators.
15. **P2.4** — Team-queue fallback for `assignedUser`.
16. **P2.5** — Playbook guard on field-change detection.

### Phase 3 — Account scoring + sync precedence (1 day)
17. **P1.8** — Pick one scoring system, delete the other.
18. **P1.9** — `PolicyAccountSync` becomes sole writer of renewal fields.
19. **P1.10** — `DeriveProfile` writes to `profileSummary`, not `description`.
20. **P2.14** — `PolicyAccountSync` stops overwriting policy `name`.
21. **P2.15, P2.16** — Config-driven carrier portal URL + commission rate.

### Phase 4 — Commission + Renewal cleanup (0.5 day)
22. **P1.11** — Fix `listSmall.json` field references.
23. **P1.12** — Fix Commission filter field references.
24. **P1.13** — Implement Lead→Opportunity create OR update changelog.
25. **P3.9, P3.10** — Complete Commission LOB enum + layout.

### Phase 5 — UI debt: missing client views (0.5 day)
26. **P1.15** — Sweep all `clientDefs/*.json`, delete references to missing `custom:views/...` files. Shrink until the UI loads cleanly with defaults.

### Phase 6 — Quick-win field cleanup (0.5 day, safe deletes)
27. **P2.1** — Collapse duplicate Account premium/count/renewal pairs.
28. **P3.6** — Delete `accountScore` + `scoreBreakdown`.
29. **P3.7** — Delete `aggregatePageId`, `policyStubId`, `policyStubStatus`, `cClientEmail`, `cRenewalDate`, orphan `chk*` flags.
30. **P3.13, P3.14** — Delete `_backup_*` folder and unreferenced layouts.

### Phase 7 — Intel consolidation + orphan decisions (1 day)
31. **P2.2** — Pick canonical writer for each native↔intel pair.
32. **P2.3** — Gap flags: compute from Policy in PHP OR delete system.
33. **P3.3, P3.4** — AI + outreach orphan fields: wire or delete.
34. **P3.11, P3.12** — Task momentum + Commission task type: keep or drop.

### Phase 8 — Automation implementation (2-3 days)
35. **P2.6** — Lead Qualification Handoff + X-Date Nurture Loop (or strike from changelog).
36. **P2.7** — Activate `crm-service-lifecycle-notifications` n8n workflow with real creds OR delete.
37. **P2.12** — Add renewal stages to `kanbanOrder`.
38. **P2.13** — Fix stage-bar to allow cross-pipeline transitions.

### Phase 9 — Structural migration (1-2 weeks, requires data migration plan)
Not blocking. Do when the above is stable.
39. **P3.1** — Account policy-level blocks → migrate data → delete ~80-120 fields off Account.
40. **P3.2** — Account household blocks → Contact → delete ~30 fields off Account.
41. **P3.5** — Account renewal workflow fields → Renewal entity.
42. **P3.8** — Contact policy-level fields → derived snapshot only.

---

## Target End State

| Metric | Current | After Phase 6 | After Phase 9 |
|---|---|---|---|
| Account field count | ~200 | ~175 | ~80 |
| P0 bugs | 6 | 0 | 0 |
| P1 bugs | 15 | 0 | 0 |
| Duplicate field pairs | ~15 | 0 | 0 |
| Missing client view refs | ~20+ | 0 | 0 |
| Orphan automation claims | 4 | 2 | 0 |
| Unauthenticated webhooks | 1 | 0 | 0 |

---

## Appendix A — Finding-to-Deep-Dive Cross Reference

| Code | Deep Dive |
|---|---|
| A* | Opportunity end-to-end save path |
| B* | Account cascading-save precedence |
| C* | PHP hooks line-by-line |
| D* | Renewal + Commission |
| E* | n8n + webhook automation |
| F* | Task module |
| FP* | Cross-entity field pollution |
| P0.1, P0.4, P0.5, P0.6, P2.17 | Initial Opportunity review |

---

## Appendix B — Files Most in Need of Attention

Ranked by number of findings touching each file:

1. `custom/Espo/Custom/Resources/metadata/entityDefs/Account.json` — ~60+ field-level findings
2. `custom/Espo/Custom/Classes/Policy/PolicyAccountSync.php` — 4 findings (P0.2, P1.9, P2.14, P2.15)
3. `custom/Espo/Custom/Classes/Account/AccountHealthManager.php` — 3 findings (P1.8, P1.9, gap count logic)
4. `custom/Espo/Custom/Resources/metadata/entityDefs/Opportunity.json` — 6 findings
5. `custom/Espo/Custom/Hooks/ActivityLog/CreateServiceTask.php` — P1.5 (duplicate task race)
6. `custom/Espo/Custom/Classes/Task/ServiceWebhookDispatcher.php` — P1.7 (silent errors)
7. All `clientDefs/*.json` — P1.15 (missing views sweep)

---

**Next step when ready:** Phase 0 is 1 day and zero risk — start there.
