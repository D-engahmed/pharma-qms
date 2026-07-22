# 03 — Product Requirements Document (PRD)

**Traces to:** 00_Project_Charter.md, 01_Glossary.md, 02_BRD.md
**Status:** Confirmed items are marked **[Confirmed]**; everything else **[TBS]**. Every feature below is either demonstrated in the prototype or stated in the clarification session — nothing is invented.

---

## 1. Product Goals

- PG1 — Give each of the four roles a dedicated application with only the screens/actions relevant to that role. **[Confirmed — clarification]**
- PG2 — Preserve the exact business workflow already demonstrated in the prototype (receive → sample → test/COA → QC review → release/approve) for Raw Material, Packaging, and Product samples. **[Confirmed — prototype]**
- PG3 — Make every GMP-relevant record change auditable and every GMP decision electronically signed. **[Confirmed — clarification]**
- PG4 — Centralize employee/role/permission administration in the Access Control Layer so no business app re-implements auth. **[Confirmed — clarification]**

## 2. Applications & MVP Boundary

MVP = the four apps below, each scoped to the features demonstrated in the prototype, running against the shared Access Control Layer.

| App | MVP Features |
|---|---|
| Storekeeper | Register Raw Material; Register Packaging Material; view own material/packaging tables with search & filters; request sampling on Raw Material or Packaging; view material/packaging detail; view/dismiss notifications; view release label and print it once released. |
| Sampler | View pending sampling requests (Raw Material + Packaging); record a sampling event; view/reprint sampling labels; view sample history; register Product samples (FP/SFP/Bulk) directly; view product sample history. |
| Analyst | View combined sample worklist (Raw Material + Packaging + Product samples); start testing on a sample; create a COA; view Certificates list; Monograph entry point present in nav (module itself is **[TBS]** — prototype stub only). |
| QC Manager | View Certificates list across all sample types; view a COA; approve or reject a COA with optional comment; on approval of a **Raw Material** COA, release the material (QC Number, QC Signature, auto-calculated Retest Date) and trigger a Storekeeper notification + printable Release Label. |

Whether Packaging/Product COA approval should also trigger an equivalent release step, or terminates at Approved/Rejected status, is **[TBS]** (Charter §5a / BRD §3.6).

## 3. Features & User Stories

### F1 — Raw Material Registration (Storekeeper)
**As a** Storekeeper, **I want to** register a received raw material lot with its identifying/quantity/date fields, **so that** it enters Quarantine and is trackable end-to-end.
- Acceptance: Receipt ID auto-generated (`RCV-YYYY-####`); required fields enforced (Material Name, Supplier, Supplier Batch No., Expiry Date, Receipt Date, Received By); record starts at status=Quarantine, samplingStatus=Not Sampled. **[Confirmed — prototype]**

### F2 — Packaging Material Registration (Storekeeper)
**As a** Storekeeper, **I want to** register received packaging materials separately from raw materials, **so that** packaging inventory and its own sampling workflow are tracked distinctly.
- Acceptance: Receipt ID auto-generated (`PKG-YYYY-####`); required fields enforced (Name, Quantity, Supplier, Receipt Date, Recipient); Type selectable from Primary/Secondary/Tertiary/Labeling/Other. **[Confirmed — prototype]**

### F3 — Sampling Request (Storekeeper)
**As a** Storekeeper, **I want to** request sampling on a Raw Material or Packaging Material, **so that** the Sampler is queued to act on it.
- Acceptance: samplingStatus transitions Not Sampled → Sampling Requested; cannot be requested twice. **[Confirmed — prototype]**

### F4 — Record a Sample (Sampler)
**As a** Sampler, **I want to** record the sampling event against a requested item, **so that** a physical sample is logged and labeled.
- Acceptance: required fields (Sample Size, No. of Containers, Sampler Name, Storage Condition, Sampling Date) enforced; samplingStatus → Sampled; printable sampling label generated; sample enters the Analyst worklist with testingStatus=Not Tested. **[Confirmed — prototype]**

### F5 — Product Sample Registration (Sampler)
**As a** Sampler, **I want to** register FP/SFP/Bulk samples directly, **so that** in-process/finished product testing is tracked independent of the RM receiving flow.
- Acceptance: own batch/qty/date fields per prototype form; own testingStatus lifecycle (Not Tested → In Testing → Completed); appears in Product History view and in the Analyst combined worklist. **[Confirmed — prototype]**

