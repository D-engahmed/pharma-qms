# Retention Policy

## Overview
Defines retention periods, archive strategy, legal hold procedures, and disposal process for audit events per 21 CFR Part 11, GMP, and business requirements.

---

## Retention Periods by Module/Entity

| Module | Entity Type | Retention Period | Regulatory Basis |
|---|---|---|---|
| **RECEIVING** | MaterialReceipt | 10 years | 21 CFR 211.180, GMP |
| | MaterialBatch | 10 years | 21 CFR 211.180, GMP |
| | QuarantineDecision | 10 years | GMP |
| **SAMPLING** | Sample | 10 years | 21 CFR 211.180, GMP |
| | SamplingPlan | 10 years | GMP |
| **ANALYSIS** | Analysis | 10 years | 21 CFR 211.194 |
| | AnalysisResult | 10 years | 21 CFR 211.194 |
| | OOSInvestigation | 10 years | 21 CFR 211.192 |
| | TestMethod | 10 years | 21 CFR 211.194 |
| **CERTIFICATE** | Certificate | 10 years | 21 CFR 211.194 |
| | CertificateTemplate | 10 years | GMP |
| **RELEASE** | MaterialRelease | 10 years | GMP |
| | MaterialMovement | 10 years | GMP |
| **USER_MGMT** | User | 7 years | 21 CFR Part 11.10(e) |
| | Role | 7 years | 21 CFR Part 11.10(e) |
| | Permission | 7 years | 21 CFR Part 11.10(e) |
| | UserRole | 7 years | 21 CFR Part 11.10(e) |
| | RolePermission | 7 years | 21 CFR Part 11.10(e) |
| | Department | 7 years | 21 CFR Part 11.10(e) |
| **SECURITY** | Login/Logout | 7 years | 21 CFR Part 11.10(e) |
| | Session | 7 years | 21 CFR Part 11.10(e) |
| | MFA Events | 7 years | 21 CFR Part 11.10(e) |
| | Password Events | 7 years | 21 CFR Part 11.10(e) |
| **WAREHOUSE** | Warehouse | 7 years | Internal |
| | Location | 7 years | Internal |
| | InventoryAdjustment | 7 years | Internal |
| **MONOGRAPH** | Monograph | 10 years | 21 CFR 211.194 |
| | TestMethod | 10 years | 21 CFR 211.194 |
| | Specification | 10 years | 21 CFR 211.194 |
| **SYSTEM** | Archive Events | 7 years | Internal |
| | Integrity Checks | 7 years | 21 CFR Part 11.10(e) |
| | Config Changes | 7 years | Internal |
| | Backup Events | 7 years | Internal |

---

## Retention Policy Rules

### RP-POL-001: Retention Start Date
- Retention period starts from `audit_events.timestamp` (event occurrence)
- Not from archive date or export date

### RP-POL-002: Minimum Retention
- No event may be disposed before its module's minimum retention period
- Legal hold extends retention indefinitely

### RP-POL-003: Archive Before Disposal
- Events must be archived to separate DB before disposal eligibility
- Archive verification (hash + count) must pass
- Minimum 30 days in archive before disposal consideration

### RP-POL-004: Disposal Authorization
- Requires dual authorization: QC Manager + System Administrator
- Both must apply electronic signature to disposal authorization
- Disposal audit event created in active DB before partition drop

### RP-POL-005: Disposal Audit Trail
- Disposal generates audit event in active DB with:
  - action = DELETE (meta)
  - module = SYSTEM
  - entity_type = AuditPartition
  - entity_id = partition name
  - old_values = {partition, event_count, date_range}
  - new_values = {disposed: true, authorized_by: [user_ids], authorized_at: timestamp}

---

## Archive Strategy

### AS-STR-001: Archive Schedule
- Monthly partitions archived after **13 months** (1 year + 1 month grace)
- Archive job runs 1st of month for previous month's partition
- Example: February 1 → archive January partition

### AS-STR-002: Archive Destination
- Separate PostgreSQL instance (audit_archive DB)
- Different VPC/account for isolation
- Read-only for application; write only for archive process
- Encrypted at rest with separate key

### AS-STR-003: Archive Format
- Same schema as active `audit_events` table
- Partitioned by year in archive DB
- Additional column: `archived_at` TIMESTAMPTZ

### AS-STR-004: Archive Verification
1. Pre-archive: Full hash chain verification on source partition
2. Copy: COPY to archive DB (pg_dump/pg_restore or COPY)
3. Post-archive: Count match + hash chain verification on destination
4. Record: `audit_archives` with archive_hash and verification_hash
5. Dual verification: Second admin reviews and signs

### AS-STR-005: Archive Access
- Queries spanning active + archive: UNION via foreign table (postgres_fdw) or application-level merge
- Audit Viewer: Transparent access (badge indicates "Archived")
- Export: Includes archived events seamlessly
- Integrity check: Can verify archive partitions independently

