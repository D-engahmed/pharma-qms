# API Specification

## Base URL
```
/api/v1/audit/
```

## Authentication
- All endpoints require valid JWT access token
- Permissions checked per endpoint (see Security Rules)

## Endpoints

### 1. Query Audit Events

**GET** `/events`

#### Query Parameters
| Parameter | Type | Required | Description |
|---|---|---|---|
| date_from | ISO8601 | Yes | Start timestamp (inclusive) |
| date_to | ISO8601 | Yes | End timestamp (inclusive) |
| actor_user_id | UUID | No | Filter by actor |
| actor_type | Enum | No | USER, SYSTEM, SCHEDULED |
| action | Enum | No | CREATE, UPDATE, DELETE, TRANSITION, SIGN, VIEW_SENSITIVE, FIELD_CHANGE |
| module | Enum | No | RECEIVING, SAMPLING, ANALYSIS, CERTIFICATE, RELEASE, USER_MGMT, SECURITY, WAREHOUSE, MONOGRAPH, SYSTEM |
| entity_type | String | No | Exact match |
| entity_id | UUID | No | Exact match |
| field_name | String | No | For FIELD_CHANGE |
| correlation_id | UUID | No | Group related events |
| session_id | UUID | No | Filter by session |
| limit | Integer | No | 1-10000 (default: 100) |
| offset | Integer | No | ≥0 (default: 0) |
| order_by | String | No | timestamp, sequence_number (default: -timestamp) |
| include_hash | Boolean | No | Include previous_hash, event_hash (default: false) |

#### Response 200
```json
{
  "count": 15420,
  "next": "/api/v1/audit/events?date_from=...&offset=100",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "sequence_number": 1234567,
      "timestamp": "2024-01-15T10:30:00.123456Z",
      "actor": {
        "user_id": "uuid",
        "name": "John Doe",
        "email": "john@example.com"
      },
      "actor_type": "USER",
      "action": "FIELD_CHANGE",
      "module": "RECEIVING",
      "entity_type": "MaterialBatch",
      "entity_id": "uuid",
      "field_name": "manufacturer_id",
      "old_values": {"manufacturer_id": "uuid-old"},
      "new_values": {"manufacturer_id": "uuid-new"},
      "correlation_id": "uuid",
      "session_id": "uuid",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "previous_hash": "a1b2c3...",
      "event_hash": "d4e5f6...",
      "digital_signature": null
    }
  ]
}
```

#### Errors
- 400: Invalid parameters
- 403: Insufficient permissions (AUDIT_VIEW required)
- 504: Query timeout

---

### 2. Get Single Event

**GET** `/events/{event_id}`

