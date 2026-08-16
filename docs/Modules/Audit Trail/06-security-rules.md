# Security Rules

## Access Control Matrix

| Role | View Audit Events | Export Audit Events | Approve Exports | Manage Archive | Verify Integrity | Configure Retention |
|---|---|---|---|---|---|---|
| System Administrator | ✅ All | ✅ All | ✅ | ✅ | ✅ | ✅ |
| QC Manager | ✅ All | ✅ All | ✅ | ❌ | ✅ | ✅ |
| QC Supervisor | ✅ Module-scoped | ✅ Module-scoped | ❌ | ❌ | ✅ | ❌ |
| QC Analyst | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Store Keeper | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Sampler | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Auditor (external) | ✅ Read-only | ✅ Read-only | ❌ | ❌ | ✅ | ❌ |

**Module-scoped**: Events where `module` matches user's operational modules (e.g., QC Supervisor sees ANALYSIS, CERTIFICATE, RELEASE)

---

## 21 CFR Part 11 Specific Controls

### 11.10(d) — Access Control

- **SR-SEC-001**: Audit trail access requires active user account with `AUDIT_VIEW` permission
- **SR-SEC-002**: Export requires `AUDIT_EXPORT` permission + approval for >10K events
- **SR-SEC-003**: Archive management requires `AUDIT_ARCHIVE` permission (System Admin only)
- **SR-SEC-004**: Integrity verification requires `AUDIT_VERIFY` permission
- **SR-SEC-005**: Failed access attempts logged to security audit (separate from business audit)

### 11.10(f) — Authority Checks

- **SR-SEC-010**: Only system processes (backend services) may WRITE audit events
- **SR-SEC-011**: Direct database INSERT on `audit_events` blocked by DB permissions
- **SR-SEC-012**: Application DB user has `INSERT, SELECT` only on audit tables
- **SR-SEC-013**: No application code path allows UPDATE/DELETE on audit tables

### 11.10(e) — Operational Checks

- **SR-SEC-020**: Hash chain verified on every export
- **SR-SEC-021**: Hash chain verified daily via scheduled job
- **SR-SEC-022**: Tamper detection triggers immediate alert (email + in-app) to System Admin + QC Manager
- **SR-SEC-023**: Verification results logged to `audit_archives` (meta-audit)

### 11.30 — Open Systems Controls

- **SR-SEC-030**: All API communication over TLS 1.2+
- **SR-SEC-031**: Export files digitally signed (PDF) or checksummed (CSV)
- **SR-SEC-032**: Archive DB connection encrypted; credentials in vault

---

## Data Protection

### Encryption at Rest

- **SR-DP-001**: Active DB: Transparent encryption (PostgreSQL TDE or volume encryption)
- **SR-DP-002**: Archive DB: Separate encryption key
- **SR-DP-003**: Export files: AES-256 at rest in object storage
- **SR-DP-004**: `user_audit_settings.shared_secret_encrypted`: Application-level encryption (Fernet/AES-GCM)

### Encryption in Transit

- **SR-DP-010**: All DB connections: TLS with certificate validation
- **SR-DP-011**: API: HTTPS only, HSTS, secure cookies
- **SR-DP-012**: Archive transfer: TLS + checksum verification

### PII Handling

- **SR-DP-020**: `actor_user_id` stored (not PII directly); join to users table for name/email
- **SR-DP-021**: `ip_address`, `user_agent` stored — considered PII, access restricted
- **SR-DP-022**: Export includes PII only if requestor has `AUDIT_VIEW_PII` permission

---

## Electronic Signature Security (Shared Secret)

### TOTP Configuration

- **SR-ES-001**: TOTP secret generated per user at first signature setup (RFC 6238, SHA-256, 30s window, 6 digits)
- **SR-ES-002**: Secret stored encrypted (`shared_secret_encrypted`) — never logged, never in plaintext
- **SR-ES-003**: Verification: `pyotp.TOTP(secret).verify(token, valid_window=1)`
- **SR-ES-004**: Rate limit: 5 failed attempts → 15 min lockout on `user_audit_settings`

### Static Secret Configuration

- **SR-ES-010**: Static secret: 32-char random string, stored as Argon2id hash
- **SR-ES-011**: Verification: Constant-time comparison
- **SR-ES-012**: Rotation: User may rotate secret via profile (requires current secret)

### Signature Non-Repudiation

- **SR-ES-020**: Signature event includes: user ID, timestamp, meaning, verification status
- **SR-ES-021**: `signed_data_hash` = SHA256 of the business data being signed
- **SR-ES-022**: Signature cannot be removed or modified (immutable audit event)
- **SR-ES-023**: Signature meaning displayed on certificate/approval printouts

---

## Audit Trail Self-Auditing

| Meta-Event | Trigger | Logged To |
|---|---|---|
| Export requested | User requests export | `audit_exports` + security audit |
| Export approved | Manager approves | `audit_exports` + security audit |
| Export downloaded | File served | Security audit |
| Integrity check run | Scheduled/on-demand | `audit_archives` (verification_hash) |
| Tamper detected | Hash mismatch | Security audit + alert |
| Archive initiated | Job starts | `audit_archives` |
| Archive verified | Second user verifies | `audit_archives` |
| Partition detached | After archive | Security audit |
| Retention disposal | Dual auth | Security audit + active DB audit event |

---

## Session & Correlation

- **SR-SC-001**: Every API request generates `correlation_id` (UUID) passed through all services
- **SR-SC-002**: `correlation_id` included in all audit events from that request
- **SR-SC-003**: `session_id` from auth token included in audit events
- **SR-SC-004**: Enables end-to-end traceability from user action to audit record

---

## Network & Infrastructure

- **SR-NI-001**: Active DB: Private subnet, no public access
- **SR-NI-002**: Archive DB: Separate VPC/account, accessible only from archive job runner
- **SR-NI-003**: Audit write path: No external dependencies (no HTTP calls in audit writer)
- **SR-NI-004**: Backup: Audit DBs backed up separately with cross-region replication