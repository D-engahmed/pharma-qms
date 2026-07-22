# 04 — Use Cases

**Traces to:** 00_Project_Charter.md, 02_BRD.md, 03_PRD.md
**Status:** Confirmed items are marked **[Confirmed]**; everything else **[TBS]**.

---

### UC-001 — Register Raw Material
**Actor:** Storekeeper
**Trigger:** A raw material lot arrives at the warehouse.
**Preconditions:** Storekeeper is authenticated and routed to the Storekeeper app.
**Main flow:**
1. Storekeeper opens "Register Material."
2. System auto-generates Receipt ID (`RCV-YYYY-####`) and defaults Receipt Date to today.
3. Storekeeper enters Material Name, Category, Supplier, Manufacturer, Country of Origin, Supplier Batch No., Mfg/Exp Date, Batch Size, Unit, Package Type, No. of Packages, Package Size (Total Qty auto-calculated), Warehouse, Location, PO No., Inv No., Received By.
4. System validates required fields (Material Name, Supplier, Supplier Batch No., Expiry Date, Receipt Date, Received By).
5. Material is saved with status=Quarantine, samplingStatus=Not Sampled.
**Postconditions:** Material appears in Storekeeper's Materials table. **[Confirmed — prototype]**

### UC-002 — Register Packaging Material
**Actor:** Storekeeper
**Trigger:** A packaging material lot arrives.
**Main flow:**
1. Storekeeper opens "Register Packaging."
2. System auto-generates Receipt ID (`PKG-YYYY-####`) and defaults Receipt Date to today.
3. Storekeeper enters Name, Type (Primary/Secondary/Tertiary/Labeling/Other), Description, Quantity, Unit, Supplier, PO No., Warehouse, Recipient, Notes.
4. System validates required fields (Name, Quantity, Supplier, Receipt Date, Recipient).
**Postconditions:** Packaging item appears in Storekeeper's Packaging table. **[Confirmed — prototype]**

### UC-003 — Request Sampling (Raw Material or Packaging)
**Actor:** Storekeeper
**Preconditions:** Item's samplingStatus = Not Sampled.
**Main flow:**
1. Storekeeper opens the item and selects "Request Sampling."
2. System sets samplingStatus = Sampling Requested.
**Postconditions:** Item appears in the Sampler's pending queue. Cannot be re-requested while already in this state. **[Confirmed — prototype]**

### UC-004 — Record a Sample
**Actor:** Sampler
**Preconditions:** Item's samplingStatus = Sampling Requested.
**Main flow:**
1. Sampler opens the item from the pending queue.
2. Sampler enters Sample Size, No. of Containers, Sampler Name, Storage Condition, Sampling Date.
3. System validates all fields are required.
4. System creates a Sample record, sets samplingStatus = Sampled, stores Storage Condition on the parent material.
5. System opens a printable Sampling Label preview.
**Postconditions:** Sample appears in Analyst's combined worklist with testingStatus = Not Tested. **[Confirmed — prototype]**

### UC-005 — Register Product Sample (FP/SFP/Bulk)
**Actor:** Sampler
**Main flow:**
1. Sampler selects product type (Finished Product, Semi-Finished Product, or Bulk).
2. Sampler enters Product Name, Batch No., Batch Size, Sample Quantity, Mfg/Exp Date, Sampling Date, Time of Sampling, and optional stage flags (export/local/UPA/FMA/toll, with free-text qualifiers where checked).
3. System validates required fields (Product Name, Batch No., Batch Size, Quantity of Sample, Sampling Date, Time of Sampling).
**Postconditions:** Product sample appears in Product Sample History and in the Analyst's combined worklist, tagged with its product type, testingStatus = Not Tested. **[Confirmed — prototype]**

### UC-006 — Start Testing / Create COA
**Actor:** Analyst
**Preconditions:** A sample (RM, Packaging, or Product) exists with testingStatus = Not Tested or In Testing.
**Main flow:**
1. Analyst selects the sample from the combined worklist and starts testing (testingStatus → In Testing).
2. Analyst completes the COA form: system auto-fills sample/material data (name, batch no., batch size, supplier, manufacturer, mfg/exp date, received date); Analyst enters Specs Code, Reference Standard (BP/USP/EP/JP/In-House), Analyst Name, Analysis Date, Remarks.
3. System validates required fields (Specs Code, Reference, Analyst Name).
4. System creates COA (`COA-YYYY-####`) with status=Draft and sets the sample's testingStatus = Completed.
**Postconditions:** COA appears in the Certificates list, visible to both Analyst and QC Manager. **[Confirmed — prototype]**

