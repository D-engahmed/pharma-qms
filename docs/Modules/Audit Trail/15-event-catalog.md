# Event Catalog

## Overview
Complete catalog of all auditable events across Mini-LIMS modules. Each entry defines the event trigger, action type, module, entity, and fields captured.

---

## Module: RECEIVING

### MaterialReceipt

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| RECEIPT_CREATED | POST /api/v1/receiving/receipts/ | CREATE | All receipt fields |
| RECEIPT_UPDATED | PATCH /api/v1/receiving/receipts/{id}/ | UPDATE | Full old/new state |
| RECEIPT_FIELD_CHANGED | PATCH (single field) | FIELD_CHANGE | field_name, old_value, new_value |
| RECEIPT_DELETED | DELETE (soft) | DELETE | Full old state, new status=CANCELLED |

### MaterialBatch

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| BATCH_CREATED | POST /api/v1/receiving/batches/ | CREATE | All batch fields |
| BATCH_UPDATED | PATCH /api/v1/receiving/batches/{id}/ | UPDATE | Full old/new state |
| BATCH_FIELD_CHANGED | PATCH (single field) | FIELD_CHANGE | field_name, old_value, new_value |
| BATCH_QUARANTINED | Status → QUARANTINE | TRANSITION | status: QUARANTINE, quarantined_by, quarantined_at, reason |
| BATCH_SAMPLING_REQUESTED | Status → SAMPLING_REQUESTED | TRANSITION | status: SAMPLING_REQUESTED, requested_by, requested_at |
| BATCH_SAMPLED | Status → SAMPLED | TRANSITION | status: SAMPLED, sampled_by, sampled_at, sample_ids[] |
| BATCH_RELEASED | Status → RELEASED | TRANSITION | status: RELEASED, released_by, released_at |
| BATCH_REJECTED | Status → REJECTED | TRANSITION | status: REJECTED, rejected_by, rejected_at, reason |
| BATCH_DELETED | DELETE (soft) | DELETE | Full old state, new status=CANCELLED |

### QuarantineDecision

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| QUARANTINE_DECISION_CREATED | POST /api/v1/receiving/quarantine/ | CREATE | All decision fields |
| QUARANTINE_DECISION_UPDATED | PATCH | UPDATE | Full old/new state |

---

## Module: SAMPLING

### Sample

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| SAMPLE_CREATED | POST /api/v1/sampling/samples/ | CREATE | All sample fields |
| SAMPLE_UPDATED | PATCH /api/v1/sampling/samples/{id}/ | UPDATE | Full old/new state |
| SAMPLE_FIELD_CHANGED | PATCH (single field) | FIELD_CHANGE | field_name, old_value, new_value |
| SAMPLE_COLLECTED | Status → COLLECTED | TRANSITION | status: COLLECTED, collected_by, collected_at, collection_notes |
| SAMPLE_LABELED | label_code set | FIELD_CHANGE | field_name: label_code, old_value, new_value |
| SAMPLE_PRINTED | label_printed_at set | FIELD_CHANGE | field_name: label_printed_at |
| SAMPLE_SHIPPED | Status → SHIPPED | TRANSITION | status: SHIPPED, shipped_to, shipped_at, shipping_doc |
| SAMPLE_RECEIVED_AT_LAB | Status → RECEIVED_AT_LAB | TRANSITION | status: RECEIVED_AT_LAB, received_by, received_at |
| SAMPLE_DISPOSED | Status → DISPOSED | TRANSITION | status: DISPOSED, disposed_by, disposed_at, reason |
| SAMPLE_DELETED | DELETE (soft) | DELETE | Full old state |

### SamplingPlan

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| SAMPLING_PLAN_CREATED | POST | CREATE | All plan fields |
| SAMPLING_PLAN_UPDATED | PATCH | UPDATE | Full old/new state |

---

## Module: ANALYSIS

