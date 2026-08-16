# Development Tasks

## Phase 1: Foundation (Milestone 1-2)

### Database & Models
- [ ] **TASK-AT-001**: Create Django models for AuditEvent, AuditEventSequence, AuditExport, AuditArchive, UserAuditSettings
- [ ] **TASK-AT-002**: Create PostgreSQL migration with partitioned audit_events table (pg_partman)
- [ ] **TASK-AT-003**: Create archive DB migration (separate connection)
- [ ] **TASK-AT-004**: Implement hash chain trigger function (compute_event_hash)
- [ ] **TASK-AT-005**: Create database users and permissions (audit_app, audit_archive, audit_reader)
- [ ] **TASK-AT-006**: Add indexes per `04-database-design.md`

### Core Services
- [ ] **TASK-AT-010**: Implement AuditEventBuilder (extract actor, action, module, old/new state)
- [ ] **TASK-AT-011**: Implement AuditWriter (transactional write, sequence reservation, bulk support)
- [ ] **TASK-AT-012**: Implement HashChainVerifier (verify range, detect mismatches/gaps)
- [ ] **TASK-AT-013**: Implement SignatureService (TOTP setup/verify, static secret setup/verify)
- [ ] **TASK-AT-014**: Implement UserAuditSettings management (CRUD, encryption)

### Django Signals / Integration Points
- [ ] **TASK-AT-020**: Create audit signal receivers for User model (create, update, deactivate)
- [ ] **TASK-AT-021**: Create audit signal receivers for auth (login, logout, password change)
- [ ] **TASK-AT-022**: Create base ModelMixin for automatic FIELD_CHANGE detection
- [ ] **TASK-AT-023**: Integrate with MaterialBatch, Sample, AnalysisResult, Certificate, Release models

---

## Phase 2: Module Integration (Milestone 3-8)

### Receiving Module
- [ ] **TASK-AT-030**: Audit MaterialReceipt create/update
- [ ] **TASK-AT-031**: Audit MaterialBatch create, status transitions, field changes
- [ ] **TASK-AT-032**: Audit Quarantine decisions
- [ ] **TASK-AT-033**: Audit Sampling requests

### Sampling Module
- [ ] **TASK-AT-040**: Audit Sample create, collect, label, ship, receive, dispose
- [ ] **TASK-AT-041**: Audit Sampling queue operations

### Analysis Module
- [ ] **TASK-AT-050**: Audit Analysis create, test assignment
- [ ] **TASK-AT-051**: Audit Result entry, update, review, approve (with signature)
- [ ] **TASK-AT-052**: Audit OOS raise, investigation, retest

### Certificate Module
- [ ] **TASK-AT-060**: Audit Certificate generate, edit, review, approve (with signature), reject, lock

### Release Module
- [ ] **TASK-AT-070**: Audit Release create, release (with signature), cancel, movement

### Warehouse Module
- [ ] **TASK-AT-080**: Audit Warehouse, Location CRUD
- [ ] **TASK-AT-081**: Audit Inventory adjustments

### Monograph Module
- [ ] **TASK-AT-090**: Audit Monograph, TestMethod, Specification CRUD

### User Management Module
- [ ] **TASK-AT-100**: Audit User CRUD, role assignment, department change
- [ ] **TASK-AT-101**: Audit Role, Permission, Department CRUD
- [ ] **TASK-AT-102**: Audit Session create, revoke

### Security Module
- [ ] **TASK-AT-110**: Audit Login (success/failed), logout, lockout
- [ ] **TASK-AT-111**: Audit Password change, reset, MFA enroll/disable

### System Module
- [ ] **TASK-AT-120**: Audit Archive job, integrity check, config changes, backup

---

## Phase 3: API & Export (Milestone 2, 9)

### REST API
- [ ] **TASK-AT-130**: Implement GET /api/v1/audit/events with all filters, pagination, sorting
- [ ] **TASK-AT-131**: Implement GET /api/v1/audit/events/{id}
- [ ] **TASK-AT-132**: Implement GET /api/v1/audit/integrity/verify
- [ ] **TASK-AT-133**: Implement POST/GET /api/v1/audit/exports
- [ ] **TASK-AT-134**: Implement POST /api/v1/audit/exports/{id}/approve
- [ ] **TASK-AT-135**: Implement GET /api/v1/audit/exports/{id}/download
- [ ] **TASK-AT-136**: Implement POST/GET /api/v1/audit/archives
- [ ] **TASK-AT-137**: Implement GET/POST/DELETE /api/v1/audit/signature/settings
- [ ] **TASK-AT-138**: Implement POST /api/v1/audit/signature/verify
- [ ] **TASK-AT-139**: Add permission classes (AUDIT_VIEW, AUDIT_EXPORT, AUDIT_VERIFY, AUDIT_ARCHIVE)
- [ ] **TASK-AT-140**: Add rate limiting per `10-api-specification.md`
- [ ] **TASK-AT-141**: Generate OpenAPI spec

### Export Generation
- [ ] **TASK-AT-150**: Implement CSV export streaming (memory efficient)
- [ ] **TASK-AT-151**: Implement PDF export with ReportLab/WeasyPrint
- [ ] **TASK-AT-152**: Implement PDF digital signing (PAdES)
- [ ] **TASK-AT-153**: Implement file hash computation (SHA-256)
- [ ] **TASK-AT-154**: Implement export approval workflow
- [ ] **TASK-AT-155**: Implement background job (Celery) for export generation

---

## Phase 4: Archive & Retention (Milestone 9)

