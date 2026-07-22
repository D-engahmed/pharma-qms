# 02 — Business Requirements Document (BRD)

**Traces to:** 00_Project_Charter.md, 01_Glossary.md
**Status:** Confirmed items are marked **[Confirmed]**; everything else is marked **[TBS]**. No business rule below is invented — each either restates prototype behavior or restates the clarification session.

---

## 1. Business Goals

- BG1 — Digitize and control the raw-material receiving-to-release lifecycle currently only simulated in the prototype. **[Confirmed — prototype]**
- BG2 — Enforce role segregation at the application level, not just the screen level: each employee only ever sees the app matching their assigned job title. **[Confirmed — clarification]**
- BG3 — Make the system's records legally defensible under GMP electronic-record rules (21 CFR Part 11 / Annex 11 style). **[Confirmed — clarification]**
- BG4 — Centralize identity and permission management so role logic is not duplicated across four codebases. **[Confirmed — clarification]**

## 2. Actors

| Actor | Business Function |
|---|---|
| Storekeeper | Registers received raw materials and packaging materials, tracks quarantine/release status, requests sampling on either, prints release labels, sees own warehouse view. |
| Sampler | Performs raw-material sampling and product sampling (FP/SFP/Bulk), prints sampling labels, maintains sample history. |
| Analyst | Manages monographs (specifications), reviews samples, performs testing, creates COAs. |
| QC Manager | Reviews COAs, approves or rejects them, releases material with QC number/signature, prints release labels. |
| Administrator | Creates employees, assigns job roles. **[Confirmed — clarification]** |

Additional roles (QA, Warehouse Manager, IT Admin, etc.) — **[TBS]**.

## 3. Business Processes

### 3.1 Material Receiving (Storekeeper)
The Storekeeper registers a received material with: Receipt ID, Material Name, Category, Supplier, Manufacturer, Supplier Batch No., Receiving Date, Total Quantity, Unit, Batch Size, Package Type, Warehouse, Manufacturing Date, Expiry Date. The material enters **Quarantine** status with Sampling Status **Not Sampled**. **[Confirmed — prototype]**

### 3.2 Sampling Request → Sampling (Storekeeper → Sampler)
A material can move to Sampling Status **Sampling Requested**, then a Sampler records the sampling event: Sample Size, Number of Containers Sampled, Sampler Name, Storage Condition, Sampling Date. This produces Sampling Status **Sampled** and a printable sampling label. Sample history is retained and reprintable at any time. **[Confirmed — prototype]**

### 3.2a Packaging Material Receiving & Sampling Request (Storekeeper)
The Storekeeper registers a received packaging material with: Name, Type (Primary/Secondary/Tertiary/Labeling/Other), Description, Quantity, Unit, Supplier, PO No., Receipt Date, Warehouse, Recipient, Notes. Each registration gets its own receipt ID (`PKG-YYYY-####`), separate from the raw-material Receipt ID series. The Storekeeper can request sampling on a registered packaging material, which creates a Packaging Sample that enters the same sample queue used by raw-material and product samples. **[Confirmed — prototype]**

### 3.3 Product Sampling (Sampler)
Independent of the RM flow, the Sampler can register Finished Product, Semi-Finished Product, or Bulk samples directly, each with its own batch/qty/date fields and its own testing-status lifecycle (Not Tested → In Testing → Completed), tracked in a separate history view. **[Confirmed — prototype]**

### 3.4 Testing & COA Creation (Analyst)
The Analyst works from three entry points: Monograph (specifications), Samples (view and start testing on samples received from the sampling team), and Certificates. The Samples queue combines raw-material samples, product samples (FP/SFP/Bulk), and packaging samples into one worklist. A COA is created from a sample with auto-filled material/sample data (name, batch no., batch size, supplier, manufacturer, mfg/exp date, received date) plus analyst-entered data: Specs Code, Reference Standard (BP/USP/EP/JP/In-House), Analyst Name, Analysis Date, Remarks. **[Confirmed — prototype]**

The Monograph entry point exists in the prototype's navigation but has no underlying data model or workflow (displays "coming soon"). Monograph management is therefore **[TBS]** beyond the fact that an entry point for it is expected. **[Confirmed limitation — prototype]**