### Analysis

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| ANALYSIS_CREATED | POST /api/v1/analysis/analyses/ | CREATE | All analysis fields |
| ANALYSIS_UPDATED | PATCH /api/v1/analysis/analyses/{id}/ | UPDATE | Full old/new state |
| ANALYSIS_FIELD_CHANGED | PATCH (single field) | FIELD_CHANGE | field_name, old_value, new_value |
| ANALYSIS_ASSIGNED | analyst_id/test_method_id set | FIELD_CHANGE | field_name, old_value, new_value |
| ANALYSIS_STARTED | Status → IN_PROGRESS | TRANSITION | status: IN_PROGRESS, started_by, started_at |
| ANALYSIS_COMPLETED | Status → COMPLETED | TRANSITION | status: COMPLETED, completed_by, completed_at |
| ANALYSIS_DELETED | DELETE (soft) | DELETE | Full old state |

### AnalysisResult

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| RESULT_ENTERED | POST /api/v1/analysis/results/ | CREATE | All result fields |
| RESULT_UPDATED | PATCH /api/v1/analysis/results/{id}/ | UPDATE | Full old/new state |
| RESULT_FIELD_CHANGED | PATCH (single field) | FIELD_CHANGE | field_name, old_value, new_value |
| RESULT_REVIEWED | Status → REVIEWED | TRANSITION | status: REVIEWED, reviewed_by, reviewed_at, review_notes |
| RESULT_APPROVED | POST /api/v1/analysis/results/{id}/approve/ | SIGN | Signature event + status: APPROVED |
| RESULT_REJECTED | Status → REJECTED | TRANSITION | status: REJECTED, rejected_by, rejected_at, reason |
| OOS_RAISED | Status → OOS | TRANSITION | status: OOS, oos_reason, raised_by, raised_at |
| OOS_INVESTIGATION_CREATED | POST /api/v1/analysis/oos/ | CREATE | All investigation fields |
| RETEST_REQUESTED | Status → RETEST_REQUESTED | TRANSITION | status: RETEST_REQUESTED, requested_by, requested_at |

### TestMethod

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| TEST_METHOD_CREATED | POST | CREATE | All method fields |
| TEST_METHOD_UPDATED | PATCH | UPDATE | Full old/new state |

---

## Module: CERTIFICATE

### Certificate

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| CERTIFICATE_GENERATED | POST /api/v1/certificates/ | CREATE | All cert fields, template_version |
| CERTIFICATE_UPDATED | PATCH /api/v1/certificates/{id}/ | UPDATE | Full old/new state |
| CERTIFICATE_FIELD_CHANGED | PATCH (single field) | FIELD_CHANGE | field_name, old_value, new_value |
| CERTIFICATE_REVIEWED | Status → REVIEWED | TRANSITION | status: REVIEWED, reviewed_by, reviewed_at, review_notes |
| CERTIFICATE_APPROVED | POST /api/v1/certificates/{id}/approve/ | SIGN | Signature event + status: APPROVED |
| CERTIFICATE_REJECTED | Status → REJECTED | TRANSITION | status: REJECTED, rejected_by, rejected_at, reason |
| CERTIFICATE_LOCKED | Status → LOCKED | TRANSITION | status: LOCKED, locked_by, locked_at |
| CERTIFICATE_DELETED | DELETE (soft) | DELETE | Full old state |

### CertificateTemplate

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| TEMPLATE_CREATED | POST | CREATE | All template fields |
| TEMPLATE_UPDATED | PATCH | UPDATE | Full old/new state |
| TEMPLATE_DELETED | DELETE | DELETE | Full old state |

---

## Module: RELEASE

### MaterialRelease

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| RELEASE_CREATED | POST /api/v1/release/releases/ | CREATE | All release fields |
| RELEASE_UPDATED | PATCH /api/v1/release/releases/{id}/ | UPDATE | Full old/new state |
| RELEASE_FIELD_CHANGED | PATCH (single field) | FIELD_CHANGE | field_name, old_value, new_value |
| MATERIAL_RELEASED | Status → RELEASED | TRANSITION | status: RELEASED, released_by, released_at, release_doc |
| RELEASE_CANCELLED | Status → CANCELLED | TRANSITION | status: CANCELLED, cancelled_by, cancelled_at, reason |
| MOVEMENT_RECORDED | POST /api/v1/release/movements/ | CREATE | All movement fields |

---

## Module: USER_MGMT