### Archive Jobs
- [ ] **TASK-AT-160**: Implement monthly archive Celery beat job
- [ ] **TASK-AT-161**: Implement pre-archive hash verification
- [ ] **TASK-AT-162**: Implement COPY to archive DB (psycopg2 COPY or pg_dump/pg_restore)
- [ ] **TASK-AT-163**: Implement post-archive verification
- [ ] **TASK-AT-164**: Implement partition detach (after verification)
- [ ] **TASK-AT-165**: Implement archive metadata recording

### Retention & Disposal
- [ ] **TASK-AT-170**: Implement retention policy configuration (per module/entity)
- [ ] **TASK-AT-171**: Implement legal hold mechanism
- [ ] **TASK-AT-172**: Implement disposal eligibility check
- [ ] **TASK-AT-173**: Implement dual-authorization disposal workflow
- [ ] **TASK-AT-174**: Implement disposal audit event + partition drop

---

## Phase 5: Frontend (Milestone 2, 9)

### Audit Viewer
- [ ] **TASK-AT-180**: Create /audit route with filter bar
- [ ] **TASK-AT-181**: Implement event table with virtualization (react-window)
- [ ] **TASK-AT-182**: Implement row expansion detail panel
- [ ] **TASK-AT-183**: Implement color-coded action/module badges
- [ ] **TASK-AT-184**: Implement pagination, sorting
- [ ] **TASK-AT-185**: Integrate with API (filters → query params)
- [ ] **TASK-AT-186**: Add WebSocket listener for real-time updates (optional)

### Export Dialog
- [ ] **TASK-AT-190**: Create export modal with format selection
- [ ] **TASK-AT-191**: Show estimated record count
- [ ] **TASK-AT-192**: Show approval warning for large exports
- [ ] **TASK-AT-193**: Poll export status, show progress
- [ ] **TASK-AT-194**: Download link on completion

### Integrity Page
- [ ] **TASK-AT-200**: Create /audit/integrity route
- [ ] **TASK-AT-201**: Show last run status, manual verification form
- [ ] **TASK-AT-202**: Display results table with mismatch details modal

### Archive Page
- [ ] **TASK-AT-210**: Create /audit/archives route (admin only)
- [ ] **TASK-AT-211**: Archive list with verify/detach actions

### Signature Setup
- [ ] **TASK-AT-220**: Create /profile/signature route
- [ ] **TASK-AT-221**: TOTP QR code generation (qrcode.react)
- [ ] **TASK-AT-222**: TOTP verification flow
- [ ] **TASK-AT-223**: Static secret setup flow

### Signature Prompt Component
- [ ] **TASK-AT-230**: Reusable modal for electronic signature
- [ ] **TASK-AT-231**: TOTP input with countdown timer
- [ ] **TASK-AT-232**: Static secret input
- [ ] **TASK-AT-233**: Loading/success/error/locked states
- [ ] **TASK-AT-234**: Integrate with Certificate approve, Result approve, Release actions

---

## Phase 6: Monitoring & Operations (Milestone 9)

- [ ] **TASK-AT-240**: Prometheus metrics (audit_write_latency, audit_events_total, integrity_check_status)
- [ ] **TASK-AT-241**: Grafana dashboards (write throughput, query latency, archive status)
- [ ] **TASK-AT-242**: Alert rules (write failures, hash mismatches, archive delays, disk space)
- [ ] **TASK-AT-243**: Structured logging (JSON, correlation_id propagation)
- [ ] **TASK-AT-244**: Backup/restore procedures for audit DBs
- [ ] **TASK-AT-245**: Disaster recovery runbook

---

## Phase 7: Testing (Continuous)

- [ ] **TASK-AT-250**: Unit tests for all services (≥90% coverage)
- [ ] **TASK-AT-251**: Integration tests for module event capture
- [ ] **TASK-AT-252**: API contract tests
- [ ] **TASK-AT-253**: Frontend component tests
- [ ] **TASK-AT-254**: E2E tests for critical journeys
- [ ] **TASK-AT-255**: Performance tests (locust/k6)
- [ ] **TASK-AT-256**: Security tests (permissions, signature, encryption)
- [ ] **TASK-AT-257**: Compliance test suite (21 CFR Part 11 evidence)

---

## Dependencies

| Task | Depends On |
|---|---|
| TASK-AT-010..014 | TASK-AT-001..006 |
| TASK-AT-020..023 | TASK-AT-010..014 |
| TASK-AT-030..120 | TASK-AT-020..023 + respective module implementations |
| TASK-AT-130..141 | TASK-AT-010..014 |
| TASK-AT-150..155 | TASK-AT-133 |
| TASK-AT-160..165 | TASK-AT-003, TASK-AT-012 |
| TASK-AT-180..186 | TASK-AT-130, TASK-AT-131 |
| TASK-AT-190..194 | TASK-AT-133, TASK-AT-134 |
| TASK-AT-220..234 | TASK-AT-013, TASK-AT-137, TASK-AT-138 |

---

## Estimated Effort (Story Points)

| Phase | Tasks | Estimate |
|---|---|---|
| Foundation | 6 | 21 |
| Module Integration | 35 | 89 |
| API & Export | 12 | 34 |
| Archive & Retention | 5 | 21 |
| Frontend | 15 | 55 |
| Monitoring | 6 | 13 |
| Testing | 8 | 40 |
| **Total** | **87** | **273** |

---

## Definition of Done per Task

- [ ] Code implemented
- [ ] Unit tests written and passing
- [ ] Integration tests passing (where applicable)
- [ ] Code reviewed and approved
- [ ] Merged to main
- [ ] Deployed to staging
- [ ] Verified in staging
- [ ] Documentation updated (if API/UI changed)