### 3.5 QC Review (QC Manager)
The QC Manager reviews a COA and either approves or rejects it, optionally with comments. **[Confirmed — prototype]**

### 3.6 Release (QC Manager)
On COA approval, the QC Manager releases the material by assigning a QC Number and QC Signature; Retest Date is auto-calculated as release date + 1 year. The material status becomes **Released**, the Storekeeper is notified, and a Release Label becomes printable containing Receipt ID, Material Name, Batch No., Batch Size, Supplier, Mfg/Exp Date, Container No., QC Number, Storage Condition, Retest Date, QC Signature, Release Date. **[Confirmed — prototype, Raw Material only]**

This release step is only wired up for Raw Material in the prototype. A COA created against a Packaging Sample or Product Sample can still be approved/rejected by the QC Manager, but no release-label/QC-number/status-update step exists for those two record types in the prototype code. Whether Packaging and Product samples should get an equivalent release step in the real system is **[TBS]** — see Charter §5a.

### 3.7 Employee & Role Management (Administrator)
An Administrator creates employee records and assigns each a single job role. On login, an employee is authenticated and routed directly to the dashboard of the application matching their role — no role-selector step exists in the real system. **[Confirmed — clarification]**

## 4. Business Rules

- BR1 — A material's Sampling Status must progress Not Sampled → Sampling Requested → Sampled; it cannot be skipped. **[Confirmed — prototype behavior]**
- BR2 — A material cannot be released until its COA has been approved by the QC Manager. **[Confirmed — prototype behavior]**
- BR3 — Retest Date is calculated automatically as Release Date + 1 year and is not manually editable. **[Confirmed — prototype]**
- BR4 — Sample ID equals Receipt ID for raw-material samples (i.e., they share the same identifier). **[Confirmed — prototype]**
- BR5 — Every employee has exactly one job role at a time, assigned by an Administrator; the employee cannot select or switch roles at login. **[Confirmed — clarification]**
- BR6 — No application may expose another application's pages or actions unless explicitly authorized by the permission model. **[Confirmed — clarification]**
- BR7 — Every create/update on Material, Sample, and COA records must be captured in an immutable audit history (who, when, old value, new value, reason where applicable). **[Confirmed — clarification, GMP requirement]**
- BR8 — GMP-significant actions (e.g., QC release) must be backed by a distinct electronic-signature record, not a free-text signature field. **[Confirmed — clarification, GMP requirement]**

- BR9 — Packaging Materials are tracked with their own receipt ID series (`PKG-YYYY-####`), distinct from the Raw Material Receipt ID series. **[Confirmed — prototype]**
- BR10 — Release (QC Number, Retest Date, status change, Release Label) applies to Raw Material only in the confirmed baseline; Packaging and Product samples terminate at COA approval/rejection unless a release step is confirmed for them later. **[Confirmed — prototype behavior, pending TBS decision on scope]**

Rules governing multi-site behavior, delegation of approval authority, and password/session policy — **[TBS]**.

## 5. Scope

**In scope:** Sections 3.1–3.7 above, and the four dedicated applications plus the shared Access Control Layer described in the Charter.

**Out of scope (pending confirmation):** Master data ownership/administration screens beyond what the prototype implies (e.g., managing the Material Name / Supplier / Manufacturer pick-lists as a governed master-data module), multi-site operations, any role beyond the five listed in Section 2.

## 6. Assumptions

- The four applications share one underlying database, per the confirmed architecture (Access Control Layer + shared DB, not four independent apps with four independent codebases in isolation). **[Confirmed — clarification]**
- "Legally valid e-signature" means, at minimum, a structured e-signature record (user, meaning, timestamp, hash, record reference, reason, status) as outlined in the clarification session; the exact signing mechanism (e.g., password re-entry) is **[TBS]**.

## 7. Out of Scope

- Anything not demonstrated in the prototype and not stated in the clarification session (see Charter §6 for the consolidated open-questions list).

## 8. Open Questions (carried from Project Charter §6)

See `00_Project_Charter.md` Section 6 for the authoritative list. This BRD does not repeat it to avoid two documents drifting out of sync — any change to that list must be made in the Charter first.

---

**Next document in sequence:** `03_PRD.md` (Product Requirements — features, user stories, acceptance criteria, MVP boundary), followed by `04_UseCases.md` and `05_User_Roles_and_Permissions.md`.
