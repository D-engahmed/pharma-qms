# 08 — Software Architecture Specification (SAS)

**Document Identifier:** RM-RRS-SAS-001  
**Version:** 1.0  
**Status:** Baseline  
**Traces to:** Project Charter, BRD, SRS, NFR  
**Compliance Reference:** ISO/IEC/IEEE 42010:2011 (Systems and software engineering — Architecture description), IEEE Std 1016-2009 (Software Design Descriptions)

---

## Table of Contents

1. [Introduction](#1-introduction)  
   1.1 [Purpose](#11-purpose)  
   1.2 [Scope](#12-scope)  
   1.3 [Definitions and Acronyms](#13-definitions-and-acronyms)  
   1.4 [References](#14-references)  

2. [Architecture Overview](#2-architecture-overview)  
   2.1 [Architectural Style and Principles](#21-architectural-style-and-principles)  
   2.2 [High-Level System Architecture](#22-high-level-system-architecture)  
   2.3 [Component Diagram](#23-component-diagram)  

3. [Architectural Views](#3-architectural-views)  
   3.1 [Logical View](#31-logical-view)  
   3.2 [Process View](#32-process-view)  
   3.3 [Physical View (Deployment)](#33-physical-view-deployment)  
   3.4 [Development View](#34-development-view)  
   3.5 [Operational View](#35-operational-view)  

4. [Architectural Decisions](#4-architectural-decisions)  
   4.1 [Application Separation](#41-application-separation)  
   4.2 [Shared Database vs. Per-App Database](#42-shared-database-vs-per-app-database)  
   4.3 [Access Control Layer as Shared Service](#43-access-control-layer-as-shared-service)  
   4.4 [Audit Trail Implementation](#44-audit-trail-implementation)  
   4.5 [Electronic Signature Implementation](#45-electronic-signature-implementation)  
   4.6 [Asynchronous Processing](#46-asynchronous-processing)  
   4.7 [Frontend Architecture](#47-frontend-architecture)  

5. [Technology Stack](#5-technology-stack)  
   5.1 [Backend Technologies](#51-backend-technologies)  
   5.2 [Frontend Technologies](#52-frontend-technologies)  
   5.3 [Infrastructure Technologies](#53-infrastructure-technologies)  

6. [Cross-Cutting Concerns](#6-cross-cutting-concerns)  
   6.1 [Security](#61-security)  
   6.2 [Audit and Logging](#62-audit-and-logging)  
   6.3 [Error Handling](#63-error-handling)  
   6.4 [Internationalisation](#64-internationalisation)  

7. [Interfaces](#7-interfaces)  
   7.1 [API Design](#71-api-design)  
   7.2 [Internal Service Communication](#72-internal-service-communication)  
   7.3 [External Dependencies](#73-external-dependencies)  

8. [Data Architecture](#8-data-architecture)  
   8.1 [Data Flow](#81-data-flow)  
   8.2 [Data Storage Strategy](#82-data-storage-strategy)  
   8.3 [Data Migration and Versioning](#83-data-migration-and-versioning)  

9. [Quality Attributes](#9-quality-attributes)  
   9.1 [Performance](#91-performance)  
   9.2 [Scalability](#92-scalability)  
   9.3 [Availability](#93-availability)  
   9.4 [Security](#94-security)  
   9.5 [Maintainability](#95-maintainability)  

10. [Appendices](#10-appendices)  
    A. [Technology Rationale](#a-technology-rationale)  
    B. [Architectural Decision Log](#b-architectural-decision-log)  
    C. [Component Inventory](#c-component-inventory)  

---

## 1. Introduction

### 1.1 Purpose
This Software Architecture Specification (SAS) documents the architectural design of the **Raw Material Receiving & Release System (RM-RRS)** . It provides a comprehensive description of the system's structure, components, interfaces, key design decisions, and the rationale behind them. This document serves as the primary reference for developers, architects, quality assurance personnel, and stakeholders, enabling informed design, implementation, and validation activities. The architecture is derived from the functional requirements in the SRS, the non-functional requirements in the NFR, and the constraints established in the Project Charter.

### 1.2 Scope
This SAS covers all components of the RM-RRS:
- **Access Control Layer**: Authentication, authorisation, audit trail, and electronic signature services.
- **Four Business Applications**: Storekeeper, Sampler, Analyst, and QC Manager applications.
- **Administrator Console**: Employee and role management.
- **Shared Data Layer**: PostgreSQL database and Redis cache/message broker.
- **Infrastructure**: Containerisation, deployment, and operational monitoring.

The architecture supports the MVP scope as defined in the PRD and SRS. Full monograph management, release workflow for packaging/product samples, multi-site support, and other TBS features are not covered but can be accommodated by the extensible architectural framework.

### 1.3 Definitions and Acronyms
| Term | Definition |
|------|------------|
| **ACL** | Access Control Layer — shared authentication, authorisation, audit, and signature services |
| **API** | Application Programming Interface |
| **COA** | Certificate of Analysis |
| **CRUD** | Create, Read, Update, Delete |
| **DRF** | Django REST Framework |
| **JWT** | JSON Web Token |
| **RBAC** | Role-Based Access Control |
| **REST** | Representational State Transfer |
| **SPA** | Single Page Application |
| **TBS** | To Be Specified |

### 1.4 References
| Document | Reference |
|----------|-----------|
| 00_Project_Charter.md | Charter |
| 06_SRS.md | Software Requirements Specification |
| 07_NFR.md | Non-Functional Requirements |
| 10_Database.md | Database Schema Specification |
| 11_API.md | API Specification |
| 12_Security.md | Security Specification |
| 13_Compliance.md | Compliance Specification |
| ISO/IEC/IEEE 42010:2011 | Systems and software engineering — Architecture description |
| IEEE Std 1016-2009 | Standard for Information Technology — Systems Design — Software Design Descriptions |
| 12-Factor App | Methodology for building modern, scalable, maintainable software-as-a-service |

---

## 2. Architecture Overview

### 2.1 Architectural Style and Principles

**Architectural Style:** The RM-RRS employs a **Microservices-inspired, multi-application architecture** built on a shared platform. While not a pure microservices deployment (as the backend is a unified Django codebase), the system is architecturally decomposed by **business capability** — each role has its own dedicated frontend application, and backend modules are organised by domain.

**Core Design Principles:**

| Principle | Description |
|-----------|-------------|
| **Separation of Concerns** | Each application and module has a single, well-defined responsibility. |
| **Least Privilege** | Users, services, and applications have only the permissions necessary to perform their functions. |
| **API-First Design** | All frontend applications interact with the backend through a well-defined RESTful API. |
| **Stateless Backend** | The backend is stateless (sessions stored in Redis), enabling horizontal scaling. |
| **Audit by Design** | Audit logging is built into the data access layer, not added as an afterthought. |
| **Immutable Records** | GMP-relevant records are never deleted; status transitions are tracked. |
| **Compliance First** | 21 CFR Part 11 and Annex 11 requirements are considered at every architectural layer. |
| **Containerisation** | All services run in containers for consistency, portability, and reproducibility. |
| **12-Factor App Conformance** | Follows 12-Factor principles: env vars for config, backing services as attached resources, stateless processes, etc. |

### 2.2 High-Level System Architecture

The system is composed of six main logical components:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  PRESENTATION LAYER                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ Storekeeper │  │   Sampler   │  │   Analyst   │  │  QC Manager │  │    Admin    │ │
│  │    App      │  │    App      │  │    App      │  │    App      │  │   Console   │ │
│  │  (React)    │  │  (React)    │  │  (React)    │  │  (React)    │  │  (React)    │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘ │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┼──────────┘
          │                │                │                │                │
          └────────────────┴────────────────┴────────────────┴────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    API GATEWAY                                         │
│                              (Nginx / Django REST API)                                 │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                   BACKEND SERVICES                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                          ACCESS CONTROL LAYER                                    │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │   │
│  │  │   AuthN     │  │   AuthZ     │  │   Audit     │  │   E-Sig     │            │   │
│  │  │  Service    │  │  Service    │  │  Service    │  │  Service    │            │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘            │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                          BUSINESS DOMAIN SERVICES                                 │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │   │
│  │  │  Materials  │  │  Packaging  │  │   Samples   │  │    COA      │            │   │
│  │  │  Service    │  │  Service    │  │  Service    │  │  Service    │            │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘            │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 DATA LAYER                                              │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────┐               │
│  │      PostgreSQL Database        │  │      Redis (Cache + Broker)     │               │
│  │  • Business Records             │  │  • Session Storage              │               │
│  │  • Audit Logs                   │  │  • Celery Broker                │               │
│  │  • E-Signature Records          │  │  • Cache                        │               │
│  └─────────────────────────────────┘  └─────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Component Diagram

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                 FRONTEND COMPONENTS                                      │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                            SHARED UI COMPONENTS                                  │    │
│  │  • Buttons, Forms, Tables, Modals, Badges, Labels, Print Components             │    │
│  │  • API Client (Axios)                                                          │    │
│  │  • State Management (React Query / Zustand)                                    │    │
│  │  • Routing (React Router)                                                      │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │ Storekeeper  │  │   Sampler    │  │   Analyst    │  │  QC Manager  │  │   Admin  │ │
│  │    App       │  │    App       │  │    App       │  │    App       │  │  Console │ │
│  │              │  │              │  │              │  │              │  │          │ │
│  │ • Materials  │  │ • Sampling   │  │ • Launcher   │  │ • COA Review │  │ • Empl.  │ │
│  │ • Packaging  │  │ • History    │  │ • Samples    │  │ • Approve/   │  │   Mgmt   │ │
│  │ • Notif.     │  │ • Product    │  │ • COA Form   │  │   Reject     │  │ • Roles  │ │
│  │ • Labels     │  │   Samples    │  │ • Certs      │  │ • Release    │  │ • Audit  │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └────┬───┘ │
└─────────┼─────────────────┼─────────────────┼─────────────────┼────────────────┼──────┘
          │                 │                 │                 │                │
          └─────────────────┴─────────────────┴─────────────────┴────────────────┘
                                            │
                                            ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                 BACKEND COMPONENTS                                       │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                         API LAYER (Django REST Framework)                        │    │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐ │    │
│  │  │                    URL Routing / Authentication / Permissions                │ │    │
│  │  └─────────────────────────────────────────────────────────────────────────────┘ │    │
│  │                                                                                  │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │    │
│  │  │   Users     │  │  Materials  │  │  Packaging  │  │   Samples   │            │    │
│  │  │   API       │  │    API      │  │    API      │  │    API      │            │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘            │    │
│  │                                                                                  │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │    │
│  │  │   COA       │  │  Notif.     │  │   Audit     │  │  E-Sig      │            │    │
│  │  │   API       │  │    API      │  │    API      │  │    API      │            │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘            │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                         BUSINESS LOGIC LAYER (Services)                          │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │    │
│  │  │    Auth     │  │  Materials  │  │  Packaging  │  │   Samples   │            │    │
│  │  │   Service   │  │  Service    │  │  Service    │  │  Service    │            │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘            │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │    │
│  │  │    COA      │  │  Notif.     │  │   Audit     │  │  E-Sig      │            │    │
│  │  │   Service   │  │  Service    │  │  Service    │  │  Service    │            │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘            │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                         DATA ACCESS LAYER (Django ORM)                           │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │    │
│  │  │  User Model │  │  Material   │  │  Packaging  │  │   Sample    │            │    │
│  │  │             │  │   Model     │  │   Model     │  │   Model     │            │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘            │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │    │
│  │  │   COA       │  │  Notification│  │  AuditLog   │  │  E-Sig      │            │    │
│  │  │   Model     │  │   Model     │  │   Model     │  │   Model     │            │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘            │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Architectural Views

### 3.1 Logical View

The logical view describes the system's functional decomposition into modules and their relationships.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              APPLICATION MODULES                                        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐ │
│  │                             ACCESS CONTROL LAYER                                  │ │
│  │                                                                                   │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                   │ │
│  │  │   Authentication │  │   Authorisation  │  │   Session       │                   │ │
│  │  │   ─────────────  │  │   ─────────────  │  │   Management    │                   │ │
│  │  │  • Login/Logout  │  │  • RBAC Engine   │  │  • Session      │                   │ │
│  │  │  • Password Hash │  │  • Permission    │  │    Storage      │                   │ │
│  │  │  • JWT/Tokens    │  │    Validation    │  │  • Timeout      │                   │ │
│  │  │  • MFA (TBS)     │  │  • API Scoping   │  │  • Invalidation │                   │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘                   │ │
│  │                                                                                   │ │
│  │  ┌─────────────────┐  ┌─────────────────┐                                        │ │
│  │  │   Audit Service  │  │  E-Signature    │                                        │ │
│  │  │   ─────────────  │  │   Service       │                                        │ │
│  │  │  • Record Change │  │  • Signature    │                                        │ │
│  │  │  • Immutable Log │  │    Generation   │                                        │ │
│  │  │  • Query/View    │  │  • Verification │                                        │ │
│  │  │  • Retention     │  │  • Integrity    │                                        │ │
│  │  └─────────────────┘  └─────────────────┘                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                         │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐ │
│  │                             BUSINESS MODULES                                      │ │
│  │                                                                                   │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                   │ │
│  │  │    Materials     │  │    Packaging    │  │     Samples     │                   │ │
│  │  │    Module        │  │    Module       │  │     Module      │                   │ │
│  │  │                  │  │                  │  │                  │                   │ │
│  │  │  • Register RM   │  │  • Register     │  │  • Record RM    │                   │ │
│  │  │  • View RM       │  │    Packaging    │  │    Sample       │                   │ │
│  │  │  • Request       │  │  • View         │  │  • Record       │                   │ │
│  │  │    Sampling      │  │    Packaging    │  │    Product      │                   │ │
│  │  │  • Release Label │  │  • Request      │  │    Sample       │                   │ │
│  │  │  • Notifications │  │    Sampling     │  │  • View History │                   │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘                   │ │
│  │                                                                                   │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                   │ │
│  │  │      COA         │  │    QC Review    │  │  Monograph      │                   │ │
│  │  │    Module        │  │    Module       │  │  (TBS)          │                   │ │
│  │  │                  │  │                  │  │                  │                   │ │
│  │  │  • Create COA    │  │  • View COA     │  │  • Stub only    │                   │ │
│  │  │  • Update COA    │  │  • Approve COA  │  │  • Full module  │                   │ │
│  │  │  • View COA      │  │  • Reject COA   │  │    TBS          │                   │ │
│  │  │  • Certificates  │  │  • Release      │  │                  │                   │ │
│  │  │    List          │  │    Material     │  │                  │                   │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘                   │ │
│  └───────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                         │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐ │
│  │                             ADMIN MODULE                                          │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                   │ │
│  │  │  Employee Mgmt   │  │   Role Mgmt     │  │  Audit View     │                   │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘                   │ │
│  └───────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Process View

The process view describes the runtime behaviour, concurrency, and communication patterns.

**Request Flow — Typical User Operation:**

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Browser │────▶│  Nginx   │────▶│  Django  │────▶│ Service  │────▶│Database  │
│  (React) │     │  (Proxy) │     │  (DRF)   │     │  Layer   │     │(Postgres)│
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                 │                │                │                │
     │    HTTP Request │                │                │                │
     │────────────────▶│                │                │                │
     │                 │   Forward      │                │                │
     │                 │────────────────▶│                │                │
     │                 │                │   Authenticate │                │
     │                 │                │   Authorise    │                │
     │                 │                │───────────────▶│                │
     │                 │                │                │   DB Query     │
     │                 │                │                │───────────────▶│
     │                 │                │                │   Results      │
     │                 │                │                │◀───────────────│
     │                 │                │   Response     │                │
     │                 │                │◀───────────────│                │
     │                 │   Response     │                │                │
     │                 │◀────────────────│                │                │
     │   HTTP Response │                │                │                │
     │◀────────────────│                │                │                │
     │                 │                │                │                │
     │   Audit Log (Async)              │                │                │
     │   ──────────────────────────────▶│  Celery       │                │
     │                                  │  Task         │                │
     │                                  │───────────────▶│  Redis Queue  │
```

**Asynchronous Workflows:**

| Workflow | Trigger | Processing | Result |
|----------|---------|------------|--------|
| Audit Trail | Any create/update on GMP record | Celery task writes audit entry to database | Audit record stored within 5 seconds |
| Notification | QC release | Celery task creates notification record | Storekeeper sees notification on next page load |
| Label Generation | Sample recorded | Synchronous (browser print) | Immediate label preview |

### 3.3 Physical View (Deployment)

**Development / Production Deployment Architecture:**

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               DEPLOYMENT ENVIRONMENT                                    │
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                            DOCKER HOST                                          │   │
│  │                                                                                  │   │
│  │  ┌────────────────────────────────────────────────────────────────────────┐   │   │
│  │  │                         DOCKER COMPOSE STACK                           │   │   │
│  │  │                                                                         │   │   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │   │   │
│  │  │  │   Nginx     │  │  Backend    │  │  Celery     │  │  Celery     │   │   │   │
│  │  │  │  (Port 443) │  │  (Django)   │  │  Worker     │  │  Beat       │   │   │   │
│  │  │  │  Reverse    │  │  (Port 8000)│  │  (Tasks)    │  │  (Scheduler)│   │   │   │
│  │  │  │  Proxy      │  │  x n        │  │  x n        │  │  x 1        │   │   │   │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │   │   │
│  │  │                                                                         │   │   │
│  │  │  ┌─────────────────────────────────────────────┐  ┌──────────────────┐ │   │   │
│  │  │  │           PostgreSQL (15+)                   │  │   Redis (7+)     │ │   │   │
│  │  │  │  • Database                                 │  │  • Session Store │ │   │   │
│  │  │  │  • WAL Archiving (for point-in-time)        │  │  • Celery Broker │ │   │   │
│  │  │  │  • Daily Backups to volume                   │  │  • Cache         │ │   │   │
│  │  │  └─────────────────────────────────────────────┘  └──────────────────┘ │   │   │
│  │  └────────────────────────────────────────────────────────────────────────┘   │   │
│  │                                                                                  │   │
│  │  ┌────────────────────────────────────────────────────────────────────────┐   │   │
│  │  │                          STATIC FILES                                  │   │   │
│  │  │  ┌─────────────────────────────────────────────────────────────────┐  │   │   │
│  │  │  │   React Build (Built once, served by Nginx)                     │  │   │   │
│  │  │  │   • storekeeper/build  • sampler/build                          │  │   │   │
│  │  │  │   • analyst/build      • qcmanager/build   • admin/build        │  │   │   │
│  │  │  └─────────────────────────────────────────────────────────────────┘  │   │   │
│  │  └────────────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                          PERSISTENT VOLUMES                                     │   │
│  │  • postgres_data  (database files)                                             │   │
│  │  • redis_data     (if persistence needed)                                      │   │
│  │  • backup_volume  (daily backups)                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

**Network Configuration:**
- Nginx: Port 443 (HTTPS), Port 80 (redirect to HTTPS)
- Backend: Internal port 8000, not exposed externally
- PostgreSQL: Internal port 5432, not exposed externally
- Redis: Internal port 6379, not exposed externally
- All internal containers communicate over a dedicated Docker network

### 3.4 Development View

The development view describes the code organisation, modules, and dependencies.

**Backend Structure (Django):**
```
backend/
├── manage.py
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── config/                          # Django project configuration
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/                       # Employee + auth
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── services.py
│   │   └── permissions.py
│   ├── materials/                   # Raw Material
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── services.py
│   ├── packaging/                   # Packaging Material
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── services.py
│   ├── sampling/                    # Samples (RM + Packaging)
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── services.py
│   ├── products/                    # Product Samples (FP/SFP/Bulk)
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── services.py
│   ├── coa/                         # COA + QC Review
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── services.py
│   ├── notifications/               # In-app notifications
│   │   ├── models.py
│   │   ├── views.py
│   │   └── services.py
│   ├── audit/                       # Audit Trail
│   │   ├── models.py
│   │   ├── services.py
│   │   └── middleware.py
│   ├── esignature/                  # Electronic Signature
│   │   ├── models.py
│   │   └── services.py
│   └── common/                      # Shared utilities
│       ├── mixins.py
│       ├── validators.py
│       ├── exceptions.py
│       └── constants.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── celery.py
```

**Frontend Structure (React — One per role):**
```
frontends/
├── shared/                          # Shared components
│   ├── components/
│   │   ├── Button/
│   │   ├── Table/
│   │   ├── Modal/
│   │   ├── Badge/
│   │   ├── Label/
│   │   ├── StatusBadge/
│   │   └── Toast/
│   ├── hooks/
│   │   ├── useAuth.js
│   │   ├── useApi.js
│   │   └── useNotifications.js
│   ├── api/
│   │   ├── client.js               # Axios instance
│   │   ├── auth.js
│   │   ├── materials.js
│   │   ├── packaging.js
│   │   ├── samples.js
│   │   └── coa.js
│   ├── utils/
│   │   ├── formatters.js
│   │   ├── validators.js
│   │   └── dateHelpers.js
│   └── styles/
│       └── theme.js
│
├── storekeeper/                     # Storekeeper App
│   ├── src/
│   │   ├── index.js
│   │   ├── App.js
│   │   ├── routes/
│   │   │   ├── Materials.jsx
│   │   │   ├── Packaging.jsx
│   │   │   └── Notifications.jsx
│   │   └── components/
│   │       ├── MaterialTable.jsx
│   │       ├── MaterialForm.jsx
│   │       └── ReleaseLabel.jsx
│   └── package.json
│
├── sampler/                         # Sampler App
│   ├── src/
│   │   ├── index.js
│   │   ├── App.js
│   │   ├── routes/
│   │   │   ├── SamplingRequests.jsx
│   │   │   ├── SampleHistory.jsx
│   │   │   ├── ProductSamples.jsx
│   │   │   └── ProductHistory.jsx
│   │   └── components/
│   │       ├── SamplingForm.jsx
│   │       ├── LabelPreview.jsx
│   │       └── ProductSampleForm.jsx
│   └── package.json
│
├── analyst/                         # Analyst App
│   ├── src/
│   │   ├── index.js
│   │   ├── App.js
│   │   ├── routes/
│   │   │   ├── Home.jsx
│   │   │   ├── Samples.jsx
│   │   │   └── Certificates.jsx
│   │   └── components/
│   │       ├── SampleWorklist.jsx
│   │       ├── COAForm.jsx
│   │       └── COAView.jsx
│   └── package.json
│
├── qcmanager/                       # QC Manager App
│   ├── src/
│   │   ├── index.js
│   │   ├── App.js
│   │   ├── routes/
│   │   │   └── COAReview.jsx
│   │   └── components/
│   │       ├── COAList.jsx
│   │       ├── COADetail.jsx
│   │       └── ReleaseModal.jsx
│   └── package.json
│
└── admin/                           # Admin Console
    ├── src/
    │   ├── index.js
    │   ├── App.js
    │   ├── routes/
    │   │   ├── Employees.jsx
    │   │   ├── Roles.jsx
    │   │   └── AuditLog.jsx
    │   └── components/
    │       ├── EmployeeForm.jsx
    │       └── AuditView.jsx
    └── package.json
```

### 3.5 Operational View

The operational view describes the runtime concerns: monitoring, logging, and operations.

**Monitoring Stack:**
- **Metrics**: Prometheus collects metrics from Django (via `django-prometheus`), PostgreSQL, Redis, and Nginx.
- **Visualisation**: Grafana dashboards for:
  - API response times and error rates
  - Database performance and connections
  - Queue lengths (Celery)
  - Resource utilisation (CPU, memory, disk)
- **Logging**: ELK stack (Elasticsearch, Logstash, Kibana) or cloud-based log aggregation (Datadog, Sentry).

**Key Operational Metrics:**

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| API Error Rate (5xx) | Nginx / Django logs | > 1% of requests |
| API Response Time (95th) | Django / Prometheus | > 500 ms |
| Database Connections | PostgreSQL | > 80% of pool |
| Celery Queue Length | Redis | > 100 tasks |
| Disk Usage (data) | Volume monitoring | > 75% |
| Login Failure Rate | Audit logs | > 5 failures/hour |
| Certificate Expiry | Nginx | 30 days before expiry |

**Backup Strategy:**
- **Full Database Backup**: Daily at 02:00 UTC
- **WAL Archiving**: Continuous for point-in-time recovery
- **Backup Retention**: 30 days (daily), 12 months (monthly), 7 years (yearly for compliance)
- **Restore Test**: Quarterly restoration test to validate backup integrity

---

## 4. Architectural Decisions

### AD-001: Application Separation

| Attribute | Value |
|-----------|-------|
| **Decision** | Build four separate frontend applications (Storekeeper, Sampler, Analyst, QC Manager) instead of a single app with role-based views. |
| **Rationale** | Confirmed in the Project Charter: each role must have a dedicated application. This ensures: (1) clear separation of concerns, (2) independent deployment and versioning, (3) reduced complexity in permission enforcement at the UI level, and (4) teams can work independently on each app. |
| **Alternatives Considered** | Single SPA with role-based routing (rejected due to Charter mandate and increased complexity of managing role-specific navigation in one codebase). |
| **Status** | Confirmed |

### AD-002: Shared Database

| Attribute | Value |
|-----------|-------|
| **Decision** | Use a single PostgreSQL database shared by all four applications. |
| **Rationale** | Confirmed in the Charter: "four applications sharing one database." This simplifies: (1) data consistency across apps, (2) reporting and analytics (single source of truth), (3) transaction management, and (4) development (single migration pipeline). |
| **Alternatives Considered** | Separate databases per app (rejected due to Charter constraint and complexity of cross-app data joins). |
| **Status** | Confirmed |

### AD-003: Access Control Layer as Shared Service

| Attribute | Value |
|-----------|-------|
| **Decision** | Implement authentication, authorisation, audit, and e-signature as shared Django apps used by all business modules. |
| **Rationale** | Confirmed in the Charter: "Access Control Layer sitting above four separate business applications." This ensures: (1) consistent security enforcement, (2) no duplication of auth logic, (3) centralised audit trail, and (4) easier compliance validation. |
| **Alternatives Considered** | Each app implementing its own auth (rejected due to Charter mandate and security risks). |
| **Status** | Confirmed |

### AD-004: Audit Trail Implementation

| Attribute | Value |
|-----------|-------|
| **Decision** | Implement audit logging using Django signals combined with a dedicated `AuditLog` model. Audit entries are created asynchronously via Celery. |
| **Rationale** | Ensures: (1) audit is not bypassed (model-level), (2) no performance impact on user requests (asynchronous), (3) immutable records (append-only), and (4) consistent format across all modules. |
| **Alternatives Considered** | Trigger-based audit in PostgreSQL (rejected due to maintainability and need for application context like user ID). |
| **Status** | Confirmed |

### AD-005: Electronic Signature Implementation

| Attribute | Value |
|-----------|-------|
| **Decision** | Model e-signatures as a separate `ElectronicSignature` entity, cryptographically linked to the signed record via a hash of the record content. |
| **Rationale** | Meets 21 CFR Part 11 requirements: (1) signature has meaning (e.g., "Approve COA"), (2) timestamped, (3) signed content is hash-verified, (4) recorded in a separate, immutable table, and (5) includes signer identity. |
| **Alternatives Considered** | Storing signature as a text field on the signed record (rejected due to lack of traceability and integrity verification). |
| **Status** | Confirmed |

### AD-006: Asynchronous Processing

| Attribute | Value |
|-----------|-------|
| **Decision** | Use Celery + Redis for asynchronous processing of audit trail logging and notifications. |
| **Rationale** | Confirmed in technology stack. Asynchronous processing: (1) prevents user request blocking, (2) improves perceived performance, and (3) provides retry mechanisms for transient failures. |
| **Alternatives Considered** | Synchronous processing (rejected due to performance impact, especially for audit logging). |
| **Status** | Confirmed |

### AD-007: Frontend State Management

| Attribute | Value |
|-----------|-------|
| **Decision** | Use React Query for server state (API data) and React Context / Zustand for client state (UI, session). |
| **Rationale** | React Query provides: (1) built-in caching and revalidation, (2) automatic background refetching, (3) optimistic updates, and (4) mutation handling. This reduces boilerplate and improves user experience. |
| **Alternatives Considered** | Redux (rejected as heavy for this use case), plain fetch (rejected due to manual caching complexity). |
| **Status** | TBS (UI framework choice still pending) |

### AD-008: API Design

| Attribute | Value |
|-----------|-------|
| **Decision** | Use Django REST Framework with ViewSets and ModelSerializers, implementing RESTful APIs with DRF's built-in permission classes. |
| **Rationale** | Confirmed technology stack. DRF provides: (1) rapid development, (2) built-in permissions and authentication, (3) OpenAPI/Swagger documentation generation, and (4) strong ecosystem support. |
| **Alternatives Considered** | GraphQL (rejected as too complex for the domain; few cases require multiple resource fetching). |
| **Status** | Confirmed |

### AD-009: Containerisation Strategy

| Attribute | Value |
|-----------|-------|
| **Decision** | Containerise all services using Docker and orchestrate with Docker Compose for both development and production. |
| **Rationale** | Confirmed in the Charter: "containers" and "Docker Compose". Benefits: (1) environment consistency across dev/prod, (2) reproducible builds, (3) simplified dependency management, and (4) portability across cloud providers. |
| **Alternatives Considered** | Kubernetes (rejected as overkill for MVP; may be considered later if scale requires it). |
| **Status** | Confirmed |

### AD-010: ID Generation

| Attribute | Value |
|-----------|-------|
| **Decision** | Generate human-readable, sequential IDs for all business records (`RCV-YYYY-####`, `COA-YYYY-####`, etc.) using database sequences or counters. |
| **Rationale** | Meets the prototype specification and industry practice: (1) human-readable (operators can read/recite easily), (2) auditable (sequence reveals order), (3) traceable to business domain. |
| **Alternatives Considered** | UUIDs (rejected due to human-unfriendliness; may cause user errors when spoken/written). |
| **Status** | Confirmed |

### AD-011: Label Printing

| Attribute | Value |
|-----------|-------|
| **Decision** | Use browser `window.print()` with a dedicated hidden `<div>` containing label content and custom CSS. |
| **Rationale** | Matches the prototype and is the simplest approach: (1) zero dependencies, (2) works on all modern browsers, (3) no backend PDF generation required. |
| **Alternatives Considered** | Backend PDF generation (wkhtmltopdf, ReportLab) (rejected as more complex and slower; browser printing is sufficient). |
| **Status** | Confirmed |

---

## 5. Technology Stack

### 5.1 Backend Technologies

| Component | Technology | Version | Source | Status |
|-----------|------------|---------|--------|--------|
| **Language** | Python | 3.11+ | Charter | Confirmed |
| **Framework** | Django | 4.2+ | Charter | Confirmed |
| **API Framework** | Django REST Framework | 3.14+ | Charter | Confirmed |
| **Database** | PostgreSQL | 15+ | Charter | Confirmed |
| **Cache / Broker** | Redis | 7+ | Charter | Confirmed |
| **Task Queue** | Celery | 5.3+ | Charter | Confirmed |
| **Task Scheduler** | Celery Beat | 5.3+ | Charter | Confirmed |
| **Authentication** | Django Auth + DRF Token/JWT | — | Charter | Confirmed |
| **Database Driver** | psycopg2-binary | 2.9+ | — | Confirmed |
| **Serialisation** | DRF Serializers | — | Charter | Confirmed |
| **API Docs** | drf-yasg / drf-spectacular | — | — | TBS |
| **Testing** | pytest-django | — | — | TBS |
| **Logging** | Python logging + structlog | — | — | TBS |
| **Monitoring** | django-prometheus | — | — | TBS |

### 5.2 Frontend Technologies

| Component | Technology | Version | Source | Status |
|-----------|------------|---------|--------|--------|
| **Language** | JavaScript / TypeScript | ES2020 / TS 5+ | Charter | TBS (TS vs JS) |
| **Framework** | React | 18+ | Charter | Confirmed |
| **Routing** | React Router | 6+ | Charter | Confirmed |
| **API Client** | Axios | 1.6+ | Charter | Confirmed |
| **Server State** | React Query | 5+ | Charter | Confirmed |
| **Client State** | Zustand / React Context | — | — | TBS |
| **UI Framework** | MUI or Ant Design | — | Charter | TBS |
| **Form Handling** | React Hook Form | — | — | TBS |
| **Validation** | Zod | — | — | TBS |
| **Build Tool** | Vite | — | — | TBS |
| **Testing** | Jest / React Testing Library | — | — | TBS |

### 5.3 Infrastructure Technologies

| Component | Technology | Version | Source | Status |
|-----------|------------|---------|--------|--------|
| **Container Runtime** | Docker | 24+ | Charter | Confirmed |
| **Orchestration** | Docker Compose | 2.20+ | Charter | Confirmed |
| **Reverse Proxy** | Nginx | 1.24+ | Charter | Confirmed |
| **Operating System** | Alpine Linux (containers) | 3.18+ | Charter | Confirmed |
| **Monitoring** | Prometheus + Grafana | — | — | TBS |
| **Log Aggregation** | ELK or Datadog | — | — | TBS |
| **Backup** | pg_dump / WAL archiving | — | — | TBS |
| **CI/CD** | GitHub Actions / GitLab CI | — | — | TBS |

---

## 6. Cross-Cutting Concerns

### 6.1 Security

| Concern | Implementation |
|---------|----------------|
| **Transport Security** | TLS 1.2+ enforced; HSTS headers |
| **Authentication** | JWT tokens (access + refresh); stored in HTTP‑only cookies (secure, SameSite) |
| **Authorisation** | Django permissions + DRF permission classes; checked at every API endpoint |
| **Input Validation** | DRF serialiser validation; additional domain‑specific validators |
| **CSRF Protection** | DRF's CSRF protection (SessionAuthentication) or SameSite cookies |
| **SQL Injection** | Django ORM (parameterised queries) |
| **XSS Protection** | React's built‑in XSS protection; content security policy (CSP) headers |
| **Secrets Management** | Environment variables (12‑Factor) — never in code |
| **Security Headers** | HSTS, CSP, X‑Content‑Type‑Options, X‑Frame‑Options, Referrer‑Policy |

### 6.2 Audit and Logging

| Concern | Implementation |
|---------|----------------|
| **Business Audit** | AuditLog model; created via Celery task on model save/delete signals |
| **Access Logs** | Nginx access logs; Django request logs |
| **Error Logs** | Django logging (error level) to console (JSON structured) |
| **Security Logs** | Login attempts, permission denials, role changes |
| **Log Retention** | 30 days for operational logs; 10 years for audit logs (compliance) |

### 6.3 Error Handling

| Layer | Approach |
|-------|----------|
| **Backend** | Custom exception classes; DRF exception handler returns standardised error responses (code, message, details) |
| **Frontend** | Global error boundary; API error interceptor to parse error responses and show toasts |
| **API Errors** | HTTP 400 (validation), 401 (unauthorised), 403 (forbidden), 404 (not found), 500 (server error) |
| **Error Response Format** | `{ "error": { "code": "VALIDATION_ERROR", "message": "…", "details": { "field": "…" } } }` |

### 6.4 Internationalisation

| Concern | Status |
|---------|--------|
| **Language Support** | English only (MVP) — TBS if multi‑language required |
| **Date/Time Format** | UTC storage; display in user's local timezone (TBS) |
| **Currency/Units** | Units configurable via drop‑down; no currency handling required |

---

## 7. Interfaces

### 7.1 API Design

**API Principles:**
- RESTful: Resources as nouns, standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Versioned: `/api/v1/...` (versioning strategy TBS)
- JSON: All requests and responses in JSON
- Authentication: JWT (Bearer token in `Authorization` header) or HTTP‑only cookie
- Pagination: `limit` and `offset` or cursor‑based (TBS)
- Filtering: Query parameters (`?status=Quarantine&samplingStatus=Requested`)
- Sorting: Query parameters (`?ordering=-created_at`)

**Resource Endpoints (High‑Level):**
| Resource | Base Path |
|----------|-----------|
| Authentication | `/api/v1/auth/` |
| Employees | `/api/v1/employees/` |
| Materials | `/api/v1/materials/` |
| Packaging | `/api/v1/packaging/` |
| Samples | `/api/v1/samples/` |
| Product Samples | `/api/v1/product-samples/` |
| COAs | `/api/v1/coas/` |
| Notifications | `/api/v1/notifications/` |
| Audit Logs | `/api/v1/audit/` |
| E‑Signatures | `/api/v1/signatures/` |

### 7.2 Internal Service Communication

| Communication | Protocol | Description |
|---------------|----------|-------------|
| Backend ↔ Database | TCP/IP (psycopg2) | SQL queries via Django ORM |
| Backend ↔ Redis | TCP/IP (redis-py) | Session storage, Celery broker |
| Backend ↔ Celery | AMQP (via Redis) | Task queue for async operations |
| Frontend ↔ Backend | HTTPS | RESTful API calls |

### 7.3 External Dependencies

| Dependency | Purpose | Fallback |
|------------|---------|----------|
| PostgreSQL | Primary data store | Database replica (if configured) |
| Redis | Cache, session store, Celery broker | Graceful degradation (cache misses) |
| Celery | Asynchronous tasks | Synchronous fallback for critical tasks |
| Nginx | Static file serving, reverse proxy | — |

---

## 8. Data Architecture

### 8.1 Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  DATA FLOW — REGISTER MATERIAL                         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌──────────────┐         │
│  │  User   │───▶│  React  │───▶│  API    │───▶│  Service │───▶│  PostgreSQL  │         │
│  │  Inputs │    │  Form   │    │  View   │    │  Layer   │    │  Material    │         │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘    │  Table       │         │
│                                                                └──────────────┘         │
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                          AUDIT TRAIL (ASYNC)                                    │   │
│  │                                                                                  │   │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌──────────────┐                  │   │
│  │  │  Signal │───▶│ Celery  │───▶│  Audit  │───▶│  PostgreSQL  │                  │   │
│  │  │  Handler│    │  Task   │    │ Service │    │  AuditLog    │                  │   │
│  │  └─────────┘    └─────────┘    └─────────┘    │  Table       │                  │   │
│  │                                                 └──────────────┘                  │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Data Storage Strategy

| Data Type | Storage | Access Pattern |
|-----------|---------|----------------|
| Business Records (Materials, Samples, COAs) | PostgreSQL | High‑frequency CRUD |
| Audit Logs | PostgreSQL (append‑only) | Write‑heavy; occasional querying |
| E‑Signature Records | PostgreSQL | Write‑once, read‑rarely |
| Session Data | Redis | High‑frequency read/write |
| Cache (Reference Lists) | Redis | Read‑heavy; periodic invalidation |
| Static Assets (React builds) | Nginx‑served files | Read‑only; CDN‑cacheable |

### 8.3 Data Migration and Versioning

| Concern | Approach |
|---------|----------|
| **Migration Tool** | Django migrations (built‑in) |
| **Migration Policy** | All migrations must be reversible (backwards‑compatible) |
| **Data Migration** | Separate data migrations in Django; run after schema migrations |
| **Rollback Plan** | Downgrade to previous migration; data loss risk assessed per migration |
| **Testing** | Migrations tested in staging before production; rollback tested quarterly |

---

## 9. Quality Attributes

### 9.1 Performance

| Concern | Design Measure |
|---------|----------------|
| API Response Time | Database indexing; N+1 query prevention (select_related, prefetch_related); pagination; caching (Redis) |
| Page Load Time | Static assets served by Nginx with gzip/brotli; client‑side caching via React Query; lazy loading |
| Database Performance | Indexes on foreign keys and frequently queried fields; query optimisation; connection pooling |
| Background Tasks | Celery with appropriate concurrency; retry logic; monitoring of queue length |

### 9.2 Scalability

| Concern | Design Measure |
|---------|----------------|
| Horizontal Scaling | Stateless backend (session stored in Redis); multiple Django instances behind Nginx |
| Database Scaling | Connection pooling; read replicas for reporting (future); partitioning for large tables |
| Frontend Scaling | Static builds hosted on CDN; each role app independently deployable |
| Background Workers | Celery workers can be scaled independently |

### 9.3 Availability

| Concern | Design Measure |
|---------|----------------|
| Uptime | Stateless design; health checks; graceful shutdown; retries on transient failures |
| Recovery | Database backups (daily + WAL archiving); restore tested quarterly |
| Graceful Degradation | Redis unavailable → cache misses, no session; Celery unavailable → fallback to synchronous processing for critical operations |
| Monitoring | Prometheus metrics; alerting on threshold violations |

### 9.4 Security

| Concern | Design Measure |
|---------|----------------|
| Data Confidentiality | TLS; role‑based access; least privilege principles; encrypted secrets |
| Data Integrity | Audit logging; e‑signature hashing; database constraints; immutable audit table |
| Authentication | Password hashing (bcrypt); session timeout; account lockout (TBS); MFA (TBS) |
| Authorisation | Permission checks at every API endpoint; UI hides unauthorised actions |

### 9.5 Maintainability

| Concern | Design Measure |
|---------|----------------|
| Code Organisation | Modular Django apps; domain‑driven organisation; clear separation of concerns |
| Documentation | OpenAPI/Swagger for APIs; README; inline code comments for complex logic |
| Testing | Unit tests (≥80% coverage); integration tests for critical workflows; E2E tests for happy paths |
| CI/CD | Automated build, test, and deployment pipeline; linting and formatting checks |
| Monitoring | Structured logging; health checks; performance metrics |

---

## 10. Appendices

### A. Technology Rationale

| Technology | Rationale |
|------------|-----------|
| **Django** | Confirmed by Charter. Provides built‑in ORM, admin interface, authentication, security features, and excellent ecosystem for CRUD applications. |
| **Django REST Framework** | Confirmed by Charter. Provides robust API building, serialisers, authentication, permissions, and browsable APIs. |
| **PostgreSQL** | Confirmed by Charter. Strong data integrity, support for JSON fields (for audit data), transactional ACID compliance, and proven in regulated environments. |
| **Redis** | Confirmed by Charter. High‑performance in‑memory data store; perfect for session management, caching, and Celery broker. |
| **React** | Confirmed by Charter. Declarative component model, strong ecosystem, and enables building separate SPAs per role. |
| **React Query** | Confirmed by Charter (required via Axios). Handles server‑state caching, revalidation, and optimistic updates with minimal boilerplate. |
| **Docker** | Confirmed by Charter. Standardises development, testing, and production environments; ensures reproducibility. |
| **Nginx** | Confirmed by Charter. Efficient static file serving, reverse proxy with SSL termination, and load balancing. |

### B. Architectural Decision Log

| Decision ID | Date | Decision | Alternatives | Status | Reason for Decision |
|-------------|------|----------|--------------|--------|---------------------|
| AD-001 | 2026-01-15 | Four separate frontend applications | Single SPA with role‑based routing | Confirmed | Charter mandate; clear separation of concerns; independent deployment |
| AD-002 | 2026-01-15 | Shared PostgreSQL database | Separate databases per app | Confirmed | Charter mandate; single source of truth; simplified transactions |
| AD-003 | 2026-01-15 | Shared Access Control Layer | Each app implements its own auth | Confirmed | Charter mandate; consistent security; centralised compliance |
| AD-004 | 2026-01-15 | Audit via Django signals + Celery | PostgreSQL triggers; synchronous logging | Confirmed | Application‑level context; async; non‑blocking |
| AD-005 | 2026-01-15 | Separate ElectronicSignature model | Text field on signed record | Confirmed | 21 CFR Part 11 compliance; integrity verification; traceability |
| AD-006 | 2026-01-15 | Celery + Redis for async tasks | Synchronous processing | Confirmed | Performance; retry capability; non‑blocking |
| AD-007 | 2026-01-15 | React Query for server state | Redux; plain fetch | TBS | Query caching, auto‑refetch, optimistic updates |
| AD-008 | 2026-01-15 | DRF ViewSets + Serializers | GraphQL; custom Flask API | Confirmed | Charter mandate; rapid development; ecosystem |
| AD-009 | 2026-01-15 | Docker + Docker Compose | Kubernetes; bare metal | Confirmed | Charter mandate; environment consistency; portability |
| AD-010 | 2026-01-15 | Human‑readable sequential IDs | UUIDs | Confirmed | Prototype; human‑friendly; auditable |
| AD-011 | 2026-01-15 | Browser `window.print()` for labels | Backend PDF generation | Confirmed | Prototype; simplicity; zero dependencies |

### C. Component Inventory

| Component | Type | Description |
|-----------|------|-------------|
| **Frontend Applications** | Presentation | Five React SPAs (Storekeeper, Sampler, Analyst, QC Manager, Admin Console) |
| **Shared UI Library** | Presentation | Buttons, forms, tables, modals, badges, labels, print components |
| **API Gateway (Nginx)** | Infrastructure | Reverse proxy; static file serving; SSL termination |
| **Django Backend** | Application | REST API; business logic; ORM; admin interface |
| **Celery Workers** | Application | Async task processing (audit logs, notifications) |
| **Celery Beat** | Application | Scheduled task scheduler (backups, reports) |
| **PostgreSQL** | Data | Primary data store |
| **Redis** | Data | Session storage; cache; Celery broker |
| **Prometheus** | Monitoring | Metrics collection |
| **Grafana** | Monitoring | Metrics visualisation |

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
| 1.0 | [Date] | [Author] | Initial baseline; all ADs documented with traceability to SRS and NFR |

