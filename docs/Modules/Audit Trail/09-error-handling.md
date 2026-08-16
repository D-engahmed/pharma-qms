# Error Handling

## Audit Write Failures

### EH-ERR-001: Database Unavailable (Active DB)

**Scenario**: `audit_events` insert fails (connection loss, disk full, constraint violation)

**Behavior**:
1. Business transaction rolls back (audit write in same TX)
2. Return 503 Service Unavailable to client
3. Alert: Critical — audit path down (PagerDuty/opsgenie)
4. Client: Retry with exponential backoff (max 3 retries)
5. Circuit breaker: Open after 5 consecutive failures, auto-close after 30s success

**Recovery**:
- DB restored → circuit breaker closes → normal operation
- No data loss (transaction atomicity)

### EH-ERR-002: Hash Chain Mismatch on Write

**Scenario**: Trigger detects `previous_hash` mismatch (concurrent insert race, manual DB tampering)

**Behavior**:
1. Insert rejected by trigger (exception)
2. Business transaction rolls back
3. Return 500 Internal Server Error
4. Alert: Critical — hash chain integrity violation
5. Log full context: expected vs actual hash, sequence numbers

**Recovery**:
- Investigate: concurrent writer bug? manual DB access?
- Fix root cause → retry

### EH-ERR-003: Sequence Number Conflict

**Scenario**: Two transactions reserve same `sequence_number`

**Behavior**:
1. Unique constraint violation on `audit_event_sequences.sequence_number`
2. Business transaction rolls back
3. Retry with new sequence reservation (application-level retry logic)

**Prevention**:
- Sequence reservation in same TX as event insert
- Use `INSERT ... ON CONFLICT DO NOTHING` + retry loop

---

## Degraded Modes

### EH-DEG-001: Read-Only Mode (Active DB Read Replica Lag)

**Trigger**: Replica lag > 30s or replica unavailable

**Behavior**:
- Audit viewer: Show "data may be stale" banner
- Redirect queries to primary (if acceptable load)
- Export: Use primary only
- No impact on audit writes (always primary)

### EH-DEG-002: Archive DB Unavailable

**Trigger**: Archive job cannot connect to archive DB

**Behavior**:
- Archive job: Retry 3x with 10min backoff
- Alert: Warning — archive delayed
- Active partition: NOT detached (retention extended)
- Next scheduled run retries

**Recovery**:
- Archive DB restored → job completes → partition detached

### EH-DEG-003: Export Generation Failure

**Trigger**: Background export job crashes or times out

**Behavior**:
- Export record: status = FAILED, error_message populated
- Alert: Warning — export failed
- User notified via in-app notification
- User may retry (new export request)

---

## Integrity Verification Failures

### EH-INT-001: Hash Mismatch Detected (Scheduled Job)

**Scenario**: Daily verification finds `event_hash` ≠ computed hash

**Behavior**:
1. Job logs: sequence_number, expected_hash, actual_hash, event JSON
2. Alert: CRITICAL — audit tamper detected
3. Creates `audit_archives` record with status=FAILED, verification_hash=mismatch_detail
4. Does NOT auto-repair (immutability)

**Response Playbook**:
1. Freeze affected partition (revoke INSERT)
2. Forensic analysis: when/what modified
3. Restore from backup if confirmed tampering
4. Document incident per 21 CFR Part 11.10(b)

### EH-INT-002: Sequence Gap Detected

**Scenario**: Missing `sequence_number` in range

**Behavior**:
1. Log gap range
2. Alert: WARNING — potential missing events
3. Cross-check with application logs (correlation_id)
4. If confirmed missing: document gap, investigate cause

### EH-INT-003: Signature Verification Failure on Export

**Scenario**: SIGN event has `verification_status` ≠ 'VERIFIED' or `signed_data_hash` mismatch

**Behavior**:
1. Export includes event with `signature_status`: 'INVALID'
2. Export PDF/CSV marks row as "Signature Invalid"
3. Alert: WARNING — invalid signature in export
4. Does not block export (completeness)

---

## Electronic Signature Errors

### EH-SIG-001: TOTP Verification Failed

**Behavior**:
- Return 400: "Invalid verification code"
- Increment failure counter on `user_audit_settings`
- After 5 failures: lock for 15 minutes
- Audit event: SECURITY:VIEW_SENSITIVE (failed_signature_attempt)

### EH-SIG-002: Static Secret Verification Failed

**Behavior**:
- Return 400: "Invalid secret"
- Constant-time comparison (no timing attack)
- Increment failure counter
- After 5 failures: lock for 15 minutes

### EH-SIG-003: Signature Secret Not Configured

**Behavior**:
- Return 409: "Electronic signature not configured for user"
- Redirect to profile → configure signature
- Audit event: USER_MGMT:VIEW_SENSITIVE (signature_setup_required)

---

## Export Errors

### EH-EXP-001: Query Timeout

**Behavior**:
- Export job: statement_timeout = 300s
- On timeout: status = FAILED, error = "Query timeout"
- Suggest: narrower date range, add filters

### EH-EXP-002: File Write Failure (Disk Full, Permissions)

**Behavior**:
- Status = FAILED, error = "File write failed"
- Alert: Warning — export storage issue
- Cleanup partial file

### EH-EXP-003: PDF Signing Failure

**Behavior**:
- Status = FAILED, error = "PDF signing failed"
- Fallback: Generate unsigned PDF + separate signature file
- Alert: Warning — signing certificate issue

---

## Error Response Format (API)

```json
{
  "error": {
    "code": "AUDIT_WRITE_FAILED",
    "message": "Audit event could not be persisted",
    "details": {
      "reason": "DB_CONSTRAINT_VIOLATION",
      "constraint": "audit_events_previous_hash_fkey",
      "retryable": true
    },
    "correlation_id": "uuid",
    "timestamp": "2024-01-15T10:30:00.123456Z"
  }
}
```

### Standard Error Codes

| Code | HTTP | Retryable | Description |
|---|---|---|---|
| AUDIT_WRITE_FAILED | 503 | Yes | DB insert failed |
| AUDIT_HASH_MISMATCH | 500 | No | Integrity violation |
| AUDIT_SEQUENCE_CONFLICT | 503 | Yes | Sequence race |
| AUDIT_SIGNATURE_INVALID | 400 | No | TOTP/secret verify failed |
| AUDIT_SIGNATURE_NOT_CONFIGURED | 409 | No | User missing signature setup |
| AUDIT_EXPORT_FAILED | 500 | Yes | Export generation failed |
| AUDIT_EXPORT_PENDING_APPROVAL | 202 | N/A | Awaiting manager approval |
| AUDIT_QUERY_TIMEOUT | 504 | Yes | Query exceeded timeout |
| AUDIT_FORBIDDEN | 403 | No | Insufficient permissions |

---

## Monitoring & Alerting

### Critical Alerts (Page Immediately)
- Audit write failure rate > 1% over 5min
- Hash chain mismatch detected
- Archive DB unreachable > 30min
- Signature verification failure rate > 10%

### Warning Alerts (Ticket + Notify)
- Replica lag > 30s
- Archive job delayed > 24h
- Export failure rate > 5%
- Sequence gap detected
- Disk usage > 80% on audit DB

### Info Alerts (Log Only)
- Export completed
- Archive completed
- Integrity check passed
- Signature configured/rotated