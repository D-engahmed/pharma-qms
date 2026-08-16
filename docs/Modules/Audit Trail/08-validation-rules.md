# Validation Rules

## Event Validation (On Write)

### VR-VAL-001: Required Fields by Action

| Action | Required Fields |
|---|---|
| All | id, sequence_number, timestamp, actor_type, action, module, entity_type, entity_id, previous_hash, event_hash |
| USER | actor_user_id NOT NULL |
| SYSTEM | actor_user_id NULL |
| FIELD_CHANGE | field_name NOT NULL, old_values NOT NULL, new_values NOT NULL |
| SIGN | digital_signature NOT NULL, digital_signature.verification_status = 'VERIFIED' |
| TRANSITION | old_values.status NOT NULL, new_values.status NOT NULL |

### VR-VAL-002: Value Constraints

- `actor_type` IN ('USER', 'SYSTEM', 'SCHEDULED')
- `action` IN ('CREATE', 'UPDATE', 'DELETE', 'TRANSITION', 'SIGN', 'VIEW_SENSITIVE', 'FIELD_CHANGE')
- `module` IN ('RECEIVING', 'SAMPLING', 'ANALYSIS', 'CERTIFICATE', 'RELEASE', 'USER_MGMT', 'SECURITY', 'WAREHOUSE', 'MONOGRAPH', 'SYSTEM')
- `timestamp` ≤ NOW() + 1 second (clock skew tolerance)
- `sequence_number` > 0
- `previous_hash` = '0' * 64 OR valid hex SHA-256 (64 chars)
- `event_hash` = valid hex SHA-256 (64 chars)
- `ip_address` valid IPv4/IPv6 or NULL
- `digital_signature` valid JSON with required fields when present

### VR-VAL-003: Cross-Field Validation

- If `actor_type` = 'USER' → `actor_user_id` NOT NULL AND user exists AND user.employment_status = 'ACTIVE'
- If `action` = 'SIGN' → `digital_signature.user_id` = `actor_user_id`
- If `action` = 'FIELD_CHANGE' → `old_values` ≠ `new_values`
- `entity_id` format valid UUID
- `correlation_id`, `session_id` valid UUID or NULL

---

## Hash Chain Validation

### VR-HASH-001: Insert-Time Validation (DB Trigger)

```sql
-- Trigger computes and validates:
-- 1. previous_hash matches previous event's event_hash
-- 2. event_hash = SHA256(concat(immutable_fields) || previous_hash)
-- 3. Rejects insert if mismatch
```

### VR-HASH-002: On-Demand Verification

Algorithm:
```
FOR each event in sequence order:
    expected_prev = (first event) ? '0'*64 : prev_event.event_hash
    IF event.previous_hash != expected_prev:
        REPORT mismatch at event.sequence_number
    computed = SHA256(concat(event_fields) || event.previous_hash)
    IF event.event_hash != computed:
        REPORT tamper at event.sequence_number
```

### VR-HASH-003: Verification Result Codes

| Code | Meaning |
|---|---|
| OK | All hashes match, sequence continuous |
| GAP | Missing sequence number(s) |
| HASH_MISMATCH | event_hash doesn't match computed |
| CHAIN_BROKEN | previous_hash doesn't link to prior event |
| ORPHAN | Event references non-existent previous |

---

## Signature Validation

### VR-SIG-001: TOTP Verification

```python
def verify_totp(secret: str, token: str) -> bool:
    totp = pyotp.TOTP(secret, digits=6, interval=30, digest='sha256')
    return totp.verify(token, valid_window=1)  # ±30s
```

### VR-SIG-002: Static Secret Verification

```python
def verify_static(stored_hash: str, provided: str) -> bool:
    return argon2.verify(stored_hash, provided)  # constant-time
```

### VR-SIG-003: Signature Data Integrity

- `signed_data_hash` = SHA256(canonical_json(business_object_at_sign_time))
- Verified on export and integrity check
- Mismatch = data modified after signing

---

## Export Validation

### VR-EXP-001: Export Completeness Check

- Exported record count = query count
- All requested fields present
- Hash chain values included for each event
- Signature verification status included

### VR-EXP-002: Export Integrity

- PDF: Verify digital signature valid, certificate chain trusted
- CSV: Verify SHA-256 checksum matches `export_record.file_hash`

---

## Archive Validation

### VR-ARC-001: Pre-Archive Verification

- Full hash chain verification on source partition
- Count verification: source count = destination count
- Hash verification: `archive_hash` = SHA256(concat all archived events)

### VR-ARC-002: Post-Archive Verification

- Archive DB: verify hash chain on inserted partition
- Compare `archive_hash` with active DB computed hash
- Record `verification_hash` in `audit_archive_metadata`

---

## Retention Validation

### VR-RET-001: Disposal Eligibility

Event eligible for disposal IF:
- `timestamp` < NOW() - retention_period(entity_type)
- No legal hold on `entity_type` + `entity_id`
- Not referenced by active business records (FK check)

### VR-RET-002: Disposal Authorization

- Requires two approvers: QC Manager + System Administrator
- Both must sign disposal authorization (electronic signature)
- Disposal audit event created in active DB before partition drop

---

## API Input Validation

### VR-API-001: Query Parameters

| Parameter | Validation |
|---|---|
| date_from | ISO8601, ≤ date_to, ≥ 1900-01-01 |
| date_to | ISO8601, ≤ NOW() + 1 day |
| actor_user_id | Valid UUID, user exists |
| action | Valid enum |
| module | Valid enum |
| entity_type | Valid known entity |
| entity_id | Valid UUID |
| limit | 1-10000 |
| offset | ≥ 0 |

### VR-API-002: Export Request

- `date_from` < `date_to`
- Range ≤ 1 year (configurable)
- `format` IN ('PDF', 'CSV')
- If estimated events > 10000 → requires approval

---

## Frontend Validation

### VR-FE-001: Audit Viewer

- Date picker: min 1900, max today
- Entity type autocomplete from known types
- Action/module multi-select from enums
- Pagination: page size 25/50/100
- Export button: disabled if no permission

### VR-FE-002: Signature Prompt

- TOTP: 6-digit numeric input, auto-focus, paste allowed
- Static: password field, show/hide toggle
- Clear error: "Invalid code" (no distinction between wrong code vs wrong user)
- Countdown timer for TOTP (30s window)