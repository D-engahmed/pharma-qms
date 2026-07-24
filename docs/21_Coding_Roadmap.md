# 21 — Coding Roadmap

**Document Identifier:** RM-RRS-CR-001
**Version:** 1.0
**Status:** Baseline
**Traces to:** Project Charter, SRS, NFR, SAS, Design Specification, Coding Standards, TDD, Implementation Roadmap
**Compliance Reference:** Agile Development Best Practices, Test-Driven Development (TDD), Continuous Integration/Continuous Delivery (CI/CD)

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Development Methodology](#2-development-methodology)
3. [Sprint Breakdown](#3-sprint-breakdown)
4. [Detailed Sprint Tasks](#4-detailed-sprint-tasks)
5. [Task Prioritisation](#5-task-prioritisation)
6. [Dependencies and Sequencing](#6-dependencies-and-sequencing)
7. [Quality Gates](#7-quality-gates)
8. [Daily Development Workflow](#8-daily-development-workflow)
9. [Code Review Process](#9-code-review-process)
10. [Appendices](#10-appendices)

---

## 1. Introduction

### 1.1 Purpose
This document defines the **Coding Roadmap** for the **Raw Material Receiving & Release System (RM-RRS)** . It provides a detailed, sprint-by-sprint breakdown of all coding activities required to implement the system, including task descriptions, estimated effort, dependencies, and quality gates. This roadmap translates the high-level implementation plan into actionable, developer-focused tasks.

### 1.2 Scope
This roadmap covers all coding activities from the initial project setup through to the final production deployment, organised into five sprints. Each sprint includes tasks for backend, frontend, testing, and integration activities. The roadmap is designed to be executed by the development team following the coding standards defined in Document 19 and the test design defined in Document 16.

### 1.3 Coding Roadmap Overview

```mermaid
flowchart LR
    subgraph Sprints["DEVELOPMENT SPRINTS"]
        S1["Sprint 1<br/>Foundation<br/>2 Weeks"]
        S2["Sprint 2<br/>Storekeeper + Sampler<br/>3 Weeks"]
        S3["Sprint 3<br/>Analyst + QC Manager<br/>3 Weeks"]
        S4["Sprint 4<br/>Integration + Testing<br/>2 Weeks"]
        S5["Sprint 5<br/>Deployment<br/>2 Weeks"]
    end

    S1 --> S2 --> S3 --> S4 --> S5
```

---

## 2. Development Methodology

### 2.1 Agile Development Framework

```mermaid
flowchart TD
    subgraph Agile["AGILE DEVELOPMENT PROCESS"]
        PB["Product Backlog<br/>Prioritised requirements"]
        S["Sprint Planning<br/>Select tasks for sprint"]
        SD["Sprint Development<br/>5-10 day sprints"]
        DR["Daily Standup<br/>15-min sync"]
        SR["Sprint Review<br/>Demo to stakeholders"]
        SA["Sprint Retrospective<br/>Process improvement"]
    end

    PB --> S --> SD --> SR --> SA
    SD --> DR
    SA --> PB
```

### 2.2 Development Practices

| Practice | Description |
|----------|-------------|
| **Test-Driven Development (TDD)** | Write tests before code; ensure each feature is testable |
| **Pair Programming** | Complex features developed in pairs for quality |
| **Continuous Integration** | Code merged and tested multiple times daily |
| **Trunk-Based Development** | Short-lived feature branches; merge to main frequently |
| **Automated Testing** | Unit, integration, and end-to-end tests in CI pipeline |
| **Code Reviews** | Every PR reviewed by at least one team member |

### 2.3 Sprint Structure

| Attribute | Value |
|-----------|-------|
| **Sprint Duration** | 2 weeks (10 working days) |
| **Story Points** | Fibonacci sequence (1, 2, 3, 5, 8, 13) |
| **Velocity** | Estimated 30-40 story points per sprint |
| **Team Capacity** | 6-8 developers at 80% capacity |
| **Definition of Done** | Code complete, tested, reviewed, merged, deployed to staging |

---

## 3. Sprint Breakdown

### 3.1 Sprint Overview

```mermaid
gantt
    title Coding Roadmap - Sprint Overview
    dateFormat  YYYY-MM-DD

    section Sprint 1
    Sprint 1 - Foundation               :s1, 2026-01-15, 10d

    section Sprint 2
    Sprint 2 - Storekeeper + Sampler    :s2, 2026-01-29, 15d

    section Sprint 3
    Sprint 3 - Analyst + QC Manager     :s3, 2026-02-19, 15d

    section Sprint 4
    Sprint 4 - Integration + Testing    :s4, 2026-03-11, 10d

    section Sprint 5
    Sprint 5 - Deployment               :s5, 2026-03-25, 10d
```

### 3.2 Sprint 1: Foundation (January 15-28, 2026)

| Sprint Goal | Key Deliverables |
|-------------|------------------|
| Establish development environment and core infrastructure | Working development environment, CI/CD pipeline, authentication, audit logging, e-signatures, shared UI components |

**Sprint 1 Backlog:**

| ID | Task | Type | Points | Owner | Dependencies |
|----|------|------|--------|-------|--------------|
| S1-001 | Project repository setup and branching strategy | Infra | 1 | DevOps | — |
| S1-002 | Docker Compose configuration (PostgreSQL, Redis, Django) | Infra | 3 | DevOps | S1-001 |
| S1-003 | CI/CD pipeline setup (GitHub Actions) | Infra | 3 | DevOps | S1-002 |
| S1-004 | Backend project structure setup | Backend | 2 | Backend Lead | — |
| S1-005 | Common module (utilities, constants, exceptions) | Backend | 3 | Backend Team | S1-004 |
| S1-006 | Users module - Employee model | Backend | 3 | Backend Team | S1-005 |
| S1-007 | Users module - Authentication (JWT + login/logout/refresh) | Backend | 5 | Backend Team | S1-006 |
| S1-008 | Users module - Permissions framework | Backend | 3 | Backend Team | S1-007 |
| S1-009 | Audit module - AuditLog model and service | Backend | 3 | Backend Team | S1-005 |
| S1-010 | Audit module - Django signals integration | Backend | 3 | Backend Team | S1-009 |
| S1-011 | E-Signature module - Signature model and hashing | Backend | 2 | Backend Team | S1-005 |
| S1-012 | Frontend monorepo setup (pnpm workspaces) | Frontend | 3 | Frontend Lead | — |
| S1-013 | Shared UI - Design system (colors, typography, spacing) | Frontend | 2 | Frontend Team | S1-012 |
| S1-014 | Shared UI - Button component | Frontend | 2 | Frontend Team | S1-013 |
| S1-015 | Shared UI - Modal component | Frontend | 3 | Frontend Team | S1-013 |
| S1-016 | Shared UI - Table component | Frontend | 3 | Frontend Team | S1-013 |
| S1-017 | Shared UI - Badge and StatusBadge components | Frontend | 2 | Frontend Team | S1-013 |
| S1-018 | Shared UI - Form components (Input, Select, DatePicker) | Frontend | 3 | Frontend Team | S1-013 |
| S1-019 | Shared API client (Axios with interceptors) | Frontend | 3 | Frontend Team | S1-012 |
| S1-020 | Shared hooks - useAuth, useToast | Frontend | 2 | Frontend Team | S1-019 |
| S1-021 | Frontend authentication integration | Frontend | 3 | Frontend Team | S1-020 |
| S1-022 | Unit tests for backend modules | Testing | 3 | Dev Team | S1-006, S1-009 |
| S1-023 | Unit tests for frontend components | Testing | 2 | Dev Team | S1-014, S1-015 |

**Sprint 1 Definition of Done:**
- ✅ Development environment runs with `docker-compose up`
- ✅ CI pipeline passes all tests on every commit
- ✅ Login endpoint returns JWT tokens
- ✅ Audit logs are created for test actions
- ✅ E-Signature records are created and verified
- ✅ Shared components are available in all apps
- ✅ Unit test coverage ≥ 70%

### 3.3 Sprint 2: Storekeeper + Sampler (January 29 - February 18, 2026)

| Sprint Goal | Key Deliverables |
|-------------|------------------|
| Implement Storekeeper and Sampler applications | Materials CRUD, Packaging CRUD, sampling workflow, notifications, labels, Storekeeper and Sampler UIs |

**Sprint 2 Backlog:**

| ID | Task | Type | Points | Owner | Dependencies |
|----|------|------|--------|-------|--------------|
| S2-001 | Materials module - Material model | Backend | 3 | Backend | S1-006 |
| S2-002 | Materials module - MaterialService | Backend | 5 | Backend | S2-001 |
| S2-003 | Materials module - MaterialSerializer | Backend | 3 | Backend | S2-001 |
| S2-004 | Materials module - MaterialViewSet | Backend | 5 | Backend | S2-002, S2-003 |
| S2-005 | Materials module - Permission classes | Backend | 2 | Backend | S2-004 |
| S2-006 | Materials module - Request sampling API | Backend | 3 | Backend | S2-004 |
| S2-007 | Materials module - Release label API | Backend | 3 | Backend | S2-004 |
| S2-008 | Packaging module - Packaging model | Backend | 2 | Backend | S1-006 |
| S2-009 | Packaging module - PackagingService | Backend | 3 | Backend | S2-008 |
| S2-010 | Packaging module - PackagingViewSet | Backend | 3 | Backend | S2-009 |
| S2-011 | Sampling module - Sample model | Backend | 3 | Backend | S2-001 |
| S2-012 | Sampling module - SampleService (record sampling) | Backend | 5 | Backend | S2-011 |
| S2-013 | Sampling module - SampleViewSet (combined list) | Backend | 5 | Backend | S2-012 |
| S2-014 | Notifications module - Notification model and API | Backend | 3 | Backend | S1-006 |
| S2-015 | Notifications module - NotificationService | Backend | 2 | Backend | S2-014 |
| S2-016 | Storekeeper App - Routing and layout | Frontend | 3 | Frontend | S1-012 |
| S2-017 | Storekeeper App - Materials table | Frontend | 5 | Frontend | S2-016 |
| S2-018 | Storekeeper App - Material form | Frontend | 5 | Frontend | S2-016 |
| S2-019 | Storekeeper App - Material view | Frontend | 3 | Frontend | S2-016 |
| S2-020 | Storekeeper App - Packaging table | Frontend | 3 | Frontend | S2-016 |
| S2-021 | Storekeeper App - Packaging form | Frontend | 3 | Frontend | S2-016 |
| S2-022 | Storekeeper App - Notification bell | Frontend | 3 | Frontend | S2-016 |
| S2-023 | Storekeeper App - Release label print | Frontend | 3 | Frontend | S2-016 |
| S2-024 | Storekeeper App - Stats cards | Frontend | 2 | Frontend | S2-016 |
| S2-025 | Sampler App - Routing and layout | Frontend | 3 | Frontend | S1-012 |
| S2-026 | Sampler App - Sampling requests list | Frontend | 5 | Frontend | S2-025 |
| S2-027 | Sampler App - Sampling form | Frontend | 5 | Frontend | S2-025 |
| S2-028 | Sampler App - Label preview | Frontend | 3 | Frontend | S2-025 |
| S2-029 | Sampler App - Sample history | Frontend | 3 | Frontend | S2-025 |
| S2-030 | Sampler App - Product samples form | Frontend | 5 | Frontend | S2-025 |
| S2-031 | Sampler App - Product history | Frontend | 3 | Frontend | S2-025 |
| S2-032 | API integration - Storekeeper app | Frontend | 3 | Frontend | S2-017, S2-004 |
| S2-033 | API integration - Sampler app | Frontend | 3 | Frontend | S2-026, S2-013 |
| S2-034 | Unit tests - Materials module | Testing | 3 | Backend | S2-004 |
| S2-035 | Unit tests - Packaging module | Testing | 2 | Backend | S2-010 |
| S2-036 | Unit tests - Sampling module | Testing | 3 | Backend | S2-013 |
| S2-037 | Unit tests - Storekeeper components | Testing | 3 | Frontend | S2-017 |
| S2-038 | Unit tests - Sampler components | Testing | 3 | Frontend | S2-026 |
| S2-039 | Integration tests - Materials workflow | Testing | 3 | QA | S2-004 |
| S2-040 | Integration tests - Sampling workflow | Testing | 3 | QA | S2-013 |

**Sprint 2 Definition of Done:**
- ✅ Storekeeper can register material (API + UI)
- ✅ Storekeeper can register packaging
- ✅ Storekeeper can request sampling (status update)
- ✅ Sampler sees pending requests
- ✅ Sampler can record a sample
- ✅ Label preview shows correct data
- ✅ Release label data generated
- ✅ Notifications created on release
- ✅ Unit test coverage ≥ 80%
- ✅ Integration tests pass

### 3.4 Sprint 3: Analyst + QC Manager (February 19 - March 10, 2026)

| Sprint Goal | Key Deliverables |
|-------------|------------------|
| Implement Analyst and QC Manager applications | Product samples, COA creation and status workflow, QC review, release workflow, admin console |

**Sprint 3 Backlog:**

| ID | Task | Type | Points | Owner | Dependencies |
|----|------|------|--------|-------|--------------|
| S3-001 | Product Samples module - ProductSample model | Backend | 3 | Backend | S1-006 |
| S3-002 | Product Samples module - ProductSampleService | Backend | 3 | Backend | S3-001 |
| S3-003 | Product Samples module - ProductSampleViewSet | Backend | 3 | Backend | S3-002 |
| S3-004 | COA module - COA model | Backend | 3 | Backend | S2-011, S3-001 |
| S3-005 | COA module - COAService (create, update, submit, complete) | Backend | 5 | Backend | S3-004 |
| S3-006 | COA module - COASerializer | Backend | 3 | Backend | S3-004 |
| S3-007 | COA module - COAViewSet | Backend | 5 | Backend | S3-005 |
| S3-008 | COA module - Approval workflow (approve/reject) | Backend | 5 | Backend | S3-007 |
| S3-009 | Release workflow - Material release with QC data | Backend | 5 | Backend | S3-008, S2-004 |
| S3-010 | COA module - E-signature integration | Backend | 3 | Backend | S1-011, S3-008 |
| S3-011 | COA module - Audit integration | Backend | 2 | Backend | S1-010, S3-008 |
| S3-012 | Analyst App - Routing and layout | Frontend | 2 | Frontend | S1-012 |
| S3-013 | Analyst App - Launcher cards | Frontend | 2 | Frontend | S3-012 |
| S3-014 | Analyst App - Combined samples worklist | Frontend | 5 | Frontend | S3-012 |
| S3-015 | Analyst App - COA form (auto-filled) | Frontend | 5 | Frontend | S3-012 |
| S3-016 | Analyst App - COA view | Frontend | 3 | Frontend | S3-012 |
| S3-017 | Analyst App - COA status actions (submit, complete) | Frontend | 3 | Frontend | S3-016 |
| S3-018 | Analyst App - Certificates list | Frontend | 3 | Frontend | S3-012 |
| S3-019 | QC Manager App - Routing and layout | Frontend | 2 | Frontend | S1-012 |
| S3-020 | QC Manager App - COA list | Frontend | 3 | Frontend | S3-019 |
| S3-021 | QC Manager App - COA detail view | Frontend | 3 | Frontend | S3-019 |
| S3-022 | QC Manager App - Approve/reject modal | Frontend | 5 | Frontend | S3-021 |
| S3-023 | QC Manager App - Release modal | Frontend | 5 | Frontend | S3-021 |
| S3-024 | Admin Console - Routing and layout | Frontend | 2 | Frontend | S1-012 |
| S3-025 | Admin Console - Employee list and management | Frontend | 5 | Frontend | S3-024 |
| S3-026 | Admin Console - Audit trail view | Frontend | 3 | Frontend | S3-024 |
| S3-027 | API integration - Analyst app | Frontend | 3 | Frontend | S3-014, S3-007 |
| S3-028 | API integration - QC Manager app | Frontend | 3 | Frontend | S3-020, S3-008 |
| S3-029 | Unit tests - Product Samples module | Testing | 3 | Backend | S3-003 |
| S3-030 | Unit tests - COA module | Testing | 3 | Backend | S3-007 |
| S3-031 | Unit tests - Release workflow | Testing | 3 | Backend | S3-009 |
| S3-032 | Unit tests - Analyst components | Testing | 3 | Frontend | S3-014 |
| S3-033 | Unit tests - QC Manager components | Testing | 3 | Frontend | S3-020 |
| S3-034 | Integration tests - COA workflow | Testing | 3 | QA | S3-007 |
| S3-035 | Integration tests - Release workflow | Testing | 3 | QA | S3-009 |

**Sprint 3 Definition of Done:**
- ✅ Product samples (FP/SFP/Bulk) can be registered
- ✅ Analyst sees combined worklist
- ✅ COA can be created (auto-filled)
- ✅ COA status workflow works: Draft → In Progress → Completed
- ✅ QC Manager can approve/reject COA
- ✅ Approve triggers release modal
- ✅ Release modal captures QC Number and Signature
- ✅ Admin can manage employees
- ✅ Audit trail view works
- ✅ Unit test coverage ≥ 80%
- ✅ Integration tests pass

### 3.5 Sprint 4: Integration + Testing (March 11-24, 2026)

| Sprint Goal | Key Deliverables |
|-------------|------------------|
| Complete integration, performance testing, security testing, and user acceptance testing | Fully tested system ready for production deployment |

**Sprint 4 Backlog:**

| ID | Task | Type | Points | Owner | Dependencies |
|----|------|------|--------|-------|--------------|
| S4-001 | API integration - End-to-end testing | Testing | 5 | QA | All backend |
| S4-002 | End-to-end workflow testing (Material → Release) | Testing | 5 | QA | All backend/frontend |
| S4-003 | Performance testing - k6 load tests | Testing | 3 | QA + DevOps | All backend |
| S4-004 | Performance optimisation | Backend | 3 | Backend | S4-003 |
| S4-005 | Security testing - OWASP ZAP | Testing | 3 | Security | All backend |
| S4-006 | Security vulnerability remediation | Backend | 3 | Backend | S4-005 |
| S4-007 | Cross-browser testing | Testing | 2 | QA | All frontend |
| S4-008 | Mobile responsive testing | Testing | 2 | QA | All frontend |
| S4-009 | Audit trail verification (all GMP actions) | Testing | 3 | QA + Compliance | S1-010 |
| S4-010 | E-signature verification | Testing | 2 | QA + Compliance | S1-011 |
| S4-011 | Defect triage and prioritisation | PM | 1 | PM | All |
| S4-012 | Critical defect resolution | Dev | 5 | Dev Team | S4-011 |
| S4-013 | High-priority defect resolution | Dev | 5 | Dev Team | S4-011 |
| S4-014 | Medium-priority defect resolution | Dev | 3 | Dev Team | S4-011 |
| S4-015 | Regression testing | Testing | 3 | QA | S4-012, S4-013 |
| S4-016 | User Acceptance Testing preparation | QA | 2 | QA | All |
| S4-017 | User Acceptance Testing execution | Testing | 5 | QA + Business | S4-016 |
| S4-018 | UAT defect resolution | Dev | 3 | Dev Team | S4-017 |
| S4-019 | API documentation (OpenAPI) | Backend | 2 | Backend | All backend |
| S4-020 | Deployment documentation | DevOps | 2 | DevOps | All |
| S4-021 | Performance test report | QA | 1 | QA | S4-003 |
| S4-022 | Security test report | Security | 1 | Security | S4-005 |

**Sprint 4 Definition of Done:**
- ✅ All end-to-end workflows tested and passing
- ✅ Performance tests pass (95th < 500ms)
- ✅ No critical or high severity vulnerabilities
- ✅ Cross-browser and responsive tests pass
- ✅ Audit trail and e-signature verified
- ✅ All critical and high-priority defects resolved
- ✅ UAT completed with sign-off
- ✅ API documentation complete
- ✅ Deployment documentation complete

### 3.6 Sprint 5: Deployment (March 25 - April 7, 2026)

| Sprint Goal | Key Deliverables |
|-------------|------------------|
| Deploy system to production with validation and go-live support | Production system operational, users trained, validation complete |

**Sprint 5 Backlog:**

| ID | Task | Type | Points | Owner | Dependencies |
|----|------|------|--------|-------|--------------|
| S5-001 | Validation documentation - IQ | Compliance | 3 | Compliance | All testing |
| S5-002 | Validation documentation - OQ | Compliance | 3 | Compliance | All testing |
| S5-003 | Validation documentation - PQ | Compliance | 3 | Compliance | S4-017 |
| S5-004 | Validation Report | Compliance | 2 | Compliance | S5-001, S5-002, S5-003 |
| S5-005 | User training materials (Storekeeper) | Training | 2 | SME | All |
| S5-006 | User training materials (Sampler) | Training | 2 | SME | All |
| S5-007 | User training materials (Analyst) | Training | 2 | SME | All |
| S5-008 | User training materials (QC Manager) | Training | 2 | SME | All |
| S5-009 | Administrator training materials | Training | 1 | SME | All |
| S5-010 | SOP development | Compliance | 5 | Compliance | All |
| S5-011 | End-user training sessions | Training | 3 | SME + Training | S5-005 to S5-009 |
| S5-012 | Staging environment deployment | DevOps | 2 | DevOps | All |
| S5-013 | Staging validation testing | QA + Compliance | 3 | QA | S5-012 |
| S5-014 | Production environment preparation | DevOps | 2 | DevOps | All |
| S5-015 | Data migration (if applicable) | DevOps | 3 | DevOps | S5-014 |
| S5-016 | Production deployment | DevOps | 3 | DevOps | S5-015 |
| S5-017 | Go-live smoke tests | QA | 2 | QA | S5-016 |
| S5-018 | Go-live verification | PM | 1 | PM | S5-017 |
| S5-019 | Post-go-live support (Week 1) | Support | 5 | All | S5-018 |
| S5-020 | Post-go-live support (Week 2) | Support | 3 | All | S5-019 |
| S5-021 | Go-live report | PM | 2 | PM | S5-020 |

**Sprint 5 Definition of Done:**
- ✅ Validation documentation complete and signed
- ✅ All user training delivered
- ✅ SOPs developed and approved
- ✅ Staging deployment validated
- ✅ Production deployment successful
- ✅ Go-live smoke tests passed
- ✅ Post-go-live support provided
- ✅ Go-live report delivered

---

## 4. Detailed Sprint Tasks

### 4.1 Sprint 1: Foundation

#### Day 1-2: Project Setup and Core Infrastructure

| Task | Steps | Estimated Hours | Team |
|------|-------|-----------------|------|
| **S1-001: Repository Setup** | 1. Create GitHub repository<br/>2. Configure branch protection rules<br/>3. Set up issue templates<br/>4. Configure CODEOWNERS | 4 | DevOps |
| **S1-002: Docker Compose** | 1. Create Dockerfile for Django<br/>2. Create docker-compose.yml<br/>3. Add PostgreSQL container<br/>4. Add Redis container<br/>5. Create entrypoint scripts | 6 | DevOps |
| **S1-003: CI/CD Pipeline** | 1. Create GitHub Actions workflow<br/>2. Add test step (pytest)<br/>3. Add linting step (flake8, isort, black)<br/>4. Add coverage reporting<br/>5. Configure auto-deploy to staging | 6 | DevOps |

**Code Example - Docker Compose:**

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: rm_rrs
      POSTGRES_USER: rm_rrs_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U rm_rrs_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./rm-rrs-backend
      dockerfile: docker/backend.Dockerfile
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://rm_rrs_user:${DB_PASSWORD}@postgres:5432/rm_rrs
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./rm-rrs-backend:/app
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: python manage.py runserver 0.0.0.0:8000

volumes:
  postgres_data:
```

#### Day 3-5: Backend Foundation

| Task | Steps | Estimated Hours | Team |
|------|-------|-----------------|------|
| **S1-004: Project Structure** | 1. Create Django project<br/>2. Create apps directory<br/>3. Configure settings (base, dev, prod)<br/>4. Set up URL routing | 4 | Backend Lead |
| **S1-005: Common Module** | 1. Create custom exceptions<br/>2. Create constants<br/>3. Create utilities (date formatting)<br/>4. Create base model mixins<br/>5. Create pagination classes | 8 | Backend Team |

**Code Example - Base Model:**

```python
# apps/common/models.py
from django.db import models
from django.utils import timezone
import uuid

class BaseModel(models.Model):
    """Abstract base model with common fields."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

# apps/common/exceptions.py
class BusinessRuleError(Exception):
    """Raised when a business rule is violated."""
    pass

class NotFoundError(BusinessRuleError):
    """Raised when a requested resource is not found."""
    pass

class ConflictError(BusinessRuleError):
    """Raised when there is a state conflict."""
    def __init__(self, message, details=None):
        self.details = details
        super().__init__(message)
```

#### Day 6-8: Users + Authentication

| Task | Steps | Estimated Hours | Team |
|------|-------|-----------------|------|
| **S1-006: Employee Model** | 1. Create Employee model<br/>2. Add fields (username, email, full_name, job_role)<br/>3. Create migrations<br/>4. Add admin configuration | 6 | Backend Team |
| **S1-007: Authentication** | 1. Install djangorestframework-simplejwt<br/>2. Create login/logout/refresh views<br/>3. Configure JWT settings<br/>4. Add token cookies | 8 | Backend Team |
| **S1-008: Permissions** | 1. Create Permission model<br/>2. Create Role model<br/>3. Create permission classes<br/>4. Add permission checking | 6 | Backend Team |

**Code Example - JWT Configuration:**

```python
# config/settings/base.py
from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_COOKIE': 'access_token',
    'AUTH_COOKIE_HTTP_ONLY': True,
    'AUTH_COOKIE_SECURE': True,
    'AUTH_COOKIE_SAMESITE': 'Strict',
}
```

#### Day 9-10: Audit + E-Signature

| Task | Steps | Estimated Hours | Team |
|------|-------|-----------------|------|
| **S1-009: Audit Module** | 1. Create AuditLog model<br/>2. Create AuditService<br/>3. Add Django signals<br/>4. Create Celery task for async audit | 8 | Backend Team |
| **S1-010: Audit Integration** | 1. Connect signals to models<br/>2. Add audit middleware<br/>3. Create admin view<br/>4. Test audit logging | 6 | Backend Team |
| **S1-011: E-Signature** | 1. Create ElectronicSignature model<br/>2. Create hashing utility<br/>3. Create SignatureService<br/>4. Add verification method | 6 | Backend Team |

### 4.2 Sprint 2: Storekeeper + Sampler

#### Week 1: Backend - Materials + Packaging

| Task | Steps | Estimated Hours | Team |
|------|-------|-----------------|------|
| **S2-001: Material Model** | 1. Define Material model fields<br/>2. Add choices for status/sampling<br/>3. Add indexes<br/>4. Create migrations | 8 | Backend |
| **S2-002: MaterialService** | 1. Implement create_material<br/>2. Implement update_material<br/>3. Implement list_materials<br/>4. Implement request_sampling<br/>5. Implement release_material | 12 | Backend |

**Code Example - MaterialService:**

```python
# apps/materials/services.py
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from decimal import Decimal

from apps.common.exceptions import BusinessRuleError, ConflictError
from apps.materials.models import Material
from apps.materials.serializers import MaterialSerializer
from apps.audit.services import AuditService
from apps.esignature.services import SignatureService
from apps.notifications.services import NotificationService

class MaterialService:
    def __init__(self, user):
        self.user = user
        self.audit_service = AuditService(user)
        self.signature_service = SignatureService(user)
        self.notification_service = NotificationService()

    @transaction.atomic
    def create_material(self, data):
        """Create a new material with audit logging."""
        # Validate data
        serializer = MaterialSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        # Generate receipt ID
        receipt_id = self._generate_receipt_id()
        
        # Create material
        material = Material.objects.create(
            receipt_id=receipt_id,
            **serializer.validated_data,
            created_by=self.user,
            updated_by=self.user,
            status='Quarantine',
            sampling_status='Not Sampled'
        )
        
        # Audit trail (async)
        self.audit_service.log_create(material)
        
        return material

    @transaction.atomic
    def request_sampling(self, material_id):
        """Request sampling on a material."""
        material = self.get_material(material_id)
        
        if material.sampling_status != 'Not Sampled':
            raise ConflictError(
                f"Sampling already {material.sampling_status.lower()}",
                details={'current_status': material.sampling_status}
            )
        
        material.sampling_status = 'Sampling Requested'
        material.updated_by = self.user
        material.save()
        
        self.audit_service.log_update(
            material,
            field_name='sampling_status',
            old_value='Not Sampled',
            new_value='Sampling Requested'
        )
        
        return material

    def _generate_receipt_id(self):
        """Generate a new receipt ID."""
        year = date.today().year
        count = Material.objects.filter(
            receipt_id__startswith=f'RCV-{year}'
        ).count() + 1
        return f'RCV-{year}-{count:04d}'
```

#### Week 2: Frontend - Storekeeper App

| Task | Steps | Estimated Hours | Team |
|------|-------|-----------------|------|
| **S2-016: Storekeeper Routing** | 1. Create App.tsx<br/>2. Configure React Router<br/>3. Create Layout component<br/>4. Add navigation tabs | 6 | Frontend |
| **S2-017: Materials Table** | 1. Create MaterialTable component<br/>2. Add search functionality<br/>3. Add filter by status<br/>4. Add pagination<br/>5. Integrate with React Query | 10 | Frontend |
| **S2-018: Material Form** | 1. Create MaterialForm component<br/>2. Add Zod validation<br/>3. Use React Hook Form<br/>4. Add auto-calculation<br/>5. Integrate API mutation | 10 | Frontend |

**Code Example - MaterialForm:**

```tsx
// apps/storekeeper/src/components/MaterialForm/MaterialForm.tsx
import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@shared/ui/Button';
import { Input } from '@shared/ui/Form/Input';
import { Select } from '@shared/ui/Form/Select';
import { DatePicker } from '@shared/ui/Form/DatePicker';
import { useCreateMaterial } from '../../hooks/useMaterials';
import { useToast } from '@shared/hooks/useToast';

// Validation schema
const materialSchema = z.object({
  material_name: z.string().min(1, 'Material name is required'),
  supplier: z.string().min(1, 'Supplier is required'),
  supplier_batch: z.string().min(1, 'Supplier batch is required'),
  exp_date: z.string().min(1, 'Expiry date is required'),
  receipt_date: z.string().min(1, 'Receipt date is required'),
  received_by: z.string().min(1, 'Received by is required'),
  category: z.string().optional(),
  manufacturer: z.string().optional(),
  batch_size: z.number().optional(),
  unit: z.string().optional(),
  package_type: z.string().optional(),
  num_packages: z.number().optional(),
  package_size: z.number().optional(),
});

type MaterialFormData = z.infer<typeof materialSchema>;

export const MaterialForm: React.FC = () => {
  const { showToast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const createMaterial = useCreateMaterial();

  const {
    control,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<MaterialFormData>({
    resolver: zodResolver(materialSchema),
    defaultValues: {
      receipt_date: new Date().toISOString().split('T')[0],
    },
  });

  const numPackages = watch('num_packages');
  const packageSize = watch('package_size');
  const totalQty = numPackages && packageSize ? numPackages * packageSize : null;

  const onSubmit = async (data: MaterialFormData) => {
    setIsSubmitting(true);
    try {
      await createMaterial.mutateAsync(data);
      showToast('Material registered successfully!', 'success');
    } catch (error) {
      showToast('Failed to register material.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="material-form">
      <div className="form-section">
        <h3>Material Information</h3>
        <div className="form-grid">
          <Controller
            name="material_name"
            control={control}
            render={({ field }) => (
              <Select
                {...field}
                label="Material Name *"
                options={[]}
                error={errors.material_name?.message}
              />
            )}
          />
          <Controller
            name="supplier"
            control={control}
            render={({ field }) => (
              <Select
                {...field}
                label="Supplier *"
                options={[]}
                error={errors.supplier?.message}
              />
            )}
          />
          {/* Additional fields */}
        </div>
      </div>
      
      <div className="form-actions">
        <Button variant="secondary" type="button">Cancel</Button>
        <Button type="submit" isLoading={isSubmitting}>Register Material</Button>
      </div>
    </form>
  );
};
```

#### Week 3: Frontend - Sampler App + Notifications

| Task | Steps | Estimated Hours | Team |
|------|-------|-----------------|------|
| **S2-025: Sampler Routing** | 1. Create Sampler App<br/>2. Configure 4 tabs<br/>3. Create Layout | 6 | Frontend |
| **S2-026: Sampling Requests** | 1. Display pending count<br/>2. Create pending table<br/>3. Add View/Sample buttons<br/>4. Filter functionality | 10 | Frontend |
| **S2-027: Sampling Form** | 1. Create SamplingForm<br/>2. Auto-fill material data<br/>3. Add validation<br/>4. Submit sample | 10 | Frontend |
| **S2-028: Label Preview** | 1. Create LabelPreview component<br/>2. Render two labels<br/>3. Add print functionality<br/>4. Use hidden print area | 8 | Frontend |

---

## 5. Task Prioritisation

### 5.1 Priority Matrix

| Priority | Definition | Examples |
|----------|------------|----------|
| **Critical** | Blocking other tasks; must be done first | Authentication, Database schema, API foundation |
| **High** | Core features for MVP | Material registration, Sampling workflow, COA creation |
| **Medium** | Important but can be deferred | Notifications, Admin console, Audit trail view |
| **Low** | Nice-to-have; post-MVP | Mobile responsiveness, Accessibility |

### 5.2 Task Prioritisation Map

```mermaid
flowchart TD
    subgraph Critical["CRITICAL"]
        C1["Authentication"]
        C2["Database Models"]
        C3["API Foundation"]
        C4["Project Structure"]
    end

    subgraph High["HIGH"]
        H1["Materials CRUD"]
        H2["Packaging CRUD"]
        H3["Sampling Workflow"]
        H4["COA Creation"]
        H5["COA Status Workflow"]
        H6["QC Approve/Reject"]
        H7["Release Workflow"]
    end

    subgraph Medium["MEDIUM"]
        M1["Notifications"]
        M2["Admin Console"]
        M3["Audit Trail View"]
        M4["Product Samples"]
        M5["Label Printing"]
    end

    subgraph Low["LOW"]
        L1["Mobile Responsive"]
        L2["Accessibility"]
        L3["Performance Optimisation"]
        L4["Extra Filtering"]
    end

    Critical --> High
    High --> Medium
    Medium --> Low
```

---

## 6. Dependencies and Sequencing

### 6.1 Task Dependency Graph

```mermaid
flowchart TD
    subgraph Backend["BACKEND DEPENDENCIES"]
        B1["Common Module"]
        B2["Users/Auth"]
        B3["Audit Module"]
        B4["E-Signature"]
        B5["Materials"]
        B6["Packaging"]
        B7["Samples"]
        B8["Notifications"]
        B9["COA"]
        B10["Release Workflow"]
    end

    B1 --> B2
    B1 --> B3
    B1 --> B4
    B2 --> B5
    B2 --> B6
    B2 --> B7
    B2 --> B8
    B2 --> B9
    B5 --> B7
    B6 --> B7
    B7 --> B9
    B9 --> B10
    B3 --> B9
    B4 --> B9
    B8 --> B10
```

### 6.2 External Dependencies

| Dependency | Owner | Status | Timeline |
|------------|-------|--------|----------|
| PostgreSQL 15+ | DevOps | Ready | Ongoing |
| Redis 7+ | DevOps | Ready | Ongoing |
| Docker/Docker Compose | DevOps | Ready | Ongoing |
| GitHub Actions | DevOps | Configured | Ongoing |
| Nginx Configuration | DevOps | To configure | Week 1 |
| SSL Certificates | DevOps | To obtain | Week 11 |
| DNS Configuration | Network Team | To set up | Week 11 |
| User Accounts (AD/LDAP) | IT | TBS | TBS |

---

## 7. Quality Gates

### 7.1 Quality Gate Definitions

| Quality Gate | Check | Passing Criteria |
|--------------|-------|------------------|
| **Gate 1: Code Quality** | Static analysis | No critical issues; < 20 major issues |
| **Gate 2: Test Coverage** | Unit test coverage | ≥ 80% on new code |
| **Gate 3: Integration** | Integration tests | All critical workflows pass |
| **Gate 4: Performance** | Load tests | 95th percentile < 500ms |
| **Gate 5: Security** | Security scans | No critical/high vulnerabilities |
| **Gate 6: Compliance** | Audit checks | All GMP actions audited |

### 7.2 Quality Gate Flow

```mermaid
flowchart TD
    QG1["Gate 1: Code Quality<br/>Linting + SAST"] --> QG2["Gate 2: Unit Tests<br/>≥80% coverage"]
    QG2 --> QG3["Gate 3: Integration<br/>All workflows"]
    QG3 --> QG4["Gate 4: Performance<br/>Load tests"]
    QG4 --> QG5["Gate 5: Security<br/>DAST"]
    QG5 --> QG6["Gate 6: Compliance<br/>Audit review"]
    QG6 --> MERGE["Merge to Main"]
```

### 7.3 Release Quality Gates

```mermaid
flowchart LR
    subgraph Gates["RELEASE QUALITY GATES"]
        R1["Unit Tests<br/>≥80% coverage"]
        R2["Integration Tests<br/>All passing"]
        R3["Performance Tests<br/>Passing"]
        R4["Security Tests<br/>No critical issues"]
        R5["UAT<br/>Sign-off"]
        R6["Validation<br/>Complete"]
    end

    R1 --> R2 --> R3 --> R4 --> R5 --> R6
```

---

## 8. Daily Development Workflow

### 8.1 Developer Daily Workflow

```mermaid
flowchart LR
    subgraph Morning["MORNING (9:00-11:00)"]
        Standup["9:00 - Daily Standup<br/>15 min"]
        Code["9:15 - Code<br/>2 hours"]
    end

    subgraph Midday["MIDDAY (11:00-15:00)"]
        Tests["11:00 - Write Tests<br/>1 hour"]
        Code2["12:00 - Code<br/>2 hours"]
        Lunch["13:00 - Lunch<br/>1 hour"]
        Code3["14:00 - Code<br/>1 hour"]
    end

    subgraph Afternoon["AFTERNOON (15:00-17:00)"]
        Review["15:00 - Code Review<br/>1 hour"]
        Integration["16:00 - Integration<br/>1 hour"]
        Commit["17:00 - Commit<br/>End of day"]
    end

    Standup --> Code --> Tests --> Code2 --> Lunch --> Code3 --> Review --> Integration --> Commit
```

### 8.2 Sprint Cadence

| Day | Activity | Time |
|-----|----------|------|
| **Monday** | Sprint Planning, Backlog refinement | 9:30-11:00 |
| **Tuesday-Thursday** | Development | All day |
| **Friday** | Code reviews, Demos | Afternoon |
| **End of Sprint** | Sprint Review, Retrospective | 2 hours |

### 8.3 Daily Standup Questions

1. **What did I complete yesterday?**
   - Share specific tasks completed, PRs merged
2. **What am I working on today?**
   - Share planned tasks, current focus
3. **What is blocking me?**
   - Identify dependencies, technical blockers

---

## 9. Code Review Process

### 9.1 Code Review Checklist

| Category | Check |
|----------|-------|
| **Functionality** | Does the code work as expected? |
| **Tests** | Are there adequate tests? Do they pass? |
| **Code Quality** | Is the code clear and maintainable? |
| **Style** | Does it follow coding standards? |
| **Security** | Are there security concerns? |
| **Performance** | Are there performance issues? |
| **Documentation** | Is it documented? |

### 9.2 Code Review Workflow

```mermaid
flowchart TD
    A[Developer creates PR] --> B[CI runs automated checks]
    B --> C[PR assigned to reviewer]
    C --> D{Reviewer reviews}
    D -->|Request changes| E[Developer addresses feedback]
    E --> C
    D -->|Approve| F[PR ready to merge]
    F --> G[Merge to main]
```

### 9.3 Review Time Commitments

| Role | Reviews Per Day | Review Time |
|------|-----------------|-------------|
| Tech Lead | 3-5 | 1-2 hours |
| Senior Dev | 2-4 | 1 hour |
| Junior Dev | 1-2 | 30 minutes |

---

## 10. Appendices

### A. Repository Structure

```
rm-rrs/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── rm-rrs-backend/
│   ├── apps/
│   ├── config/
│   ├── tests/
│   ├── requirements/
│   ├── docker/
│   └── manage.py
├── rm-rrs-frontend/
│   ├── apps/
│   ├── shared/
│   ├── package.json
│   └── pnpm-workspace.yaml
├── docker-compose.yml
├── docker-compose.prod.yml
└── README.md
```

### B. Git Branching Strategy

```mermaid
flowchart TD
    M["main<br/>(production)"]
    D["develop<br/>(staging)"]
    F1["feature/materials-api<br/>(feature branch)"]
    F2["feature/material-form<br/>(feature branch)"]
    H["hotfix/critical-bug<br/>(hotfix branch)"]

    M --> D
    D --> F1
    D --> F2
    F1 --> D
    F2 --> D
    M --> H
    H --> M
    H --> D
```

### C. Commit Message Examples

```bash
# Feature commit
git commit -m "feat(materials): add material registration form"

# Bug fix commit
git commit -m "fix(sampling): fix pending count display"

# Refactor commit
git commit -m "refactor(audit): extract audit service to separate module"

# Test commit
git commit -m "test(coa): add unit tests for COA service"

# Documentation commit
git commit -m "docs(api): update OpenAPI specification for materials endpoint"

# Style commit
git commit -m "style(components): fix formatting in MaterialForm"
```

### D. Coding Sprints Timeline

| Sprint | Start Date | End Date | Duration | Key Focus |
|--------|------------|----------|----------|-----------|
| Sprint 1 | 2026-01-15 | 2026-01-28 | 10 days | Foundation |
| Sprint 2 | 2026-01-29 | 2026-02-18 | 15 days | Storekeeper + Sampler |
| Sprint 3 | 2026-02-19 | 2026-03-10 | 15 days | Analyst + QC Manager |
| Sprint 4 | 2026-03-11 | 2026-03-24 | 10 days | Integration + Testing |
| Sprint 5 | 2026-03-25 | 2026-04-07 | 10 days | Deployment |

---

**Document Approval**

| Role | Name | Date |
|------|------|------|
| Author | [Name] | [Date] |
| Reviewer (Tech Lead) | [Name] | [Date] |
| Reviewer (Project Manager) | [Name] | [Date] |
| Approver | [Name] | [Date] |

---

**Change History**

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | [Date] | [Author] | Initial baseline coding roadmap |

