# 07 — Non‑Functional Requirements (NFR)

**Document Identifier:** RM-RRS-NFR-001  
**Version:** 1.0  
**Status:** Baseline  
**Traces to:** Project Charter, BRD, SRS  
**Compliance Reference:** ISO/IEC 25010:2011 (Systems and software Quality Requirements and Evaluation – System and software quality models), IEEE Std 830-1998  

---

## Table of Contents

1. [Introduction](#1-introduction)  
   1.1 [Purpose](#11-purpose)  
   1.2 [Scope](#12-scope)  
   1.3 [References](#13-references)  

2. [Quality Attributes and Requirements](#2-quality-attributes-and-requirements)  
   2.1 [Performance](#21-performance)  
   2.2 [Security](#22-security)  
   2.3 [Reliability and Availability](#23-reliability-and-availability)  
   2.4 [Usability](#24-usability)  
   2.5 [Maintainability](#25-maintainability)  
   2.6 [Portability](#26-portability)  
   2.7 [Scalability](#27-scalability)  
   2.8 [Data Management](#28-data-management)  
   2.9 [Audit and Compliance (NFR perspective)](#29-audit-and-compliance-nfr-perspective)  

3. [Compliance and Regulatory Requirements](#3-compliance-and-regulatory-requirements)  

4. [Appendices](#4-appendices)  
   A. [Traceability Matrix](#a-traceability-matrix)  
   B. [Performance Metrics and Monitoring](#b-performance-metrics-and-monitoring)  

---

## 1. Introduction

### 1.1 Purpose
This document defines the **Non‑Functional Requirements (NFR)** for the Raw Material Receiving & Release System (RM‑RRS). These requirements describe the system’s quality attributes – including performance, security, reliability, usability, maintainability, and compliance – that are critical to successful operation in a GMP‑regulated pharmaceutical environment. They complement the functional requirements specified in the SRS and serve as the basis for design, implementation, and validation.

### 1.2 Scope
This NFR document applies to all components of the RM‑RRS: the four role‑specific applications (Storekeeper, Sampler, Analyst, QC Manager), the Access Control Layer, the shared database, and all supporting infrastructure. It covers both operational and developmental quality attributes, and where applicable, references industry standards for software quality.

### 1.3 References
| Document | Reference |
|----------|-----------|
| 00_Project_Charter.md | Charter |
| 02_BRD.md | Business Requirements Document |
| 06_SRS.md | Software Requirements Specification |
| ISO/IEC 25010:2011 | Systems and software engineering – Systems and software Quality Requirements and Evaluation (SQuaRE) – System and software quality models |
| IEEE Std 830-1998 | IEEE Recommended Practice for Software Requirements Specifications |
| 21 CFR Part 11 | Electronic Records; Electronic Signatures |
| EU GMP Annex 11 | Computerised Systems |
| ISO 27001 | Information Security Management (informative) |

---

## 2. Quality Attributes and Requirements

Each requirement is assigned a unique ID, a priority (High/Medium/Low), and a status (Confirmed/TBS). The priority reflects business criticality for MVP delivery.

### 2.1 Performance

| ID | Requirement | Target / Metric | Priority | Status |
|----|-------------|-----------------|----------|--------|
| **NFR-PERF-001** | API response time (95th percentile) | < 500 ms for typical CRUD operations (view, register, update) | High | Confirmed |
| **NFR-PERF-002** | API response time (95th percentile) for complex queries | < 1.5 s for search/filter on large datasets (e.g., combined sample list with > 1000 records) | Medium | Confirmed |
| **NFR-PERF-003** | Concurrent users per application | Support at least 10 concurrent users without degradation; target 50 concurrent users as scalability goal | High | Confirmed |
| **NFR-PERF-004** | Page load time (First Contentful Paint) | < 2 seconds on standard corporate network (10 Mbps) | Medium | TBS |
| **NFR-PERF-005** | Database query performance | All queries must execute within 100 ms on indexed lookups; complex joins < 500 ms | High | Confirmed |
| **NFR-PERF-006** | Batch/background task performance | Notifications and audit trail logging must not delay user‑facing operations; asynchronous processing must complete within 5 seconds of trigger | Medium | Confirmed |
| **NFR-PERF-007** | Label printing performance | Label preview and print initiation must complete within 2 seconds | Low | Confirmed |

### 2.2 Security

| ID | Requirement | Target / Metric | Priority | Status |
|----|-------------|-----------------|----------|--------|
| **NFR-SEC-001** | Transport encryption | All network traffic (frontend‑backend, backend‑database) must use TLS 1.2 or higher. | High | Confirmed |
| **NFR-SEC-002** | Password storage | Passwords must be hashed using bcrypt (cost factor ≥ 12) or Django’s PBKDF2 with sufficient iterations. | High | Confirmed |
| **NFR-SEC-003** | Session management | Session timeout: 30 minutes of inactivity; sessions must be invalidated on logout. | High | Confirmed |
| **NFR-SEC-004** | Account lockout | After 5 consecutive failed login attempts, account locked for 15 minutes (configurable). | Medium | TBS |
| **NFR-SEC-005** | Multi‑factor authentication (MFA) | MFA shall be supported (e.g., TOTP) for all users; implementation details TBS. | Medium | TBS |
| **NFR-SEC-006** | Role‑based access control | API endpoints must enforce permission checks; unauthorised requests must return HTTP 403 Forbidden. | High | Confirmed |
| **NFR-SEC-007** | Input validation and sanitisation | All user inputs must be validated and sanitised to prevent injection attacks (SQL, XSS, CSRF). | High | Confirmed |
| **NFR-SEC-008** | Audit logging of security events | Login attempts (success/failure), password changes, role changes, and permission changes must be logged. | High | TBS |
| **NFR-SEC-009** | Least privilege principle | Application service accounts must have only necessary database permissions. | Medium | TBS |

### 2.3 Reliability and Availability

| ID | Requirement | Target / Metric | Priority | Status |
|----|-------------|-----------------|----------|--------|
| **NFR-REL-001** | System availability | 99.5% uptime (≤ 3.65 hours downtime per month) excluding planned maintenance windows. | High | Confirmed |
| **NFR-REL-002** | Data backup | Automated daily backups of the database; backups stored off‑site (or in a separate region). | High | TBS |
| **NFR-REL-003** | Recovery Point Objective (RPO) | ≤ 1 hour (maximum acceptable data loss). | High | TBS |
| **NFR-REL-004** | Recovery Time Objective (RTO) | ≤ 4 hours (maximum acceptable downtime to restore service). | High | TBS |
| **NFR-REL-005** | Graceful degradation | In case of partial system failure (e.g., Redis unavailable), core functionality (viewing data) must remain available; users must receive clear error messages. | Medium | Confirmed |
| **NFR-REL-006** | Error handling | All unhandled exceptions must be caught and logged; end‑users must see a user‑friendly error page (not stack traces). | High | Confirmed |
| **NFR-REL-007** | Health checks | The system must provide a `/health` endpoint for infrastructure monitoring (returns 200 OK when healthy). | Medium | TBS |
| **NFR-REL-008** | Retry mechanism for background tasks | Celery tasks (notifications, audit logs) must have retry logic with exponential backoff on failure. | Medium | TBS |

### 2.4 Usability

| ID | Requirement | Target / Metric | Priority | Status |
|----|-------------|-----------------|----------|--------|
| **NFR-US-001** | Role‑specific views | Each user sees only the navigation, pages, and actions permitted by their role; no role‑specific content may appear outside that role’s app. | High | Confirmed |
| **NFR-US-002** | Consistent UI design | All applications must use the same UI framework (TBS: MUI or Ant Design) and follow a common design system (colours, typography, spacing) as per the prototype. | High | TBS (framework) |
| **NFR-US-003** | Responsive design | The interface must be usable on desktop (primary) and tablet (secondary) screen sizes. | Medium | TBS |
| **NFR-US-004** | Accessibility | System must comply with WCAG 2.1 Level AA (excluding non‑text content that is purely decorative). | Low | TBS |
| **NFR-US-005** | User help and tooltips | Critical fields and actions must have inline help or tooltips explaining their purpose. | Low | TBS |
| **NFR-US-006** | Error messages | Error messages must be clear, actionable, and avoid technical jargon. | Medium | Confirmed |

### 2.5 Maintainability

| ID | Requirement | Target / Metric | Priority | Status |
|----|-------------|-----------------|----------|--------|
| **NFR-MAINT-001** | Code modularity | Backend: Django applications separated by domain (materials, sampling, coa, users). Frontend: components per feature and role. | High | Confirmed |
| **NFR-MAINT-002** | Logging | Structured logging (JSON format) for all backend services; logs must include correlation ID for request tracing. | Medium | TBS |
| **NFR-MAINT-003** | Monitoring and alerting | System metrics (response times, error rates, resource utilisation) must be collected and made visible (e.g., Prometheus + Grafana). | Medium | TBS |
| **NFR-MAINT-004** | Documentation | API documentation (OpenAPI/Swagger) must be auto‑generated and kept up‑to‑date. | High | Confirmed |
| **NFR-MAINT-005** | Test coverage | Unit test coverage ≥ 80% for backend business logic; integration tests for critical workflows. | High | TBS |
| **NFR-MAINT-006** | Database migration | Migration scripts must be version‑controlled and reversible. | High | Confirmed |
| **NFR-MAINT-007** | Environment configuration | All environment‑specific settings must be externalised (environment variables); no hard‑coded secrets. | High | Confirmed |

### 2.6 Portability

| ID | Requirement | Target / Metric | Priority | Status |
|----|-------------|-----------------|----------|--------|
| **NFR-PORT-001** | Containerisation | The entire application stack (Django, React, Nginx, PostgreSQL, Redis) must run in Docker containers. | High | Confirmed |
| **NFR-PORT-002** | Orchestration | Docker Compose must be used for development and production deployment. | High | Confirmed |
| **NFR-PORT-003** | Operating system compatibility | Backend containers must run on Linux (Alpine or Debian‑based); frontend statically built and served via Nginx. | High | Confirmed |
| **NFR-PORT-004** | Database compatibility | PostgreSQL must be used; no vendor‑specific SQL features that cannot be ported to other compliant RDBMS. | Medium | Confirmed |

### 2.7 Scalability

| ID | Requirement | Target / Metric | Priority | Status |
|----|-------------|-----------------|----------|--------|
| **NFR-SCAL-001** | Horizontal scaling | The backend (Django) must be stateless to allow multiple instances behind a load balancer. | Medium | TBS |
| **NFR-SCAL-002** | Database read replicas | For future growth, the design must support read replicas for reporting queries. | Low | TBS |
| **NFR-SCAL-003** | Caching | Frequently accessed data (e.g., reference lists, material names) must be cached (Redis) to reduce database load. | Medium | TBS |

### 2.8 Data Management

| ID | Requirement | Target / Metric | Priority | Status |
|----|-------------|-----------------|----------|--------|
| **NFR-DATA-001** | Data retention | Business records (Materials, Samples, COAs) retained for 7 years after expiry/release; audit logs retained for 10 years. | High | Confirmed |
| **NFR-DATA-002** | Data archival | When retention period expires, data may be archived (exported) and purged with proper approval. | Low | TBS |
| **NFR-DATA-003** | Data backup and recovery | Daily full database backups; point‑in‑time recovery (WAL archiving) for PostgreSQL. | High | TBS |
| **NFR-DATA-004** | Data integrity constraints | Foreign keys, uniqueness, and check constraints enforced at the database level. | High | Confirmed |
| **NFR-DATA-005** | Audit trail immutability | Audit log records must never be updated or deleted; any modification attempt must be prevented. | High | Confirmed |
| **NFR-DATA-006** | Time synchronisation | All servers must synchronise with a reliable NTP source to ensure accurate timestamps. | High | TBS |

### 2.9 Audit and Compliance (NFR Perspective)

| ID | Requirement | Target / Metric | Priority | Status |
|----|-------------|-----------------|----------|--------|
| **NFR-COMP-001** | Electronic signature compliance | Signatures must meet 21 CFR Part 11 and Annex 11 requirements: content (meaning, timestamp, signer, hash) and integrity (cryptographic binding). | High | Confirmed |
| **NFR-COMP-002** | Audit trail completeness | Every create/update/delete on GMP‑relevant records must be recorded; no blind spots. | High | Confirmed |
| **NFR-COMP-003** | Record authenticity | Each record must be attributable to its author; no anonymous changes. | High | Confirmed |
| **NFR-COMP-004** | System validation support | The system must be designed to facilitate IQ/OQ/PQ; validation documentation must be prepared. | High | TBS (scope TBS) |
| **NFR-COMP-005** | ALCOA+ adherence | The system design must explicitly support Attributable, Legible, Contemporaneous, Original, Accurate, Complete, Consistent, Enduring, and Available data. | High | Confirmed (as target) |

---

## 3. Compliance and Regulatory Requirements

The system must comply with applicable regulatory frameworks:

| Regulation | Applicable Section | Status |
|------------|---------------------|--------|
| **21 CFR Part 11** | Electronic Records; Electronic Signatures | Target compliance; detailed mapping to be documented in 13_Compliance.md |
| **EU GMP Annex 11** | Computerised Systems | Target compliance; similar to Part 11 |
| **Data Protection (GDPR/CCPA)** | Personal data (employee names, possibly email) must be protected; data subject rights (access, deletion) must be supported if applicable. | TBS (depends on jurisdiction) |
| **ISO 27001** | Information security management framework (informative) | TBS |

---

## 4. Appendices

### A. Traceability Matrix

| NFR ID | Source(s) | SRS Reference |
|--------|-----------|---------------|
| NFR-PERF-001 | Charter §7 (implied performance), BRD | SRS §3.3.1 |
| NFR-PERF-002 | BRD (large dataset) | SRS §3.3.1 |
| NFR-PERF-003 | Charter (containerised, 10 users) | SRS §3.3.1 |
| NFR-SEC-001 | Charter §7 (HTTPS) | SRS §3.3.2 |
| NFR-SEC-002 | Industry best practice | SRS §3.3.2 |
| NFR-SEC-003 | SRS FR‑ACL‑007 | SRS §3.1.1 |
| NFR-REL-001 | Business criticality | SRS §3.3.4 |
| NFR-REL-002 | Data protection | SRS §3.4.3 |
| NFR-US-001 | BR6 | SRS §3.3.5 |
| NFR-MAINT-001 | Architectural constraints | SRS §3.3.6 |
| NFR-PORT-001 | Charter §7 | SRS §2.4 |
| NFR-DATA-001 | GMP requirement | SRS §3.4.3 |
| NFR-COMP-001 | BR8 | SRS §3.1.1 |

### B. Performance Metrics and Monitoring

| Metric | Tool/Method | Threshold | Action |
|--------|-------------|-----------|--------|
| API response time (95th percentile) | APM (e.g., New Relic, Prometheus) | > 500 ms | Investigate and optimise |
| Error rate (HTTP 5xx) | Log aggregation | > 1% | Alert on‑call |
| Database connection pool usage | Database monitoring | > 80% | Increase pool size or scale |
| CPU/Memory utilisation | Container metrics | > 85% for 5 min | Scale horizontally |
| Disk usage (data + logs) | System monitoring | > 75% | Archive/purge old logs |
| Queue length (Celery) | Redis monitoring | > 100 tasks pending | Increase workers |

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
| 1.0 | [22/7/2026] | [***Ahmed Abdullah***] | Initial baseline from confirmed requirements; TBS items clearly marked |

---