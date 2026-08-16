# Database Design

## Active Audit Database (Primary PostgreSQL)

### Tables

#### audit_events (partitioned by month)

```sql
CREATE TABLE audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sequence_number BIGINT NOT NULL,
    timestamp TIMESTAMPTZ(6) NOT NULL,
    actor_user_id UUID,
    actor_type VARCHAR(20) NOT NULL CHECK (actor_type IN ('USER', 'SYSTEM', 'SCHEDULED')),
    action VARCHAR(30) NOT NULL CHECK (action IN (
        'CREATE', 'UPDATE', 'DELETE', 'TRANSITION', 'SIGN', 
        'VIEW_SENSITIVE', 'FIELD_CHANGE'
    )),
    module VARCHAR(30) NOT NULL CHECK (module IN (
        'RECEIVING', 'SAMPLING', 'ANALYSIS', 'CERTIFICATE', 'RELEASE',
        'USER_MGMT', 'SECURITY', 'WAREHOUSE', 'MONOGRAPH', 'SYSTEM'
    )),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    field_name VARCHAR(100),
    old_values JSONB,
    new_values JSONB,
    correlation_id UUID,
    session_id UUID,
    ip_address INET,
    user_agent TEXT,
    previous_hash CHAR(64) NOT NULL,
    event_hash CHAR(64) NOT NULL,
    digital_signature JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (timestamp);
```

#### Monthly Partitions (auto-created via pg_partman or migration)

```sql
-- Example: January 2024
CREATE TABLE audit_events_2024_01 PARTITION OF audit_events
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

#### audit_event_sequences

```sql
CREATE TABLE audit_event_sequences (
    id BIGSERIAL PRIMARY KEY,
    event_id UUID NOT NULL UNIQUE REFERENCES audit_events(id),
    sequence_number BIGINT NOT NULL UNIQUE,
    partition_key DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_aes_partition ON audit_event_sequences(partition_key);
```

#### audit_exports

```sql
CREATE TABLE audit_exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requested_by_id UUID NOT NULL REFERENCES users(id),
    approved_by_id UUID REFERENCES users(id),
    status VARCHAR(20) NOT NULL CHECK (status IN (
        'PENDING', 'APPROVED', 'GENERATING', 'COMPLETED', 'FAILED'
    )),
    format VARCHAR(10) NOT NULL CHECK (format IN ('PDF', 'CSV')),
    date_from TIMESTAMPTZ NOT NULL,
    date_to TIMESTAMPTZ NOT NULL,
    filters JSONB,
    file_path TEXT,
    file_hash CHAR(64),
    record_count BIGINT,
    error_message TEXT,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);
