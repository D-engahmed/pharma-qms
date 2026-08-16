# Acceptance Criteria

## Overview
Each requirement from `02-requirements.md` and `07-audit-requirements.md` maps to acceptance criteria below. Criteria are written in Gherkin-style Given/When/Then format for clarity.

---

## Event Capture

### AC-AT-001: CREATE Events
**Given** a user creates a new MaterialBatch via API
**When** the transaction commits
**Then** an audit event exists with:
- action = "CREATE"
- module = "RECEIVING"
- entity_type = "MaterialBatch"
- entity_id = created batch ID
- new_values = full batch representation
- old_values = null
- actor = creating user
- hash chain valid

### AC-AT-002: UPDATE Events (Full Object)
**Given** a user updates a MaterialBatch (multiple fields)
**When** the transaction commits
**Then** an audit event exists with:
- action = "UPDATE"
- old_values = full previous state
- new_values = full new state
- FIELD_CHANGE events NOT created for this update

### AC-AT-003: FIELD_CHANGE Events (Granular)
**Given** a user updates a single field on MaterialBatch (e.g., manufacturer_id)
**When** the transaction commits
**Then** a FIELD_CHANGE event exists with:
- action = "FIELD_CHANGE"
- field_name = "manufacturer_id"
- old_values = {"manufacturer_id": "old-uuid"}
- new_values = {"manufacturer_id": "new-uuid"}
- No UPDATE event created

### AC-AT-004: DELETE Events (Soft Delete)
**Given** a user deactivates a MaterialBatch (status = CANCELLED)
**When** the transaction commits
**Then** an audit event exists with:
- action = "DELETE"
- old_values = full previous state
- new_values = {"status": "CANCELLED", ...}
- Entity NOT hard deleted from database

### AC-AT-005: TRANSITION Events
**Given** a batch transitions QUARANTINE → SAMPLED via sampling request
**When** the workflow service processes transition
**Then** a TRANSITION event exists with:
- action = "TRANSITION"
- old_values = {"status": "QUARANTINE"}
- new_values = {"status": "SAMPLED", "sampled_by": "user-id", "sampled_at": "timestamp"}
- correlation_id links to sampling request

### AC-AT-006: SIGN Events (Electronic Signature)
**Given** a QC Manager approves a certificate with valid TOTP
**When** the approval is processed
**Then** a SIGN event exists with:
- action = "SIGN"
- digital_signature present with:
  - user_id = approver
  - verification_status = "VERIFIED"
  - signature_type = "SHARED_SECRET_TOTP"
  - meaning = "Approved Certificate of Analysis for batch MB-2024-001"
  - signed_data_hash = SHA256(certificate data at sign time)

### AC-AT-007: VIEW_SENSITIVE Events
**Given** a user views a Certificate of Analysis
**When** the certificate detail API is called
**Then** a VIEW_SENSITIVE event exists with:
- action = "VIEW_SENSITIVE"
- entity_type = "Certificate"
- entity_id = certificate ID
- No old_values/new_values

### AC-AT-008: User Management Events
**Given** any user management action occurs (login, role change, password reset, etc.)
**When** the action completes
**Then** corresponding SECURITY or USER_MGMT event exists per `07-audit-requirements.md` CR-AR-001

### AC-AT-009: All Modules Covered
**Given** actions in Receiving, Sampling, Analysis, Certificate, Release, Warehouse, Monograph, Security, System
**When** any business operation occurs
**Then** audit events generated per `07-audit-requirements.md` CR-AR-002 through CR-AR-010

---

## Integrity

### AC-AT-010: Hash Chain on Insert
**Given** an audit event is inserted
**When** the DB trigger fires
**Then** event_hash = SHA256(concat(immutable_fields) || previous_hash)
**And** previous_hash = previous event's event_hash (or '0'*64 for first)

### AC-AT-011: Tamper Detection
**Given** an event's data is manually modified in DB
**When** integrity verification runs
**Then** mismatch reported with:
- sequence_number of tampered event
- expected vs actual event_hash
- error_type = "HASH_MISMATCH"

### AC-AT-012: Chain Break Detection
**Given** an event's previous_hash is manually modified
**When** integrity verification runs
**Then** mismatch reported with error_type = "CHAIN_BROKEN"

### AC-AT-013: Gap Detection
**Given** a sequence number is missing (e.g., 100, 101, 103)
**When** integrity verification runs
**Then** gap reported with error_type = "GAP"

### AC-AT-014: Daily Verification Job
**Given** it is 02:00 UTC
**When** scheduled job runs
**Then** previous day's partition verified
**And** result logged to audit_archives
**And** alert sent if mismatches found

---

## Electronic Signatures

