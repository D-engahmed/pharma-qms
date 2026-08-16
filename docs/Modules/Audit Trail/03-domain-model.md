# Domain Model

## AuditEvent

The central entity representing a single auditable action.

### Attributes

| Field | Type | Required | Notes |
|---|---|---|---|
| id | UUID | Yes | Primary key |
| sequence_number | BIGINT | Yes | Monotonic global sequence |
| timestamp | TIMESTAMPTZ(6) | Yes | UTC, microsecond precision |
| actor_user_id | UUID | No | NULL for SYSTEM actor |
| actor_type | VARCHAR(20) | Yes | USER \| SYSTEM \| SCHEDULED |
| action | VARCHAR(30) | Yes | CREATE, UPDATE, DELETE, TRANSITION, SIGN, VIEW_SENSITIVE, FIELD_CHANGE |
| module | VARCHAR(30) | Yes | RECEIVING, SAMPLING, ANALYSIS, CERTIFICATE, RELEASE, USER_MGMT, SECURITY, WAREHOUSE, MONOGRAPH, SYSTEM |
| entity_type | VARCHAR(50) | Yes | e.g., MaterialBatch, Sample, AnalysisResult, Certificate, User, Role |
| entity_id | UUID | Yes | References the affected entity |
| field_name | VARCHAR(100) | No | Required for FIELD_CHANGE action |
| old_values | JSONB | No | Previous state (full object or changed fields) |
| new_values | JSONB | No | New state (full object or changed fields) |
| correlation_id | UUID | No | Groups related events (e.g., single API request) |
| session_id | UUID | No | Links to user session |
| ip_address | INET | No | Client IP |
| user_agent | TEXT | No | Client user agent |
| previous_hash | CHAR(64) | Yes | SHA-256 hex of previous event |
| event_hash | CHAR(64) | Yes | SHA-256 hex of this event (computed) |
| digital_signature | JSONB | No | Present for SIGN actions |

### Digital Signature Structure (when action = SIGN)

```json
{
  "user_id": "uuid",
  "timestamp": "2024-01-15T10:30:00.123456Z",
  "meaning": "Approved analysis results for batch MB-2024-001",
  "signature_type": "SHARED_SECRET_TOTP",
  "verification_status": "VERIFIED",
  "signed_data_hash": "sha256_hex_of_signed_content"
}
```

### Actions Enum

| Action | Description | Typical Modules |
|---|---|---|
| CREATE | Entity created | All |
| UPDATE | Entity updated (full object in old/new) | All |
| DELETE | Entity soft-deleted | All |
| TRANSITION | Workflow state change | RECEIVING, SAMPLING, ANALYSIS, CERTIFICATE, RELEASE |
| SIGN | Electronic signature applied | CERTIFICATE, ANALYSIS, RELEASE |
| VIEW_SENSITIVE | Sensitive data accessed | CERTIFICATE, ANALYSIS, USER_MGMT |
| FIELD_CHANGE | Single field modified | All (granular) |

### Modules Enum

| Module | Description |
|---|---|
| RECEIVING | Material receipt, batch, quarantine |
| SAMPLING | Sampling queue, sample creation, tracking |
| ANALYSIS | Test execution, results, review, approval |
| CERTIFICATE | Certificate generation, review, approval |
| RELEASE | Material release, movement |
| USER_MGMT | User, role, permission, department, auth |
| SECURITY | Login, logout, password, session, MFA |
| WAREHOUSE | Warehouse, location, inventory |
| MONOGRAPH | Monograph, test method, specification |
| SYSTEM | Scheduled jobs, archive, config changes |

---

## AuditEventSequence

Tracks global sequence for ordering guarantees.

### Attributes

| Field | Type | Required | Notes |
|---|---|---|---|
| id | BIGSERIAL | Yes | Primary key |
| event_id | UUID | Yes | FK to AuditEvent |
| sequence_number | BIGINT | Yes | Monotonic, unique |
| partition_key | DATE | Yes | Month partition (YYYY-MM-01) |
| created_at | TIMESTAMPTZ | Yes | |

