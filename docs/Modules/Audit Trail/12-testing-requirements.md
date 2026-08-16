# Testing Requirements

## Test Categories

### 1. Unit Tests (Backend)

#### AuditEventBuilder
- **UT-AT-001**: Build CREATE event from model instance
- **UT-AT-002**: Build UPDATE event with dirty fields only
- **UT-AT-003**: Build FIELD_CHANGE events (one per changed field)
- **UT-AT-004**: Build TRANSITION event with status old/new
- **UT-AT-005**: Build SIGN event with signature data
- **UT-AT-006**: Actor resolution: user from request, SYSTEM for jobs

#### AuditWriter
- **UT-AT-010**: Single event write in transaction
- **UT-AT-011**: Bulk event write (same transaction)
- **UT-AT-012**: Sequence number reservation atomicity
- **UT-AT-013**: Rollback on hash trigger failure
- **UT-AT-014**: Retry logic for sequence conflicts

#### HashChain
- **UT-AT-020**: Compute hash from event fields
- **UT-AT-021**: Verify chain continuity
- **UT-AT-022**: Detect single event tamper
- **UT-AT-023**: Detect missing sequence (gap)
- **UT-AT-024**: Detect reordered events

#### SignatureVerification
- **UT-AT-030**: TOTP valid token (current window)
- **UT-AT-031**: TOTP valid token (±1 window)
- **UT-AT-032**: TOTP invalid token
- **UT-AT-033**: TOTP rate limiting (5 failures → lock)
- **UT-AT-034**: Static secret valid
- **UT-AT-035**: Static secret invalid (constant-time)
- **UT-AT-036**: Static secret rate limiting
- **UT-AT-037**: Signature data hash matches business object

#### ArchiveService
- **UT-AT-040**: Select events for archival (date range)
- **UT-AT-041**: Verify hash chain before archive
- **UT-AT-042**: Copy to archive DB with count match
- **UT-AT-043**: Verify archive DB hash chain
- **UT-AT-044**: Record archive metadata

#### ExportService
- **UT-AT-050**: Query events with filters
- **UT-AT-051**: Stream to CSV (memory efficient)
- **UT-AT-052**: Generate PDF with signature
- **UT-AT-053**: Compute file hash
- **UT-AT-054**: Approval workflow

---

### 2. Integration Tests (Backend)

#### Event Capture Integration
- **IT-AT-001**: User login → SECURITY event created
- **IT-AT-002**: Material receipt create → RECEIVING:CREATE event
- **IT-AT-003**: Batch status QUARANTINE→SAMPLED → TRANSITION event
- **IT-AT-004**: Sample field change → FIELD_CHANGE event per field
- **IT-AT-005**: Analysis result enter → FIELD_CHANGE + TRANSITION
- **IT-AT-006**: Certificate approve → SIGN event with signature
- **IT-AT-007**: Material release → RELEASE:TRANSITION + SIGN

#### Hash Chain Integration
- **IT-AT-010**: Concurrent writes maintain chain order
- **IT-AT-011**: Partition boundary chain continuity
- **IT-AT-012**: Trigger rejects manual INSERT with wrong hash
- **IT-AT-013**: Daily verification job detects injected event

#### Archive Integration
- **IT-AT-020**: Monthly archive job completes successfully
- **IT-AT-021**: Archive verification catches corrupted data
- **IT-AT-022**: Partition detach after verified archive
- **IT-AT-023**: Query spans active + archive DB seamlessly

#### Export Integration
- **IT-AT-030**: Export 100K events to CSV < 60s
- **IT-AT-031**: Export 100K events to signed PDF < 120s
- **IT-AT-032**: Export approval required > 10K events
- **IT-AT-033**: Export file hash matches recorded hash
- **IT-AT-034**: Export includes all filter-matched events

#### Signature Integration
- **IT-AT-040**: TOTP setup → verify → sign flow
- **IT-AT-041**: Static secret setup → verify → sign flow
- **IT-AT-042**: Signature required on certificate approve
- **IT-AT-043**: Signature required on result approve
- **IT-AT-044**: Signature required on material release

---

### 3. API Tests

#### Query Endpoints
- **API-AT-001**: GET /events with all filter combinations
- **API-AT-002**: Pagination (limit, offset, next/prev links)
- **API-AT-003**: Sorting (timestamp, sequence_number, asc/desc)
- **API-AT-004**: Date range boundaries (inclusive)
- **API-AT-005**: Permission denial (403) for unauthorized roles
- **API-AT-006**: Query timeout handling (504)

#### Export Endpoints
- **API-AT-010**: POST /exports creates request
- **API-AT-011**: POST /exports approval workflow
- **API-AT-012**: GET /exports/{id} status progression
- **API-AT-013**: GET /exports/{id}/download serves file
- **API-AT-014**: Export list with filters

#### Integrity Endpoints
- **API-AT-020**: GET /integrity/verify full range
- **API-AT-021**: GET /integrity/verify sequence range
- **API-AT-022**: GET /integrity/verify date range
- **API-AT-023**: Mismatch response format

#### Signature Endpoints
- **API-AT-030**: POST /signature/settings setup TOTP
- **API-AT-031**: POST /signature/settings setup static
- **API-AT-032**: POST /signature/verify valid
- **API-AT-033**: POST /signature/verify invalid
- **API-AT-034**: DELETE /signature/settings

---

### 4. Frontend Tests (React/TypeScript)

