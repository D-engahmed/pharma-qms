# 05 — User Roles and Permissions

**Traces to:** 00_Project_Charter.md, 02_BRD.md, 03_PRD.md, 04_UseCases.md
**Status:** Confirmed items are marked **[Confirmed]**; everything else **[TBS]**. Permissions here describe *what the prototype demonstrates as being possible for each role*, mapped onto the confirmed Employee → Role → Permission → App → Page → Action model. No permission is hard-coded in the frontend; the Access Control Layer is the source of truth at runtime. **[Confirmed — clarification]**

---

## 1. Model

```
Employee ──has one──▶ Job Role ──has many──▶ Permission ──scopes──▶ (App, Page, Action)
```

- One employee = exactly one job role at a time. **[Confirmed — clarification, BR5]**
- An Administrator is the only role that can create employees and assign roles. **[Confirmed — clarification]**
- No app may render a menu item or route for a page it has no permission on. **[Confirmed — clarification, BR6]**

## 2. Job Roles (confirmed set)

| Role | Routed App |
|---|---|
| Storekeeper | Storekeeper App |
| Sampler | Sampler App |
| Analyst | Analyst App |
| QC Manager | QC Manager App |
| Administrator | Access Control Layer's admin console (not one of the four business apps) |

Any additional role (QA, Warehouse Manager, IT Admin, etc.) — **[TBS]**.

## 3. Permission Matrix

Legend: C = Create, R = Read/View, U = Update, X = Execute action (e.g., request/approve/release/print), — = no access.

### 3.1 Storekeeper App

| Page / Action | Storekeeper | Sampler | Analyst | QC Manager |
|---|---|---|---|---|
| Materials table (view) | R | — | — | — |
| Register Material | CX | — | — | — |
| View Material detail | R | — | — | — |
| Request Sampling (Material) | X | — | — | — |
| Packaging table (view) | R | — | — | — |
| Register Packaging | CX | — | — | — |
| View Packaging detail | R | — | — | — |
| Request Sampling (Packaging) | X | — | — | — |
| Notifications (view/dismiss) | RU | — | — | — |
| Release Label (view/print) | RX | — | — | RX |

### 3.2 Sampler App

| Page / Action | Storekeeper | Sampler | Analyst | QC Manager |
|---|---|---|---|---|
| Sampling Requests queue (view) | — | R | — | — |
| Record Sample | — | CX | — | — |
| Sample History (view/reprint label) | — | RX | — | — |
| Product Samples: register FP/SFP/Bulk | — | CX | — | — |
| Product Sample History (view) | — | R | — | — |

### 3.3 Analyst App

| Page / Action | Storekeeper | Sampler | Analyst | QC Manager |
|---|---|---|---|---|
| Monograph entry point (stub — **[TBS]** functionality) | — | — | R | — |
| Combined Samples worklist (RM + Packaging + Product) (view) | — | — | R | — |
| Start Testing | — | — | X | — |
| Create/Edit COA (Draft) | — | — | CU | — |
| Certificates list (view own) | — | — | R | R |

### 3.4 QC Manager App

| Page / Action | Storekeeper | Sampler | Analyst | QC Manager |
|---|---|---|---|---|
| Certificates list (all) (view) | — | — | — | R |
| View COA | — | — | R | R |
| Approve COA | — | — | — | X |
| Reject COA (+ comment) | — | — | — | X |
| Release Raw Material (QC No./Signature) | — | — | — | CX |

### 3.5 Access Control Layer (Administrator)

| Page / Action | Administrator |
|---|---|
| Create Employee | CX |
| Assign/Change Job Role | U |
| Deactivate Employee | U |
| View Audit Trail | R |
| Manage Roles/Permissions | CRU |

Whether Administrator can also view/edit business data directly (Materials, Samples, COAs) is **[TBS]** — not demonstrated in the prototype and not stated in clarification.

## 4. Cross-Cutting Rules

- PR1 — No employee sees any page outside their own app's permission set. **[Confirmed — clarification, BR6]**
- PR2 — All Create/Update actions on Material, Packaging, Sample, and COA records must produce an Audit Trail entry regardless of role. **[Confirmed — clarification, BR7]**
- PR3 — QC release and QC approve/reject actions must be backed by an Electronic Signature record. **[Confirmed — clarification, BR8]** Exact scope of which additional actions (if any) require e-signature beyond QC decisions is **[TBS]**.
- PR4 — Password policy, MFA, session timeout, and account lockout rules are enforced by the Access Control Layer for every role identically unless stated otherwise; specifics are **[TBS]** (Charter §6).

## 5. Open Questions (carried forward)

- Should Packaging/Product COA approval carry its own execute-level permission distinct from Raw Material release, given the release-flow gap noted in Charter §5a? **[TBS]**
- Delegation/substitute-approver permissions for QC Manager absence. **[TBS]**
- Whether Administrator permission set includes any business-data visibility. **[TBS]**

---

**Next document in sequence (per the agreed hierarchy):** `06_SRS.md` (Software Requirements Specification).
