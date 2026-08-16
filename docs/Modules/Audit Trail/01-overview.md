# Mini-LIMS Audit Trail Module — Overview

## Purpose

The Audit Trail module provides a tamper-evident, immutable record of all security-sensitive and business-critical actions within the Mini-LIMS application. It ensures compliance with **21 CFR Part 11** (Electronic Records; Electronic Signatures) for pharmaceutical laboratory operations.

The module captures:
- **Security events**: Authentication, authorization changes, user lifecycle, permission modifications
- **Business events**: Material receipt, sampling, analysis, certificate generation, approval, release — every workflow transition
- **Data modifications**: Create, read (sensitive), update, delete operations on regulated entities — **every field-level change**

## Scope

| In Scope | Out of Scope |
|---|---|
| All user-initiated actions via API/UI | Technical infrastructure logs (web server, DB engine) |
| System-automated workflow transitions | Debug/trace logs |
| Data changes to regulated entities (field-level) | Application performance metrics |
| Electronic signatures for approvals | Non-GxP administrative activity |

## Design Principles

1. **Immutability**: Once written, audit records cannot be modified or deleted through application functionality
2. **Completeness**: Every regulated action generates an audit event — no gaps, including field-level changes
3. **Traceability**: Each event links to actor, timestamp, action, entity, before/after state (per field)
4. **Integrity**: Cryptographic hash chaining detects tampering
5. **Access Control**: Read access restricted to authorized roles (QC Manager, System Administrator, Auditor)
6. **Retention**: Configurable retention meeting 21 CFR Part 11.10(e) requirements
7. **Export**: Complete, human-readable export for regulatory inspection

## 21 CFR Part 11 Alignment

| Requirement | Implementation |
|---|---|
| 11.10(a) Validation | Automated tests verify audit generation for all workflows |
| 11.10(b) Audit trail | Complete, time-stamped, immutable event log with field-level changes |
| 11.10(c) Record retention | Configurable retention with archive to separate DB before disposal |
| 11.10(d) Access control | Role-based access to audit viewer |
| 11.10(e) Operational checks | Hash chain verification, digital signatures |
| 11.10(f) Authority checks | Permission-gated audit write (system-only) |
| 11.10(g) Training | Documented in training materials |
| 11.10(h) Policies | SOPs reference this module |
| 11.30 Controls for open systems | TLS, digital signatures for data exchange |
| 11.50 Signature manifestations | Printed name, date, time, meaning on approvals |
| 11.70 Signature linking | Shared-secret MFA for critical approvals |
| 11.100 General requirements | Unique identity, non-repudiation |
| 11.200 Electronic signature components | Electronic signature = user + timestamp + meaning + shared-secret verification |

## Core Entities


AuditEvent
  ├── Actor (User or System)
  ├── Timestamp (UTC, microsecond precision)
  ├── Action (CREATE, UPDATE, DELETE, TRANSITION, SIGN, VIEW_SENSITIVE, FIELD_CHANGE)
  ├── Module (Receiving, Sampling, Analysis, Certificate, Release, UserMgmt, Security, Warehouse, Monograph, System)
  ├── Entity Type (MaterialBatch, Sample, AnalysisResult, Certificate, User, Role, etc.)
  ├── Entity ID
  ├── Field Name (for FIELD_CHANGE events)
  ├── Old Value (JSONB)
  ├── New Value (JSONB)
  ├── Metadata (IP, User Agent, Correlation ID, Session ID)
  ├── Hash Chain (SHA-256 of previous event + current event)
  ├── Digital Signature (for approval/sign events)
  └── Signature Meaning (e.g., "Approved analysis results for batch MB-2024-001")

AuditEventSequence
  ├── Global sequence number (monotonic)
  └── Partition by month for performance

AuditExport
  ├── Export request metadata
  ├── Date range
  ├── Filters applied
  ├── File reference (signed PDF/CSV)
  └── Requestor + approver

AuditArchive
  ├── Archived event range
  ├── Storage location (separate DB)
  ├── Archive timestamp
  ├── Integrity hash at archive time
  └── Retention expiry
```

## Module Boundaries

- **Writes**: Only backend services — never direct DB inserts, never frontend
- **Reads**: Audit Viewer UI (authorized roles), API for export, automated integrity checks
- **No business logic**: Audit trail records facts; it does not enforce workflows
- **Separation**: Audit database user has INSERT/SELECT only — no UPDATE/DELETE
- **Archive DB**: Separate PostgreSQL instance with read-only application access