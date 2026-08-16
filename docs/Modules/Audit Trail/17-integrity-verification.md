# Integrity Verification

## Overview
Comprehensive design for hash chain integrity, digital signatures, tamper detection, and verification procedures meeting 21 CFR Part 11.10(e) requirements.

---

## Hash Chain Design

### Hash Algorithm
- **Algorithm**: SHA-256 (FIPS 180-4)
- **Output**: 64-character hexadecimal string
- **Implementation**: PostgreSQL `digest(data, 'sha256')` → `encode(..., 'hex')`

### Hash Input Construction
```sql
hash_input := 
    NEW.id::text || '|' ||
    NEW.sequence_number::text || '|' ||
    NEW.timestamp::text || '|' ||
    COALESCE(NEW.actor_user_id::text, '') || '|' ||
    NEW.actor_type || '|' ||
    NEW.action || '|' ||
    NEW.module || '|' ||
    NEW.entity_type || '|' ||
    NEW.entity_id::text || '|' ||
    COALESCE(NEW.field_name, '') || '|' ||
    COALESCE(NEW.old_values::text, '') || '|' ||
    COALESCE(NEW.new_values::text, '') || '|' ||
    COALESCE(NEW.correlation_id::text, '') || '|' ||
    COALESCE(NEW.session_id::text, '') || '|' ||
    COALESCE(NEW.ip_address::text, '') || '|' ||
    COALESCE(NEW.user_agent, '') || '|' ||
    COALESCE(NEW.digital_signature::text, '') || '|' ||
    NEW.previous_hash;
```

### Chain Properties
- **Genesis Hash**: First event in each partition has `previous_hash = '0' * 64`
- **Continuity**: `event_n.previous_hash = event_{n-1}.event_hash`
- **Immutability**: Any field change → different `event_hash` → chain break detected
- **Partition Boundary**: Each monthly partition starts new chain (genesis hash)

---

## Digital Signatures (21 CFR Part 11.70, 11.200)

### Signature Components
Per 21 CFR 11.200, electronic signature includes:
1. **Printed name** of signer
2. **Date and time** of signature
3. **Meaning** of signature (approval, review, authorship)

### Implementation
```json
{
  "user_id": "uuid",
  "user_name": "Jane Smith",
  "user_email": "jane@example.com",
  "timestamp": "2024-01-15T10:30:00.123456Z",
  "meaning": "Approved Certificate of Analysis for batch MB-2024-001",
  "signature_type": "SHARED_SECRET_TOTP",
  "verification_status": "VERIFIED",
  "signed_data_hash": "a1b2c3d4e5f6..."
}
```

### Signed Data Hash
- `signed_data_hash` = SHA-256(canonical_json(business_object_at_sign_time))
- Canonical JSON: sorted keys, no whitespace, deterministic
- Verified on export and integrity check
- Links signature to exact business data state

### Signature Types

#### SHARED_SECRET_TOTP
- RFC 6238 TOTP (SHA-256, 30s window, 6 digits)
- Secret stored encrypted in `user_audit_settings.shared_secret_encrypted`
- Verification: `pyotp.TOTP(secret).verify(token, valid_window=1)`

#### SHARED_SECRET_STATIC
- 32-character random string
- Stored as Argon2id hash
- Verification: constant-time comparison

### Non-Repudiation
- Signature event immutable (hash chain)
- `signed_data_hash` prevents post-signature data modification
- Signer identity bound to active user account
- Timestamp from trusted server clock (NTP-synced)

---

## Verification Procedures

### IV-PROC-001: On-Demand Verification (API)
**Endpoint**: `GET /api/v1/audit/integrity/verify`

**Algorithm**:
```python
def verify_hash_chain(from_seq: int, to_seq: int) -> VerificationResult:
    events = fetch_events_in_sequence_range(from_seq, to_seq)
    mismatches = []
    
    for i, event in enumerate(events):
        # Check previous_hash links to prior event
        expected_prev = '0' * 64 if i == 0 else events[i-1].event_hash
        if event.previous_hash != expected_prev:
            mismatches.append(Mismatch(
                sequence=event.sequence_number,
                type='CHAIN_BROKEN',
                expected=expected_prev,
                actual=event.previous_hash
            ))
        
        # Recompute event_hash
        computed = compute_hash(event, expected_prev)
        if event.event_hash != computed:
            mismatches.append(Mismatch(
                sequence=event.sequence_number,
                type='HASH_MISMATCH',
                expected=computed,
                actual=event.event_hash
            ))
    
    # Check for gaps
    sequences = [e.sequence_number for e in events]
    for seq in range(from_seq, to_seq + 1):
        if seq not in sequences:
            mismatches.append(Mismatch(
                sequence=seq,
                type='GAP',
                expected='event present',
                actual='missing'
            ))
    
    return VerificationResult(
        status='OK' if not mismatches else 'MISMATCH',
        verified_count=len(events),
        mismatches=mismatches
    )
```