### User

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| USER_CREATED | POST /api/v1/users/ | CREATE | All user fields (no password) |
| USER_UPDATED | PATCH /api/v1/users/{id}/ | UPDATE | Full old/new state |
| USER_FIELD_CHANGED | PATCH (single field) | FIELD_CHANGE | field_name, old_value, new_value |
| USER_DEACTIVATED | employment_status → INACTIVE | TRANSITION | employment_status: ACTIVE→INACTIVE |
| USER_REACTIVATED | employment_status → ACTIVE | TRANSITION | employment_status: INACTIVE→ACTIVE |
| USER_DELETED | DELETE (soft) | DELETE | Full old state |
| PASSWORD_CHANGED | POST /api/v1/auth/password/change/ | UPDATE | force_password_change flag |
| PASSWORD_RESET_REQUESTED | POST /api/v1/auth/password/reset/ | VIEW_SENSITIVE | IP, email |
| PASSWORD_RESET_COMPLETED | POST /api/v1/auth/password/reset/confirm/ | UPDATE | force_password_change cleared |

### Role

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| ROLE_CREATED | POST /api/v1/roles/ | CREATE | All role fields |
| ROLE_UPDATED | PATCH /api/v1/roles/{id}/ | UPDATE | Full old/new state |
| ROLE_DELETED | DELETE (soft) | DELETE | Full old state |

### Permission

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| PERMISSION_CREATED | POST /api/v1/permissions/ | CREATE | All permission fields |
| PERMISSION_UPDATED | PATCH | UPDATE | Full old/new state |

### UserRole (Assignment)

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| ROLE_ASSIGNED | POST /api/v1/users/{id}/roles/ | FIELD_CHANGE | field_name: user_roles, old_value: [], new_value: [role_id] |
| ROLE_REMOVED | DELETE /api/v1/users/{id}/roles/{role_id}/ | FIELD_CHANGE | field_name: user_roles, old_value: [role_id], new_value: [] |

### RolePermission (Assignment)

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| PERMISSION_GRANTED | POST /api/v1/roles/{id}/permissions/ | FIELD_CHANGE | field_name: role_permissions, old_value: [], new_value: [perm_id] |
| PERMISSION_REVOKED | DELETE /api/v1/roles/{id}/permissions/{perm_id}/ | FIELD_CHANGE | field_name: role_permissions, old_value: [perm_id], new_value: [] |

### Department

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| DEPARTMENT_CREATED | POST /api/v1/departments/ | CREATE | All department fields |
| DEPARTMENT_UPDATED | PATCH | UPDATE | Full old/new state |
| DEPARTMENT_DELETED | DELETE (soft) | DELETE | Full old state |

---

## Module: SECURITY

### Authentication

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| LOGIN_SUCCESS | POST /api/v1/auth/login/ | SIGN (login) | success=true, IP, user_agent |
| LOGIN_FAILED | POST /api/v1/auth/login/ | VIEW_SENSITIVE | success=false, IP, user_agent, reason |
| LOGOUT | POST /api/v1/auth/logout/ | SIGN (logout) | session_duration |
| ACCOUNT_LOCKED | Failed attempts threshold | TRANSITION | locked_until, failed_count |
| ACCOUNT_UNLOCKED | Admin unlock / timeout | TRANSITION | unlocked_by |

### Session

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| SESSION_CREATED | Login success | CREATE | session_id, IP, user_agent, expires_at |
| SESSION_REVOKED | Logout / admin revoke | DELETE | session_id, reason |
| SESSION_EXPIRED | Background cleanup | DELETE | session_id, reason=EXPIRED |

### MFA

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| MFA_ENROLLED | POST /api/v1/auth/mfa/enroll/ | FIELD_CHANGE | mfa_enabled: false→true, mfa_type |
| MFA_DISABLED | POST /api/v1/auth/mfa/disable/ | FIELD_CHANGE | mfa_enabled: true→false |
| MFA_VERIFIED | Login with MFA | VIEW_SENSITIVE | mfa_type, success |

---

## Module: WAREHOUSE

### Warehouse

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| WAREHOUSE_CREATED | POST /api/v1/warehouse/warehouses/ | CREATE | All warehouse fields |
| WAREHOUSE_UPDATED | PATCH | UPDATE | Full old/new state |
| WAREHOUSE_DELETED | DELETE (soft) | DELETE | Full old state |

### Location

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| LOCATION_CREATED | POST /api/v1/warehouse/locations/ | CREATE | All location fields |
| LOCATION_UPDATED | PATCH | UPDATE | Full old/new state |
| LOCATION_DELETED | DELETE (soft) | DELETE | Full old state |

