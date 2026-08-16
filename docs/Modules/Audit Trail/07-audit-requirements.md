# Audit Requirements

## Completeness Requirements

### CR-AR-001: User Management Module
Every action in User Management generates audit events:

| Action | Event Type | Fields Captured |
|---|---|---|
| User login | SECURITY:SIGN (login) | IP, user agent, success/failure |
| User logout | SECURITY:SIGN (logout) | Session duration |
| Password change | USER_MGMT:UPDATE | Old hash (not stored), new hash (not stored), force_change flag |
| User created | USER_MGMT:CREATE | All user fields except password |
| User updated | USER_MGMT:UPDATE / FIELD_CHANGE | Per-field changes |
| User deactivated | USER_MGMT:TRANSITION | employment_status: ACTIVE→INACTIVE |
| Role assigned | USER_MGMT:FIELD_CHANGE | user_roles: added role_id |
| Role removed | USER_MGMT:FIELD_CHANGE | user_roles: removed role_id |
| Permission granted | USER_MGMT:FIELD_CHANGE | role_permissions: added perm_id |
| Permission revoked | USER_MGMT:FIELD_CHANGE | role_permissions: removed perm_id |
| Department changed | USER_MGMT:FIELD_CHANGE | department_id old/new |
| Session created | SECURITY:CREATE | session_id, ip, user_agent |
| Session revoked | SECURITY:DELETE | session_id, reason |

### CR-AR-002: Receiving Module
| Action | Event Type | Fields Captured |
|---|---|---|
| Material receipt created | RECEIVING:CREATE | All receipt fields |
| Batch created | RECEIVING:CREATE | All batch fields |
| Batch status change | RECEIVING:TRANSITION | status old/new |
| Quarantine decision | RECEIVING:TRANSITION | status: QUARANTINE, sampled_by, sampled_at |
| Sampling requested | RECEIVING:TRANSITION | status: SAMPLING_REQUESTED |
| Field edit (any) | RECEIVING:FIELD_CHANGE | Per-field |

### CR-AR-003: Sampling Module
| Action | Event Type | Fields Captured |
|---|---|---|
| Sample created | SAMPLING:CREATE | All sample fields |
| Sample collected | SAMPLING:TRANSITION | status: COLLECTED, collected_by, collected_at |
| Sample labeled | SAMPLING:FIELD_CHANGE | label_code, label_printed_at |
| Sample shipped | SAMPLING:TRANSITION | status: SHIPPED, shipped_to, shipped_at |
| Sample received at lab | SAMPLING:TRANSITION | status: RECEIVED_AT_LAB |
| Sample disposed | SAMPLING:TRANSITION | status: DISPOSED, reason |

### CR-AR-004: Analysis Module
| Action | Event Type | Fields Captured |
|---|---|---|
| Analysis created | ANALYSIS:CREATE | All analysis fields |
| Test assigned | ANALYSIS:FIELD_CHANGE | analyst_id, test_method_id |
| Result entered | ANALYSIS:FIELD_CHANGE | result_value, entered_by, entered_at |
| Result updated | ANALYSIS:FIELD_CHANGE | result_value old/new, reason |
| Result reviewed | ANALYSIS:TRANSITION | status: REVIEWED, reviewed_by, reviewed_at |
| Result approved | ANALYSIS:SIGN | Signature event with meaning |
| Out-of-spec (OOS) raised | ANALYSIS:TRANSITION | status: OOS, oos_reason |
| OOS investigation | ANALYSIS:CREATE | Investigation record |
| Retest requested | ANALYSIS:TRANSITION | status: RETEST_REQUESTED |

### CR-AR-005: Certificate Module
| Action | Event Type | Fields Captured |
|---|---|---|
| Certificate generated | CERTIFICATE:CREATE | All cert fields, template_version |
| Certificate edited | CERTIFICATE:FIELD_CHANGE | Per-field |
| Certificate reviewed | CERTIFICATE:TRANSITION | status: REVIEWED |
| Certificate approved | CERTIFICATE:SIGN | Signature event |
| Certificate rejected | CERTIFICATE:TRANSITION | status: REJECTED, reason |
| Certificate locked | CERTIFICATE:TRANSITION | status: LOCKED |

### CR-AR-006: Release Module
| Action | Event Type | Fields Captured |
|---|---|---|
| Release created | RELEASE:CREATE | All release fields |
| Material released | RELEASE:TRANSITION | status: RELEASED, released_by, released_at |
| Release cancelled | RELEASE:TRANSITION | status: CANCELLED, reason |
| Movement recorded | RELEASE:FIELD_CHANGE | location_from, location_to, quantity |

