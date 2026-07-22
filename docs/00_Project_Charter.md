# 00 — Project Charter

**System Name (working title):** Raw Material Receiving & Release System (RM-RRS)
**Document Status:** Confirmed baseline — items not yet decided are explicitly marked **To Be Specified (TBS)**
**Traceability:** This is the root document. Every downstream document (BRD, PRD, SRS, SAS, TDD, etc.) must trace back to a statement in this Charter or in the source material below (the v3 HTML prototype and prior clarification session).

---

## 1. Source of Truth

This Charter — and everything downstream of it — is derived only from:

1. Thex prototype `pharma-prototype-v3.html` (a single-file, in-memory HTML simulation of the workflow).
2. A code-level review of the prototype conducted after the initial Charter/Glossary/BRD baseline, which surfaced a **Packaging Materials module** (Storekeeper tab, its own registration form, its own `PKG-YYYY-####` receipt ID series, a sampling-request flow, and detail view) that exists in the prototype but was missed in the original baseline. This module is now folded into the Charter/Glossary/BRD as of this revision.
3. The clarification exchange in which the following was explicitly confirmed:
   - The system must be built with **Django + React + containers**.
   - There is an **Access Control Layer** sitting above four separate business applications.
   - An employee logs in directly and is routed to the one application matching their assigned job title — there is **no role-selector login** in the real system (unlike the prototype).
   - The system must support **GMP electronic records**: audit trails and legally valid e-signatures (21 CFR Part 11 / Annex 11 style).
   - "Four seprated apps" means one dedicated application each for: **Storekeeper, Sampler, Analyst, QC Manager**.

Nothing beyond these two sources is assumed. Anything not covered is marked TBS in this and all downstream documents rather than invented.

## 2. Vision

Replace manual / paper-based (or ad-hoc spreadsheet) tracking of raw material receiving, sampling, testing, and QC release with a single, role-segregated, audit-ready electronic system, so that every material lot's lifecycle — from goods receipt to warehouse release — is captured as a legally defensible electronic record.

## 3. Objectives

- O1 — Give each of the four roles (Storekeeper, Sampler, Analyst, QC Manager) a dedicated application scoped to only the pages and actions their role is permitted to use.
- O2 — Centralize identity, role assignment, and permissions in one Access Control Layer shared by all four apps, so no application re-implements login or authorization.
- O3 — Make every create/update/delete on a GMP-relevant record produce an immutable audit trail entry (who, when, old value, new value, reason where applicable).
- O4 — Support electronic signatures as first-class, separately modeled records (not just a text field) wherever a GMP decision is made (e.g., QC release).
- O5 — Preserve the business workflow already demonstrated in the prototype (material registration → sampling → testing/COA → QC review → release) without silently changing its logic.

## 4. Scope

**In scope (confirmed):**
- Employee/role/permission management owned by this system (an administrator assigns roles; no external identity source is assumed unless stated otherwise).
- Four business applications: Storekeeper, Sampler, Analyst, QC Manager.
- Raw material receiving and quarantine tracking.
- Raw material sampling and sample labeling.
- Product sampling (Finished Product / Semi-Finished Product / Bulk), as demonstrated in the prototype.
- **Packaging material receiving** (Primary / Secondary / Tertiary / Labeling / Other) and its sampling-request flow, tracked separately from raw materials via a distinct `PKG-` ID series, as demonstrated in the prototype.
- Monograph (specification) management, testing tracking, and Certificate of Analysis (COA) creation. Note: the prototype's Monograph entry point is a UI stub only ("coming soon") — no monograph data model or workflow is demonstrated in the prototype code. Monograph fields/workflow beyond the entry point are <notification>**TBS**.</notification>
- QC review of COA, approve/reject, and material release with QC number, retest date, and QC signature.
- Audit trail and electronic signature as platform-level services used by all four apps.

**Out of scope (unless later confirmed):**
- Any workflow, object, or field not present in the prototype and not explicitly stated in the clarification session.
- Anything listed as TBS in Section 6.

## 5. Actors (confirmed)

| Actor | Source |
|---|---|
| Storekeeper | Prototype + clarification |
| Sampler | Prototype + clarification |
| Analyst | Prototype + clarification |
| QC Manager | Prototype + clarification |
| Administrator (assigns roles) | Clarification session |

Any additional role (QA, Warehouse Manager, System Operator, IT Admin, etc.) is **TBS**.

## 5a. Prototype Gap Note

The prototype's QC release logic (`submitRelease`) only updates a record in the Raw Material list (matched by `materialId`). Packaging samples and Product samples (FP/SFP/Bulk) carry `materialId: null`, so a COA created against a packaging or product sample can be reviewed and approved/rejected by the QC Manager, but the prototype does **not** wire up a full "release" state (QC Number/Retest Date/status change) for those two sample types — only for Raw Material. Whether Packaging and Product samples should get their own release step in the real system, or whether COA approval is their terminal state, is **TBS**.

## 6. Explicit Open Questions (To Be Specified)

These are called out here so every downstream document inherits the same list instead of each author guessing independently:

- Password policy, MFA, LDAP/Active Directory integration
- Electronic signature mechanism (password re-entry vs. other methods)
- Source IP / device-browser capture in audit trail
- Workflow delegation (e.g., substitute approver)
- Multi-site / multi-warehouse support
- Ownership model for master data (materials, suppliers, manufacturers)
- Notification channels (email, SMS, in-app)
- File/attachment storage strategy
- Deployment topology beyond Docker Compose (Kubernetes, reverse proxy choice, object storage)
- Backup / disaster recovery policy
- UI framework choice between MUI and Ant Design
- Whether the four React apps ship as independent SPAs or one shell with route-based separation
- Whether Packaging and Product (FP/SFP/Bulk) samples get their own QC release step, or terminate at COA approval (see §5a)
- Full Monograph data model and workflow (prototype only shows a stub entry point)

## 7. Constraints (confirmed)

- Backend: Django, Django REST Framework, PostgreSQL, Redis, Celery, Docker, Nginx.
- Frontend: React, React Router, React Query, Axios.
- Must be architected as **four separate business applications** sitting behind a shared Access Control Layer and shared database — not one application with role-based conditionals.
- Must be capable of supporting GMP validation (IQ/OQ/PQ) later; exact validation scope is TBS.

## 8. Success Criteria

- An employee created by an administrator and assigned a single role can log in and land directly on that role's dashboard with no visibility into other apps' pages.
- Every state-changing action on a Material, Sample, or COA record produces a corresponding audit record.
- The confirmed end-to-end workflow (receive → sample → test/COA → QC approve → release) can be executed by four different logged-in users, each restricted to their own app, matching the behavior already demonstrated in the prototype.

## 9. Stakeholders

- Requesting stakeholder / product owner (the user directing this project).
- End users: Storekeeper, Sampler, Analyst, QC Manager, Administrator.
- Quality/Compliance function (implied by GMP requirement) — specific stakeholder TBS.

## 10. Document Hierarchy This Charter Feeds

```
00 Project Charter → 01 Glossary → 02 BRD → 03 PRD → 04 Use Cases → 05 Roles & Permissions
→ 06 SRS → (07 NFR / 08 SAS + 09design) → 10 Database → 11 API → 12 Security → 13 Compliance
→ 16 TDD → 17/18 Backend/Frontend Architecture → 19 Coding Standards
→ 20 Implementation Roadmap → 21 Coding Roadmap → 22 Testing → 25 Deployment
```

Every later document must cite which line of this Charter (or which prototype behavior) it is implementing. If a requirement changes, this Charter is updated first, and downstream documents are revised to match.