### F6 — Testing & COA Creation (Analyst)
**As an** Analyst, **I want to** start testing on any queued sample (RM, Packaging, or Product) and produce a COA, **so that** QC review can occur.
- Acceptance: COA auto-fills sample/material data; required fields enforced (Specs Code, Reference, Analyst Name); COA created with status=Draft; source sample's testingStatus → Completed. **[Confirmed — prototype]**

### F7 — QC Review: Approve/Reject (QC Manager)
**As a** QC Manager, **I want to** approve or reject a COA with an optional comment, **so that** only qualified material proceeds to release.
- Acceptance: on Approve, release flow is triggered (Raw Material only, per current prototype wiring); on Reject, comment stored, and for Raw Material the linked material status → Rejected. Rejection behavior for Packaging/Product COAs is **[TBS]** (no linked status field exists for them in the prototype). **[Confirmed — prototype, with noted gap]**

### F8 — Release (QC Manager)
**As a** QC Manager, **I want to** assign a QC Number and signature on COA approval, **so that** the material is formally released with a defensible record.
- Acceptance: QC Number and QC Signature required; Retest Date auto-calculated (release date + 1 year, not editable); material status → Released; Storekeeper notified; Release Label becomes printable. Scope: Raw Material only in the current baseline. **[Confirmed — prototype]**

### F9 — Notifications (Storekeeper)
**As a** Storekeeper, **I want to** be notified when a material I registered is released, **so that** I know to move it to the released warehouse and print its label.
- Acceptance: notification created on release referencing Receipt ID, QC Number, Retest Date; dismissible. **[Confirmed — prototype]**

### F10 — Employee & Role Management (Administrator)
**As an** Administrator, **I want to** create employees and assign exactly one job role each, **so that** login routes them directly to their app.
- Acceptance: no role-selector step for the employee; login → Access Control Layer resolves role → redirect to that role's dashboard. **[Confirmed — clarification]** (Replaces the prototype's role-selector login entirely, which is explicitly a demo-only mechanism.)

### F11 — Audit Trail (Platform / all apps)
**As a** Compliance stakeholder, **I want** every create/update on Material, Sample, Packaging, and COA records captured immutably, **so that** the system holds up as a GMP electronic record.
- Acceptance: who/when/old value/new value/reason(where applicable) captured per change. **[Confirmed — clarification]**

### F12 — Electronic Signature (Platform / QC Manager at minimum)
**As a** Compliance stakeholder, **I want** GMP decisions backed by a structured e-signature record, **so that** signatures are legally defensible, not a free-text field.
- Acceptance: e-signature record includes user, meaning, timestamp, hash, record reference, reason, status. Exact signing mechanism (e.g., password re-entry) is **[TBS]**. **[Confirmed — clarification]**

## 4. Navigation (per app)

| App | Confirmed screens |
|---|---|
| Storekeeper | Materials tab (table + register + view + request sampling); Packaging tab (table + register + view + request sampling); Notifications panel. |
| Sampler | Sampling Requests; Sample History; Product Samples (register FP/SFP/Bulk); Product Sample History. |
| Analyst | Home launcher (Monograph stub, Samples, Certificates); combined Samples worklist; COA form/view; Certificates list. |
| QC Manager | Certificates list; COA view; Approve/Reject action; Release modal; Release Label. |

## 5. Out of Scope for MVP

- Monograph data model/workflow (stub only in prototype) — **[TBS]**
- Release step for Packaging/Product samples — **[TBS]**
- Anything in Charter §6 open-questions list (MFA, LDAP, delegation, multi-site, notification channels beyond in-app, file storage, deployment topology beyond confirmed stack, backup/DR, UI kit choice, SPA-vs-shell decision)

## 6. Future Releases (not yet scoped)

- Monograph management module
- Packaging/Product release workflow (if confirmed in scope)
- Multi-site/multi-warehouse support
- MFA / LDAP integration

---

**Next document in sequence:** `04_UseCases.md`, followed by `05_User_Roles_and_Permissions.md`.
