# 10 — Database Design Specification

**Document Identifier:** RM-RRS-DB-001  
**Version:** 1.0  
**Status:** Baseline  
**Traces to:** Project Charter, SRS, NFR, SAS, Design Specification  
**Compliance Reference:** ISO/IEC 11179 (Metadata Registries), PostgreSQL Best Practices  

---

## Table of Contents

1. [Introduction](#1-introduction)  
   1.1 [Purpose](#11-purpose)  
   1.2 [Scope](#12-scope)  
   1.3 [References](#13-references)  

2. [Database Overview](#2-database-overview)  
   2.1 [Database Management System](#21-database-management-system)  
   2.2 [Naming Conventions](#22-naming-conventions)  
   2.3 [Schema Design Principles](#23-schema-design-principles)  

3. [Entity-Relationship Diagram](#3-entity-relationship-diagram)  

4. [Table Specifications](#4-table-specifications)  
   4.1 [Employee](#41-employee)  
   4.2 [Material](#42-material)  
   4.3 [Packaging](#43-packaging)  
   4.4 [Sample](#44-sample)  
   4.5 [ProductSample](#45-productsample)  
   4.6 [COA](#46-coa)  
   4.7 [Notification](#47-notification)  
   4.8 [AuditLog](#48-auditlog)  
   4.9 [ElectronicSignature](#49-electronicsignature)  

5. [Indexing Strategy](#5-indexing-strategy)  
   5.1 [Index Definitions by Table](#51-index-definitions-by-table)  
   5.2 [Partial and Covering Indexes](#52-partial-and-covering-indexes)  

6. [Constraints and Data Integrity](#6-constraints-and-data-integrity)  
   6.1 [Primary and Foreign Keys](#61-primary-and-foreign-keys)  
   6.2 [Unique Constraints](#62-unique-constraints)  
   6.3 [Check Constraints](#63-check-constraints)  
   6.4 [Default Values](#64-default-values)  

7. [Audit and History](#7-audit-and-history)  
   7.1 [Audit Trail Table](#71-audit-trail-table)  
   7.2 [Audit Trigger Mechanism](#72-audit-trigger-mechanism)  

8. [Migration and Versioning](#8-migration-and-versioning)  
   8.1 [Migration Tool](#81-migration-tool)  
   8.2 [Migration Policy](#82-migration-policy)  
   8.3 [Rollback Plan](#83-rollback-plan)  

9. [Performance and Optimisation](#9-performance-and-optimisation)  
   9.1 [Connection Pooling](#91-connection-pooling)  
   9.2 [Partitioning Strategy](#92-partitioning-strategy)  
   9.3 [Vacuum and Maintenance](#93-vacuum-and-maintenance)  

10. [Appendices](#10-appendices)  
    A. [Data Dictionary](#a-data-dictionary)  
    B. [Migration Scripts Template](#b-migration-scripts-template)  
    C. [Sample Data](#c-sample-data)  

---

## 1. Introduction

### 1.1 Purpose
This document defines the database design for the **Raw Material Receiving & Release System (RM-RRS)** . It provides a comprehensive description of the database schema, including table structures, relationships, constraints, indexes, and migration strategies. The design is derived from the functional and non‑functional requirements documented in the SRS and follows the architectural principles outlined in the SAS. This document serves as the authoritative source for database developers, DBAs, and validation teams.

### 1.2 Scope
This specification covers all persistent data storage required by the RM-RRS MVP, including:
- **Access Control**: Employee accounts, roles, and permissions.
- **Business Records**: Materials, Packaging, Samples (RM + Packaging), Product Samples, COAs.
- **Compliance Records**: Audit logs and electronic signatures.
- **Operational Data**: Notifications.

The database is designed for **PostgreSQL 15+** and is containerised with Docker. All data is stored in a single shared database instance.

### 1.3 References

| Document | Reference |
|----------|-----------|
| 00_Project_Charter.md | Charter |
| 06_SRS.md | Software Requirements Specification |
| 07_NFR.md | Non‑Functional Requirements |
| 08_SAS.md | Software Architecture Specification |
| 09_Design.md | Design Specification |
| PostgreSQL Documentation | https://www.postgresql.org/docs/15/ |
| ISO/IEC 11179 | Metadata Registry Standard |

---

## 2. Database Overview

### 2.1 Database Management System

| Attribute | Value |
|-----------|-------|
| **DBMS** | PostgreSQL 15+ |
| **Character Set** | UTF‑8 |
| **Collation** | `en_US.UTF‑8` |
| **Time Zone** | UTC for all timestamps (with time zone) |
| **Extensions** | `uuid-ossp` (for UUID generation), `btree_gin` (for JSONB indexing) |

**Connection String Format:**
```
postgresql://user:password@host:5432/rm_rrs?sslmode=require
```

### 2.2 Naming Conventions

| Object | Convention | Example |
|--------|------------|---------|
| Database name | `rm_rrs` | `rm_rrs` |
| Schema name | `public` (default) | `public` |
| Table names | `snake_case`, plural | `materials`, `samples` |
| Column names | `snake_case`, singular | `receipt_id`, `material_name` |
| Primary keys | `id` (UUID) | `id UUID PRIMARY KEY` |
| Foreign keys | `referenced_table_id` | `material_id` |
| Indexes | `idx_table_column` | `idx_materials_receipt_id` |
| Unique constraints | `uq_table_column` | `uq_materials_receipt_id` |
| Check constraints | `ck_table_rule` | `ck_material_status` |

### 2.3 Schema Design Principles

1. **Normalisation**: Tables are normalised to 3NF to avoid redundancy.
2. **Audit Readiness**: Every business table includes `created_at`, `updated_at`, `created_by_id`, `updated_by_id`.
3. **Immutable Audit**: The `audit_log` table is append‑only; no updates or deletes.
4. **Soft Deletes**: Business records are never physically deleted; status fields indicate active state.
5. **Human‑Readable IDs**: Each business entity has a formatted identifier (e.g., `RCV-2026-0001`) in addition to the internal UUID.
6. **JSONB for Flexible Data**: Where schema may evolve (e.g., `stages` in `product_sample`), `JSONB` is used.
7. **Referential Integrity**: Foreign key constraints enforce relationships; cascading deletes are restricted.

---

## 3. Entity-Relationship Diagram

```mermaid
erDiagram
    EMPLOYEE ||--o{ MATERIAL : "created_by"
    EMPLOYEE ||--o{ PACKAGING : "created_by"
    EMPLOYEE ||--o{ SAMPLE : "created_by"
    EMPLOYEE ||--o{ PRODUCT_SAMPLE : "created_by"
    EMPLOYEE ||--o{ COA : "created_by"
    EMPLOYEE ||--o{ AUDIT_LOG : "user_id"
    EMPLOYEE ||--o{ ELECTRONIC_SIGNATURE : "user_id"

    MATERIAL ||--o{ SAMPLE : "has"
    PACKAGING ||--o{ SAMPLE : "has"
    MATERIAL ||--o{ COA : "linked_to"
    SAMPLE ||--o{ COA : "generates"
    PRODUCT_SAMPLE ||--o{ COA : "generates"

    EMPLOYEE {
        uuid id PK
        string username UK
        string password_hash
        string full_name
        string email
        string job_role
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    MATERIAL {
        uuid id PK
        string receipt_id UK
        string material_name
        string category
        string supplier
        string manufacturer
        string supplier_batch
        date mfg_date
        date exp_date
        decimal batch_size
        string unit
        string package_type
        int num_packages
        decimal package_size
        decimal total_qty
        string warehouse
        string location
        string po_no
        string inv_no
        date receipt_date
        string received_by
        string status
        string sampling_status
        string qc_number
        string qc_sign
        date retest_date
        date released_date
        string storage_condition
        timestamp created_at
        timestamp updated_at
        uuid created_by_id
        uuid updated_by_id
    }

    PACKAGING {
        uuid id PK
        string receipt_id UK
        string name
        string type
        text description
        decimal qty
        string unit
        string supplier
        string po
        date receipt_date
        string warehouse
        string recipient
        text notes
        string sampling_status
        timestamp created_at
        timestamp updated_at
        uuid created_by_id
        uuid updated_by_id
    }

    SAMPLE {
        uuid id PK
        string sample_id
        uuid material_id FK
        uuid packaging_id FK
        string sample_type
        string material_name
        string receipt_id
        string supplier_batch
        string supplier
        string manufacturer
        date receipt_date
        decimal batch_size
        date mfg_date
        date exp_date
        string unit
        decimal sample_size
        int containers
        string sampler
        string storage
        date sampling_date
        string testing_status
        timestamp created_at
        timestamp updated_at
        uuid created_by_id
        uuid updated_by_id
    }

    PRODUCT_SAMPLE {
        uuid id PK
        string sample_id UK
        string product_name
        string product_type
        string batch_no
        decimal batch_size
        string unit
        date mfg_date
        date exp_date
        decimal sample_size
        time time_of_sampling
        date sampling_date
        jsonb stages
        string testing_status
        timestamp created_at
        timestamp updated_at
        uuid created_by_id
        uuid updated_by_id
    }

    COA {
        string id PK
        uuid sample_id FK
        string sample_src
        uuid material_id FK
        string receipt_id
        string sample_name
        string batch_no
        string batch_size
        string supplier
        string manufacturer
        string mfg_date
        string exp_date
        string received_date
        string specs_code
        string reference
        string analyst
        date analysis_date
        text remarks
        string status
        date created_date
        text qc_comment
        timestamp created_at
        timestamp updated_at
        uuid created_by_id
        uuid updated_by_id
    }

    NOTIFICATION {
        uuid id PK
        string target_role
        string title
        text message
        boolean read
        timestamp created_at
    }

    AUDIT_LOG {
        uuid id PK
        uuid user_id FK
        string username
        timestamp timestamp
        string action
        string entity_type
        string entity_id
        jsonb old_value
        jsonb new_value
        string field_name
        text reason
        inet source_ip
        string session_id
        timestamp created_at
    }

    ELECTRONIC_SIGNATURE {
        uuid id PK
        uuid user_id FK
        string username
        timestamp timestamp
        string meaning
        string record_type
        string record_id
        string record_hash
        string signature_hash
        text reason
        string status
        inet source_ip
        timestamp created_at
    }
```

---

## 4. Table Specifications

### 4.1 Employee

**Purpose:** Stores user accounts and job role assignments.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | No | `gen_random_uuid()` | Primary key |
| `username` | VARCHAR(50) | No | — | Unique login name |
| `password_hash` | VARCHAR(255) | No | — | bcrypt hash |
| `full_name` | VARCHAR(100) | No | — | Employee's full name |
| `email` | VARCHAR(100) | Yes | NULL | Email address |
| `job_role` | VARCHAR(20) | No | — | `storekeeper`, `sampler`, `analyst`, `qcmanager` |
| `is_active` | BOOLEAN | No | `TRUE` | Account enabled? |
| `created_at` | TIMESTAMPTZ | No | `NOW()` | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | No | `NOW()` | Last update timestamp |

**Unique Constraints:**
- `uq_employee_username` on `username`

**Indexes:**
- `idx_employee_job_role` on `job_role`
- `idx_employee_is_active` on `is_active`
- `idx_employee_username` on `username` (unique B‑tree)

**Check Constraints:**
- `job_role IN ('storekeeper', 'sampler', 'analyst', 'qcmanager')`

---

### 4.2 Material

**Purpose:** Stores raw material registrations.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | No | `gen_random_uuid()` | Primary key |
| `receipt_id` | VARCHAR(20) | No | — | `RCV-YYYY-####` |
| `material_name` | VARCHAR(100) | No | — | Name of material |
| `category` | VARCHAR(50) | Yes | NULL | e.g., API, Excipient |
| `supplier` | VARCHAR(100) | No | — | Supplier name |
| `manufacturer` | VARCHAR(100) | Yes | NULL | Manufacturer name |
| `country_origin` | VARCHAR(50) | Yes | NULL | Country of origin |
| `supplier_batch` | VARCHAR(50) | No | — | Supplier's batch/lot number |
| `mfg_date` | DATE | Yes | NULL | Manufacturing date |
| `exp_date` | DATE | No | — | Expiry date |
| `batch_size` | DECIMAL(10,2) | Yes | NULL | Batch size (numeric) |
| `unit` | VARCHAR(20) | Yes | NULL | Unit of measure |
| `package_type` | VARCHAR(50) | Yes | NULL | e.g., Drum, Bag |
| `num_packages` | INTEGER | Yes | NULL | Number of packages |
| `package_size` | DECIMAL(10,2) | Yes | NULL | Size per package |
| `total_qty` | DECIMAL(10,2) | Yes | NULL | Auto‑calculated (num_packages × package_size) |
| `warehouse` | VARCHAR(50) | Yes | NULL | Warehouse name/code |
| `location` | VARCHAR(50) | Yes | NULL | Shelf/bin location |
| `po_no` | VARCHAR(50) | Yes | NULL | Purchase Order number |
| `inv_no` | VARCHAR(50) | Yes | NULL | Invoice number |
| `receipt_date` | DATE | No | — | Date received |
| `received_by` | VARCHAR(100) | No | — | Person who received |
| `status` | VARCHAR(20) | No | `'Quarantine'` | Quarantine, Released, Rejected |
| `sampling_status` | VARCHAR(20) | No | `'Not Sampled'` | Not Sampled, Sampling Requested, Sampled |
| `qc_number` | VARCHAR(20) | Yes | NULL | QC release number (`QC-YYYY-####`) |
| `qc_sign` | VARCHAR(100) | Yes | NULL | QC Manager signature |
| `retest_date` | DATE | Yes | NULL | Retest date = release date + 1 year |
| `released_date` | DATE | Yes | NULL | Date of release |
| `storage_condition` | VARCHAR(50) | Yes | NULL | From sampling record |
| `created_at` | TIMESTAMPTZ | No | `NOW()` | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | No | `NOW()` | Last update timestamp |
| `created_by_id` | UUID (FK) | No | — | Employee who created |
| `updated_by_id` | UUID (FK) | No | — | Employee who last updated |

**Unique Constraints:**
- `uq_material_receipt_id` on `receipt_id`

**Foreign Keys:**
- `material.created_by_id` → `employee.id`
- `material.updated_by_id` → `employee.id`

**Check Constraints:**
- `status IN ('Quarantine', 'Released', 'Rejected')`
- `sampling_status IN ('Not Sampled', 'Sampling Requested', 'Sampled')`

**Indexes:**
- `idx_material_receipt_id` on `receipt_id`
- `idx_material_status` on `status`
- `idx_material_sampling_status` on `sampling_status`
- `idx_material_supplier_batch` on `supplier_batch`
- `idx_material_exp_date` on `exp_date`
- `idx_material_created_at` on `created_at`
- `idx_material_material_name` on `material_name`
- `idx_material_supplier` on `supplier`

---

### 4.3 Packaging

**Purpose:** Stores packaging material registrations.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | No | `gen_random_uuid()` | Primary key |
| `receipt_id` | VARCHAR(20) | No | — | `PKG-YYYY-####` |
| `name` | VARCHAR(100) | No | — | Packaging name |
| `type` | VARCHAR(20) | No | — | Primary, Secondary, Tertiary, Labelling, Other |
| `description` | TEXT | Yes | NULL | Detailed description |
| `qty` | DECIMAL(10,2) | No | — | Quantity received |
| `unit` | VARCHAR(20) | Yes | NULL | Unit of measure |
| `supplier` | VARCHAR(100) | No | — | Supplier name |
| `po` | VARCHAR(50) | Yes | NULL | Purchase Order number |
| `receipt_date` | DATE | No | — | Date received |
| `warehouse` | VARCHAR(50) | Yes | NULL | Warehouse location |
| `recipient` | VARCHAR(100) | No | — | Person who received |
| `notes` | TEXT | Yes | NULL | Additional notes |
| `sampling_status` | VARCHAR(20) | No | `'Not Sampled'` | Not Sampled, Sampling Requested, Sampled |
| `created_at` | TIMESTAMPTZ | No | `NOW()` | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | No | `NOW()` | Last update timestamp |
| `created_by_id` | UUID (FK) | No | — | Employee who created |
| `updated_by_id` | UUID (FK) | No | — | Employee who last updated |

**Unique Constraints:**
- `uq_packaging_receipt_id` on `receipt_id`

**Foreign Keys:**
- `packaging.created_by_id` → `employee.id`
- `packaging.updated_by_id` → `employee.id`

**Check Constraints:**
- `type IN ('Primary', 'Secondary', 'Tertiary', 'Labelling', 'Other')`
- `sampling_status IN ('Not Sampled', 'Sampling Requested', 'Sampled')`

**Indexes:**
- `idx_packaging_receipt_id` on `receipt_id`
- `idx_packaging_name` on `name`
- `idx_packaging_type` on `type`
- `idx_packaging_supplier` on `supplier`
- `idx_packaging_created_at` on `created_at`

---

### 4.4 Sample

**Purpose:** Stores raw material and packaging samples.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | No | `gen_random_uuid()` | Primary key |
| `sample_id` | VARCHAR(20) | No | — | For RM: same as receipt_id; for packaging: `PKG-SMP-YYYY-####` |
| `material_id` | UUID (FK) | Yes | NULL | References `material.id` (for RM samples) |
| `packaging_id` | UUID (FK) | Yes | NULL | References `packaging.id` (for packaging samples) |
| `sample_type` | VARCHAR(20) | No | `'RM'` | `RM` or `Packaging` |
| `material_name` | VARCHAR(100) | Yes | NULL | Denormalised for quick display |
| `receipt_id` | VARCHAR(20) | Yes | NULL | Denormalised |
| `supplier_batch` | VARCHAR(50) | Yes | NULL | Denormalised |
| `supplier` | VARCHAR(100) | Yes | NULL | Denormalised |
| `manufacturer` | VARCHAR(100) | Yes | NULL | Denormalised |
| `receipt_date` | DATE | Yes | NULL | Denormalised |
| `batch_size` | DECIMAL(10,2) | Yes | NULL | Denormalised |
| `mfg_date` | DATE | Yes | NULL | Denormalised |
| `exp_date` | DATE | Yes | NULL | Denormalised |
| `unit` | VARCHAR(20) | Yes | NULL | Denormalised |
| `sample_size` | DECIMAL(10,2) | No | — | Amount sampled |
| `containers` | INTEGER | No | — | Number of containers sampled |
| `sampler` | VARCHAR(100) | No | — | Sampler's name |
| `storage` | VARCHAR(50) | No | — | Storage condition |
| `sampling_date` | DATE | No | — | Date sampled |
| `testing_status` | VARCHAR(20) | No | `'Not Tested'` | Not Tested, In Testing, Completed |
| `created_at` | TIMESTAMPTZ | No | `NOW()` | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | No | `NOW()` | Last update timestamp |
| `created_by_id` | UUID (FK) | No | — | Employee who created |
| `updated_by_id` | UUID (FK) | No | — | Employee who last updated |

**Foreign Keys:**
- `sample.material_id` → `material.id` (ON DELETE SET NULL, but deletes not allowed)
- `sample.packaging_id` → `packaging.id` (ON DELETE SET NULL)
- `sample.created_by_id` → `employee.id`
- `sample.updated_by_id` → `employee.id`

**Check Constraints:**
- `testing_status IN ('Not Tested', 'In Testing', 'Completed')`
- `sample_type IN ('RM', 'Packaging')`

**Indexes:**
- `idx_sample_sample_id` on `sample_id`
- `idx_sample_material_id` on `material_id`
- `idx_sample_packaging_id` on `packaging_id`
- `idx_sample_testing_status` on `testing_status`
- `idx_sample_sampling_date` on `sampling_date`
- `idx_sample_sampler` on `sampler`
- `idx_sample_sample_type` on `sample_type`

---

### 4.5 ProductSample

**Purpose:** Stores product samples (Finished Product, Semi‑Finished Product, Bulk).

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | No | `gen_random_uuid()` | Primary key |
| `sample_id` | VARCHAR(20) | No | — | `FP-YYYY-####`, `SFP-YYYY-####`, `BLK-YYYY-####` |
| `product_name` | VARCHAR(100) | No | — | Name of the product |
| `product_type` | VARCHAR(20) | No | — | `Finished Product`, `Semi-Finished Product`, `Bulk` |
| `batch_no` | VARCHAR(50) | No | — | Manufacturer's batch number |
| `batch_size` | DECIMAL(10,2) | No | — | Batch size |
| `unit` | VARCHAR(20) | Yes | NULL | Unit of measure |
| `mfg_date` | DATE | Yes | NULL | Manufacturing date |
| `exp_date` | DATE | Yes | NULL | Expiry date |
| `sample_size` | DECIMAL(10,2) | No | — | Quantity sampled |
| `time_of_sampling` | TIME | No | — | Time of sampling |
| `sampling_date` | DATE | No | — | Date sampled |
| `stages` | JSONB | No | `'[]'` | Array of stage labels (e.g., `["Export to: USA", "Local Market"]`) |
| `testing_status` | VARCHAR(20) | No | `'Not Tested'` | Not Tested, In Testing, Completed |
| `created_at` | TIMESTAMPTZ | No | `NOW()` | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | No | `NOW()` | Last update timestamp |
| `created_by_id` | UUID (FK) | No | — | Employee who created |
| `updated_by_id` | UUID (FK) | No | — | Employee who last updated |

**Unique Constraints:**
- `uq_product_sample_sample_id` on `sample_id`

**Foreign Keys:**
- `product_sample.created_by_id` → `employee.id`
- `product_sample.updated_by_id` → `employee.id`

**Check Constraints:**
- `product_type IN ('Finished Product', 'Semi-Finished Product', 'Bulk')`
- `testing_status IN ('Not Tested', 'In Testing', 'Completed')`

**Indexes:**
- `idx_product_sample_sample_id` on `sample_id`
- `idx_product_sample_product_name` on `product_name`
- `idx_product_sample_product_type` on `product_type`
- `idx_product_sample_batch_no` on `batch_no`
- `idx_product_sample_testing_status` on `testing_status`
- `idx_product_sample_sampling_date` on `sampling_date`
- `idx_product_sample_stages` on `stages` (GIN index for JSONB queries)

---

### 4.6 COA

**Purpose:** Stores Certificates of Analysis.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | VARCHAR(20) | No | — | `COA-YYYY-####` (primary key) |
| `sample_id` | UUID | No | — | References `sample.id` or `product_sample.id` |
| `sample_src` | VARCHAR(10) | No | — | `rm`, `fp`, `pkg` (source type) |
| `material_id` | UUID (FK) | Yes | NULL | For RM samples only; otherwise NULL |
| `receipt_id` | VARCHAR(20) | No | — | Denormalised for display |
| `sample_name` | VARCHAR(200) | No | — | Name of sample with type suffix |
| `batch_no` | VARCHAR(50) | No | — | Batch/lot number |
| `batch_size` | VARCHAR(50) | No | — | Size with unit |
| `supplier` | VARCHAR(100) | No | — | Supplier name |
| `manufacturer` | VARCHAR(100) | Yes | NULL | Manufacturer name |
| `mfg_date` | VARCHAR(50) | Yes | NULL | Manufacturing date (formatted) |
| `exp_date` | VARCHAR(50) | Yes | NULL | Expiry date (formatted) |
| `received_date` | VARCHAR(50) | Yes | NULL | Received date (formatted) |
| `specs_code` | VARCHAR(50) | No | — | Specification code |
| `reference` | VARCHAR(20) | No | — | `BP 2025`, `USP`, `EP`, `JP`, `In-House` |
| `analyst` | VARCHAR(100) | No | — | Analyst's name |
| `analysis_date` | DATE | Yes | NULL | Date of analysis |
| `remarks` | TEXT | Yes | NULL | Optional remarks |
| `status` | VARCHAR(20) | No | `'Draft'` | Draft, In Progress, Completed, Approved, Rejected |
| `created_date` | DATE | No | — | Date COA was created |
| `qc_comment` | TEXT | Yes | NULL | QC Manager comment on approval/rejection |
| `created_at` | TIMESTAMPTZ | No | `NOW()` | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | No | `NOW()` | Last update timestamp |
| `created_by_id` | UUID (FK) | No | — | Employee who created |
| `updated_by_id` | UUID (FK) | No | — | Employee who last updated |

**Foreign Keys:**
- `coa.material_id` → `material.id` (ON DELETE SET NULL)
- `coa.created_by_id` → `employee.id`
- `coa.updated_by_id` → `employee.id`

**Check Constraints:**
- `status IN ('Draft', 'In Progress', 'Completed', 'Approved', 'Rejected')`
- `reference IN ('BP 2025', 'USP', 'EP', 'JP', 'In-House')`
- `sample_src IN ('rm', 'fp', 'pkg')`

**Indexes:**
- `idx_coa_id` on `id` (primary key)
- `idx_coa_sample_id` on `sample_id`
- `idx_coa_status` on `status`
- `idx_coa_receipt_id` on `receipt_id`
- `idx_coa_analyst` on `analyst`
- `idx_coa_created_date` on `created_date`
- `idx_coa_created_at` on `created_at`

---

### 4.7 Notification

**Purpose:** Stores in‑app notifications (primarily for Storekeeper).

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | No | `gen_random_uuid()` | Primary key |
| `target_role` | VARCHAR(20) | No | — | `storekeeper` (future: other roles) |
| `title` | VARCHAR(100) | No | — | Notification title |
| `message` | TEXT | No | — | Notification message body |
| `read` | BOOLEAN | No | `FALSE` | Whether user has read it |
| `created_at` | TIMESTAMPTZ | No | `NOW()` | Creation timestamp |

**Indexes:**
- `idx_notification_target_role` on `target_role`
- `idx_notification_read` on `read` (partial index for unread)
- `idx_notification_created_at` on `created_at`

**Partial Index:**
- `CREATE INDEX idx_notification_unread ON notification(created_at) WHERE read = false;`

---

### 4.8 AuditLog

**Purpose:** Immutable audit trail for all GMP‑relevant operations.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | No | `gen_random_uuid()` | Primary key |
| `user_id` | UUID (FK) | No | — | Who performed the action |
| `username` | VARCHAR(50) | No | — | Denormalised username (snapshot) |
| `timestamp` | TIMESTAMPTZ | No | `NOW()` | Action timestamp |
| `action` | VARCHAR(20) | No | — | `CREATE`, `UPDATE`, `DELETE`, `LOGIN`, `LOGOUT` |
| `entity_type` | VARCHAR(20) | No | — | Table name (e.g., `material`, `coa`) |
| `entity_id` | VARCHAR(20) | No | — | Business identifier (e.g., `RCV-2026-0001`) |
| `old_value` | JSONB | Yes | NULL | Old state (JSON) |
| `new_value` | JSONB | Yes | NULL | New state (JSON) |
| `field_name` | VARCHAR(50) | Yes | NULL | For partial updates |
| `reason` | TEXT | Yes | NULL | Optional reason for change |
| `source_ip` | INET | Yes | NULL | Client IP address |
| `session_id` | VARCHAR(50) | Yes | NULL | Session/tracking ID |
| `created_at` | TIMESTAMPTZ | No | `NOW()` | Insertion timestamp |

**Foreign Keys:**
- `audit_log.user_id` → `employee.id` (ON DELETE RESTRICT)

**Indexes:**
- `idx_audit_timestamp` on `timestamp`
- `idx_audit_user_id` on `user_id`
- `idx_audit_entity_type` on `entity_type`
- `idx_audit_entity_id` on `entity_id`
- `idx_audit_action` on `action`

**Note:** This table is append‑only. No `UPDATE` or `DELETE` operations are permitted via application logic.

---

### 4.9 ElectronicSignature

**Purpose:** Stores structured electronic signatures for GMP decisions.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | No | `gen_random_uuid()` | Primary key |
| `user_id` | UUID (FK) | No | — | Signer's ID |
| `username` | VARCHAR(50) | No | — | Denormalised username (snapshot) |
| `timestamp` | TIMESTAMPTZ | No | `NOW()` | Signature timestamp |
| `meaning` | VARCHAR(100) | No | — | e.g., `Approve COA`, `Release Material` |
| `record_type` | VARCHAR(20) | No | — | `coa`, `material` |
| `record_id` | VARCHAR(20) | No | — | Business identifier of signed record |
| `record_hash` | VARCHAR(100) | No | — | SHA‑256 hash of record content |
| `signature_hash` | VARCHAR(100) | No | — | SHA‑256 hash of signature data |
| `reason` | TEXT | Yes | NULL | Optional reason |
| `status` | VARCHAR(20) | No | `'executed'` | `executed`, `revoked` (future) |
| `source_ip` | INET | Yes | NULL | Client IP address |
| `created_at` | TIMESTAMPTZ | No | `NOW()` | Insertion timestamp |

**Foreign Keys:**
- `electronic_signature.user_id` → `employee.id` (ON DELETE RESTRICT)

**Indexes:**
- `idx_esig_user_id` on `user_id`
- `idx_esig_timestamp` on `timestamp`
- `idx_esig_record_type` on `record_type`
- `idx_esig_record_id` on `record_id`
- `idx_esig_status` on `status`

---

## 5. Indexing Strategy

### 5.1 Index Definitions by Table

| Table | Index Name | Columns | Purpose |
|-------|------------|---------|---------|
| `employee` | `idx_employee_username` | `username` | Fast login lookup |
| `employee` | `idx_employee_job_role` | `job_role` | Filter by role |
| `material` | `idx_material_receipt_id` | `receipt_id` | Lookup by receipt ID |
| `material` | `idx_material_status` | `status` | Filter by quarantine/released/rejected |
| `material` | `idx_material_sampling_status` | `sampling_status` | Filter by sampling status |
| `material` | `idx_material_supplier_batch` | `supplier_batch` | Search by batch |
| `material` | `idx_material_exp_date` | `exp_date` | Expiry alerts |
| `material` | `idx_material_created_at` | `created_at` | Sorting |
| `packaging` | `idx_packaging_receipt_id` | `receipt_id` | Lookup |
| `packaging` | `idx_packaging_type` | `type` | Filter by type |
| `sample` | `idx_sample_sample_id` | `sample_id` | Lookup |
| `sample` | `idx_sample_testing_status` | `testing_status` | Analyst worklist |
| `sample` | `idx_sample_material_id` | `material_id` | Join |
| `sample` | `idx_sample_packaging_id` | `packaging_id` | Join |
| `product_sample` | `idx_product_sample_sample_id` | `sample_id` | Lookup |
| `product_sample` | `idx_product_sample_product_type` | `product_type` | Filter |
| `product_sample` | `idx_product_sample_testing_status` | `testing_status` | Analyst worklist |
| `product_sample` | `idx_product_sample_stages` | `stages` (GIN) | JSONB query |
| `coa` | `idx_coa_status` | `status` | QC filter |
| `coa` | `idx_coa_sample_id` | `sample_id` | Join |
| `coa` | `idx_coa_receipt_id` | `receipt_id` | Lookup |
| `audit_log` | `idx_audit_timestamp` | `timestamp` | Date range queries |
| `audit_log` | `idx_audit_user_id` | `user_id` | User audit trail |
| `audit_log` | `idx_audit_entity_type` | `entity_type` | Entity filter |
| `audit_log` | `idx_audit_entity_id` | `entity_id` | Record-specific audit |
| `notification` | `idx_notification_target_role` | `target_role` | Role filter |
| `notification` | `idx_notification_unread` | `created_at` where `read=false` | Efficient unread check |
| `electronic_signature` | `idx_esig_record_id` | `record_id` | Signature lookup |

### 5.2 Partial and Covering Indexes

**Partial Index:**
```sql
-- For fast unread notification count
CREATE INDEX idx_notification_unread ON notification(created_at) 
WHERE read = false;
```

**Covering Index:**
```sql
-- For fast material list queries
CREATE INDEX idx_material_list ON material(receipt_id, material_name, status, sampling_status, created_at) 
INCLUDE (supplier, supplier_batch, exp_date);
```

**JSONB Index (GIN):**
```sql
-- For querying stages in product_sample
CREATE INDEX idx_product_sample_stages ON product_sample USING GIN (stages);
```

---

## 6. Constraints and Data Integrity

### 6.1 Primary and Foreign Keys

All tables use `UUID` as primary keys (except `coa` which uses a string ID). Foreign keys reference the `id` column of the respective parent table.

**Foreign Key Actions:**
- `ON DELETE RESTRICT` or `SET NULL` (never cascade delete for business records)
- Audit and signature tables use `ON DELETE RESTRICT` to preserve history.

### 6.2 Unique Constraints

| Table | Constraint Name | Column(s) |
|-------|-----------------|-----------|
| `employee` | `uq_employee_username` | `username` |
| `material` | `uq_material_receipt_id` | `receipt_id` |
| `packaging` | `uq_packaging_receipt_id` | `receipt_id` |
| `product_sample` | `uq_product_sample_sample_id` | `sample_id` |
| `coa` | (primary key) | `id` |

### 6.3 Check Constraints

```sql
-- Employee
ALTER TABLE employee ADD CONSTRAINT ck_employee_job_role 
CHECK (job_role IN ('storekeeper', 'sampler', 'analyst', 'qcmanager'));

-- Material
ALTER TABLE material ADD CONSTRAINT ck_material_status 
CHECK (status IN ('Quarantine', 'Released', 'Rejected'));

ALTER TABLE material ADD CONSTRAINT ck_material_sampling_status 
CHECK (sampling_status IN ('Not Sampled', 'Sampling Requested', 'Sampled'));

-- Packaging
ALTER TABLE packaging ADD CONSTRAINT ck_packaging_type 
CHECK (type IN ('Primary', 'Secondary', 'Tertiary', 'Labelling', 'Other'));

ALTER TABLE packaging ADD CONSTRAINT ck_packaging_sampling_status 
CHECK (sampling_status IN ('Not Sampled', 'Sampling Requested', 'Sampled'));

-- Sample
ALTER TABLE sample ADD CONSTRAINT ck_sample_testing_status 
CHECK (testing_status IN ('Not Tested', 'In Testing', 'Completed'));

ALTER TABLE sample ADD CONSTRAINT ck_sample_type 
CHECK (sample_type IN ('RM', 'Packaging'));

-- ProductSample
ALTER TABLE product_sample ADD CONSTRAINT ck_product_sample_type 
CHECK (product_type IN ('Finished Product', 'Semi-Finished Product', 'Bulk'));

ALTER TABLE product_sample ADD CONSTRAINT ck_product_sample_testing_status 
CHECK (testing_status IN ('Not Tested', 'In Testing', 'Completed'));

-- COA
ALTER TABLE coa ADD CONSTRAINT ck_coa_status 
CHECK (status IN ('Draft', 'In Progress', 'Completed', 'Approved', 'Rejected'));

ALTER TABLE coa ADD CONSTRAINT ck_coa_reference 
CHECK (reference IN ('BP 2025', 'USP', 'EP', 'JP', 'In-House'));

ALTER TABLE coa ADD CONSTRAINT ck_coa_sample_src 
CHECK (sample_src IN ('rm', 'fp', 'pkg'));

-- Notification
ALTER TABLE notification ADD CONSTRAINT ck_notification_target_role 
CHECK (target_role = 'storekeeper');  -- future roles can be added

-- AuditLog
-- No check constraints needed.

-- ElectronicSignature
ALTER TABLE electronic_signature ADD CONSTRAINT ck_esig_status 
CHECK (status IN ('executed', 'revoked'));
```

### 6.4 Default Values

- `created_at`, `updated_at`: `NOW()` (or `CURRENT_TIMESTAMP`)
- `is_active` (Employee): `TRUE`
- `status` (Material): `'Quarantine'`
- `sampling_status` (Material, Packaging): `'Not Sampled'`
- `testing_status` (Sample, ProductSample): `'Not Tested'`
- `status` (COA): `'Draft'`
- `read` (Notification): `FALSE`
- `stages` (ProductSample): `'[]'::jsonb`

---

## 7. Audit and History

### 7.1 Audit Trail Table

The `audit_log` table captures all state changes. It is append‑only; records are never updated or deleted.

**Audit Trigger Mechanism:**
- Use **Django signals** (post_save, post_delete) to asynchronously write to `audit_log` via Celery.
- Capture old and new values using Django's `get_prep_value` or `model_to_dict`.
- For updates, only changed fields are logged (field_name, old_value, new_value).

### 7.2 Audit Trigger Mechanism (PostgreSQL Alternative)

If a database‑level trigger is preferred:

```sql
CREATE OR REPLACE FUNCTION audit_trigger() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (user_id, username, action, entity_type, entity_id, new_value, timestamp)
        VALUES (current_user_id(), current_user, 'CREATE', TG_TABLE_NAME, NEW.id, to_jsonb(NEW), NOW());
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (user_id, username, action, entity_type, entity_id, old_value, new_value, timestamp)
        VALUES (current_user_id(), current_user, 'UPDATE', TG_TABLE_NAME, NEW.id, to_jsonb(OLD), to_jsonb(NEW), NOW());
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (user_id, username, action, entity_type, entity_id, old_value, timestamp)
        VALUES (current_user_id(), current_user, 'DELETE', TG_TABLE_NAME, OLD.id, to_jsonb(OLD), NOW());
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

**Note:** The application will use Django signals for flexibility and better integration with Celery for async processing.

---

## 8. Migration and Versioning

### 8.1 Migration Tool

Use **Django migrations** (`python manage.py makemigrations`, `python manage.py migrate`). All migration files are stored in version control.

### 8.2 Migration Policy

- **Backward‑compatible**: All migrations must be reversible (safe to rollback).
- **Data migrations**: Must be separate from schema migrations and tested in staging.
- **Zero‑downtime**: Use `--noinput` and careful planning for large tables (add columns with default values, create indexes concurrently).
- **Index creation**: Use `CONCURRENTLY` for indexes on large tables.

### 8.3 Rollback Plan

- If a migration fails, the deployment pipeline should stop.
- Rollback to the previous migration: `python manage.py migrate <app_name> <previous_migration>`.
- Data loss may occur if data migrations have been run; ensure backups are taken before deployment.

**Backup Before Any Migration**: Always take a full database backup before applying migrations to production.

---

## 9. Performance and Optimisation

### 9.1 Connection Pooling

Use **PgBouncer** or Django's built‑in connection pooling (`CONN_MAX_AGE`) to manage database connections.

**Recommended Settings:**
- `CONN_MAX_AGE = 60` (seconds)
- PgBouncer pool size = number of backend instances × 10.

### 9.2 Partitioning Strategy

For tables expected to grow large:
- `audit_log`: Partition by date (monthly or quarterly).
- `notification`: Partition by date (monthly).

**Example Partitioning for `audit_log`:**
```sql
CREATE TABLE audit_log_y2026m01 PARTITION OF audit_log
FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

### 9.3 Vacuum and Maintenance

- Schedule `VACUUM ANALYZE` during low‑traffic hours (daily).
- Monitor bloat using `pg_stat_user_tables`.
- Use `autovacuum` with appropriate settings (scale factor, threshold).

**Recommended autovacuum settings:**
```
autovacuum_vacuum_scale_factor = 0.05
autovacuum_analyze_scale_factor = 0.02
autovacuum_vacuum_threshold = 1000
```

---

## 10. Appendices

### A. Data Dictionary

| Entity | Description | Business Identifier |
|--------|-------------|---------------------|
| Employee | System user | `username` |
| Material | Raw material lot | `receipt_id` (RCV-...) |
| Packaging | Packaging material lot | `receipt_id` (PKG-...) |
| Sample | RM or packaging sample | `sample_id` (same as receipt for RM) |
| ProductSample | FP/SFP/Bulk sample | `sample_id` (FP-/SFP-/BLK-...) |
| COA | Certificate of Analysis | `id` (COA-...) |
| Notification | In‑app notification | `id` (UUID) |
| AuditLog | Immutable audit entry | `id` (UUID) |
| ElectronicSignature | E‑signature record | `id` (UUID) |

### B. Migration Scripts Template

**Example Initial Migration (001_initial):**
```python
# Generated by Django
from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('username', models.CharField(max_length=50, unique=True)),
                # ... other fields
            ],
        ),
        # ... other models
        migrations.AddIndex(
            model_name='material',
            index=models.Index(fields=['receipt_id'], name='idx_material_receipt_id'),
        ),
        # ... other indexes
    ]
```

### C. Sample Data

```sql
-- Insert sample employee
INSERT INTO employee (id, username, password_hash, full_name, job_role, is_active)
VALUES (gen_random_uuid(), 'storekeeper1', 'hashed_password', 'John Storekeeper', 'storekeeper', true);

-- Insert sample material
INSERT INTO material (id, receipt_id, material_name, supplier, supplier_batch, exp_date, receipt_date, received_by)
VALUES (gen_random_uuid(), 'RCV-2026-0001', 'Paracetamol', 'PharmaChem Ltd', 'BATCH-2024-001', '2027-01-15', '2026-01-15', 'John Storekeeper');

-- Insert sample packaging
INSERT INTO packaging (id, receipt_id, name, type, qty, supplier, receipt_date, recipient)
VALUES (gen_random_uuid(), 'PKG-2026-0001', 'Aluminium Blister Foil', 'Primary', 500, 'PackCo Inc', '2026-01-15', 'John Storekeeper');
```

---

**Document Approval**

| Role | Name | Date |
|------|------|------|
| Author | [Name] | [Date] |
| Reviewer (DBA) | [Name] | [Date] |
| Reviewer (Architecture) | [Name] | [Date] |
| Approver | [Name] | [Date] |

---

**Change History**

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | [Date] | [Author] | Initial baseline database design |