---

## AuditExport

Represents an export request and result.

### Attributes

| Field | Type | Required | Notes |
|---|---|---|---|
| id | UUID | Yes | Primary key |
| requested_by_id | UUID | Yes | User who requested export |
| approved_by_id | UUID | No | User who approved (if required) |
| status | VARCHAR(20) | Yes | PENDING, APPROVED, GENERATING, COMPLETED, FAILED |
| format | VARCHAR(10) | Yes | PDF, CSV |
| date_from | TIMESTAMPTZ | Yes | |
| date_to | TIMESTAMPTZ | Yes | |
| filters | JSONB | No | Applied filters |
| file_path | TEXT | No | Storage path (S3/local) |
| file_hash | CHAR(64) | No | SHA-256 of export file |
| record_count | BIGINT | No | Events in export |
| error_message | TEXT | No | If failed |
| requested_at | TIMESTAMPTZ | Yes | |
| completed_at | TIMESTAMPTZ | No | |

---

## AuditArchive

Tracks archival operations to separate DB.

### Attributes

| Field | Type | Required | Notes |
|---|---|---|---|
| id | UUID | Yes | Primary key |
| date_from | TIMESTAMPTZ | Yes | |
| date_to | TIMESTAMPTZ | Yes | |
| event_count | BIGINT | Yes | |
| archive_hash | CHAR(64) | Yes | Hash of all archived events |
| archive_db_connection | TEXT | Yes | Connection string (encrypted) |
| status | VARCHAR(20) | Yes | IN_PROGRESS, VERIFIED, FAILED |
| initiated_by_id | UUID | Yes | |
| verified_by_id | UUID | No | |
| initiated_at | TIMESTAMPTZ | Yes | |
| verified_at | TIMESTAMPTZ | No | |

---

## UserAuditSettings (Per-user signature config)

### Attributes

| Field | Type | Required | Notes |
|---|---|---|---|
| user_id | UUID | Yes | PK, FK to users |
| shared_secret_encrypted | TEXT | Yes | Encrypted TOTP secret or static secret |
| secret_type | VARCHAR(20) | Yes | TOTP \| STATIC |
| is_active | BOOLEAN | Yes | |
| created_at | TIMESTAMPTZ | Yes | |
| updated_at | TIMESTAMPTZ | Yes | |

---

## Relationships

```text
User 1 ────────< AuditEvent (actor_user_id)
AuditEvent 1 ──< AuditEventSequence
User 1 ────────< AuditExport (requested_by_id)
User 1 ────────< AuditExport (approved_by_id)
User 1 ────────< AuditArchive (initiated_by_id)
User 1 ────────< AuditArchive (verified_by_id)
User 1 ────────< UserAuditSettings
```

---

## Event Payload Examples

### FIELD_CHANGE (MaterialBatch.manufacturer_id changed)

```json
{
  "action": "FIELD_CHANGE",
  "module": "RECEIVING",
  "entity_type": "MaterialBatch",
  "entity_id": "uuid",
  "field_name": "manufacturer_id",
  "old_values": {"manufacturer_id": "uuid-old"},
  "new_values": {"manufacturer_id": "uuid-new"}
}
```

### TRANSITION (Sample: COLLECTED → IN_TESTING)

```json
{
  "action": "TRANSITION",
  "module": "SAMPLING",
  "entity_type": "Sample",
  "entity_id": "uuid",
  "old_values": {"status": "COLLECTED"},
  "new_values": {"status": "IN_TESTING"}
}
```

### SIGN (Certificate approval)

```json
{
  "action": "SIGN",
  "module": "CERTIFICATE",
  "entity_type": "Certificate",
  "entity_id": "uuid",
  "digital_signature": {
    "user_id": "uuid",
    "timestamp": "2024-01-15T10:30:00.123456Z",
    "meaning": "Approved Certificate of Analysis for batch MB-2024-001",
    "signature_type": "SHARED_SECRET_TOTP",
    "verification_status": "VERIFIED",
    "signed_data_hash": "a1b2c3..."
  }
}
```