### AC-AT-015: TOTP Setup
**Given** a user configures TOTP signature
**When** they scan QR and enter valid code
**Then** user_audit_settings created with:
- secret_type = "TOTP"
- shared_secret_encrypted = encrypted secret
- is_active = true

### AC-AT-016: TOTP Verification
**Given** a user with TOTP configured
**When** they enter current 6-digit code
**Then** verification succeeds
**And** SIGN event created with verification_status = "VERIFIED"

### AC-AT-017: TOTP Rejection
**Given** a user with TOTP configured
**When** they enter invalid code
**Then** verification fails
**And** failure counter incremented
**And** after 5 failures, 15-minute lockout

### AC-AT-018: Static Secret Setup
**Given** a user configures static secret
**When** they enter and confirm secret
**Then** user_audit_settings created with:
- secret_type = "STATIC"
- shared_secret_encrypted = Argon2id hash
- is_active = true

### AC-AT-019: Static Secret Verification
**Given** a user with static secret configured
**When** they enter correct secret
**Then** verification succeeds (constant-time comparison)

### AC-AT-020: Signature Meaning on Records
**Given** a certificate is approved with signature
**When** certificate PDF is generated
**Then** PDF includes:
- "Approved by: Jane Smith"
- "Date: 2024-01-15 10:30:00 UTC"
- "Meaning: Approved Certificate of Analysis for batch MB-2024-001"

---

## Query & Export

### AC-AT-021: Filtered Query
**Given** audit events exist across modules
**When** user queries with date_from, module=ANALYSIS, action=SIGN
**Then** only matching events returned
**And** pagination works (limit, offset)
**And** total count accurate

### AC-AT-022: Export CSV
**Given** user requests CSV export for date range
**When** export completes
**Then** file contains all matching events
**And** columns: all event fields + hash chain
**And** .sha256 checksum file provided
**And** export record file_hash matches

### AC-AT-023: Export PDF (Signed)
**Given** user requests PDF export
**When** export completes
**Then** PDF digitally signed (PAdES)
**And** signature valid, certificate chain trusted
**And** all events rendered with formatting
**And** export record file_hash matches

### AC-AT-024: Export Approval
**Given** export estimated > 10,000 events
**When** user requests export
**Then** status = PENDING_APPROVAL
**And** QC Manager notified
**And** export only generates after approval

---

## Archive

### AC-AT-025: Archive Job
**Given** monthly archive job runs for January 2024
**When** job completes
**Then** events Jan 1 - Jan 31 copied to archive DB
**And** event count matches
**And** archive_hash = SHA256(all archived events)
**And** audit_archives record created with status=VERIFIED

### AC-AT-026: Partition Detach
**Given** archive verified
**When** admin detaches partition
**Then** partition no longer in active DB
**And** active DB query for those dates returns zero
**And** archive DB query returns events

---

## Retention

### AC-AT-027: Retention Periods
**Given** events older than module-specific retention
**When** annual review runs
**Then** eligible events identified
**And** legal holds checked
**And** disposal candidates listed

### AC-AT-028: Disposal Authorization
**Given** disposal candidates approved by QC Manager + System Admin
**When** both sign disposal authorization
**Then** disposal audit event created in active DB
**And** archive partition dropped
**And** audit_archive_metadata updated

---

## Security

### AC-AT-029: Write Path Protection
**Given** application DB user attempts UPDATE on audit_events
**When** query executes
**Then** permission denied (DB level)

### AC-AT-030: Role-Based Access
**Given** QC Analyst accesses /audit
**When** page loads
**Then** 403 Forbidden (no AUDIT_VIEW permission)

**Given** QC Supervisor accesses /audit
**When** page loads
**Then** only ANALYSIS, CERTIFICATE, RELEASE events visible

### AC-AT-031: PII Protection
**Given** user without AUDIT_VIEW_PII exports events
**When** export generated
**Then** ip_address, user_agent, actor name/email masked

---

## Performance

### AC-AT-032: Write Latency
**Given** sustained load of 1,000 events/sec
**When** measuring p99 latency
**Then** p99 < 50ms

### AC-AT-033: Query Performance
**Given** 100M events in active DB
**When** filtered query (date + module + entity)
**Then** response < 2 seconds

### AC-AT-034: Export Performance
**Given** 100K events matching export criteria
**When** CSV export runs
**Then** completes < 60 seconds

---

## Compliance (21 CFR Part 11)

### AC-AT-035: Validation Evidence
**Given** automated test suite runs
**When** all tests pass
**Then** test report generated showing:
- All workflow actions generate audit events
- Hash chain integrity verified
- Signature requirements met
- Retention policies enforced
- Access controls effective

### AC-AT-036: Audit Trail Review
**Given** regulator requests audit trail for batch MB-2024-001
**When** export generated with filters
**Then** complete history from receipt to release
**And** all signatures verified
**And** hash chain intact
**And** exported as signed PDF