---

## Legal Hold

### LH-HLD-001: Hold Triggers
- Regulatory inspection notice
- Litigation hold notice
- Quality investigation (OOS, deviation, complaint)
- Management directive

### LH-HLD-002: Hold Scope
- Applied per `entity_type` + `entity_id` combination
- Example: Hold all events for `MaterialBatch` + `batch_id = "uuid"`
- Hold applies to both active and archive DB

### LH-HLD-003: Hold Implementation
- `legal_holds` table in active DB:
  ```sql
  CREATE TABLE legal_holds (
      id UUID PRIMARY KEY,
      entity_type VARCHAR(50) NOT NULL,
      entity_id UUID NOT NULL,
      reason TEXT NOT NULL,
      issued_by UUID NOT NULL REFERENCES users(id),
      issued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      released_by UUID REFERENCES users(id),
      released_at TIMESTAMPTZ,
      is_active BOOLEAN GENERATED ALWAYS AS (released_at IS NULL) STORED
  );
  CREATE UNIQUE INDEX uq_legal_hold_active ON legal_holds(entity_type, entity_id) WHERE is_active;
  ```

### LH-HLD-004: Hold Enforcement
- Archive job: SKIP partitions containing held events
- Disposal check: BLOCK disposal if any hold exists for partition entities
- Query: No change (holds don't affect read access)
- Export: Includes held events normally

### LH-HLD-005: Hold Release
- Only issuer or System Administrator can release
- Requires electronic signature
- Release audit event generated
- Disposal eligibility re-evaluated after release

---

## Disposal Process

### DP-PRC-001: Annual Review (January)
1. System identifies partitions where `max(timestamp) < NOW() - retention(module)`
2. Cross-reference with `legal_holds` → exclude held partitions
3. Generate disposal candidates report
4. Distribute to QC Manager + System Administrator

### DP-PRC-002: Dual Authorization
1. Both reviewers examine report
2. Each applies electronic signature (TOTP/static) to disposal authorization
3. Authorization recorded in `disposal_authorizations` table:
   ```sql
   CREATE TABLE disposal_authorizations (
       id UUID PRIMARY KEY,
       partition_name VARCHAR(100) NOT NULL,
       date_from TIMESTAMPTZ NOT NULL,
       date_to TIMESTAMPTZ NOT NULL,
       event_count BIGINT NOT NULL,
       authorized_by UUID[] NOT NULL, -- both user IDs
       authorized_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
       signatures JSONB NOT NULL -- both signature objects
   );
   ```

### DP-PRC-003: Disposal Execution
1. System creates disposal audit event in active DB
2. System drops partition in archive DB: `DROP TABLE audit_events_archive_YYYY_MM`
3. System drops partition in active DB (if still attached): `ALTER TABLE audit_events DETACH PARTITION ...; DROP TABLE ...`
4. Update `audit_archive_metadata` with disposal timestamp

### DP-PRC-004: Disposal Verification
- Post-disposal: Verify partitions no longer exist
- Verify disposal audit event present in active DB
- Report to both authorizers

---

## Configuration

### Retention Configuration (Database Table)
```sql
CREATE TABLE retention_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module VARCHAR(30) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    retention_years INTEGER NOT NULL CHECK (retention_years > 0),
    archive_after_months INTEGER NOT NULL DEFAULT 13,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(module, entity_type)
);
```

### Default Policies (Seeded)
```sql
INSERT INTO retention_policies (module, entity_type, retention_years, archive_after_months) VALUES
('RECEIVING', 'MaterialReceipt', 10, 13),
('RECEIVING', 'MaterialBatch', 10, 13),
('SAMPLING', 'Sample', 10, 13),
('ANALYSIS', 'Analysis', 10, 13),
('ANALYSIS', 'AnalysisResult', 10, 13),
('CERTIFICATE', 'Certificate', 10, 13),
('RELEASE', 'MaterialRelease', 10, 13),
('USER_MGMT', 'User', 7, 13),
('SECURITY', 'Session', 7, 13),
('WAREHOUSE', 'Warehouse', 7, 13),
('MONOGRAPH', 'Monograph', 10, 13),
('SYSTEM', 'ArchiveEvent', 7, 13);
```

---

## Monitoring & Compliance

### RP-MON-001: Retention Compliance Report
- Monthly report showing:
  - Partitions by age
  - Retention status (active, archived, eligible, held)
  - Upcoming disposal candidates
  - Legal holds active

### RP-MON-002: Alerting
- Alert if partition not archived within 14 months
- Alert if disposal candidate not reviewed within 30 days
- Alert if legal hold exceeds 2 years (review required)

### RP-MON-003: Audit Evidence
- Retention policy changes logged as SYSTEM:FIELD_CHANGE
- Disposal authorizations fully audited
- Legal hold actions fully audited
- Available for regulatory inspection