### CR-AR-007: Warehouse Module
| Action | Event Type | Fields Captured |
|---|---|---|
| Warehouse CRUD | WAREHOUSE:CREATE/UPDATE/DELETE | All fields |
| Location CRUD | WAREHOUSE:FIELD_CHANGE | Per-field |
| Inventory adjustment | WAREHOUSE:FIELD_CHANGE | quantity old/new, reason |

### CR-AR-008: Monograph Module
| Action | Event Type | Fields Captured |
|---|---|---|
| Monograph CRUD | MONOGRAPH:CREATE/UPDATE/DELETE | All fields |
| Test method CRUD | MONOGRAPH:FIELD_CHANGE | Per-field |
| Specification change | MONOGRAPH:FIELD_CHANGE | spec_min, spec_max, spec_unit old/new |

### CR-AR-009: Security Module
| Action | Event Type | Fields Captured |
|---|---|---|
| Failed login | SECURITY:VIEW_SENSITIVE | IP, user_agent, reason (invalid creds, locked, inactive) |
| Account locked | SECURITY:TRANSITION | locked_until, failed_count |
| MFA enrolled/disabled | SECURITY:FIELD_CHANGE | mfa_enabled, mfa_type |
| Password reset requested | SECURITY:VIEW_SENSITIVE | IP, email |
| Password reset completed | SECURITY:UPDATE | force_password_change cleared |

### CR-AR-010: System Module
| Action | Event Type | Fields Captured |
|---|---|---|
| Archive job run | SYSTEM:CREATE | archive record |
| Integrity check run | SYSTEM:VIEW_SENSITIVE | result, mismatches |
| Config changed | SYSTEM:FIELD_CHANGE | config_key, old_value, new_value |
| Backup completed | SYSTEM:CREATE | backup metadata |

---

## Integrity Requirements

### IR-AR-001: Hash Chain Continuity
- Every event's `previous_hash` must equal previous event's `event_hash` in sequence order
- First event in partition: `previous_hash` = '0' * 64
- Verified on insert (trigger), on export, on archive, daily scheduled

### IR-AR-002: Sequence Monotonicity
- `sequence_number` strictly increasing globally
- No gaps allowed (gap = potential missing event)
- Gaps detected and alerted

### IR-AR-003: Timestamp Ordering
- Events within same `correlation_id` must have non-decreasing timestamps
- Clock skew tolerance: ±1 second (NTP-synced servers)

### IR-AR-004: Signature Verification
- Every SIGN event must have valid `digital_signature.verification_status` = 'VERIFIED'
- `signed_data_hash` must match hash of business data at sign time

---

## Retention Requirements

### RR-AR-001: Minimum Retention Periods

| Module / Entity Type | Retention | Regulation Basis |
|---|---|---|
| User Management | 7 years | 21 CFR Part 11.10(e) |
| Receiving / Batches | 10 years | GMP / 21 CFR 211.180 |
| Sampling | 10 years | GMP |
| Analysis / Results | 10 years | 21 CFR 211.194 |
| Certificates | 10 years | 21 CFR 211.194 |
| Release | 10 years | GMP |
| Warehouse | 7 years | Internal |
| Monograph | 10 years | 21 CFR 211.194 |
| Security events | 7 years | 21 CFR Part 11.10(e) |
| System events | 7 years | Internal |

### RR-AR-002: Legal Hold
- Legal hold overrides retention
- Hold applied per `entity_type` + `entity_id`
- Hold events never archived/disposed until released

### RR-AR-003: Archive Before Disposal
- Events moved to archive DB before retention expiry
- Archive verified (hash + count) before active partition detached
- Disposal requires dual authorization + disposal audit event

---

## Export Requirements

### ER-AR-001: Export Completeness
- Export must include ALL events matching filters (no sampling)
- Export includes: all event fields, hash chain values, signature verification status

### ER-AR-002: Export Integrity
- PDF: Digitally signed with org certificate (PAdES)
- CSV: SHA-256 checksum file (.sha256) alongside
- Export record stores `file_hash` for later verification

### ER-AR-003: Export Authorization
- Export > 10,000 events requires QC Manager approval
- Export of security events requires System Administrator approval
- All exports logged with requestor, approver, filters, timestamp

---

## Performance Requirements

### PR-AR-001: Write Latency
- p50: < 10ms
- p99: < 50ms
- Measured from service call to audit event committed

### PR-AR-002: Query Performance
- Filtered query (date + module + entity): < 2s on 100M events
- Full partition scan (integrity check): < 5 min per monthly partition

### PR-AR-003: Export Performance
- 100K events to CSV: < 60s
- 100K events to signed PDF: < 120s

### PR-AR-004: Archive Performance
- 10M events archive: < 4 hours
- Verification: < 30 min