### IV-PROC-002: Scheduled Daily Verification
- **Schedule**: 02:00 UTC daily
- **Scope**: Previous day's partition (full)
- **Output**: 
  - Log to `audit_archives` with `verification_hash`
  - Metrics: events verified, duration, mismatches
  - Alert on any mismatch (CRITICAL)

### IV-PROC-003: Export-Time Verification
- Every export includes hash chain verification of exported range
- Export record stores `verification_status` and `mismatch_count`
- PDF/CSV includes verification summary page

### IV-PROC-004: Archive-Time Verification
- Pre-archive: Full verification of source partition
- Post-archive: Full verification of destination partition
- Cross-verification: `archive_hash` matches source computed hash

---

## Tamper Detection & Response

### TD-DET-001: Detection Points
1. **Insert-time**: DB trigger rejects invalid `previous_hash`
2. **Scheduled**: Daily job detects historical tampering
3. **On-demand**: API verification for investigations
4. **Export**: Verification before signing
5. **Archive**: Pre/post verification

### TD-DET-002: Mismatch Classification
| Type | Cause | Severity |
|---|---|---|
| HASH_MISMATCH | Event data modified after write | CRITICAL |
| CHAIN_BROKEN | Previous hash altered or event inserted | CRITICAL |
| GAP | Sequence number missing (deleted event?) | HIGH |
| ORPHAN | Previous hash references non-existent event | HIGH |

### TD-RES-001: Response Playbook (Critical)
1. **Immediate**: Freeze affected partition (revoke INSERT/UPDATE)
2. **Notify**: Page System Admin + QC Manager + Security Officer
3. **Investigate**: 
   - Check DB audit logs (PostgreSQL `pgaudit`)
   - Identify when/what modified
   - Determine scope (single event? range?)
4. **Recover**:
   - If confirmed tampering: Restore from latest clean backup
   - If false positive (bug): Document, fix bug, re-verify
5. **Document**: Incident report per 21 CFR Part 11.10(b)
6. **Prevent**: Root cause fix, additional controls

### TD-RES-002: Response Playbook (Gap)
1. **Investigate**: Cross-reference with application logs (correlation_id)
2. **Determine**: Legitimate gap (system downtime) vs missing events
3. **Document**: Gap recorded in integrity log with explanation
4. **Monitor**: Increased verification frequency for affected range

---

## Integrity Metadata

### Verification Hash
- Computed at verification time: SHA-256(concat(all verified event_hashes))
- Stored in `audit_archives.verification_hash`
- Enables verification-of-verification

### Integrity Check Log
```sql
CREATE TABLE integrity_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    check_type VARCHAR(20) NOT NULL, -- SCHEDULED, ON_DEMAND, EXPORT, ARCHIVE
    date_from TIMESTAMPTZ NOT NULL,
    date_to TIMESTAMPTZ NOT NULL,
    from_sequence BIGINT,
    to_sequence BIGINT,
    events_verified BIGINT NOT NULL,
    mismatches JSONB, -- array of mismatch objects
    status VARCHAR(20) NOT NULL, -- PASSED, FAILED
    verification_hash CHAR(64),
    initiated_by UUID REFERENCES users(id),
    initiated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);
```

---

## Performance Optimization

### IV-PERF-001: Incremental Verification
- Daily job verifies only previous day's partition
- Full verification quarterly (or on demand)
- Merkle tree approach for large ranges (future enhancement)

### IV-PERF-002: Parallel Verification
- Partition-level parallelism (each monthly partition independent)
- Worker pool processes partitions concurrently
- Target: 1M events/minute verification throughput

### IV-PERF-003: Indexing for Verification
- `audit_events` indexed on `sequence_number` (unique)
- `audit_events` indexed on `timestamp` (partition key)
- Enables fast range scans for verification

---

## Compliance Evidence (21 CFR Part 11.10(e))

### CE-EVD-001: Operational System Checks
- Hash chain verification = operational check
- Daily automated + on-demand manual
- Results logged and retained

### CE-EVD-002: Authority Checks
- Only system processes write audit events
- Verification requires `AUDIT_VERIFY` permission
- Results immutable once logged

### CE-EVD-003: Device Checks
- NTP synchronization verified (clock drift < 1s)
- Database integrity (checksums, WAL)
- Storage health (SMART, RAID status)

### CE-EVD-004: Documentation
- This document = design specification
- Verification procedures = SOPs
- Incident reports = deviation records
- All retained per retention policy

---

## Future Enhancements

### FE-INT-001: Merkle Tree Aggregation
- Per-partition Merkle root stored in `audit_archives`
- Enables O(log n) range verification
- Reduces full verification time

### FE-INT-002: Blockchain Anchoring
- Periodic anchoring to public blockchain (optional)
- Provides external timestamp proof
- Regulatory acceptance varies

### FE-INT-003: Hardware Security Module (HSM)
- Hash computation in HSM
- Key management for PDF signing
- FIPS 140-2 Level 3 compliance