### UC-007 — QC Review: Approve COA (leads to Release for Raw Material)
**Actor:** QC Manager
**Preconditions:** COA exists with status=Draft.
**Main flow:**
1. QC Manager opens the COA and selects Approve, optionally entering a comment.
2. System sets COA status = Approved.
3. If the COA is linked to a Raw Material (materialId present), system opens the Release modal (see UC-008).
4. If the COA is linked to a Packaging or Product sample (no materialId), no further status change occurs on the source record in the current prototype — **[TBS]** whether an equivalent release/close-out step is needed.
**Postconditions:** For Raw Material: proceeds to release. For Packaging/Product: COA is Approved with no linked record update (gap, flagged for decision). **[Confirmed — prototype, with noted gap per Charter §5a]**

### UC-008 — Release Raw Material
**Actor:** QC Manager
**Preconditions:** COA just approved and linked to a Raw Material.
**Main flow:**
1. System proposes an auto-generated QC Number and an auto-calculated Retest Date (release date + 1 year, read-only).
2. QC Manager enters QC Signature.
3. System validates QC Number and QC Signature are present.
4. System sets material status = Released, stores QC Number/Signature/Retest Date/Released Date.
5. System creates a notification to the Storekeeper referencing Receipt ID, QC Number, Retest Date.
**Postconditions:** Release Label becomes available/printable to both QC Manager and Storekeeper. **[Confirmed — prototype]**

### UC-009 — Reject COA
**Actor:** QC Manager
**Main flow:**
1. QC Manager selects Reject on a COA, optionally with a comment.
2. System sets COA status = Rejected.
3. If linked to a Raw Material, system sets the material status = Rejected.
4. If linked to Packaging/Product sample, no linked-record status change occurs in the current prototype — **[TBS]**, same gap as UC-007.
**Postconditions:** Rejected COA visible in Certificates list with QC Manager's comment. **[Confirmed — prototype, with noted gap]**

### UC-010 — View/Reprint Sampling Label
**Actor:** Sampler
**Main flow:** Sampler selects a past sample from history and reprints its label using stored sample data.
**Postconditions:** Label reproduced identically to original. **[Confirmed — prototype]**

### UC-011 — View/Print Release Label
**Actor:** Storekeeper, QC Manager
**Preconditions:** Material status = Released.
**Main flow:** User opens the released material and prints the Release Label containing Receipt ID, Material Name, Batch No., Batch Size, Supplier, Mfg/Exp Date, Container No., QC Number, Storage Condition, Retest Date, QC Signature, Release Date.
**[Confirmed — prototype]**

### UC-012 — Dismiss/View Notification
**Actor:** Storekeeper
**Main flow:** Storekeeper opens the notification bell, views release notifications, dismisses individually.
**[Confirmed — prototype]**

### UC-013 — Employee Login and Role-Based Routing
**Actor:** Any Employee
**Preconditions:** Administrator has created the employee and assigned exactly one job role.
**Main flow:**
1. Employee authenticates (credentials TBS beyond username/password per Charter §7 Employee model).
2. Access Control Layer loads employee, role, and permissions.
3. Employee is redirected directly to their role's dashboard (Storekeeper/Sampler/Analyst/QC Manager).
**Postconditions:** No role-selector step is shown; employee cannot see other apps' pages/menus. **[Confirmed — clarification]** (This fully replaces the prototype's `selectRole()` demo mechanism, which is explicitly out of scope for the real system.)

### UC-014 — Create Employee & Assign Role
**Actor:** Administrator
**Main flow:** Administrator creates an employee record (fields per Charter §7 Employee Model) and assigns exactly one job role.
**Postconditions:** Employee can now log in and is routed per UC-013. **[Confirmed — clarification]**

### UC-015 — Monograph Management
**Actor:** Analyst
**Status:** **[TBS]** — the prototype only shows a "Monograph" entry point that displays "Monograph module coming soon!" with no underlying data model. This use case cannot be specified further until the monograph workflow is confirmed.

---

**Next document in sequence:** `05_User_Roles_and_Permissions.md`.
