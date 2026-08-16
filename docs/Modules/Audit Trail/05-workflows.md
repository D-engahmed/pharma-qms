# Workflows

## 1. Event Capture Workflow

### Synchronous Capture (Critical Path)

```
Business Operation
       │
       ▼
┌──────────────────┐
│ Service Layer    │
│ (e.g., Material  │
│  Receipt Service)│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ AuditEvent       │
│ Builder          │
│ - Extract actor  │
│ - Determine      │
│   action/module  │
│ - Capture old/new│
│   state          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Audit Writer     │
│ (Async, same TX) │
│ - Compute hash   │
│ - Insert event   │
│ - Reserve seq #  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Business TX      │
│ Commits          │
└────────┬─────────┘
         │
         ▼
    Audit event
    persisted
```

**Key Rules**:
- Audit write occurs in **same database transaction** as business operation
- If audit write fails → business transaction rolls back (zero data loss)
- Sequence number reserved via `audit_event_sequences` insert in same TX
- Hash computed by DB trigger (immutable, cannot be bypassed)

### Asynchronous Capture (High-Volume, Non-Critical)

For bulk operations (e.g., batch import):
- Events written to staging table in same TX
- Background worker flushes to `audit_events` with hash chain
- Worker verifies continuity, alerts on gaps

---

## 2. Field-Level Change Capture

### Automatic (ORM-Level)

```
Model.save()
       │
       ▼
┌──────────────────┐
│ Dirty Field      │
│ Detection        │
│ (Django signals  │
│  or custom       │
│  Model.save)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ For each changed │
│ field:           │
│ Create FIELD_    │
│ CHANGE event     │
└────────┬─────────┘
```

**Implementation**: Django `pre_save` signal compares `instance._state.fields_cache` with current values.

### Manual (Complex Transitions)

For workflow transitions involving multiple fields:
```python
# Service explicitly builds audit events
audit_events = [
    AuditEvent(action='TRANSITION', entity=batch, old={'status': 'QUARANTINE'}, new={'status': 'SAMPLED'}),
    AuditEvent(action='FIELD_CHANGE', entity=batch, field='sampled_by', new=sampler_id),
    AuditEvent(action='FIELD_CHANGE', entity=batch, field='sampled_at', new=now()),
]
AuditWriter.bulk_write(audit_events)
```

---

## 3. Electronic Signature Workflow

```
User clicks "Approve"
       │
       ▼
┌──────────────────┐
│ Frontend:        │
│ - Show meaning   │
│ - Prompt shared  │
│   secret (TOTP   │
│   or static)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Backend:         │
│ - Verify secret  │
│ - Verify user    │
│   has permission │
│ - Build SIGN     │
│   event          │
│ - Write in TX    │
└────────┬─────────┘
         │
         ▼
    Signature
    recorded
```

**Shared Secret Verification**:
- TOTP: `pyotp.TOTP(secret).verify(token, valid_window=1)`
- Static: Constant-time comparison with stored hash (Argon2)

---

## 4. Hash Chain Integrity Verification

### On-Demand Verification (API)

```
GET /api/v1/audit/integrity/verify?from=seq&to=seq
       │
       ▼
┌──────────────────┐
│ Verification     │
│ Service          │
│ - Fetch events   │
│   in range       │
│ - Recompute      │
│   each hash      │
│ - Compare with   │
│   stored         │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Result:          │
│ - OK: all match  │
│ - MISMATCH: list │
│   of broken seq  │
└──────────────────┘
```

### Scheduled Verification (Daily Job)

```
Daily 02:00 UTC
       │
       ▼
┌──────────────────┐
│ Verify previous  │
│ day's partition  │
│ - Full scan      │
│ - Report gaps    │
│ - Alert on       │
│   mismatch       │
└────────┬─────────┘
         │
         ▼
    Alert if
    tampered
```

---

## 5. Export Workflow

```
User requests export
       │
       ▼
┌──────────────────┐
│ Create export    │
│ record: PENDING  │
└────────┬─────────┘
         │
         ▼ (if high volume)
┌──────────────────┐
│ Require approval │
│ (QC Manager)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Background job:  │
│ - Query events   │
│ - Stream to file │
│ - Compute hash   │
│ - Sign PDF /     │
│   checksum CSV   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Update export    │
│ record:          │
│ COMPLETED +      │
│ file_path + hash │
└────────┬─────────┘
         │
         ▼
    User downloads
```

---

## 6. Archive Workflow

```
Monthly (configurable)
       │
       ▼
┌──────────────────┐
│ Archive job:     │
│ - Select events  │
│   older than     │
│   threshold      │
│ - Verify hash    │
│   chain          │
│ - COPY to archive│
│   DB             │
│ - Verify counts  │
│   & hashes       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Record in        │
│ audit_archives   │
│ - Verified by    │
│   second user    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ DETACH partition │
│ from active DB   │
│ (after verification)    │
└──────────────────┘
```

---

## 7. Retention & Disposal Workflow

```
Annual review
       │
       ▼
┌──────────────────┐
│ Identify events  │
│ past retention   │
│ - Check legal    │
│   holds          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Dual auth:       │
│ - QC Manager +   │
│   System Admin   │
│ - Create disposal│
│   audit event    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ DROP archive     │
│ partition        │
└──────────────────┘
```