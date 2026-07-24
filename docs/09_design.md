# 09 — Design Specification

**Document Identifier:** RM-RRS-DES-001
**Version:** 1.0
**Status:** Baseline
**Traces to:** Project Charter, SRS, NFR, SAS
**Compliance Reference:** IEEE Std 1016-2009 (Software Design Descriptions), ISO/IEC/IEEE 42010:2011

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Design Overview](#2-design-overview)
3. [Architecture Refinement](#3-architecture-refinement)
4. [Detailed Component Design](#4-detailed-component-design)
5. [Database Design](#5-database-design)
6. [UI/UX Design](#6-uiux-design)
7. [API Design](#7-api-design)
8. [Security Design](#8-security-design)
9. [Operational Design](#9-operational-design)
10. [Appendices](#10-appendices)

---

## 1. Introduction

### 1.1 Purpose
This Design Specification document provides the detailed design of the **Raw Material Receiving & Release System (RM-RRS)** . It translates the architectural vision defined in the SAS into concrete, implementable designs for all system components — backend services, frontend applications, database schema, API interfaces, UI/UX, security, and operations. This document serves as the primary reference for developers during implementation and for quality assurance during validation.

### 1.2 Scope
This document covers the detailed design of all confirmed MVP components:
- **Access Control Layer**: Authentication, authorisation, audit trail, e-signature services
- **Four Business Applications**: Storekeeper, Sampler, Analyst, QC Manager
- **Administrator Console**: Employee and role management
- **Database Schema**: Complete entity definitions and relationships
- **API Design**: Detailed endpoint specifications with request/response examples
- **UI/UX Design**: Design system, wireframes, component specifications
- **Security Design**: Authentication, authorisation, data protection
- **Operational Design**: Deployment, monitoring, backup, recovery

### 1.3 References
| Document | Reference |
|----------|-----------|
| 00_Project_Charter.md | Charter |
| 06_SRS.md | Software Requirements Specification |
| 07_NFR.md | Non-Functional Requirements |
| 08_SAS.md | Software Architecture Specification |
| IEEE Std 1016-2009 | Standard for Software Design Descriptions |

---

## 2. Design Overview

### 2.1 Design Principles

| Principle | Description | Application |
|-----------|-------------|-------------|
| **Separation of Concerns** | Each module has a single, well-defined responsibility | Domain-driven modules; feature-based components |
| **DRY** | Avoid duplication of logic or data definitions | Shared UI components; shared utilities; code generation |
| **Single Responsibility** | Each class/component has one reason to change | Service classes handle one domain; React components one UI concern |
| **Open/Closed** | Open for extension, closed for modification | Pluggable permission system; configurable workflows |
| **Dependency Inversion** | Depend on abstractions, not concretions | Service interfaces; dependency injection |
| **Fail Fast** | Detect errors at the earliest opportunity | Input validation at API boundary; form validation in UI |
| **Audit by Design** | Audit logging is built in, not added on | Django signals; middleware; decorators for audit |

### 2.2 Design Goals

| Goal | Description | Metric |
|------|-------------|--------|
| **Correctness** | Accurately implements business workflow | All use cases pass validation |
| **Usability** | Intuitive interfaces matching prototype | Low training time; task completion rate |
| **Performance** | Fast response times per NFR | < 500 ms API response |
| **Security** | Data protected per regulatory requirements | No security vulnerabilities |
| **Maintainability** | Easy to extend and modify | High cohesion; low coupling |
| **Compliance** | Meets 21 CFR Part 11 / Annex 11 | Audit trail and e-signature coverage |

---

## 3. Architecture Refinement

### 3.1 High-Level System Architecture

```mermaid
flowchart TB
    subgraph Presentation["PRESENTATION LAYER"]
        SK["Storekeeper App<br/>(React)"]
        SM["Sampler App<br/>(React)"]
        AN["Analyst App<br/>(React)"]
        QC["QC Manager App<br/>(React)"]
        AD["Admin Console<br/>(React)"]
    end

    subgraph Gateway["API GATEWAY"]
        NGINX["Nginx Reverse Proxy"]
        API["Django REST API"]
    end

    subgraph Backend["BACKEND SERVICES"]
        subgraph ACL["ACCESS CONTROL LAYER"]
            AuthN["AuthN Service"]
            AuthZ["AuthZ Service"]
            Audit["Audit Service"]
            ESig["E-Signature Service"]
        end

        subgraph Domain["BUSINESS DOMAIN SERVICES"]
            Mat["Materials Service"]
            Pkg["Packaging Service"]
            Samp["Samples Service"]
            COA["COA Service"]
            Notif["Notifications Service"]
        end
    end

    subgraph Data["DATA LAYER"]
        PG[("PostgreSQL<br/>Database")]
        Redis[("Redis<br/>Cache + Broker")]
    end

    SK --> NGINX
    SM --> NGINX
    AN --> NGINX
    QC --> NGINX
    AD --> NGINX

    NGINX --> API
    API --> AuthN
    API --> AuthZ
    API --> Audit
    API --> ESig
    API --> Mat
    API --> Pkg
    API --> Samp
    API --> COA
    API --> Notif

    AuthN --> PG
    AuthZ --> PG
    Audit --> PG
    ESig --> PG
    Mat --> PG
    Pkg --> PG
    Samp --> PG
    COA --> PG
    Notif --> PG

    AuthN --> Redis
    AuthZ --> Redis
    Audit -.-> Redis
    ESig -.-> Redis
```

### 3.2 Backend Module Dependencies

```mermaid
flowchart TD
    Common["COMMON UTILITIES<br/>• BaseModel<br/>• Validators<br/>• Exceptions<br/>• Pagination"]

    Users["USERS<br/>• User Model<br/>• Auth Service<br/>• Permissions"]
    AuditMod["AUDIT<br/>• Audit Model<br/>• Signals<br/>• Middleware"]
    ESigMod["ESIGNATURE<br/>• Sig Model<br/>• Sig Service"]

    Materials["MATERIALS<br/>• Material Model<br/>• Service"]
    Packaging["PACKAGING<br/>• Packaging Model<br/>• Service"]
    Sampling["SAMPLING<br/>• Sample Model<br/>• Service"]

    Products["PRODUCTS<br/>• FPSample Model<br/>• Service"]
    COAMod["COA<br/>• COA Model<br/>• Service"]
    NotifMod["NOTIFICATIONS<br/>• Notif Model<br/>• Service"]

    Common --> Users
    Common --> AuditMod
    Common --> ESigMod

    Users --> Materials
    Users --> Packaging
    Users --> Sampling
    Users --> Products
    Users --> COAMod
    Users --> NotifMod

    AuditMod --> Materials
    AuditMod --> Packaging
    AuditMod --> Sampling
    AuditMod --> Products
    AuditMod --> COAMod

    ESigMod --> COAMod

    Materials --> Sampling
    Packaging --> Sampling
    Sampling --> Products
    Products --> COAMod
    Sampling --> COAMod
    COAMod --> NotifMod
```

### 3.3 Data Architecture Refinement

```mermaid
erDiagram
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
        date exp_date
        string status
        string sampling_status
        string qc_number
        date retest_date
        timestamp created_at
        timestamp updated_at
    }

    PACKAGING {
        uuid id PK
        string receipt_id UK
        string name
        string type
        decimal qty
        string supplier
        date receipt_date
        string recipient
        string sampling_status
        timestamp created_at
    }

    SAMPLE {
        uuid id PK
        string sample_id
        uuid material_id FK
        uuid packaging_id FK
        string sample_type
        decimal sample_size
        int containers
        string sampler
        string storage
        date sampling_date
        string testing_status
        timestamp created_at
    }

    PRODUCT_SAMPLE {
        uuid id PK
        string sample_id UK
        string product_name
        string product_type
        string batch_no
        decimal batch_size
        decimal sample_size
        time time_of_sampling
        date sampling_date
        jsonb stages
        string testing_status
        timestamp created_at
    }

    COA {
        string id PK
        uuid sample_id FK
        string sample_src
        uuid material_id FK
        string receipt_id
        string sample_name
        string batch_no
        string specs_code
        string reference
        string analyst
        string status
        date created_date
        text qc_comment
        timestamp created_at
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
        inet source_ip
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
        timestamp created_at
    }

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
```

---

## 4. Detailed Component Design

### 4.1 Access Control Layer Components

#### 4.1.1 Authentication Service

| Attribute | Specification |
|-----------|---------------|
| **Purpose** | Authenticate employees using username/password; issue session tokens |
| **Technology** | Django Authentication + JWT (djangorestframework-simplejwt) |
| **Package** | `apps.users.services.AuthService` |

**Authentication Flow:**

```mermaid
sequenceDiagram
    participant Browser as User Browser
    participant Login as Login View
    participant Auth as Auth Service
    participant DB as Database
    participant JWT as JWT Generator

    Browser->>Login: Enter credentials
    Login->>Auth: Validate credentials
    Auth->>DB: Query employee by username
    DB-->>Auth: Return employee record
    Auth->>Auth: Verify password hash
    Auth->>JWT: Generate access + refresh tokens
    JWT-->>Auth: Return tokens
    Auth-->>Login: Return user + tokens
    Login-->>Browser: Set HTTP-only cookies + redirect
    Login->>Audit: Async log login event
    Note over Browser: User redirected to role dashboard
```

**JWT Token Structure:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "uuid",
    "username": "jdoe",
    "full_name": "John Doe",
    "job_role": "storekeeper"
  }
}
```

#### 4.1.2 Authorisation Service

| Attribute | Specification |
|-----------|---------------|
| **Purpose** | Enforce role-based permissions at API and UI levels |
| **Technology** | Django permissions + DRF permission classes |
| **Package** | `apps.users.permissions` + `apps.users.services.AuthorizationService` |

**Permission Checking Flow:**

```mermaid
sequenceDiagram
    participant Client as Client
    participant View as API View
    participant AuthZ as AuthZ Service
    participant Logic as Business Logic
    participant Audit as Audit Service

    Client->>View: API Request + JWT
    View->>AuthZ: Extract & decode token
    AuthZ->>AuthZ: Get user from cache/DB
    AuthZ->>AuthZ: Check required permission
    alt Has Permission
        AuthZ-->>View: Authorised
        View->>Logic: Execute business logic
        Logic-->>View: Return result
        View-->>Client: HTTP 200 Response
    else No Permission
        AuthZ-->>View: Forbidden
        AuthZ->>Audit: Async log permission denial
        View-->>Client: HTTP 403 Forbidden
    end
```

**Role → Permissions Mapping:**

| Role | Permissions |
|------|-------------|
| Storekeeper | `materials.view`, `materials.create`, `materials.update`, `packaging.view`, `packaging.create`, `packaging.update`, `materials.request_sampling`, `packaging.request_sampling` |
| Sampler | `samples.view`, `samples.create`, `samples.print_label`, `product_samples.view`, `product_samples.create` |
| Analyst | `samples.view`, `samples.start_testing`, `coa.view`, `coa.create`, `coa.update`, `coa.submit`, `coa.complete` |
| QC Manager | `coa.view`, `coa.approve`, `coa.reject`, `materials.release` |
| Admin | `employees.*`, `roles.*`, `audit.*` |

#### 4.1.3 Electronic Signature Service

| Attribute | Specification |
|-----------|---------------|
| **Purpose** | Create and verify electronic signatures for GMP decisions |
| **Technology** | Django models + cryptographic hashing (SHA-256) |
| **Package** | `apps.esignature.services.SignatureService` |

**Signature Flow:**

```mermaid
sequenceDiagram
    participant User as QC User
    participant UI as QC App
    participant Sig as Signature Service
    participant DB as Database
    participant Audit as Audit Service

    User->>UI: Click Approve COA
    UI->>Sig: Request signature creation
    Sig->>Sig: Collect context (user, meaning, record)
    Sig->>Sig: Hash record content (SHA-256)
    Sig->>DB: Create SignatureRecord
    DB-->>Sig: Confirm creation
    Sig->>Audit: Async log signature event
    Sig-->>UI: Signature confirmation
    UI-->>User: Display success
    UI->>COA: Advance COA status
```

---

### 4.2 Storekeeper Application Components

#### 4.2.1 Material Registration Component

| Attribute | Specification |
|-----------|---------------|
| **Purpose** | Register incoming raw materials |
| **Component** | `MaterialForm.tsx` |
| **State** | React Hook Form + Zod validation |
| **API** | POST `/api/v1/materials/` |

**Form Field Mapping:**

| Field | Type | Required | Default | Validation |
|-------|------|----------|---------|------------|
| `receiptId` | Text (auto) | Yes | `RCV-YYYY-####` | Auto-generated |
| `materialName` | Dropdown | Yes | — | Must be in list |
| `supplier` | Dropdown | Yes | — | Must be in list |
| `supplierBatch` | Text | Yes | — | Not empty |
| `expDate` | Date | Yes | — | Must be future |
| `receiptDate` | Date | Yes | Today | — |
| `receivedBy` | Text | Yes | — | Not empty |

**Validation Rules:**
- Required fields: `materialName`, `supplier`, `supplierBatch`, `expDate`, `receiptDate`, `receivedBy`
- `totalQty` = `numPackages` × `packageSize` (auto-calculated)

#### 4.2.2 Material Table Component

| Attribute | Specification |
|-----------|---------------|
| **Purpose** | Display materials with search and filter capabilities |
| **Component** | `MaterialTable.tsx` |
| **State** | React Query (server state) |
| **API** | GET `/api/v1/materials/?search=&status=&sampling=` |

**Columns:**
Receipt ID | Material Name | Supplier Batch | Receiving Date | Total Qty | Status | Sampling Status | Expire Date | Actions

**Features:**
- Server-side pagination (20 records per page)
- Search across Receipt ID, Material Name, Supplier Batch
- Filter by Status, Sampling Status
- Inline actions (View, Request Sampling, Print Label)

---

### 4.3 Sampler Application Components

#### 4.3.1 Sampling Form Component

| Attribute | Specification |
|-----------|---------------|
| **Purpose** | Record a sampling event |
| **Component** | `SamplingForm.tsx` |
| **State** | React Hook Form + Zod validation |
| **API** | POST `/api/v1/samples/` |

**Form Field Mapping:**

| Field | Type | Required | Source |
|-------|------|----------|--------|
| `sampleId` | Text (auto) | Yes | Material.receiptId |
| `materialName` | Text | Yes | Material.materialName |
| `sampleSize` | Number | Yes | User input |
| `containers` | Number | Yes | User input |
| `sampler` | Text | Yes | User input |
| `storageCondition` | Dropdown | Yes | Ambient/Refrigerated/Frozen/Protected/CRT |
| `samplingDate` | Date | Yes | User input (defaults to today) |

**Post-Save Behaviour:**
1. Create sample record (testingStatus = Not Tested)
2. Update material samplingStatus → Sampled
3. Open Label Preview (two labels side by side)

#### 4.3.2 Product Sample Registration Component

| Attribute | Specification |
|-----------|---------------|
| **Purpose** | Register FP, SFP, and Bulk samples |
| **Component** | `ProductSampleForm.tsx` |
| **State** | React Hook Form + Zod validation |
| **API** | POST `/api/v1/product-samples/` |

**Sample ID Generation:**
- Finished Product: `FP-YYYY-####`
- Semi-Finished Product: `SFP-YYYY-####`
- Bulk: `BLK-YYYY-####`

**Stage Checkboxes with Conditional Text:**
- [ ] Export to: [___________]
- [ ] Local Market
- [ ] UPA
- [ ] F.M.A
- [ ] For Toll: [___________]

---

### 4.4 Analyst Application Components

#### 4.4.1 Combined Samples Worklist

| Attribute | Specification |
|-----------|---------------|
| **Purpose** | Display all samples (RM, Packaging, Product) in one unified view |
| **Component** | `SampleWorklist.tsx` |
| **State** | React Query |
| **API** | GET `/api/v1/samples/combined/` |

**Type Tags:**
| Type | Badge Style |
|------|-------------|
| Raw Material | `badge-sampled` (green) |
| Packaging | `badge-packaging` (purple) |
| FP | `badge-fp` (amber) |
| SFP | `badge-sfp` (blue) |
| Bulk | `badge-bulk` (green) |

#### 4.4.2 COA Creation Component

| Attribute | Specification |
|-----------|---------------|
| **Purpose** | Create Certificate of Analysis from a sample |
| **Component** | `COAForm.tsx` |
| **State** | React Hook Form + Zod validation |
| **API** | POST `/api/v1/coas/` |

**COA Status Workflow:**

```mermaid
stateDiagram-v2
    [*] --> Draft: Create COA
    Draft --> InProgress: Submit for Review
    InProgress --> Completed: Mark Completed
    Completed --> Approved: QC Approve
    Completed --> Rejected: QC Reject
    Approved --> [*]
    Rejected --> [*]
```

---

### 4.5 QC Manager Application Components

#### 4.5.1 COA Detail Component (QC Manager View)

| Attribute | Specification |
|-----------|---------------|
| **Purpose** | Display full COA with approve/reject actions |
| **Component** | `COADetail.tsx` |
| **State** | React Query |
| **API** | GET `/api/v1/coas/{id}/` |

**COA Detail Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  CERTIFICATE OF ANALYSIS                                    │
│  COA-2026-0001  ·  Issued: 15/01/2026                      │
├─────────────────────────────────────────────────────────────┤
│  Material & Sample Details                                 │
│  ┌───────────────┐  ┌───────────────┐                     │
│  │ Sample Name   │  │ Paracetamol   │                     │
│  │ Batch No.     │  │ BATCH-2024-001│                     │
│  │ Batch Size    │  │ 1000 kg       │                     │
│  │ Supplier      │  │ PharmaChem Ltd│                     │
│  │ Manufacturer  │  │ BASF SE       │                     │
│  │ Mfg Date      │  │ 15/01/2025    │                     │
│  │ Exp Date      │  │ 15/01/2027    │                     │
│  │ Received Date │  │ 15/01/2026    │                     │
│  └───────────────┘  └───────────────┘                     │
│  Status: [Completed]  QC Comment: [optional]               │
├─────────────────────────────────────────────────────────────┤
│  [Reject]  [Approve COA]                                   │
└─────────────────────────────────────────────────────────────┘
```

#### 4.5.2 Release Modal Component

| Attribute | Specification |
|-----------|---------------|
| **Purpose** | Release raw material after COA approval |
| **Component** | `ReleaseModal.tsx` |
| **State** | React Hook Form + Zod validation |
| **API** | POST `/api/v1/materials/{id}/release/` |

**Release Flow:**

```mermaid
flowchart TD
    A[QC Manager approves COA] --> B[Release Modal opens]
    B --> C[Enter QC Number]
    C --> D[Enter QC Signature]
    D --> E[Auto-calc Retest Date = Today + 1 year]
    E --> F[Submit Release]
    F --> G[Material status → Released]
    G --> H[Store QC Number/Signature/Retest Date]
    H --> I[Create Notification for Storekeeper]
    I --> J[Release Label becomes available]
    J --> K[Audit + E-Signature recorded]
```

---

## 5. Database Design

### 5.1 Entity-Relationship Diagram

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

### 5.2 Table Indexing Strategy

```mermaid
flowchart LR
    subgraph Material["MATERIAL Indexes"]
        M1["idx_receipt_id"]
        M2["idx_status"]
        M3["idx_sampling_status"]
        M4["idx_supplier_batch"]
        M5["idx_exp_date"]
        M6["idx_created_at"]
        M7["idx_material_name"]
        M8["idx_supplier"]
    end

    subgraph Sample["SAMPLE Indexes"]
        S1["idx_sample_id"]
        S2["idx_material_id"]
        S3["idx_testing_status"]
        S4["idx_sampling_date"]
        S5["idx_sampler"]
    end

    subgraph COA["COA Indexes"]
        C1["idx_id"]
        C2["idx_sample_id"]
        C3["idx_status"]
        C4["idx_receipt_id"]
        C5["idx_analyst"]
        C6["idx_created_date"]
    end

    subgraph Audit["AUDIT_LOG Indexes"]
        A1["idx_timestamp"]
        A2["idx_user_id"]
        A3["idx_entity_type"]
        A4["idx_entity_id"]
        A5["idx_action"]
    end
```

### 5.3 Data Integrity Constraints

**Check Constraints:**
- `status IN ('Quarantine', 'Released', 'Rejected')`
- `sampling_status IN ('Not Sampled', 'Sampling Requested', 'Sampled')`
- `coa.status IN ('Draft', 'In Progress', 'Completed', 'Approved', 'Rejected')`
- `product_type IN ('Finished Product', 'Semi-Finished Product', 'Bulk')`

**Unique Constraints:**
- `material.receipt_id` UNIQUE
- `packaging.receipt_id` UNIQUE
- `product_sample.sample_id` UNIQUE
- `coa.id` PRIMARY KEY
- `employee.username` UNIQUE

---

## 6. UI/UX Design

### 6.1 Design System

**Colour Palette:**

| Variable | Hex | Usage |
|----------|-----|-------|
| `--primary` | #2d6a4f | Primary actions, links, success states |
| `--primary-light` | #e8f4ee | Primary background |
| `--info` | #2563a8 | Information, sampling status |
| `--info-light` | #eff4fb | Info background |
| `--warning` | #b7791f | Warning, quarantine status |
| `--warning-light` | #fef9ec | Warning background |
| `--danger` | #c0392b | Error, rejection, delete |
| `--danger-light` | #fdf0ee | Danger background |
| `--purple` | #6d28d9 | QC Manager, release labels |
| `--bg` | #f5f5f3 | Page background |
| `--surface` | #ffffff | Card/modal backgrounds |
| `--border` | #e8e8e5 | Borders |
| `--text` | #1a1a18 | Primary text |
| `--text2` | #5a5a55 | Secondary text |
| `--text3` | #9a9a94 | Muted text |

**Typography:**

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Body | DM Sans | 14px | 400 |
| Headings | DM Sans | 20px | 600 |
| Labels | DM Sans | 12px | 500 |
| Table cells | DM Sans | 13px | 400 |
| IDs/Batch | DM Mono | 12px | 500 |
| Badges | DM Sans | 11px | 500 |
| Print | DM Mono | 11px | 400 |

### 6.2 UI Component Inventory

| Component | Purpose |
|-----------|---------|
| `Button` | Reusable button with variants |
| `Table` | Data table with sorting/pagination |
| `Modal` | Overlay modal with header/footer |
| `Badge` | Status indicators |
| `StatusBadge` | Role/status badges |
| `Label` | Print label component |
| `Toast` | Notification toast |
| `PrintArea` | Hidden print container |
| `Form` | Form with validation |
| `Input` | Text input |
| `Select` | Dropdown select with add option |
| `DatePicker` | Date input |
| `Textarea` | Multi-line text input |
| `Checkbox` | Checkbox with label |
| `Pagination` | Table pagination |
| `StatsCard` | Dashboard statistics |
| `SearchBar` | Search input with icon |
| `FilterDropdown` | Filter select |

### 6.3 Badge Colour Coding

```mermaid
flowchart LR
    subgraph Status["Material Status"]
        Q["Quarantine"] --> QS["badge-quarantine<br/>#b7791f"]
        R["Released"] --> RS["badge-released<br/>#2d6a4f"]
        RJ["Rejected"] --> RJS["badge-rejected<br/>#c0392b"]
    end

    subgraph Sampling["Sampling Status"]
        NS["Not Sampled"] --> NSS["badge-notsampled<br/>#9a9a94"]
        SR["Sampling Requested"] --> SRS["badge-requested<br/>#2563a8"]
        S["Sampled"] --> SS["badge-sampled<br/>#2d6a4f"]
    end

    subgraph Testing["Testing Status"]
        NT["Not Tested"] --> NTS["badge-nottested<br/>#9a9a94"]
        IT["In Testing"] --> ITS["badge-intesting<br/>#2563a8"]
        C["Completed"] --> CS["badge-completed<br/>#92400e"]
    end

    subgraph COA["COA Status"]
        D["Draft"] --> DS["badge-draft<br/>#9a9a94"]
        IP["In Progress"] --> IPS["badge-inprogress<br/>#2563a8"]
        A["Approved"] --> AS["badge-approved<br/>#2d6a4f"]
        RJ2["Rejected"] --> RJS2["badge-rejected<br/>#c0392b"]
    end

    subgraph Type["Sample Type"]
        PKG["Packaging"] --> PS["badge-packaging<br/>#6d28d9"]
        FP["Finished Product"] --> FPS["badge-fp<br/>#d97706"]
        SFP["Semi-Finished"] --> SFPS["badge-sfp<br/>#0ea5e9"]
        BLK["Bulk"] --> BKS["badge-bulk<br/>#16a34a"]
    end
```

### 6.4 Print Design

**Label Print CSS:**
- Font: DM Mono (monospace)
- Labels: 250px min-width, side by side
- Headers: Coloured bars (green, blue, purple)
- Data: `display: flex; gap: 6px` with key (gray) and value (bold)
- Dividers: Dashed lines between sections
- Page break: `page-break-inside: avoid` on each label

**Print Styles:**
```css
@media print {
  body * { visibility: hidden; }
  #printArea, #printArea * { visibility: visible; }
  #printArea { 
    position: fixed; 
    inset: 0; 
    padding: 30px; 
    background: #fff; 
  }
}
```

---

## 7. API Design

### 7.1 API Architecture

**Base URL:** `https://api.rm-rrs.example.com/api/v1/`

**Authentication:** JWT Bearer token (or HTTP‑only cookie)

**Headers:**
```
Authorization: Bearer <access_token>
Accept: application/json
Content-Type: application/json
X-Correlation-ID: <uuid>
```

**Response Format:**
```json
{
  "data": { ... },
  "meta": { "total": 100, "page": 1, "per_page": 20 },
  "errors": null
}
```

**Error Response:**
```json
{
  "data": null,
  "meta": {},
  "errors": [
    {
      "code": "VALIDATION_ERROR",
      "message": "The field 'material_name' is required.",
      "field": "material_name"
    }
  ]
}
```

### 7.2 API Endpoints

```mermaid
flowchart LR
    subgraph Auth["Authentication"]
        LOGIN["POST /auth/login/"]
        LOGOUT["POST /auth/logout/"]
        REFRESH["POST /auth/refresh/"]
        ME["GET /auth/me/"]
    end

    subgraph Materials["Materials (Storekeeper)"]
        M_LIST["GET /materials/"]
        M_CREATE["POST /materials/"]
        M_DETAIL["GET /materials/{id}/"]
        M_UPDATE["PATCH /materials/{id}/"]
        M_REQ["POST /materials/{id}/request-sampling/"]
        M_LABEL["GET /materials/{id}/label/"]
    end

    subgraph Packaging["Packaging (Storekeeper)"]
        P_LIST["GET /packaging/"]
        P_CREATE["POST /packaging/"]
        P_DETAIL["GET /packaging/{id}/"]
        P_REQ["POST /packaging/{id}/request-sampling/"]
    end

    subgraph Samples["Samples (Sampler + Analyst)"]
        S_LIST["GET /samples/"]
        S_REQ["GET /samples/requests/"]
        S_CREATE["POST /samples/"]
        S_HIST["GET /samples/history/"]
        S_DETAIL["GET /samples/{id}/"]
        S_LABEL["GET /samples/{id}/label/"]
        S_TEST["POST /samples/{id}/start-testing/"]
    end

    subgraph Product["Product Samples (Sampler + Analyst)"]
        PS_LIST["GET /product-samples/"]
        PS_CREATE["POST /product-samples/"]
        PS_DETAIL["GET /product-samples/{id}/"]
    end

    subgraph COA["COA (Analyst + QC Manager)"]
        C_LIST["GET /coas/"]
        C_CREATE["POST /coas/"]
        C_DETAIL["GET /coas/{id}/"]
        C_UPDATE["PATCH /coas/{id}/"]
        C_SUBMIT["POST /coas/{id}/submit/"]
        C_COMPLETE["POST /coas/{id}/complete/"]
        C_APPROVE["POST /coas/{id}/approve/"]
        C_REJECT["POST /coas/{id}/reject/"]
    end

    subgraph Notif["Notifications (Storekeeper)"]
        N_LIST["GET /notifications/"]
        N_READ["PATCH /notifications/{id}/"]
        N_DEL["DELETE /notifications/{id}/"]
    end

    subgraph Admin["Employees (Admin)"]
        E_LIST["GET /employees/"]
        E_CREATE["POST /employees/"]
        E_DETAIL["GET /employees/{id}/"]
        E_UPDATE["PATCH /employees/{id}/"]
        E_DEL["DELETE /employees/{id}/"]
        AUDIT["GET /audit/"]
    end
```

### 7.3 Request/Response Examples

**Create Material (POST /materials/):**

Request:
```json
{
  "material_name": "Paracetamol",
  "supplier": "PharmaChem Ltd",
  "supplier_batch": "BATCH-2024-001",
  "exp_date": "2027-01-15",
  "receipt_date": "2026-01-15",
  "received_by": "John Smith"
}
```

Response:
```json
{
  "data": {
    "id": "mat_abc123",
    "receipt_id": "RCV-2026-0047",
    "material_name": "Paracetamol",
    "status": "Quarantine",
    "sampling_status": "Not Sampled"
  }
}
```

### 7.4 Error Codes

| HTTP Status | Code | Description |
|-------------|------|-------------|
| 400 | `VALIDATION_ERROR` | Invalid input data |
| 400 | `DUPLICATE_ENTITY` | Record already exists |
| 401 | `UNAUTHORIZED` | No/invalid authentication |
| 403 | `FORBIDDEN` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resource not found |
| 409 | `CONFLICT` | State conflict |
| 422 | `UNPROCESSABLE_ENTITY` | Business rule violation |
| 500 | `INTERNAL_ERROR` | Server error |

---

## 8. Security Design

### 8.1 Authentication Flow

```mermaid
sequenceDiagram
    participant User as User
    participant FE as Frontend
    participant BE as Backend
    participant DB as Database
    participant Cache as Redis

    User->>FE: Enter username/password
    FE->>BE: POST /auth/login/
    BE->>DB: Query employee
    DB-->>BE: Return employee
    BE->>BE: Verify password hash
    BE->>Cache: Store session
    BE-->>FE: Return JWT (HTTP-only cookie)
    FE-->>User: Redirect to role dashboard

    Note over FE,BE: Token Refresh
    FE->>BE: API request with expired token
    BE-->>FE: 401 Unauthorized
    FE->>BE: POST /auth/refresh/
    BE->>Cache: Validate refresh token
    BE-->>FE: New access token
    FE->>BE: Retry original request
```

### 8.2 Data Protection Summary

| Concern | Measure |
|---------|---------|
| **Transport** | TLS 1.2+; HSTS headers |
| **At Rest** | Database encrypted at rest |
| **Secrets** | Environment variables; never in code |
| **PII** | Minimal PII stored; audit logs masked |
| **Backups** | Encrypted before off-site transfer |
| **Passwords** | bcrypt hashed; never logged |
| **Tokens** | HTTP-only cookies; not accessible via JS |

### 8.3 Audit Coverage

```mermaid
flowchart LR
    subgraph Events["Audited Events"]
        E1["Material CRUD"]
        E2["Packaging CRUD"]
        E3["Sample CRUD"]
        E4["Product Sample CRUD"]
        E5["COA CRUD"]
        E6["Employee CRUD"]
        E7["Login/Logout"]
        E8["Permission Denials"]
        E9["QC Approve/Reject"]
    end

    subgraph Fields["Audit Fields"]
        F1["User ID"]
        F2["Timestamp"]
        F3["Action Type"]
        F4["Entity Type"]
        F5["Entity ID"]
        F6["Old Value (JSON)"]
        F7["New Value (JSON)"]
        F8["Reason"]
        F9["Source IP"]
    end

    Events --> Fields
```

---

## 9. Operational Design

### 9.1 Deployment Architecture

```mermaid
flowchart TB
    subgraph External["EXTERNAL"]
        DNS["DNS: rm-rrs.example.com"]
        LB["Load Balancer"]
    end

    subgraph App["APPLICATION SERVERS"]
        N1["Nginx + Backend 1"]
        N2["Nginx + Backend 2"]
        N3["Nginx + Backend 3"]
    end

    subgraph Workers["BACKGROUND WORKERS"]
        W1["Celery Worker 1"]
        W2["Celery Worker 2"]
        WB["Celery Beat"]
    end

    subgraph Data["DATA STORE"]
        PG[("PostgreSQL<br/>Primary + Replica")]
        Redis[("Redis<br/>Session + Cache + Broker")]
    end

    DNS --> LB
    LB --> N1
    LB --> N2
    LB --> N3

    N1 --> PG
    N2 --> PG
    N3 --> PG
    N1 --> Redis
    N2 --> Redis
    N3 --> Redis

    W1 --> PG
    W2 --> PG
    W1 --> Redis
    W2 --> Redis
    WB --> Redis

    subgraph Volumes["PERSISTENT VOLUMES"]
        V1["postgres_data"]
        V2["redis_data"]
        V3["backup_volume"]
    end

    PG --> V1
    Redis --> V2
```

### 9.2 Monitoring and Alerting

```mermaid
flowchart LR
    subgraph Metrics["KEY METRICS"]
        M1["API Response Time<br/>>500ms → Alert"]
        M2["Error Rate<br/>>1% → Alert"]
        M3["Login Failures<br/>>5/hour → Alert"]
        M4["DB Connections<br/>>80% → Alert"]
        M5["Queue Length<br/>>100 → Alert"]
        M6["CPU/Memory<br/>>85% → Alert"]
        M7["Disk Usage<br/>>75% → Alert"]
    end

    subgraph Channels["ALERT CHANNELS"]
        C1["PagerDuty<br/>Critical"]
        C2["Email<br/>Warning"]
        C3["Slack<br/>Info"]
    end

    M1 --> C1
    M2 --> C1
    M3 --> C2
    M4 --> C2
    M5 --> C2
    M6 --> C2
    M7 --> C3
```

### 9.3 Backup Strategy

| Type | Frequency | Retention |
|------|-----------|-----------|
| Full Database Backup | Daily (02:00 UTC) | 30 days |
| WAL Archiving | Continuous | 7 days |
| Monthly Backup | Last day of month | 12 months |
| Yearly Backup | 31 December | 7 years |
| Application Code | Per commit | Unlimited (Git) |

**RTO:** 4 hours | **RPO:** 1 hour

---

## 10. Appendices

### A. Architectural Decision Log

| Decision ID | Decision | Rationale | Status |
|-------------|----------|-----------|--------|
| DES-001 | JWT with HTTP-only cookies | Secure; prevents XSS token theft | Confirmed |
| DES-002 | Audit via Django signals + Celery | Application-context; async; non-blocking | Confirmed |
| DES-003 | `window.print()` for labels | Simple; matches prototype | Confirmed |
| DES-004 | Shared frontend monorepo (pnpm) | Code reuse; consistent versions | TBS |
| DES-005 | React Query for server state | Caching; revalidation; optimistic updates | TBS |
| DES-006 | PostgreSQL JSONB for audit logs | Flexible; queryable; schema evolution | Confirmed |
| DES-007 | Human-readable sequential IDs | Prototype; human-friendly; auditable | Confirmed |

### B. Design Standards Checklist

| Standard | Status |
|----------|--------|
| All IDs auto-generated per specification | ✅ |
| All forms have validation | ✅ |
| All UI labels match prototype | ✅ |
| All API endpoints have permissions | ✅ |
| All GMP records have audit logging | ✅ |
| All QC decisions have e-signatures | ✅ |
| All errors handled with user-friendly messages | ✅ |
| Print functionality available where specified | ✅ |
| Notifications trigger on release | ✅ |
| Role-based navigation enforced | ✅ |

---

**Document Approval**

| Role | Name | Date |
|------|------|------|
| Author | [Name] | [Date] |
| Reviewer (Architecture) | [Name] | [Date] |
| Reviewer (Product) | [Name] | [Date] |
| Approver | [Name] | [Date] |

---

**Change History**

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | [Date] | [Author] | Initial baseline with mermaid diagrams |

