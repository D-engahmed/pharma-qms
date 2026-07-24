# 06 — Software Requirements Specification (SRS)

**Document Identifier:** RM-RRS-SRS-001  
**Version:** 1.0  
**Status:** Baseline  
**Traces to:** Project Charter, Glossary, BRD, PRD, Use Cases, Roles & Permissions  
**Compliance Reference:** IEEE Std 830-1998 / ISO/IEC/IEEE 29148:2018  

---

## Table of Contents
1. [Introduction](#1-introduction)  
   1.1 [Purpose](#11-purpose)  
   1.2 [Scope](#12-scope)  
   1.3 [Definitions, Acronyms, and Abbreviations](#13-definitions-acronyms-and-abbreviations)  
   1.4 [References](#14-references)  
   1.5 [Overview](#15-overview)  

2. [Overall Description](#2-overall-description)  
   2.1 [Product Perspective](#21-product-perspective)  
   2.2 [User Characteristics](#22-user-characteristics)  
   2.3 [Operating Environment](#23-operating-environment)  
   2.4 [Design and Implementation Constraints](#24-design-and-implementation-constraints)  
   2.5 [Assumptions and Dependencies](#25-assumptions-and-dependencies)  

3. [Specific Requirements](#3-specific-requirements)  
   3.1 [Functional Requirements](#31-functional-requirements)  
      3.1.1 [Access Control Layer](#311-access-control-layer)  
      3.1.2 [Storekeeper Application](#312-storekeeper-application)  
      3.1.3 [Sampler Application](#313-sampler-application)  
      3.1.4 [Analyst Application](#314-analyst-application)  
      3.1.5 [QC Manager Application](#315-qc-manager-application)  
      3.1.6 [Administrator Console](#316-administrator-console)  
   3.2 [External Interface Requirements](#32-external-interface-requirements)  
      3.2.1 [User Interfaces](#321-user-interfaces)  
      3.2.2 [Software Interfaces](#322-software-interfaces)  
      3.2.3 [Communication Interfaces](#323-communication-interfaces)  
   3.3 [Non-Functional Requirements](#33-non-functional-requirements)  
      3.3.1 [Performance](#331-performance)  
      3.3.2 [Security](#332-security)  
      3.3.3 [Audit and Compliance](#333-audit-and-compliance)  
      3.3.4 [Reliability and Availability](#334-reliability-and-availability)  
      3.3.5 [Usability](#335-usability)  
      3.3.6 [Maintainability](#336-maintainability)  
   3.4 [Data Requirements](#34-data-requirements)  
      3.4.1 [Data Entities](#341-data-entities)  
      3.4.2 [Data Integrity](#342-data-integrity)  
      3.4.3 [Data Retention](#343-data-retention)  

4. [Appendices](#4-appendices)  
   A. [ID Generation Specifications](#a-id-generation-specifications)  
   B. [State Transition Diagrams](#b-state-transition-diagrams)  
   C. [Data Model Summary](#c-data-model-summary)  
   D. [Traceability Matrix](#d-traceability-matrix)  

---

## 1. Introduction

### 1.1 Purpose
The purpose of this Software Requirements Specification (SRS) is to define the complete functional and non-functional requirements for the **Raw Material Receiving & Release System (RM-RRS)** . The system is a GMP-compliant electronic record solution that manages the lifecycle of pharmaceutical raw materials, packaging materials, and product samples – from warehouse receiving through quality control (QC) testing and final release. This document serves as the authoritative source for all development, validation, and compliance activities, and is intended for system architects, developers, quality assurance personnel, and regulatory stakeholders.

### 1.2 Scope
The RM-RRS encompasses the following components, as confirmed in the Project Charter and clarification sessions:

- **Four role‑specific business applications**: Storekeeper, Sampler, Analyst, QC Manager.
- **One shared Access Control Layer**: authentication, authorization, audit trail, and electronic signature services.
- **One shared PostgreSQL database** containing all business and platform records.
- **Administrator Console** for employee management and role assignment.

The system supports the end‑to‑end business processes demonstrated in the provided prototype, including:
- Registration of raw materials and packaging materials with quarantine status.
- Sampling request, sample execution, and label generation.
- Direct registration of Finished Product (FP), Semi‑Finished Product (SFP), and Bulk samples.
- Analytical testing and Certificate of Analysis (COA) creation.
- QC Manager review, approval/rejection, and material release (raw material only, per current confirmed scope).

**Out of scope** for this version: Monograph management (full functionality), release workflow for packaging/product samples, multi‑site operations, external identity providers, and any features not explicitly present in the prototype or confirmed in the clarification session. These are marked as **TBS** (To Be Specified) and will be addressed in future releases.

### 1.3 Definitions, Acronyms, and Abbreviations
| Term | Definition | Source |
|------|------------|--------|
| **RM** | Raw Material – material received and tracked through the QC lifecycle. | Glossary |
| **FP** | Finished Product – a product sample type registered by the Sampler. | Glossary |
| **SFP** | Semi‑Finished Product – a product sample type registered by the Sampler. | Glossary |
| **Bulk** | A third product sample type registered by the Sampler. | Glossary |
| **Packaging Material** | Material registered separately from raw materials with its own receipt ID and sampling flow. | Glossary |
| **COA** | Certificate of Analysis – record of test results for a sample, subject to QC review. | Glossary |
| **QC** | Quality Control | Glossary |
| **GMP** | Good Manufacturing Practice | Glossary |
| **21 CFR Part 11** | US FDA regulation on electronic records and electronic signatures. | Glossary |
| **Annex 11** | EU GMP guideline for computerized systems. | Glossary |
| **ALCOA+** | Data integrity principles (Attributable, Legible, Contemporaneous, Original, Accurate, + Complete, Consistent, Enduring, Available). | Glossary |
| **TBS** | To Be Specified – requirement not yet confirmed; awaiting stakeholder decision. | Charter |

### 1.4 References
| Document | Reference |
|----------|-----------|
| 00_Project_Charter.md | Charter |
| 01_Glossary.md | Glossary |
| 02_BRD.md | Business Requirements Document |
| 03_PRD.md | Product Requirements Document |
| 04_UseCases.md | Use Cases |
| 05_User_Roles_and_Permissions.md | Roles & Permissions |
| Prototype `pharma-prototype-v3.html` | Source of business workflow |
| IEEE Std 830-1998 (R2009) | IEEE Recommended Practice for Software Requirements Specifications |
| ISO/IEC/IEEE 29148:2018 | Systems and software engineering – Life cycle processes – Requirements engineering |
| 21 CFR Part 11 | Electronic Records; Electronic Signatures |
| EU GMP Annex 11 | Computerised Systems |

### 1.5 Overview
The remainder of this SRS describes:
- **Section 2** – Overall description, including product perspective, user characteristics, and constraints.
- **Section 3** – Detailed functional and non‑functional requirements, organised by system component.
- **Section 4** – Appendices with supporting specifications (ID formats, state diagrams, data model, traceability).

---

## 2. Overall Description

### 2.1 Product Perspective
The RM-RRS is a new, greenfield system designed to replace manual paper‑based tracking. It is composed of four separate frontend applications (React) and one backend API (Django REST Framework) that share a common database and platform services. All applications rely on the **Access Control Layer** for authentication, authorisation, audit, and e‑signature.

**System Context Diagram**
```
┌─────────────────────────────────────────────────────────────────┐
│                    ACCESS CONTROL LAYER                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────┐   │
│  │   AuthN     │  │   AuthZ     │  │  Audit      │  │ E-Sig │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  STOREKEEPER    │  │    SAMPLER      │  │    ANALYST      │
│  • Materials    │  │ • Sampling Req. │  │ • Samples       │
│  • Packaging    │  │ • Sample Hist.  │  │ • COA Creation  │
│  • Req. Sampling│  │ • Product Reg.  │  │ • Certificates  │
│  • Notifications│  │ • Prod. History │  │ • Monograph(TBS)│
│  • Release Label│  │ • Label Reprint │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
                    ┌─────────────────────┐
                    │  QC MANAGER         │
                    │  • COA Review       │
                    │  • Approve/Reject   │
                    │  • Release Material │
                    │  • Release Label    │
                    └─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  ADMIN CONSOLE      │
                    │  • Employee Mgmt    │
                    │  • Role Assignment  │
                    │  • Audit Trail View │
                    └─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  SHARED DATABASE    │
                    │  (PostgreSQL)       │
                    │  • Business tables  │
                    │  • Audit logs       │
                    │  • E‑Sig records    │
                    └─────────────────────┘
```

### 2.2 User Characteristics
| User Class | Technical Expertise | Frequency | Primary Tasks |
|------------|---------------------|-----------|---------------|
| Storekeeper | Low to medium | Daily | Register materials, request sampling, handle notifications, print labels |
| Sampler | Low to medium | Daily | Perform sampling, register product samples, reprint labels |
| Analyst | Medium to high | Daily | Test samples, create COAs, manage certificates, (future) monographs |
| QC Manager | Medium to high | Daily | Review COAs, approve/reject, release materials |
| Administrator | High | Weekly/Monthly | Manage employees, roles, audit trail review |

### 2.3 Operating Environment
| Component | Environment |
|-----------|-------------|
| Backend | Linux container (Docker), Python 3.11+, Django 4+, DRF |
| Frontend | Modern browsers (Chrome ≥110, Firefox ≥110, Edge ≥110, Safari ≥15) |
| Database | PostgreSQL 15+ |
| Cache/Message Broker | Redis 7+ |
| Web Server | Nginx (reverse proxy) |
| Container Orchestration | Docker Compose (development and production) |

### 2.4 Design and Implementation Constraints
| Constraint | Source | Status |
|------------|--------|--------|
| Backend must use Django + Django REST Framework | Charter §7 | Confirmed |
| Frontend must use React + React Router + React Query + Axios | Charter §7 | Confirmed |
| Architect as four separate business applications | Charter §7 | Confirmed |
| Support GMP electronic records (audit trails, e‑signatures) | Charter §7 | Confirmed |
| Containerise with Docker; deploy via Docker Compose | Charter §7 | Confirmed |
| No external identity provider; internal employee management | Charter §6 (TBS) | TBS |
| Frontend UI framework (MUI or Ant Design) | Charter §6 | TBS |
| SPAs vs unified shell | Charter §6 | TBS |

### 2.5 Assumptions and Dependencies
**Assumptions**
- The four business applications will share a single database instance.
- The system will operate in a controlled environment with stable network connectivity.
- Employees have individual user accounts; no shared accounts will be used.
- The organisation will provide a suitable Nginx reverse proxy for production deployment.
- The prototype workflow is fully representative of business needs for the MVP.

**Dependencies**
- PostgreSQL and Redis services must be available for the backend.
- The organisation's certificate infrastructure (for HTTPS) will be in place.
- Regulatory classification (21 CFR Part 11 / Annex 11) is confirmed; validation scope will be defined later.

---

## 3. Specific Requirements

### 3.1 Functional Requirements

The functional requirements are organised by system component. Each requirement is identified by a unique code (e.g., **FR‑ACL‑001**) and includes: description, preconditions, postconditions, business rules, and traceability to source documents. All confirmed requirements are marked **[Confirmed]** ; items still open are marked **[TBS]** .

#### 3.1.1 Access Control Layer

| ID | Requirement | Source | Status |
|----|-------------|--------|--------|
| **FR‑ACL‑001** | **Authentication** – The system shall authenticate employees using a username and password combination. Credentials shall be transmitted over HTTPS. | Clarification | Confirmed |
| **FR‑ACL‑002** | **Role‑Based Routing** – Immediately after successful authentication, the system shall redirect the employee to the dashboard of the application that corresponds to their assigned job role. No role selection screen shall be presented. | Clarification, PRD F10 | Confirmed |
| **FR‑ACL‑003** | **Permission Enforcement** – The system shall enforce role‑based permissions at both the API and UI layers. Employees shall not be able to view or access any page, action, or data element outside their granted permissions. | Clarification, BR6 | Confirmed |
| **FR‑ACL‑004** | **Employee Management** – An Administrator shall be able to create, edit, and deactivate employee records. Each employee shall be assigned exactly one job role at a time. | Clarification, UC‑014 | Confirmed |
| **FR‑ACL‑005** | **Audit Trail** – For every create, update, or delete operation performed on any GMP‑relevant record (Material, Packaging, Sample, COA), the system shall create an immutable audit trail entry containing: user ID, timestamp, action type, old value (JSON), new value (JSON), and an optional reason field when applicable. Audit entries shall be append‑only and never modifiable. | Clarification, BR7 | Confirmed |
| **FR‑ACL‑006** | **Electronic Signature** – For every GMP‑significant decision (e.g., QC release, COA approval/rejection), the system shall create a structured electronic signature record that includes: signer user ID, meaning of the signature (e.g., "Approve COA", "Release Material"), timestamp, cryptographic hash or reference to the record being signed, reason (optional), and signature status (e.g., "executed"). | Clarification, BR8 | Confirmed |
| **FR‑ACL‑007** | **Session Management** – The system shall enforce session timeout (default 30 minutes) and require re‑authentication for sensitive actions (scope of sensitive actions TBS). | Charter §6 | TBS |
| **FR‑ACL‑008** | **Password Policy** – The system shall enforce minimum password complexity requirements (length, character classes) and password expiration intervals (TBS). | Charter §6 | TBS |

#### 3.1.2 Storekeeper Application

| ID | Requirement | Source | Status |
|----|-------------|--------|--------|
| **FR‑SK‑001** | **Register Raw Material** – The Storekeeper shall be able to register a received raw material lot. Required fields: Material Name, Supplier, Supplier Batch No., Expiry Date, Receipt Date, Received By. Optional fields: Category, Manufacturer, Country of Origin, Mfg Date, Batch Size, Unit, Package Type, No. of Packages, Package Size, Warehouse, Location, PO No., Invoice No. Total Quantity shall be auto‑calculated as No. of Packages × Package Size if both are provided. Receipt ID is auto‑generated: `RCV‑YYYY‑####`. Receipt Date defaults to today. Material status = Quarantine; Sampling Status = Not Sampled. | Prototype, UC‑001 | Confirmed |
| **FR‑SK‑002** | **Register Packaging Material** – The Storekeeper shall be able to register a received packaging material lot. Required fields: Name, Quantity, Supplier, Receipt Date, Recipient. Type must be selected from: Primary, Secondary, Tertiary, Labelling, Other. Optional: Description, Unit, PO No., Warehouse, Notes. Receipt ID auto‑generated: `PKG‑YYYY‑####`. Receipt Date defaults to today. | Prototype, UC‑002 | Confirmed |
| **FR‑SK‑003** | **View Raw Materials Table** – The Storekeeper shall view a paginated, searchable, filterable table of all raw materials. Columns: Receipt ID, Material Name (with Category sub‑label), Supplier Batch No., Receiving Date, Total Qty, Status, Sampling Status, Expire Date, Actions (View, Request Sampling, Release Label). Search by any field; filters by status and sampling status. | Prototype, PRD F1 | Confirmed |
| **FR‑SK‑004** | **View Packaging Table** – The Storekeeper shall view a table of all packaging materials with columns: Receipt ID, Name, Type, Description, Qty, Unit, Supplier, Receipt Date, Recipient, Warehouse, Sampling Status, Actions (View, Request Sampling). | Prototype, UC‑002 | Confirmed |
| **FR‑SK‑005** | **Request Sampling (Raw Material)** – The Storekeeper shall be able to request sampling on a raw material whose Sampling Status = Not Sampled. Upon confirmation, Sampling Status becomes Sampling Requested. The material appears in the Sampler's pending queue. | Prototype, UC‑003 | Confirmed |
| **FR‑SK‑006** | **Request Sampling (Packaging)** – The Storekeeper shall be able to request sampling on a packaging material (Sampling Status = Not Sampled or null). The system shall create a Packaging Sample record with sample type "Packaging" and set its testing status to Not Tested. The sample appears in the Sampler's pending queue and the Analyst's worklist. | Prototype, UC‑003 | Confirmed |
| **FR‑SK‑007** | **Notifications** – The Storekeeper shall receive notifications when a material is released by the QC Manager. Each notification shall include: Material Name, Receipt ID, QC Number, Retest Date. Notifications shall be dismissible individually. A bell icon with a red dot shall indicate unread notifications. | Prototype, UC‑012 | Confirmed |
| **FR‑SK‑008** | **Release Label** – The Storekeeper shall be able to view and print a Release Label for any material with status = Released. The label shall contain: Receipt ID, Material Name, Batch No., Batch Size, Supplier, Mfg Date, Exp Date, Container No., QC Number, Storage Condition, Retest Date, QC Signature, Release Date. | Prototype, UC‑011 | Confirmed |
| **FR‑SK‑009** | **Dashboard Statistics** – The Storekeeper dashboard shall display live statistics: Total Materials, In Quarantine, Sampling Requested, Released. | Prototype | Confirmed |

#### 3.1.3 Sampler Application

| ID | Requirement | Source | Status |
|----|-------------|--------|--------|
| **FR‑SM‑001** | **View Sampling Requests** – The Sampler shall view a table of materials with Sampling Status = Sampling Requested. A prominent pending counter shows the total count. Filters: Pending Only (default) and View All. Search by material name, receipt ID, or batch. | Prototype, UC‑003 | Confirmed |
| **FR‑SM‑002** | **Record Sample** – The Sampler shall record a sampling event on a requested material. Required fields: Sample Size, No. of Containers Sampled, Sampler Name, Storage Condition (Ambient / Refrigerated / Frozen / Protected from Light / CRT), Sampling Date. Sample ID is auto‑filled as the Receipt ID (for raw materials). Upon save: Sampling Status = Sampled; a Sample record is created with Testing Status = Not Tested; the sample appears in the Analyst's worklist. | Prototype, UC‑004 | Confirmed |
| **FR‑SM‑003** | **Sampling Label Generation** – Immediately after saving a sample, the system shall preview two printable labels: QC Sample Label (green header) and Sampled Container Label (blue header). Both labels shall include sample data; re‑printing is available from Sample History. | Prototype, UC‑010 | Confirmed |
| **FR‑SM‑004** | **Sample History** – The Sampler shall view a searchable history of all recorded raw material and packaging samples. Columns: Sample ID, Material Name, Receipt ID, Supplier Batch, Sample Size, Containers, Sampler, Sampling Date, Storage Condition. Each row shall have a "Print Labels" action to reprint the two labels. | Prototype, UC‑010 | Confirmed |
| **FR‑SM‑005** | **Register Product Sample** – The Sampler shall register Finished Product (FP), Semi‑Finished Product (SFP), and Bulk samples directly. Required fields: Product Name, Batch No., Batch Size, Quantity of Sample, Sampling Date, Time of Sampling. Optional: Mfg Date, Exp Date, Unit, and stage checkboxes (Export to, Local Market, UPA, F.M.A, For Toll) with conditional text fields. Sample ID is auto‑generated with type prefixes: `FP‑YYYY‑####`, `SFP‑YYYY‑####`, `BLK‑YYYY‑####`. Testing Status = Not Tested. The sample appears in Product Sample History and the Analyst's worklist. | Prototype, UC‑005 | Confirmed |
| **FR‑SM‑006** | **Product Sample History** – The Sampler shall view a searchable, filterable table of all product samples (FP/SFP/Bulk). Columns: Sample ID, Product Name, Type (badge), Batch No., Batch Size, Sample Qty, Mfg Date, Exp Date, Sampling Date, Sampler, Testing Status. Filter by product type. | Prototype, UC‑005 | Confirmed |

#### 3.1.4 Analyst Application

| ID | Requirement | Source | Status |
|----|-------------|--------|--------|
| **FR‑AN‑001** | **Home Launcher** – The Analyst home screen shall display three cards: Monograph (stub), Samples, Certificates. Each card shows a live badge count (number of pending samples, total COAs). | Prototype | Confirmed |
| **FR‑AN‑002** | **Combined Samples Worklist** – The Analyst shall view a unified, paginated, searchable, and filterable worklist combining raw material samples, packaging samples, and product samples (FP/SFP/Bulk). Columns: Receipt ID, Material Name (with type tag for product/packaging), Supplier Batch, Receipt Date, Sample Qty, Container No., Sampling Date, Sampler, Expire Date, Testing Status, Actions. Filter by Testing Status. | Prototype, PRD F6 | Confirmed |
| **FR‑AN‑003** | **Start Testing / Create COA** – The Analyst shall start testing on any sample (Testing Status = Not Tested or In Testing). The system shall auto‑fill the COA form with all available material/sample data: Sample Name, Batch No., Batch Size, Supplier, Manufacturer, Mfg Date, Exp Date, Received Date. The Analyst must enter: Specs Code, Reference (BP/USP/EP/JP/In‑House), Analyst Name, Analysis Date (defaults to today), and optional Remarks. Upon submission, a COA is created with status = Draft, and the sample's Testing Status becomes Completed. | Prototype, UC‑006 | Confirmed |
| **FR‑AN‑004** | **COA Status Workflow** – The Analyst shall advance a COA through statuses: Draft → In Progress → Completed. Each transition triggers an audit trail entry. When status becomes Completed, the COA becomes visible to the QC Manager for review. | Prototype, UC‑006 | Confirmed |
| **FR‑AN‑005** | **View Certificates List** – The Analyst shall view a list of all COAs with columns: Receipt ID, Sample Name, Batch No., Analyst, Created Date, Status (badge), View action. Search and filter by status. | Prototype, PRD F6 | Confirmed |
| **FR‑AN‑006** | **Monograph Entry (Stub)** – The Analyst navigation shall include a "Monograph" entry point. The full monograph management functionality is not yet defined; the MVP shall show a placeholder screen with a "coming soon" message. | Prototype | TBS (full module) |

#### 3.1.5 QC Manager Application

| ID | Requirement | Source | Status |
|----|-------------|--------|--------|
| **FR‑QC‑001** | **COA Review Dashboard** – The QC Manager shall view a list of all COAs with columns: Receipt ID, Sample Name, Batch No., Analyst, Created Date, Status, View action. Search and filter by status. | Prototype, UC‑007 | Confirmed |
| **FR‑QC‑002** | **View COA** – The QC Manager shall open a COA detail view showing all material/sample data, analyst data, status badge, and QC Manager comment field. | Prototype | Confirmed |
| **FR‑QC‑003** | **Approve COA** – For a COA with status = Completed, the QC Manager may approve it. Upon approval: COA status → Approved; the system records the approval with an e‑signature (per FR‑ACL‑006). If the COA is linked to a Raw Material (materialId exists), the system shall immediately open the Release Material modal (FR‑QC‑005). | Prototype, UC‑007 | Confirmed |
| **FR‑QC‑004** | **Reject COA** – For a COA with status = Completed, the QC Manager may reject it. Upon rejection: COA status → Rejected; the system records the rejection with an e‑signature. If the COA is linked to a Raw Material, the material's status becomes Rejected. | Prototype, UC‑009 | Confirmed |
| **FR‑QC‑005** | **Release Raw Material** – After COA approval, the QC Manager shall release the associated Raw Material by providing: QC Number (auto‑suggested `QC‑YYYY‑####`, editable), QC Signature (free text). The Retest Date is auto‑calculated as Release Date + 1 year (displayed, read‑only). Upon submission: material status → Released; QC Number, QC Signature, Retest Date, and Release Date are stored; the Storekeeper receives a notification. The Release Label becomes available. | Prototype, UC‑008 | Confirmed |
| **FR‑QC‑006** | **Release Label (QC Manager)** – The QC Manager shall have the same Release Label view/print capability as the Storekeeper (FR‑SK‑008) for materials that were released. | Prototype, UC‑011 | Confirmed |
| **FR‑QC‑007** | **QC Manager Comments** – The QC Manager may add free‑text comments when approving or rejecting a COA; comments are stored with the COA record. | Prototype, UC‑007/009 | Confirmed |

#### 3.1.6 Administrator Console

| ID | Requirement | Source | Status |
|----|-------------|--------|--------|
| **FR‑AD‑001** | **Create Employee** – The Administrator shall create an employee record with fields: Username (unique), Password (hashed), Full Name, Email (optional), Job Role (drop‑down of Storekeeper, Sampler, Analyst, QC Manager). | Clarification, UC‑014 | Confirmed |
| **FR‑AD‑002** | **Edit Employee** – The Administrator shall edit employee details, including changing the Job Role. | Clarification | Confirmed |
| **FR‑AD‑003** | **Deactivate Employee** – The Administrator shall deactivate an employee, preventing them from logging in. | Clarification | Confirmed |
| **FR‑AD‑004** | **View Audit Trail** – The Administrator shall view the full audit trail with search and filtering by user, date, entity type. | Clarification | Confirmed |
| **FR‑AD‑005** | **Role Management** – The Administrator shall view the current role definitions and permissions (read‑only). Modifying permissions is TBS. | Clarification | TBS |

---

### 3.2 External Interface Requirements

#### 3.2.1 User Interfaces
The system shall provide responsive web‑based interfaces tailored to each role, as specified in the prototype and PRD. All interfaces shall:
- Use the selected UI framework (MUI or Ant Design – TBS).
- Support modern browsers (Chrome, Firefox, Edge, Safari).
- Be accessible (WCAG 2.1 Level AA compliance – TBS).
- Present labels, status badges, and icons consistent with the prototype's visual design.

#### 3.2.2 Software Interfaces
| Interface | Description | Protocol |
|-----------|-------------|----------|
| Frontend ↔ Backend API | All business operations performed via RESTful API over HTTPS. | HTTPS / JSON |
| Backend ↔ PostgreSQL | Persistent data storage using Django ORM. | TCP/IP |
| Backend ↔ Redis | Session storage, Celery broker, caching. | TCP/IP |
| Backend ↔ Celery | Asynchronous tasks (notifications, audit logging). | AMQP (via Redis) |
| Frontend ↔ Browser Print API | Print labels using `window.print()`. | Browser API |

#### 3.2.3 Communication Interfaces
- All external communications shall be encrypted using TLS 1.2 or higher.
- The system shall expose only the necessary ports (80/443 for web, with Nginx as reverse proxy).
- Internal communication between containers shall be over a secured Docker network.

---

### 3.3 Non‑Functional Requirements

#### 3.3.1 Performance
| ID | Requirement | Target | Status |
|----|-------------|--------|--------|
| **NFR‑PERF‑001** | API response time (95th percentile) | < 500 ms for typical operations | Confirmed |
| **NFR‑PERF‑002** | Concurrent users per application | 10 users (initial), scalable to 50 | Confirmed |
| **NFR‑PERF‑003** | Page load time (first contentful paint) | < 2 seconds on typical network | TBS |
| **NFR‑PERF‑004** | Database query performance | All queries with < 100ms execution for indexed lookups | TBS |

#### 3.3.2 Security
| ID | Requirement | Target | Status |
|----|-------------|--------|--------|
| **NFR‑SEC‑001** | Transport encryption | TLS 1.2+ mandatory for all traffic | Confirmed |
| **NFR‑SEC‑002** | Password hashing | bcrypt (or Django's default PBKDF2) with sufficient iteration count | Confirmed |
| **NFR‑SEC‑003** | Session timeout | 30 minutes of inactivity | Confirmed |
| **NFR‑SEC‑004** | Brute‑force protection | Account lockout after N failed attempts (N TBS) | TBS |
| **NFR‑SEC‑005** | MFA | Multi‑factor authentication | TBS |
| **NFR‑SEC‑006** | Audit logging of security events | Login attempts, privilege changes, access denials | TBS |

#### 3.3.3 Audit and Compliance
| ID | Requirement | Target | Status |
|----|-------------|--------|--------|
| **NFR‑AUD‑001** | Immutable audit trail | Append‑only, time‑stamped, user‑attributable | Confirmed |
| **NFR‑AUD‑002** | Electronic signature records | Structured records with meaning, timestamp, hash, status | Confirmed |
| **NFR‑AUD‑003** | Record retention | 7 years minimum (per GMP) | Confirmed |
| **NFR‑AUD‑004** | Time synchronisation | All servers must synchronise with NTP | TBS |
| **NFR‑AUD‑005** | ALCOA+ compliance | System design must support ALCOA+ principles | Confirmed (as target) |

#### 3.3.4 Reliability and Availability
| ID | Requirement | Target | Status |
|----|-------------|--------|--------|
| **NFR‑REL‑001** | System availability | 99.5% uptime (excluding planned maintenance) | Confirmed |
| **NFR‑REL‑002** | Data backup | Daily automated backups, off‑site storage | TBS |
| **NFR‑REL‑003** | Disaster recovery | RPO ≤ 1 hour, RTO ≤ 4 hours (TBS) | TBS |
| **NFR‑REL‑004** | Graceful degradation | Error handling with user‑friendly messages | Confirmed |

#### 3.3.5 Usability
| ID | Requirement | Target | Status |
|----|-------------|--------|--------|
| **NFR‑US‑001** | Role‑specific views | Each role sees only its own app pages/actions | Confirmed |
| **NFR‑US‑002** | Consistent navigation | Top bar, tabs, breadcrumbs (if applicable) per prototype | Confirmed |
| **NFR‑US‑003** | Responsive design | Works on desktop (primary) and tablet (secondary) | TBS |
| **NFR‑US‑004** | Help/documentation | User help accessible within the app (TBS) | TBS |

#### 3.3.6 Maintainability
| ID | Requirement | Target | Status |
|----|-------------|--------|--------|
| **NFR‑MAINT‑001** | Code modularity | Separation of concerns (Django DRF, React components) | Confirmed |
| **NFR‑MAINT‑002** | Logging | Structured logging (JSON) for all services | TBS |
| **NFR‑MAINT‑003** | Monitoring | Health checks, metrics collection (e.g., Prometheus) | TBS |

---

### 3.4 Data Requirements

#### 3.4.1 Data Entities
The system shall manage the following primary data entities (full schema details in Appendix C):

| Entity | Description | Key Attributes |
|--------|-------------|----------------|
| **Employee** | System user | Username, password_hash, full_name, email, job_role, is_active |
| **Material** | Raw material lot | receipt_id, material_name, supplier, supplier_batch, exp_date, status, sampling_status, qc_number, etc. |
| **Packaging** | Packaging material lot | receipt_id (PKG‑...), name, type, qty, supplier, recipient, sampling_status |
| **Sample** | Raw material / packaging sample | sample_id (=receipt_id for RM), material_id, sample_size, containers, sampler, storage, sampling_date, testing_status |
| **FPSample** | Product sample (FP/SFP/Bulk) | sample_id (FP‑...), product_name, product_type, batch_no, batch_size, sample_size, stages, testing_status |
| **COA** | Certificate of Analysis | id (COA‑...), sample_id, sample_name, batch_no, specs_code, reference, analyst, status, qc_comment |
| **Notification** | In‑app notification | target_role, title, message, read_status, created_at |
| **AuditLog** | Immutable audit entry | user_id, timestamp, action, entity_type, entity_id, old_value, new_value, reason |
| **ElectronicSignature** | Structured e‑signature record | user_id, timestamp, meaning, record_reference, hash, reason, status |

#### 3.4.2 Data Integrity
- All primary keys are UUID or auto‑incrementing integers.
- Foreign keys enforce referential integrity (cascade deletions restricted).
- Unique constraints on `employee.username`, `material.receipt_id`, `packaging.receipt_id`, `coa.id`.
- Date/time fields use UTC.
- Audit logs are never updated or deleted.

#### 3.4.3 Data Retention
- Business records (Materials, Samples, COAs) shall be retained for 7 years after the associated batch expiry date or release date, whichever is longer.
- Audit logs shall be retained for 10 years.
- Notifications older than 90 days may be automatically purged.

---

## 4. Appendices

### A. ID Generation Specifications

| Entity | Format | Example |
|--------|--------|---------|
| Raw Material Receipt | `RCV‑YYYY‑####` (counter resets yearly) | RCV-2025-0001 |
| Packaging Receipt | `PKG‑YYYY‑####` | PKG-2025-0001 |
| Packaging Sample | `PKG‑SMP‑YYYY‑####` | PKG-SMP-2025-0001 |
| Finished Product Sample | `FP‑YYYY‑####` | FP-2025-0001 |
| Semi‑Finished Product Sample | `SFP‑YYYY‑####` | SFP-2025-0001 |
| Bulk Sample | `BLK‑YYYY‑####` | BLK-2025-0001 |
| COA | `COA‑YYYY‑####` | COA-2025-0001 |
| QC Release Number | `QC‑YYYY‑####` (suggested, editable) | QC-2025-0001 |

### B. State Transition Diagrams

**Material Status**
```
[Quarantine] --(QC Release)--> [Released]
[Quarantine] --(QC Reject)----> [Rejected]
```

**Sampling Status**
```
[Not Sampled] --(Request)--> [Sampling Requested] --(Sample)--> [Sampled]
```

**COA Status**
```
[Draft] --(Submit)--> [In Progress] --(Complete)--> [Completed]
                                                     |
                                       (Approve)     |     (Reject)
                                          ▼          |          ▼
                                      [Approved]     |      [Rejected]
```

**Product Sample Testing Status**
```
[Not Tested] --(Start)--> [In Testing] --(Complete)--> [Completed]
```

### C. Data Model Summary

A high‑level entity‑relationship diagram is provided below. Full schema specifications will be detailed in the Database Design document (`10_Database.md`).

```
Employee ──┬─── has one JobRole
           │
           ├── creates/updates ──┬── Material
           │                     ├── Packaging
           │                     ├── Sample
           │                     ├── FPSample
           │                     └── COA
           │
           ├── generates ── AuditLog
           └── generates ── ElectronicSignature

Material ── has many ── Sample (one per sampling event)
Sample ── has one ── COA (through analyst creation)
FPSample ── has one ── COA (through analyst creation)
Packaging ── has many ── Sample (one per sampling request)

Notification ── owned by ── Storekeeper (target role)
```

### D. Traceability Matrix

| Requirement ID | Source Document | Section |
|----------------|-----------------|---------|
| FR‑ACL‑001 | Charter §7, Clarification | Authentication |
| FR‑ACL‑002 | Clarification, PRD F10 | Routing |
| FR‑ACL‑003 | BR6 | Permissions |
| FR‑ACL‑004 | Clarification, UC‑014 | Admin |
| FR‑ACL‑005 | BR7 | Audit |
| FR‑ACL‑006 | BR8 | E‑Sig |
| FR‑SK‑001 | Prototype, UC‑001 | Register RM |
| FR‑SK‑002 | Prototype, UC‑002 | Register Packaging |
| FR‑SK‑003 | Prototype, PRD F1 | View RM |
| FR‑SK‑004 | Prototype, UC‑002 | View Packaging |
| FR‑SK‑005 | Prototype, UC‑003 | Request Sampling RM |
| FR‑SK‑006 | Prototype, UC‑003 | Request Sampling Pkg |
| FR‑SK‑007 | Prototype, UC‑012 | Notifications |
| FR‑SK‑008 | Prototype, UC‑011 | Release Label |
| FR‑SM‑001 | Prototype, UC‑003 | Sampling Requests |
| FR‑SM‑002 | Prototype, UC‑004 | Record Sample |
| FR‑SM‑003 | Prototype, UC‑010 | Labels |
| FR‑SM‑004 | Prototype, UC‑010 | History |
| FR‑SM‑005 | Prototype, UC‑005 | Register Product |
| FR‑SM‑006 | Prototype, UC‑005 | Product History |
| FR‑AN‑001 | Prototype | Launcher |
| FR‑AN‑002 | Prototype, PRD F6 | Worklist |
| FR‑AN‑003 | Prototype, UC‑006 | COA Creation |
| FR‑AN‑004 | Prototype, UC‑006 | COA Workflow |
| FR‑AN‑005 | Prototype, PRD F6 | Certificates |
| FR‑QC‑001 | Prototype, UC‑007 | Dashboard |
| FR‑QC‑002 | Prototype | View COA |
| FR‑QC‑003 | Prototype, UC‑007 | Approve |
| FR‑QC‑004 | Prototype, UC‑009 | Reject |
| FR‑QC‑005 | Prototype, UC‑008 | Release |
| FR‑QC‑006 | Prototype, UC‑011 | Label (QC) |
| FR‑AD‑001 | Clarification, UC‑014 | Create Employee |

---

**Document Approval**

| Role | Name | Date |
|------|------|------|
| Author | [***Ahmed Abdullah***] | [22/7/2026] |
| Reviewer (Product) | [Name] | [Date] |
| Reviewer (QA/Compliance) | [Name] | [Date] |
| Approver | [Name] | [Date] |

---

**Change History**

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | [22/7/2026] | [***Ahmed Abdullah***] | Initial baseline from confirmed Charter, BRD, PRD, Use Cases, Roles & Permissions |