#### Audit Viewer
- **FE-AT-001**: Filter bar updates URL query params
- **FE-AT-002**: Date presets set correct range
- **FE-AT-003**: Table loads first page on filter change
- **FE-AT-004**: Row expansion shows detail panel
- **FE-AT-005**: Detail panel shows field changes correctly
- **FE-AT-006**: Detail panel shows signature verification
- **FE-AT-007**: Pagination loads subsequent pages
- **FE-AT-008**: Sorting toggles asc/desc
- **FE-AT-009**: Export button opens dialog with inherited filters
- **FE-AT-010**: Real-time WebSocket updates table (if enabled)

#### Export Dialog
- **FE-AT-020**: Format selection (PDF/CSV)
- **FE-AT-021**: Estimated records updates with filters
- **FE-AT-022**: Approval warning shown > 10K
- **FE-AT-023**: Status polling shows progress
- **FE-AT-024**: Download link appears on completion

#### Integrity Page
- **FE-AT-030**: Manual verification range input
- **FE-AT-031**: Results table shows pass/fail
- **FE-AT-032**: Mismatch detail modal displays correctly

#### Signature Setup
- **FE-AT-040**: TOTP QR code renders
- **FE-AT-041**: TOTP verification succeeds
- **FE-AT-042**: Static secret setup succeeds
- **FE-AT-043**: Signature prompt modal appears on sign action
- **FE-AT-044**: TOTP countdown timer updates
- **FE-AT-045**: Error states (invalid, locked)

---

### 5. End-to-End Tests (Playwright/Cypress)

#### Critical User Journeys
- **E2E-AT-001**: Complete material receipt → sampling → analysis → certificate → release with full audit trail
- **E2E-AT-002**: User creates batch, edits fields, verifies FIELD_CHANGE events
- **E2E-AT-003**: QC Analyst enters results, QC Supervisor reviews, QC Manager approves with signature
- **E2E-AT-004**: Export audit trail for regulatory inspection
- **E2E-AT-005**: Archive job runs, verification passes, partition detached
- **E2E-AT-006**: Tamper detection: manual DB edit → integrity check alerts

---

### 6. Performance Tests

#### Load Tests
- **PT-AT-001**: 10,000 events/sec sustained write for 1 hour
- **PT-AT-002**: Concurrent writes (50 threads) maintain chain integrity
- **PT-AT-003**: Query 100M events with filters < 2s
- **PT-AT-004**: Export 100K events CSV < 60s
- **PT-AT-005**: Export 100K events PDF < 120s
- **PT-AT-006**: Archive 10M events < 4 hours
- **PT-AT-007**: Integrity verify 1M events < 5 min

#### Stress Tests
- **PT-AT-010**: Burst 50K events/sec for 5 min
- **PT-AT-011**: DB connection pool exhaustion handling
- **PT-AT-012**: Disk space exhaustion during write

---

### 7. Security Tests

- **ST-AT-001**: Direct DB INSERT blocked by permissions
- **ST-AT-002**: UPDATE/DELETE on audit_events blocked
- **ST-AT-003**: Export requires AUDIT_EXPORT permission
- **ST-AT-004**: Signature secret never exposed in API/logs
- **ST-AT-005**: TOTP rate limiting enforced
- **ST-AT-006**: Static secret constant-time comparison
- **ST-AT-007**: PII in exports requires AUDIT_VIEW_PII
- **ST-AT-008**: Archive DB read-only for app user

---

### 8. Compliance Tests (21 CFR Part 11)

- **CT-AT-001**: All workflow actions generate audit events
- **CT-AT-002**: Events immutable (no UPDATE/DELETE path)
- **CT-AT-003**: Hash chain detects tampering
- **CT-AT-004**: Electronic signature includes meaning, timestamp, user
- **CT-AT-005**: Signature manifestation on printed records
- **CT-AT-006**: Signature linked to signed data (hash)
- **CT-AT-007**: Retention periods enforced per module
- **CT-AT-008**: Legal hold prevents disposal
- **CT-AT-009**: Disposal requires dual authorization
- **CT-AT-010**: Export integrity (signed PDF, checksummed CSV)
- **CT-AT-011**: Access control per role matrix
- **CT-AT-012**: Audit trail self-auditing (meta-events logged)

---

## Test Data Requirements

### Fixtures
- 10 users with various roles
- 100 MaterialBatches across statuses
- 500 Samples
- 1,000 AnalysisResults
- 200 Certificates
- 100 Releases
- Pre-computed hash chains for verification tests
- Corrupted events for negative testing

### Test Database
- Separate test PostgreSQL instance
- Seeded via migration + fixture scripts
- Partitioned audit_events table (test partitions)
- Archive DB for archive tests

---

## CI/CD Integration

### Pipeline Stages
1. **Unit Tests**: Run on every commit (must pass)
2. **Integration Tests**: Run on PR merge to main
3. **API Tests**: Run on PR merge
4. **Frontend Tests**: Run on PR merge
5. **E2E Tests**: Run nightly / on release branch
6. **Performance Tests**: Run weekly / on performance branch
7. **Security Tests**: Run on every commit (SAST) + weekly (DAST)
8. **Compliance Tests**: Run on release candidate

### Quality Gates
- Unit test coverage ≥ 90% (audit module)
- Integration test coverage ≥ 80%
- Zero critical/high security findings
- All compliance tests pass
- Performance benchmarks within 20% of baseline