```

#### audit_archives

```sql
CREATE TABLE audit_archives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date_from TIMESTAMPTZ NOT NULL,
    date_to TIMESTAMPTZ NOT NULL,
    event_count BIGINT NOT NULL,
    archive_hash CHAR(64) NOT NULL,
    archive_db_connection TEXT NOT NULL, -- encrypted
    status VARCHAR(20) NOT NULL CHECK (status IN ('IN_PROGRESS', 'VERIFIED', 'FAILED')),
    initiated_by_id UUID NOT NULL REFERENCES users(id),
    verified_by_id UUID REFERENCES users(id),
    initiated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    verified_at TIMESTAMPTZ
);
```

#### user_audit_settings

```sql
CREATE TABLE user_audit_settings (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    shared_secret_encrypted TEXT NOT NULL,
    secret_type VARCHAR(20) NOT NULL CHECK (secret_type IN ('TOTP', 'STATIC')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## Archive Audit Database (Separate PostgreSQL Instance)

### Tables (Read-Only for Application)

#### audit_events_archive (partitioned by year)

```sql
CREATE TABLE audit_events_archive (
    id UUID PRIMARY KEY,
    sequence_number BIGINT NOT NULL,
    timestamp TIMESTAMPTZ(6) NOT NULL,
    actor_user_id UUID,
    actor_type VARCHAR(20) NOT NULL,
    action VARCHAR(30) NOT NULL,
    module VARCHAR(30) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    field_name VARCHAR(100),
    old_values JSONB,
    new_values JSONB,
    correlation_id UUID,
    session_id UUID,
    ip_address INET,
    user_agent TEXT,
    previous_hash CHAR(64) NOT NULL,
    event_hash CHAR(64) NOT NULL,
    digital_signature JSONB,
    archived_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (timestamp);
```

#### audit_archive_metadata

```sql
CREATE TABLE audit_archive_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_date_from TIMESTAMPTZ NOT NULL,
    source_date_to TIMESTAMPTZ NOT NULL,
    event_count BIGINT NOT NULL,
    archive_hash CHAR(64) NOT NULL,
    verification_hash CHAR(64) NOT NULL, -- hash verified at archive time
    archived_by UUID NOT NULL,
    archived_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## Key Constraints

### audit_events

- `sequence_number` UNIQUE (enforced via audit_event_sequences)
- `event_hash` = SHA256(concat fields || previous_hash) — validated by trigger
- `previous_hash` of first event in partition = '0' * 64
- `actor_user_id` NOT NULL when `actor_type` = 'USER'
- `field_name` NOT NULL when `action` = 'FIELD_CHANGE'
- `digital_signature` NOT NULL when `action` = 'SIGN'

### Partitions

- One partition per month for active DB
- One partition per year for archive DB
- Partitions created automatically via pg_partman or scheduled job

---

## Recommended Indexes

### Active DB

```sql
-- Query patterns
CREATE INDEX idx_ae_timestamp ON audit_events(timestamp);
CREATE INDEX idx_ae_actor ON audit_events(actor_user_id) WHERE actor_user_id IS NOT NULL;
CREATE INDEX idx_ae_action ON audit_events(action);
CREATE INDEX idx_ae_module ON audit_events(module);
CREATE INDEX idx_ae_entity ON audit_events(entity_type, entity_id);
CREATE INDEX idx_ae_correlation ON audit_events(correlation_id) WHERE correlation_id IS NOT NULL;
CREATE INDEX idx_ae_session ON audit_events(session_id) WHERE session_id IS NOT NULL;

-- Composite for common filters
CREATE INDEX idx_ae_module_ts ON audit_events(module, timestamp);
CREATE INDEX idx_ae_entity_ts ON audit_events(entity_type, entity_id, timestamp);
CREATE INDEX idx_ae_actor_ts ON audit_events(actor_user_id, timestamp) WHERE actor_user_id IS NOT NULL;

-- Hash chain verification
CREATE INDEX idx_ae_seq ON audit_events(sequence_number);
```

### Archive DB

```sql
CREATE INDEX idx_aea_timestamp ON audit_events_archive(timestamp);
CREATE INDEX idx_aea_entity ON audit_events_archive(entity_type, entity_id);
CREATE INDEX idx_aea_actor ON audit_events_archive(actor_user_id) WHERE actor_user_id IS NOT NULL;
CREATE INDEX idx_aea_module_ts ON audit_events_archive(module, timestamp);
```

---

## Database Users & Permissions

### Application User (audit_app)

```sql
-- Active DB
GRANT INSERT, SELECT ON audit_events TO audit_app;
GRANT INSERT, SELECT ON audit_event_sequences TO audit_app;
GRANT INSERT, SELECT, UPDATE ON audit_exports TO audit_app;
GRANT INSERT, SELECT, UPDATE ON audit_archives TO audit_app;
GRANT SELECT, INSERT, UPDATE ON user_audit_settings TO audit_app;

-- NO UPDATE, DELETE on audit_events, audit_event_sequences
-- NO TRUNCATE
```

### Archive Process User (audit_archive)

```sql
-- Active DB
GRANT SELECT ON audit_events TO audit_archive;
GRANT SELECT ON audit_event_sequences TO audit_archive;
GRANT INSERT, UPDATE ON audit_archives TO audit_archive;

-- Archive DB
GRANT INSERT ON audit_events_archive TO audit_archive;
GRANT INSERT ON audit_archive_metadata TO audit_archive;
```

### Read-Only Auditor (audit_reader)

```sql
-- Active DB
GRANT SELECT ON audit_events, audit_event_sequences, audit_exports, audit_archives TO audit_reader;

-- Archive DB
GRANT SELECT ON audit_events_archive, audit_archive_metadata TO audit_reader;
```

---

## Hash Chain Trigger (Active DB)

```sql
CREATE OR REPLACE FUNCTION compute_event_hash()
RETURNS TRIGGER AS $$
DECLARE
    prev_hash CHAR(64);
    hash_input TEXT;
BEGIN
    -- Get previous event hash in same partition
    SELECT event_hash INTO prev_hash
    FROM audit_events
    WHERE sequence_number = NEW.sequence_number - 1
    LIMIT 1;

    IF prev_hash IS NULL THEN
        prev_hash := repeat('0', 64);
    END IF;

    NEW.previous_hash := prev_hash;

    -- Compute hash: SHA256(concat of all immutable fields || previous_hash)
    hash_input := NEW.id::text || NEW.sequence_number::text || 
                  NEW.timestamp::text || COALESCE(NEW.actor_user_id::text, '') ||
                  NEW.actor_type || NEW.action || NEW.module || NEW.entity_type ||
                  NEW.entity_id::text || COALESCE(NEW.field_name, '') ||
                  COALESCE(NEW.old_values::text, '') || COALESCE(NEW.new_values::text, '') ||
                  COALESCE(NEW.correlation_id::text, '') || COALESCE(NEW.session_id::text, '') ||
                  COALESCE(NEW.ip_address::text, '') || COALESCE(NEW.user_agent, '') ||
                  COALESCE(NEW.digital_signature::text, '') || prev_hash;

    NEW.event_hash := encode(digest(hash_input, 'sha256'), 'hex');
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER trg_audit_event_hash
BEFORE INSERT ON audit_events
FOR EACH ROW EXECUTE FUNCTION compute_event_hash();
```

---

## Deletion Policy

- **Active DB**: NO hard deletes. Partitions may be DETACHED and moved to archive DB after retention period.
- **Archive DB**: NO deletes. Disposal requires dual-authorization, generates disposal event in active DB, then partition DROP in archive DB.
- **Audit exports/archives metadata**: Never deleted.