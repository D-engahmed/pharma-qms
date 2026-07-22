# 01 — Glossary

**Traces to:** 00_Project_Charter.md
**Purpose:** Controlled terminology so every later document (BRD, SRS, TDD, etc.) uses the same words for the same concepts. Terms are drawn only from the prototype and the confirmed clarifications; anything not evidenced there is marked TBS.

| Term | Definition | Source |
|---|---|---|
| **RM** | Raw Material — the material type received and tracked from goods receipt through release. | Prototype |
| **FP** | Finished Product — a product-sample type registered by the Sampler. | Prototype |
| **SFP** | Semi-Finished Product — a product-sample type registered by the Sampler, distinct from Bulk and FP. | Prototype |
| **Bulk** | A third product-sample type registered by the Sampler alongside FP and SFP. | Prototype |
| **Packaging Material** | A material registered by the Storekeeper distinct from Raw Material, classified as Primary, Secondary, Tertiary, Labeling, or Other, tracked with its own receipt ID series and its own sampling-request flow. | Prototype |
| **Receipt ID** | Unique identifier assigned to a received material lot; also used as the Sample ID for its corresponding raw-material sample. Packaging materials use a separate `PKG-YYYY-####` receipt ID series. | Prototype |
| **Supplier Batch No.** | The batch/lot number assigned by the supplier for a received material. | Prototype |
| **Quarantine** | Status of a received material before QC release; material in this state may not be used in production. | Prototype |
| **Released** | Status of a material after QC Manager approval and assignment of a QC Number. | Prototype |
| **Rejected** | Status of a material or COA that failed QC review. | Prototype |
| **Sampling Status** | Tracks whether a material is Not Sampled, Sampling Requested, or Sampled. | Prototype |
| **Sample** | A physical raw-material sample taken by the Sampler against a received material, recorded with sample size, number of containers, storage condition, sampler name, and sampling date. | Prototype |
| **Product Sample** | A sample of FP, SFP, or Bulk registered directly by the Sampler (not derived from an RM receipt), tracked separately with its own testing status. | Prototype |
| **Packaging Sample** | A sample generated when sampling is requested against a registered Packaging Material; enters the same testing/COA queue as raw-material and product samples, tagged with sample type "Packaging". | Prototype |
| **Monograph** | The analyst-managed specification for a material against which testing is performed. | Prototype |
| **COA (Certificate of Analysis)** | The analyst-created record of test results for a sample, including specs code, reference standard, analyst name, analysis date, and remarks; subject to QC Manager review. | Prototype |
| **Reference Standard** | The pharmacopoeia or internal standard a COA is tested against (e.g., BP, USP, EP, JP, In-House). | Prototype |
| **QC Number** | Identifier assigned by the QC Manager at the moment a material is released. | Prototype |
| **Retest Date** | Date by which a released material must be retested; auto-calculated as release date + 1 year in the prototype. | Prototype |
| **QC Signature** | The QC Manager's recorded signature/name at time of release. | Prototype |
| **Release Label** | The printable label generated once a material is released, containing receipt, batch, QC, and storage details. | Prototype |
| **Sampling Label** | The printable label generated after a sampling event is recorded. | Prototype |
| **Employee** | A user of the system whose job role is assigned by an Administrator. | Clarification |
| **Job Role / Role** | The single job title assigned to an employee, determining which of the four applications they are routed to at login. | Clarification |
| **Administrator** | The role responsible for creating employees and assigning their job role. | Clarification |
| **Access Control Layer** | The shared platform service (authentication, authorization, RBAC, audit, e-signature, session/user management) sitting above the four business applications. | Clarification |
| **Audit Trail** | The immutable record of who changed what, when, from what old value to what new value, and why (where applicable), required for GMP compliance. | Clarification |
| **Electronic Signature (e-signature)** | A GMP-style signature record (distinct from a plain text field) tied to a meaning, timestamp, and record reference, required for legally valid electronic records. | Clarification |
| **21 CFR Part 11** | US FDA regulation governing electronic records and electronic signatures; referenced as the compliance target. | Clarification |
| **Annex 11** | EU GMP guideline governing computerized systems; referenced alongside 21 CFR Part 11 as a compliance target. | Clarification |
| **ALCOA+** | Data integrity principle set (Attributable, Legible, Contemporaneous, Original, Accurate, + Complete, Consistent, Enduring, Available) — referenced as a target for the compliance document; detailed mapping is TBS. | Clarification (referenced, not yet detailed) |

**Terms intentionally not yet defined (TBS):** IQ/OQ/PQ validation terminology beyond the acronym, cost center/department vocabulary, notification-channel terminology, multi-site/warehouse vocabulary — these will be added when the corresponding requirement is confirmed.