#### Response 200
```json
{
  "id": "uuid",
  "sequence_number": 1234567,
  "timestamp": "2024-01-15T10:30:00.123456Z",
  "actor_user_id": "uuid",
  "actor_type": "USER",
  "action": "SIGN",
  "module": "CERTIFICATE",
  "entity_type": "Certificate",
  "entity_id": "uuid",
  "field_name": null,
  "old_values": {"status": "PENDING_APPROVAL"},
  "new_values": {"status": "APPROVED"},
  "correlation_id": "uuid",
  "session_id": "uuid",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "previous_hash": "a1b2c3...",
  "event_hash": "d4e5f6...",
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

---

### 3. Verify Hash Chain Integrity

**GET** `/integrity/verify`

#### Query Parameters
| Parameter | Type | Required | Description |
|---|---|---|---|
| from_sequence | Integer | No | Start sequence (inclusive) |
| to_sequence | Integer | No | End sequence (inclusive) |
| date_from | ISO8601 | No | Alternative to sequence |
| date_to | ISO8601 | No | Alternative to sequence |

#### Response 200
```json
{
  "status": "OK",
  "verified_count": 10000,
  "from_sequence": 1230001,
  "to_sequence": 1240000,
  "first_event_timestamp": "2024-01-15T00:00:00Z",
  "last_event_timestamp": "2024-01-15T23:59:59Z",
  "mismatches": []
}
```

#### Response 200 (With Mismatches)
```json
{
  "status": "MISMATCH",
  "verified_count": 9998,
  "mismatches": [
    {
      "sequence_number": 1234567,
      "expected_previous_hash": "a1b2c3...",
      "actual_previous_hash": "deadbeef...",
      "expected_event_hash": "d4e5f6...",
      "actual_event_hash": "d4e5f6...",
      "error_type": "CHAIN_BROKEN"
    }
  ]
}
```

#### Errors
- 403: Insufficient permissions (AUDIT_VERIFY required)

---

### 4. Request Export

**POST** `/exports`

#### Request Body
```json
{
  "date_from": "2024-01-01T00:00:00Z",
  "date_to": "2024-01-31T23:59:59Z",
  "format": "PDF",
  "filters": {
    "module": ["RECEIVING", "SAMPLING"],
    "action": ["CREATE", "TRANSITION", "SIGN"],
    "entity_type": ["MaterialBatch", "Sample"]
  }
}
```

#### Response 202
```json
{
  "id": "uuid",
  "status": "PENDING_APPROVAL",
  "estimated_records": 15420,
  "requires_approval": true,
  "requested_at": "2024-01-15T10:30:00Z"
}
```

#### Response 201 (No Approval Needed)
```json
{
  "id": "uuid",
  "status": "GENERATING",
  "estimated_records": 500,
  "requires_approval": false,
  "requested_at": "2024-01-15T10:30:00Z"
}
```

---

### 5. Approve Export

**POST** `/exports/{export_id}/approve`

#### Response 200
```json
{
  "id": "uuid",
  "status": "GENERATING",
  "approved_by": "uuid",
  "approved_at": "2024-01-15T10:35:00Z"
}
```

---

### 6. Get Export Status

**GET** `/exports/{export_id}`

#### Response 200
```json
{
  "id": "uuid",
  "status": "COMPLETED",
  "format": "PDF",
  "date_from": "2024-01-01T00:00:00Z",
  "date_to": "2024-01-31T23:59:59Z",
  "filters": {...},
  "file_path": "s3://bucket/exports/audit-export-uuid.pdf",
  "file_hash": "a1b2c3...",
  "record_count": 15420,
  "requested_by": "uuid",
  "approved_by": "uuid",
  "requested_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:45:00Z"
}
```

---

### 7. Download Export

**GET** `/exports/{export_id}/download`

#### Response
- 200: File stream (application/pdf or text/csv)
- Headers: Content-Disposition, Content-Length, X-File-Hash

---

### 8. List Exports

**GET** `/exports`

#### Query Parameters
| Parameter | Type | Required | Description |
|---|---|---|---|
| status | Enum | No | PENDING, APPROVED, GENERATING, COMPLETED, FAILED |
| requested_by | UUID | No | Filter by requestor |
| date_from | ISO8601 | No | Request date |
| date_to | ISO8601 | No | Request date |
| limit | Integer | No | 1-100 (default: 20) |
| offset | Integer | No | ≥0 |

---

### 9. Archive Management

**POST** `/archives`

#### Request Body
```json
{
  "date_from": "2023-01-01T00:00:00Z",
  "date_to": "2023-12-31T23:59:59Z"
}
```

#### Response 202
```json
{
  "id": "uuid",
  "status": "IN_PROGRESS",
  "initiated_at": "2024-01-15T02:00:00Z"
}
```

**GET** `/archives/{archive_id}`

**GET** `/archives`

---

### 10. Signature Configuration

**GET** `/signature/settings`

#### Response 200
```json
{
  "configured": true,
  "secret_type": "TOTP",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**POST** `/signature/settings`

#### Request Body
```json
{
  "secret_type": "TOTP",
  "totp_token": "123456"  // For verification during setup
}
```

**DELETE** `/signature/settings` — Disable signature (requires current secret)

---

### 11. Verify Signature

**POST** `/signature/verify`

#### Request Body
```json
{
  "token": "123456",  // TOTP code or static secret
  "data_hash": "a1b2c3..."  // Hash of data being signed
}
```

#### Response 200
```json
{
  "verified": true,
  "signature": {
    "user_id": "uuid",
    "timestamp": "2024-01-15T10:30:00.123456Z",
    "signature_type": "SHARED_SECRET_TOTP",
    "signed_data_hash": "a1b2c3..."
  }
}
```

#### Response 400
```json
{
  "verified": false,
  "error": "INVALID_TOKEN"
}
```

---

## WebSocket (Real-time Audit Stream)

**WS** `/ws/audit/stream?token={jwt}`

### Messages

**Server → Client** (New Event)
```json
{
  "type": "AUDIT_EVENT",
  "event": { ... }  // Same as GET /events/{id}
}
```

**Server → Client** (Integrity Alert)
```json
{
  "type": "INTEGRITY_ALERT",
  "severity": "CRITICAL",
  "message": "Hash chain mismatch at sequence 1234567",
  "details": { ... }
}
```

---

## Rate Limits

| Endpoint | Limit |
|---|---|
| GET /events | 60 req/min |
| GET /events/{id} | 120 req/min |
| GET /integrity/verify | 10 req/min |
| POST /exports | 5 req/min |
| POST /exports/{id}/approve | 10 req/min |
| GET /exports/{id}/download | 10 req/min |
| POST /signature/verify | 30 req/min |

---

## OpenAPI Specification
Full OpenAPI 3.0 spec available at: `/api/v1/audit/openapi.json`