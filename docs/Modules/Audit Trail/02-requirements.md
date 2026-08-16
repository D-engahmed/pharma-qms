# Functional and Non-Functional Requirements

## Functional Requirements

### Event Capture

- **FR-AT-001**: The system SHALL automatically generate an audit event for every CREATE operation on regulated entities
- **FR-AT-002**: The system SHALL automatically generate an audit event for every UPDATE operation on regulated entities, recording each changed field with old and new values
- **FR-AT-003**: The system SHALL automatically generate an audit event for every DELETE operation on regulated entities (soft delete only)
- **FR-AT-004**: The system SHALL automatically generate an audit event for every workflow state TRANSITION (e.g., MaterialBatch: QUARANTINE → SAMPLED)
- **FR-AT-005**: The system SHALL automatically generate an audit event for every electronic SIGN operation (certificate approval, result review, material release)
- **FR-AT-006**: The system SHALL automatically generate an audit event for VIEW_SENSITIVE operations (viewing certificates, analysis results, PII)
- **FR-AT-007**: The system SHALL capture field-level changes as individual FIELD_CHANGE events with field name, old value, new value
- **FR-AT-008**: The system SHALL capture all User Management events (login, logout, password change, role assignment, user create/update/deactivate)

### Event Content

- **FR-AT-010**: Each audit event SHALL contain: actor (user ID or SYSTEM), timestamp (UTC, microsecond), action, module, entity type, entity ID
- **FR-AT-011**: For FIELD_CHANGE events: field name, old value (JSONB), new value (JSONB)
- **FR-AT-012**: For SIGN events: signature meaning, signature type (SHARED_SECRET), verification status
- **FR-AT-013**: Each event SHALL include metadata: IP address, user agent, correlation ID, session ID
- **FR-AT-014**: Each event SHALL include a hash chain value linking to the previous event

### Integrity & Immutability

- **FR-AT-020**: Audit events SHALL be immutable — no UPDATE or DELETE through application functionality
- **FR-AT-021**: The system SHALL compute SHA-256 hash chain: H(current_event || previous_hash)
- **FR-AT-022**: The system SHALL verify hash chain integrity on demand and on schedule
- **FR-AT-023**: The system SHALL detect and alert on hash chain mismatches (tamper evidence)

### Electronic Signatures (21 CFR Part 11)

- **FR-AT-030**: Critical approvals SHALL require electronic signature with shared-secret verification
- **FR-AT-031**: Electronic signature SHALL capture: user ID, timestamp, signature meaning, verification result
- **FR-AT-032**: Shared secret SHALL be configured per user (TOTP or static secret) and verified at sign time
- **FR-AT-033**: Signature manifestation SHALL display: printed name, date/time, meaning on printed/exported records

### Query & Export

- **FR-AT-040**: Authorized users SHALL query audit events with filters: date range, actor, action, module, entity type, entity ID
- **FR-AT-041**: Authorized users SHALL export audit events to signed PDF and CSV
- **FR-AT-042**: Export SHALL include: all event fields, hash chain values, signature verification status
- **FR-AT-043**: Export SHALL be digitally signed (PDF) or checksummed (CSV) for integrity

### Archival (Separate DB)

- **FR-AT-050**: The system SHALL support archiving events older than configurable threshold to separate PostgreSQL database
- **FR-AT-051**: Archive operation SHALL verify hash chain integrity before transfer
- **FR-AT-052**: Archive DB SHALL be read-only for application; write access only for archive process
- **FR-AT-053**: Archive SHALL record: event range, archive timestamp, integrity hash at archive time

### Retention & Disposal

- **FR-AT-060**: Retention period SHALL be configurable per module/entity type (default: 7 years per 21 CFR Part 11)
- **FR-AT-061**: Legal hold SHALL prevent disposal of specific events/entities
- **FR-AT-062**: Disposal SHALL require dual authorization and generate disposal audit event

## Non-Functional Requirements

- **NFR-AT-001**: Audit write latency SHALL not exceed 50ms p99 (async write acceptable with durability guarantee)
- **NFR-AT-002**: System SHALL sustain 10,000 events/second peak write throughput
- **NFR-AT-003**: Query response SHALL not exceed 2 seconds for filtered queries on 100M events (with proper indexing)
- **NFR-AT-004**: Hash chain verification SHALL process 1M events/minute
- **NFR-AT-005**: Export of 100K events SHALL complete within 60 seconds
- **NFR-AT-006**: Archive of 10M events SHALL complete within 4 hours
- **NFR-AT-007**: 99.9% availability for audit write path
- **NFR-AT-008**: Zero data loss — audit events persisted before business transaction commits
- **NFR-AT-009**: PostgreSQL primary DB for active events; separate PostgreSQL instance for archive
- **NFR-AT-010**: All requirements testable via automated test suite