### Inventory

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| INVENTORY_ADJUSTED | POST /api/v1/warehouse/inventory/adjust/ | FIELD_CHANGE | quantity: old→new, reason, adjusted_by |

---

## Module: MONOGRAPH

### Monograph

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| MONOGRAPH_CREATED | POST /api/v1/monograph/monographs/ | CREATE | All monograph fields |
| MONOGRAPH_UPDATED | PATCH | UPDATE | Full old/new state |
| MONOGRAPH_DELETED | DELETE (soft) | DELETE | Full old state |

### TestMethod

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| TEST_METHOD_CREATED | POST /api/v1/monograph/test-methods/ | CREATE | All method fields |
| TEST_METHOD_UPDATED | PATCH | UPDATE | Full old/new state |

### Specification

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| SPECIFICATION_CHANGED | PATCH (spec_min/spec_max/spec_unit) | FIELD_CHANGE | field_name, old_value, new_value |

---

## Module: SYSTEM

### Archive

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| ARCHIVE_JOB_STARTED | Scheduled job | CREATE | date_from, date_to |
| ARCHIVE_JOB_COMPLETED | Job success | UPDATE | event_count, archive_hash, duration |
| ARCHIVE_JOB_FAILED | Job failure | UPDATE | error_message |
| ARCHIVE_VERIFIED | Admin verification | UPDATE | verified_by, verified_at |
| PARTITION_DETACHED | Admin detach | DELETE | partition_name, event_count |

### Integrity

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| INTEGRITY_CHECK_STARTED | Scheduled / manual | VIEW_SENSITIVE | range |
| INTEGRITY_CHECK_PASSED | Verification OK | UPDATE | verified_count, duration |
| INTEGRITY_CHECK_FAILED | Mismatches found | UPDATE | mismatch_count, details |

### Configuration

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| CONFIG_CHANGED | Admin settings change | FIELD_CHANGE | config_key, old_value, new_value |

### Backup

| Event | Trigger | Action | Fields Captured |
|---|---|---|---|
| BACKUP_COMPLETED | Scheduled backup | CREATE | backup_id, size, duration, location |
| BACKUP_FAILED | Backup failure | CREATE | error_message |

---

## Field-Level Change Mapping

For every UPDATE that results in FIELD_CHANGE events, the following fields are individually tracked per module:

### Common Fields (All Entities)
- `created_at` (immutable, never changes)
- `updated_at` (changes on every update)
- `created_by_id`, `updated_by_id`

### MaterialBatch Specific
- `material_id`, `supplier_id`, `manufacturer_id`
- `batch_number`, `mfg_date`, `exp_date`
- `quantity`, `uom`, `status`
- `quarantine_reason`, `sampled_by`, `sampled_at`

### Sample Specific
- `sample_number`, `batch_id`, `material_id`
- `status`, `collected_by`, `collected_at`
- `label_code`, `label_printed_at`
- `shipped_to`, `shipped_at`, `received_at_lab`

### AnalysisResult Specific
- `result_value`, `result_unit`, `result_text`
- `status`, `entered_by`, `entered_at`
- `reviewed_by`, `reviewed_at`, `approved_by`, `approved_at`
- `oos_reason`, `investigation_id`

### Certificate Specific
- `certificate_number`, `batch_id`, `template_id`
- `status`, `generated_by`, `generated_at`
- `reviewed_by`, `reviewed_at`
- `approved_by`, `approved_at`, `locked_by`, `locked_at`
- `results_json` (full results snapshot)

---

## Event Volume Estimates (Daily)

| Module | Events/Day | Peak Events/Min |
|---|---|---|
| RECEIVING | 5,000 | 200 |
| SAMPLING | 3,000 | 150 |
| ANALYSIS | 15,000 | 500 |
| CERTIFICATE | 2,000 | 100 |
| RELEASE | 1,000 | 50 |
| USER_MGMT | 500 | 50 |
| SECURITY | 10,000 | 1,000 |
| WAREHOUSE | 1,000 | 50 |
| MONOGRAPH | 100 | 10 |
| SYSTEM | 500 | 20 |
| **TOTAL** | **38,100** | **~2,130** |

Annual estimate: ~14M events/year → Partition strategy validated.