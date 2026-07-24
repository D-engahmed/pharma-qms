# 17/18 — Backend and Frontend Architecture

**Document Identifier:** RM-RRS-ARCH-001
**Version:** 1.0
**Status:** Baseline
**Traces to:** Project Charter, SRS, NFR, SAS, Design Specification, Security Specification
**Compliance Reference:** 12-Factor App, Django Best Practices, React Best Practices, Containerization Standards

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Backend Architecture](#2-backend-architecture)
3. [Frontend Architecture](#3-frontend-architecture)
4. [Cross-Cutting Concerns](#4-cross-cutting-concerns)
5. [Communication Patterns](#5-communication-patterns)
6. [Implementation Roadmap](#6-implementation-roadmap)
7. [Appendices](#7-appendices)

---

## 1. Introduction

### 1.1 Purpose
This document defines the detailed **Backend and Frontend Architecture** for the **Raw Material Receiving & Release System (RM-RRS)** . It provides the complete architectural blueprint for both the Django backend and React frontend applications, including module structures, component hierarchies, state management, API integration, security implementation, and deployment considerations. This document serves as the authoritative implementation guide for all development teams.

### 1.2 Scope
This architecture covers:
- **Backend**: Django application structure, module organisation, service layer, API design, database access, security implementation, Celery integration
- **Frontend**: React monorepo structure, component architecture, state management, routing, API client, shared utilities, build configuration
- **Cross-Cutting**: Authentication, authorisation, audit logging, error handling, logging, monitoring

### 1.3 Architecture Overview

```mermaid
flowchart TB
    subgraph Frontend["FRONTEND (React)"]
        direction TB
        SK["Storekeeper App"]
        SM["Sampler App"]
        AN["Analyst App"]
        QC["QC Manager App"]
        AD["Admin Console"]
        Shared["Shared Components<br/>API Client, Hooks, Utils"]
    end

    subgraph Gateway["API GATEWAY"]
        Nginx["Nginx Reverse Proxy"]
    end

    subgraph Backend["BACKEND (Django)"]
        subgraph API["API Layer"]
            Views["DRF Views/ViewSets"]
            Serializers["DRF Serializers"]
        end

        subgraph Services["Service Layer"]
            AuthSvc["Auth Service"]
            MatSvc["Materials Service"]
            PkgSvc["Packaging Service"]
            SampSvc["Samples Service"]
            COASvc["COA Service"]
            NotifSvc["Notification Service"]
            AuditSvc["Audit Service"]
            ESigSvc["E-Signature Service"]
        end

        subgraph Data["Data Layer"]
            ORM["Django ORM"]
            Models["Django Models"]
            Migrations["Django Migrations"]
        end
    end

    subgraph Infrastructure["INFRASTRUCTURE"]
        PG["PostgreSQL"]
        Redis["Redis"]
        Celery["Celery Workers"]
    end

    Frontend --> Gateway
    Gateway --> Backend
    Backend --> Infrastructure
```

---

## 2. Backend Architecture

### 2.1 Technology Stack

| Component | Technology | Version | Justification |
|-----------|------------|---------|---------------|
| Language | Python | 3.11+ | Charter confirmed; ecosystem maturity |
| Framework | Django | 4.2+ | Built-in ORM, admin, security, migrations |
| API Framework | Django REST Framework | 3.14+ | Robust API building, serialisers, permissions |
| Database | PostgreSQL | 15+ | ACID compliance, JSON support, GMP proven |
| Cache/Broker | Redis | 7+ | Session storage, Celery broker, caching |
| Task Queue | Celery | 5.3+ | Asynchronous audit logging, notifications |
| API Docs | drf-spectacular | — | OpenAPI 3.0 generation |
| Testing | pytest | 7.0+ | Django integration, fixtures, coverage |

### 2.2 Backend Project Structure

```
rm-rrs-backend/
├── manage.py
├── pyproject.toml                      # Dependencies and project metadata
├── requirements/
│   ├── base.txt                       # Production dependencies
│   ├── dev.txt                        # Development dependencies
│   ├── test.txt                       # Testing dependencies
│   └── prod.txt                       # Production only (Gunicorn, etc.)
├── .env.example                       # Environment variables template
├── docker/
│   ├── backend.Dockerfile             # Django application container
│   ├── celery.Dockerfile              # Celery worker container
│   ├── nginx.Dockerfile               # Nginx container
│   └── entrypoint.sh                  # Container entrypoint
├── config/                            # Django project configuration
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                    # Shared settings (all environments)
│   │   ├── development.py             # Development overrides
│   │   ├── production.py              # Production overrides
│   │   └── testing.py                 # Testing overrides
│   ├── urls.py                        # Root URL configuration
│   ├── wsgi.py                        # WSGI entry point
│   └── asgi.py                        # ASGI entry point (future)
├── apps/                              # Django applications (modules)
│   ├── __init__.py
│   ├── common/                        # Shared utilities
│   │   ├── __init__.py
│   │   ├── constants.py               # System-wide constants
│   │   ├── exceptions.py              # Custom exception classes
│   │   ├── mixins.py                  # Reusable model mixins
│   │   ├── pagination.py              # Custom pagination classes
│   │   ├── validators.py              # Shared validators
│   │   ├── utils.py                   # General utilities
│   │   └── enums.py                   # Django enumeration classes
│   ├── users/                         # Employee + Authentication
│   │   ├── __init__.py
│   │   ├── admin.py                   # Django admin configuration
│   │   ├── apps.py                    # App configuration
│   │   ├── models.py                  # Employee, Role, Permission models
│   │   ├── views.py                   # API views (login, logout, me)
│   │   ├── serializers.py             # User serializers
│   │   ├── services.py                # AuthService, PermissionService
│   │   ├── permissions.py             # Custom DRF permission classes
│   │   ├── validators.py              # User-specific validators
│   │   ├── urls.py                    # URL routing
│   │   ├── middleware.py              # Authentication middleware
│   │   └── tests/
│   │       ├── test_models.py
│   │       ├── test_serializers.py
│   │       ├── test_services.py
│   │       └── test_api.py
│   ├── materials/                     # Raw Material Management
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py                  # Material model
│   │   ├── views.py                   # Material API views
│   │   ├── serializers.py             # Material serializers
│   │   ├── services.py                # MaterialService
│   │   ├── validators.py              # Material validators
│   │   ├── urls.py
│   │   └── tests/
│   ├── packaging/                     # Packaging Material Management
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py                  # Packaging model
│   │   ├── views.py                   # Packaging API views
│   │   ├── serializers.py             # Packaging serializers
│   │   ├── services.py                # PackagingService
│   │   ├── validators.py
│   │   ├── urls.py
│   │   └── tests/
│   ├── sampling/                      # Sample Management (RM + Packaging)
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py                  # Sample model
│   │   ├── views.py                   # Sample API views
│   │   ├── serializers.py             # Sample serializers
│   │   ├── services.py                # SampleService
│   │   ├── validators.py
│   │   ├── urls.py
│   │   └── tests/
│   ├── products/                      # Product Sample Management (FP/SFP/Bulk)
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py                  # ProductSample model
│   │   ├── views.py                   # Product Sample API views
│   │   ├── serializers.py             # Product Sample serializers
│   │   ├── services.py                # ProductSampleService
│   │   ├── validators.py
│   │   ├── urls.py
│   │   └── tests/
│   ├── coa/                           # COA + QC Review
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py                  # COA model
│   │   ├── views.py                   # COA API views
│   │   ├── serializers.py             # COA serializers
│   │   ├── services.py                # COAService
│   │   ├── validators.py              # COA validators
│   │   ├── urls.py
│   │   └── tests/
│   ├── notifications/                 # In-app Notifications
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py                  # Notification model
│   │   ├── views.py                   # Notification API views
│   │   ├── serializers.py             # Notification serializers
│   │   ├── services.py                # NotificationService
│   │   ├── urls.py
│   │   └── tests/
│   ├── audit/                         # Audit Trail
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py                  # AuditLog model
│   │   ├── views.py                   # Audit API views
│   │   ├── serializers.py             # Audit serializers
│   │   ├── services.py                # AuditService
│   │   ├── signals.py                 # Django signals for audit
│   │   ├── middleware.py              # Audit context middleware
│   │   ├── urls.py
│   │   └── tests/
│   └── esignature/                    # Electronic Signatures
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py                  # ElectronicSignature model
│       ├── views.py                   # Signature API views
│       ├── serializers.py             # Signature serializers
│       ├── services.py                # SignatureService
│       ├── hashing.py                 # Cryptographic utilities
│       ├── urls.py
│       └── tests/
├── middleware/                        # Global middleware
│   ├── __init__.py
│   ├── audit_middleware.py            # Capture request context for audit
│   ├── permissions_middleware.py      # Enforce permissions at request level
│   └── logging_middleware.py          # Structured request logging
├── tasks/                             # Celery tasks
│   ├── __init__.py
│   ├── audit_tasks.py                 # Asynchronous audit logging
│   ├── notification_tasks.py          # Notification creation
│   ├── cleanup_tasks.py               # Data purging (future)
│   └── reporting_tasks.py             # Scheduled reports (future)
├── celery.py                          # Celery app configuration
├── celerybeat-schedule                # Celery Beat schedule file
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── fixtures/
│   │   ├── test_data.json             # Base test fixtures
│   │   └── sample_data.json           # Sample data for development
│   ├── unit/                          # Unit tests
│   │   ├── test_models.py
│   │   ├── test_serializers.py
│   │   ├── test_services.py
│   │   └── test_validators.py
│   ├── integration/                   # Integration tests
│   │   ├── test_api.py
│   │   ├── test_workflows.py
│   │   └── test_audit.py
│   └── e2e/                           # End-to-end tests
│       └── test_end_to_end.py
├── scripts/
│   ├── seed_data.py                   # Data seeding script
│   └── test_data_generator.py         # Test data generation
└── docs/
    └── api/
        └── openapi.yaml               # Auto-generated API docs
```

### 2.3 Module Dependencies

```mermaid
flowchart TD
    subgraph Apps["DJANGO APPLICATIONS"]
        Common["common<br/>Utilities, constants, exceptions"]
        Users["users<br/>Authentication, RBAC"]
        Materials["materials<br/>Raw material CRUD"]
        Packaging["packaging<br/>Packaging CRUD"]
        Sampling["sampling<br/>Sample management"]
        Products["products<br/>Product samples"]
        COA["coa<br/>COA + QC review"]
        Notifications["notifications<br/>In-app notifications"]
        Audit["audit<br/>Audit trail"]
        ESignature["esignature<br/>Electronic signatures"]
    end

    subgraph Services["SERVICES"]
        AuthSvc["AuthService"]
        MatSvc["MaterialService"]
        PkgSvc["PackagingService"]
        SampSvc["SampleService"]
        ProdSvc["ProductSampleService"]
        CoaSvc["COAService"]
        NotifSvc["NotificationService"]
        AuditSvc["AuditService"]
        ESigSvc["SignatureService"]
    end

    %% Dependencies
    Common --> Users
    Common --> Materials
    Common --> Packaging
    Common --> Sampling
    Common --> Products
    Common --> COA
    Common --> Notifications
    Common --> Audit
    Common --> ESignature

    Users --> Materials
    Users --> Packaging
    Users --> Sampling
    Users --> Products
    Users --> COA
    Users --> Notifications
    Users --> Audit
    Users --> ESignature

    Materials --> Sampling
    Packaging --> Sampling
    Sampling --> Products
    Products --> COA
    Sampling --> COA
    COA --> Notifications
    COA --> Audit
    COA --> ESignature

    Audit --> ESignature
    Audit --> Users
```

### 2.4 Service Layer Architecture

```mermaid
flowchart TD
    subgraph Services["SERVICE LAYER PATTERNS"]
        direction TB
        S1["Service Class<br/>Domain logic, validation, orchestration"]
        S2["Repository Pattern<br/>Data access abstraction (Django ORM)"]
        S3["DTO Pattern<br/>Data Transfer Objects for API"]
        S4["Factory Pattern<br/>Object creation for complex entities"]
    end

    subgraph ServiceExamples["EXAMPLE: MaterialService"]
        SE1["create_material(data) → Material"]
        SE2["update_material(id, data) → Material"]
        SE3["get_material(id) → Material"]
        SE4["list_materials(filters) → QuerySet"]
        SE5["request_sampling(id) → Material"]
        SE6["release_material(id, qc_data) → Material"]
        SE7["get_release_label(id) → dict"]
    end
```

**Service Class Template:**

```python
# apps/materials/services.py
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.common.exceptions import BusinessRuleError, ConflictError
from apps.materials.models import Material
from apps.materials.serializers import MaterialSerializer
from apps.audit.services import AuditService
from apps.esignature.services import SignatureService
from apps.notifications.services import NotificationService

class MaterialService:
    """Service layer for Material operations."""

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

        # Create material
        material = Material.objects.create(
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

        # Business rule check
        if material.sampling_status != 'Not Sampled':
            raise ConflictError(
                "Sampling already requested or completed",
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

    @transaction.atomic
    def release_material(self, material_id, qc_data):
        """Release a material after QC approval."""
        material = self.get_material(material_id)

        # Validate QC data
        if not qc_data.get('qc_number'):
            raise ValidationError("QC Number is required")
        if not qc_data.get('qc_signature'):
            raise ValidationError("QC Signature is required")

        # Calculate retest date (release date + 1 year)
        from datetime import date, timedelta
        release_date = date.today()
        retest_date = release_date + timedelta(days=365)

        # Update material
        material.status = 'Released'
        material.qc_number = qc_data['qc_number']
        material.qc_sign = qc_data['qc_signature']
        material.retest_date = retest_date
        material.released_date = release_date
        material.updated_by = self.user
        material.save()

        # Create electronic signature
        self.signature_service.create_signature(
            meaning='Release Material',
            record_type='material',
            record_id=material.receipt_id,
            reason=f"QC Number: {qc_data['qc_number']}"
        )

        # Audit trail
        self.audit_service.log_update(material)

        # Create notification for storekeeper
        self.notification_service.create_notification(
            target_role='storekeeper',
            title=f"Material Released: {material.material_name}",
            message=(
                f"Receipt ID: {material.receipt_id} · "
                f"QC No: {qc_data['qc_number']} · "
                f"Retest by: {retest_date.strftime('%d/%m/%Y')}"
            )
        )

        return material

    def get_material(self, material_id):
        """Get a material by ID."""
        try:
            return Material.objects.get(id=material_id)
        except Material.DoesNotExist:
            raise NotFoundError(f"Material {material_id} not found")

    def list_materials(self, filters=None):
        """List materials with filtering."""
        queryset = Material.objects.all()
        if filters:
            if filters.get('status'):
                queryset = queryset.filter(status=filters['status'])
            if filters.get('sampling_status'):
                queryset = queryset.filter(
                    sampling_status=filters['sampling_status']
                )
            if filters.get('search'):
                queryset = queryset.filter(
                    Q(material_name__icontains=filters['search']) |
                    Q(receipt_id__icontains=filters['search']) |
                    Q(supplier_batch__icontains=filters['search'])
                )
        return queryset
```

### 2.5 API Layer Architecture

```mermaid
flowchart TD
    subgraph API["API LAYER"]
        V1["ViewSet<br/>CRUD operations"]
        V2["APIView<br/>Custom endpoints"]
        V3["Permission Classes<br/>Access control"]
        V4["Authentication Classes<br/>JWT validation"]
        V5["Pagination Classes<br/>Page size/offset"]
        V6["Filter Backends<br/>Search, filter, sort"]
    end

    subgraph Request["REQUEST FLOW"]
        R1["Request"] --> R2["Authentication"]
        R2 --> R3["Permission Check"]
        R3 --> R4["View Logic"]
        R4 --> R5["Service Layer"]
        R5 --> R6["Response"]
    end
```

**ViewSet Template:**

```python
# apps/materials/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.materials.models import Material
from apps.materials.serializers import (
    MaterialSerializer,
    MaterialListSerializer,
    MaterialDetailSerializer,
    RequestSamplingSerializer,
    ReleaseLabelSerializer
)
from apps.materials.services import MaterialService
from apps.materials.permissions import HasMaterialPermission
from apps.common.pagination import StandardResultsSetPagination

class MaterialViewSet(viewsets.ModelViewSet):
    """API endpoint for Materials."""

    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated, HasMaterialPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'sampling_status']
    search_fields = ['receipt_id', 'material_name', 'supplier_batch']
    ordering_fields = ['receipt_id', 'created_at', 'material_name']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return MaterialListSerializer
        if self.action == 'retrieve':
            return MaterialDetailSerializer
        if self.action == 'request_sampling':
            return RequestSamplingSerializer
        if self.action == 'release_label':
            return ReleaseLabelSerializer
        return MaterialSerializer

    def get_service(self):
        """Get MaterialService instance with current user."""
        return MaterialService(self.request.user)

    def perform_create(self, serializer):
        """Create material with service layer."""
        service = self.get_service()
        material = service.create_material(serializer.validated_data)
        serializer.instance = material

    @action(detail=True, methods=['post'])
    def request_sampling(self, request, pk=None):
        """Request sampling on a material."""
        service = self.get_service()
        try:
            material = service.request_sampling(pk)
            serializer = self.get_serializer(material)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ConflictError as e:
            return Response(
                {'errors': [{'code': 'CONFLICT', 'message': str(e)}]},
                status=status.HTTP_409_CONFLICT
            )

    @action(detail=True, methods=['get'])
    def release_label(self, request, pk=None):
        """Get release label data for a material."""
        service = self.get_service()
        material = service.get_material(pk)

        if material.status != 'Released':
            return Response(
                {'errors': [{
                    'code': 'UNPROCESSABLE_ENTITY',
                    'message': 'Material must be released to generate label'
                }]},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        label_data = service.get_release_label(pk)
        return Response({'data': label_data})
```

### 2.6 Database Access Layer

```mermaid
flowchart TD
    subgraph DAL["DATABASE ACCESS LAYER"]
        M1["Django Models<br/>Table definitions, relationships"]
        M2["Django ORM<br/>Query building, execution"]
        M3["Migrations<br/>Schema version control"]
        M4["Raw SQL<br/>Complex queries (rare)"]
        M5["Connection Pooling<br/>PgBouncer / Django"]
    end

    subgraph ModelExample["EXAMPLE: Material Model"]
        ME1["class Material(models.Model):"]
        ME2["    receipt_id = models.CharField(max_length=20, unique=True)"]
        ME3["    material_name = models.CharField(max_length=100)"]
        ME4["    supplier = models.CharField(max_length=100)"]
        ME5["    supplier_batch = models.CharField(max_length=50)"]
        ME6["    status = models.CharField(max_length=20, default='Quarantine')"]
        ME7["    sampling_status = models.CharField(max_length=20, default='Not Sampled')"]
        ME8["    created_by = models.ForeignKey('users.Employee', ...)"]
        ME9["    created_at = models.DateTimeField(auto_now_add=True)"]
        ME10["    updated_at = models.DateTimeField(auto_now=True)"]
    end
```

### 2.7 Celery Configuration

```python
# celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
app = Celery('rm_rrs')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# tasks/audit_tasks.py
from celery import shared_task
from apps.audit.services import AuditService

@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def log_audit_task(self, user_id, action, entity_type, entity_id, old_value, new_value):
    """Asynchronous audit logging task."""
    try:
        service = AuditService(user_id)
        service.create_audit_entry(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value
        )
    except Exception as e:
        self.retry(exc=e)

# tasks/notification_tasks.py
@shared_task
def create_notification_task(target_role, title, message):
    """Asynchronous notification creation task."""
    from apps.notifications.services import NotificationService
    service = NotificationService()
    service.create_notification(
        target_role=target_role,
        title=title,
        message=message
    )
```

---

## 3. Frontend Architecture

### 3.1 Technology Stack

| Component | Technology | Version | Justification |
|-----------|------------|---------|---------------|
| Language | TypeScript | 5.0+ | Type safety for large codebase |
| Framework | React | 18.0+ | Charter confirmed; component model |
| Build Tool | Vite | 5.0+ | Fast builds, HMR, modern |
| Package Manager | pnpm | 8.0+ | Workspace support, disk efficient |
| Routing | React Router | 6.0+ | Declarative routing, nested routes |
| API Client | Axios | 1.6+ | Charter confirmed; interceptors |
| Server State | TanStack Query | 5.0+ | Caching, revalidation, mutations |
| Client State | Zustand | 4.0+ | Simple, scalable state management |
| Forms | React Hook Form | 7.0+ | Performance, validation integration |
| Validation | Zod | 3.0+ | Schema validation, TypeScript integration |
| UI Framework | MUI or Ant Design | — | Charter TBS |
| Testing | Jest + React Testing Library | — | Unit and component testing |
| E2E | Cypress | 13.0+ | End-to-end workflow testing |

### 3.2 Frontend Project Structure

```
rm-rrs-frontend/
├── package.json                          # Root package.json
├── pnpm-workspace.yaml                   # Workspace configuration
├── turbo.json                            # Build orchestration (TurboRepo)
├── .eslintrc.js                          # ESLint configuration
├── .prettierrc.js                        # Prettier configuration
├── tsconfig.base.json                    # Shared TypeScript config
├── vitest.config.ts                      # Vitest configuration
├── .env.example                          # Environment variables template
├── .github/
│   └── workflows/
│       ├── ci.yml                        # CI pipeline
│       └── deploy.yml                    # Deployment pipeline
├── docker/
│   └── frontend.Dockerfile               # Frontend container
├── shared/                               # Shared packages
│   ├── ui/                               # Shared UI components
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── components/
│   │   │   │   ├── Button/
│   │   │   │   │   ├── Button.tsx
│   │   │   │   │   ├── Button.module.css
│   │   │   │   │   ├── Button.test.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   ├── Table/
│   │   │   │   │   ├── Table.tsx
│   │   │   │   │   ├── Table.module.css
│   │   │   │   │   └── index.ts
│   │   │   │   ├── Modal/
│   │   │   │   │   ├── Modal.tsx
│   │   │   │   │   ├── Modal.module.css
│   │   │   │   │   └── index.ts
│   │   │   │   ├── Badge/
│   │   │   │   │   ├── Badge.tsx
│   │   │   │   │   ├── Badge.module.css
│   │   │   │   │   └── index.ts
│   │   │   │   ├── StatusBadge/
│   │   │   │   │   ├── StatusBadge.tsx
│   │   │   │   │   ├── StatusBadge.module.css
│   │   │   │   │   └── index.ts
│   │   │   │   ├── Label/
│   │   │   │   │   ├── Label.tsx
│   │   │   │   │   ├── Label.module.css
│   │   │   │   │   └── index.ts
│   │   │   │   ├── Toast/
│   │   │   │   │   ├── Toast.tsx
│   │   │   │   │   ├── Toast.module.css
│   │   │   │   │   └── index.ts
│   │   │   │   ├── PrintArea/
│   │   │   │   │   ├── PrintArea.tsx
│   │   │   │   │   ├── PrintArea.module.css
│   │   │   │   │   └── index.ts
│   │   │   │   ├── StatsCard/
│   │   │   │   │   ├── StatsCard.tsx
│   │   │   │   │   ├── StatsCard.module.css
│   │   │   │   │   └── index.ts
│   │   │   │   ├── SearchBar/
│   │   │   │   │   ├── SearchBar.tsx
│   │   │   │   │   ├── SearchBar.module.css
│   │   │   │   │   └── index.ts
│   │   │   │   └── Form/
│   │   │   │       ├── Input.tsx
│   │   │   │       ├── Select.tsx
│   │   │   │       ├── DatePicker.tsx
│   │   │   │       ├── Textarea.tsx
│   │   │   │       ├── Checkbox.tsx
│   │   │   │       └── index.ts
│   │   │   ├── hooks/
│   │   │   │   ├── useToast.ts
│   │   │   │   └── useMediaQuery.ts
│   │   │   ├── styles/
│   │   │   │   ├── theme.ts
│   │   │   │   ├── colors.ts
│   │   │   │   ├── typography.ts
│   │   │   │   └── spacing.ts
│   │   │   └── utils/
│   │   │       └── formatters.ts
│   │   └── tsconfig.json
│   ├── api/                              # Shared API client
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── client.ts                # Axios instance
│   │   │   ├── auth.ts                  # Auth endpoints
│   │   │   ├── materials.ts             # Materials endpoints
│   │   │   ├── packaging.ts             # Packaging endpoints
│   │   │   ├── samples.ts               # Samples endpoints
│   │   │   ├── products.ts              # Product samples endpoints
│   │   │   ├── coa.ts                   # COA endpoints
│   │   │   ├── notifications.ts         # Notifications endpoints
│   │   │   ├── employees.ts             # Employees endpoints
│   │   │   ├── audit.ts                 # Audit endpoints
│   │   │   ├── types.ts                 # Shared types/interfaces
│   │   │   └── interceptors.ts          # Request/response interceptors
│   │   └── tsconfig.json
│   ├── hooks/                            # Shared React hooks
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── useAuth.ts
│   │   │   ├── useApi.ts
│   │   │   ├── useQuery.ts
│   │   │   ├── useMutation.ts
│   │   │   ├── useToast.ts
│   │   │   ├── useNotifications.ts
│   │   │   ├── useDebounce.ts
│   │   │   └── usePrint.ts
│   │   └── tsconfig.json
│   └── utils/                            # Shared utilities
│       ├── package.json
│       ├── src/
│       │   ├── index.ts
│       │   ├── formatters.ts             # Date, number formatting
│       │   ├── validators.ts             # Zod schemas
│       │   ├── dateHelpers.ts            # Date utilities
│       │   ├── idGenerators.ts           # ID generation
│       │   ├── constants.ts              # System constants
│       │   └── validation.ts             # Shared validation rules
│       └── tsconfig.json
├── apps/                                 # Application packages
│   ├── storekeeper/                      # Storekeeper App
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── index.html
│   │   ├── src/
│   │   │   ├── main.tsx                  # Entry point
│   │   │   ├── App.tsx                   # Root component
│   │   │   ├── App.module.css
│   │   │   ├── providers.tsx             # Context providers
│   │   │   ├── routes/
│   │   │   │   ├── index.ts              # Route configuration
│   │   │   │   ├── Layout.tsx            # Layout wrapper
│   │   │   │   ├── Materials.tsx         # Materials page
│   │   │   │   ├── Packaging.tsx         # Packaging page
│   │   │   │   └── Notifications.tsx     # Notifications page
│   │   │   ├── components/
│   │   │   │   ├── MaterialTable.tsx
│   │   │   │   ├── MaterialForm.tsx
│   │   │   │   ├── MaterialView.tsx
│   │   │   │   ├── PackagingTable.tsx
│   │   │   │   ├── PackagingForm.tsx
│   │   │   │   ├── PackagingView.tsx
│   │   │   │   ├── StatsCards.tsx
│   │   │   │   ├── NotificationBell.tsx
│   │   │   │   ├── NotificationList.tsx
│   │   │   │   └── ReleaseLabel.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useMaterials.ts
│   │   │   │   └── usePackaging.ts
│   │   │   ├── stores/
│   │   │   │   └── useAppStore.ts
│   │   │   └── types/
│   │   │       └── index.ts
│   │   └── tsconfig.json
│   ├── sampler/                          # Sampler App
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── index.html
│   │   ├── src/
│   │   │   ├── main.tsx
│   │   │   ├── App.tsx
│   │   │   ├── providers.tsx
│   │   │   ├── routes/
│   │   │   │   ├── index.ts
│   │   │   │   ├── Layout.tsx
│   │   │   │   ├── SamplingRequests.tsx
│   │   │   │   ├── SampleHistory.tsx
│   │   │   │   ├── ProductSamples.tsx
│   │   │   │   └── ProductHistory.tsx
│   │   │   ├── components/
│   │   │   │   ├── SamplingTable.tsx
│   │   │   │   ├── SamplingForm.tsx
│   │   │   │   ├── LabelPreview.tsx
│   │   │   │   ├── ProductSampleForm.tsx
│   │   │   │   ├── ProductHistoryTable.tsx
│   │   │   │   └── PendingCounter.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useSamples.ts
│   │   │   │   └── useProductSamples.ts
│   │   │   └── stores/
│   │   │       └── useSampleStore.ts
│   │   └── tsconfig.json
│   ├── analyst/                          # Analyst App
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── index.html
│   │   ├── src/
│   │   │   ├── main.tsx
│   │   │   ├── App.tsx
│   │   │   ├── providers.tsx
│   │   │   ├── routes/
│   │   │   │   ├── index.ts
│   │   │   │   ├── Layout.tsx
│   │   │   │   ├── Home.tsx             # Launcher
│   │   │   │   ├── Samples.tsx
│   │   │   │   └── Certificates.tsx
│   │   │   ├── components/
│   │   │   │   ├── LauncherCards.tsx
│   │   │   │   ├── SampleWorklist.tsx
│   │   │   │   ├── COAForm.tsx
│   │   │   │   ├── COAView.tsx
│   │   │   │   ├── CertificatesList.tsx
│   │   │   │   └── MonographStub.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useSamples.ts
│   │   │   │   └── useCOA.ts
│   │   │   └── stores/
│   │   │       └── useAnalystStore.ts
│   │   └── tsconfig.json
│   ├── qcmanager/                        # QC Manager App
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── index.html
│   │   ├── src/
│   │   │   ├── main.tsx
│   │   │   ├── App.tsx
│   │   │   ├── providers.tsx
│   │   │   ├── routes/
│   │   │   │   ├── index.ts
│   │   │   │   ├── Layout.tsx
│   │   │   │   └── COAReview.tsx
│   │   │   ├── components/
│   │   │   │   ├── COAList.tsx
│   │   │   │   ├── COADetail.tsx
│   │   │   │   ├── ReleaseModal.tsx
│   │   │   │   └── QCActionModal.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useCOA.ts
│   │   │   └── stores/
│   │   │       └── useQCMStore.ts
│   │   └── tsconfig.json
│   └── admin/                            # Admin Console
│       ├── package.json
│       ├── vite.config.ts
│       ├── index.html
│       ├── src/
│       │   ├── main.tsx
│       │   ├── App.tsx
│       │   ├── providers.tsx
│       │   ├── routes/
│       │   │   ├── index.ts
│       │   │   ├── Layout.tsx
│       │   │   ├── Employees.tsx
│       │   │   ├── AuditLog.tsx
│       │   │   └── Roles.tsx
│       │   ├── components/
│       │   │   ├── EmployeeTable.tsx
│       │   │   ├── EmployeeForm.tsx
│       │   │   ├── AuditView.tsx
│       │   │   └── RoleList.tsx
│       │   ├── hooks/
│       │   │   ├── useEmployees.ts
│       │   │   └── useAudit.ts
│       │   └── stores/
│       │       └── useAdminStore.ts
│       └── tsconfig.json
└── deployment/                           # Deployment configuration
    ├── docker-compose.yml
    └── nginx.conf
```

### 3.3 Frontend Component Architecture

```mermaid
flowchart TD
    subgraph Structure["COMPONENT ARCHITECTURE"]
        direction TB
        Pages["Pages<br/>Route-level components"]
        Layouts["Layouts<br/>Shared layout wrappers"]
        Features["Features<br/>Feature-specific components"]
        Shared["Shared Components<br/>Reusable UI elements"]
        Hooks["Custom Hooks<br/>Logic reuse"]
        Stores["Stores<br/>State management"]
    end

    subgraph DataFlow["DATA FLOW"]
        API["API Client"] --> Query["React Query"]
        Query --> Components["Components"]
        Components --> Stores["Zustand Stores"]
        Stores --> Components
        Components --> Mutations["React Query Mutations"]
        Mutations --> API
    end
```

### 3.4 State Management Architecture

```mermaid
flowchart TD
    subgraph State["STATE MANAGEMENT"]
        subgraph ServerState["SERVER STATE (React Query)"]
            Q1["useQuery()<br/>Data fetching, caching, revalidation"]
            Q2["useMutation()<br/>Create, update, delete"]
            Q3["queryClient<br/>Global cache management"]
        end

        subgraph ClientState["CLIENT STATE (Zustand)"]
            Z1["Auth Store<br/>User, token, role"]
            Z2["UI Store<br/>Theme, modal state, notifications"]
            Z3["Form Store<br/>Form data, validation state"]
        end

        subgraph LocalState["LOCAL STATE"]
            L1["useState<br/>Component-specific state"]
            L2["useReducer<br/>Complex local state"]
            L3["useRef<br/>Mutable references"]
        end
    end
```

**React Query Configuration:**

```typescript
// shared/api/client.ts
import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000,           // 30 seconds
      cacheTime: 300000,          // 5 minutes
      retry: 1,
      refetchOnWindowFocus: true,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 0,
      onError: (error) => {
        // Global error handling
      }
    }
  }
})

// shared/hooks/useQuery.ts
import { useQuery as useRQ, useMutation as useRQM } from '@tanstack/react-query'
import { api } from '../api/client'

export const useMaterials = (filters?: MaterialFilters) => {
  return useRQ({
    queryKey: ['materials', filters],
    queryFn: () => api.materials.list(filters),
  })
}

export const useCreateMaterial = () => {
  return useRQM({
    mutationFn: (data: CreateMaterialData) => api.materials.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['materials'] })
    }
  })
}
```

**Zustand Store Example:**

```typescript
// apps/storekeeper/stores/useAppStore.ts
import { create } from 'zustand'

interface AppState {
  // Notification state
  notifications: Notification[]
  unreadCount: number
  addNotification: (notification: Notification) => void
  markAsRead: (id: string) => void
  dismissAll: () => void

  // UI state
  isLoading: boolean
  setLoading: (loading: boolean) => void
}

export const useAppStore = create<AppState>((set, get) => ({
  notifications: [],
  unreadCount: 0,

  addNotification: (notification) => {
    set((state) => ({
      notifications: [notification, ...state.notifications],
      unreadCount: state.unreadCount + 1
    }))
  },

  markAsRead: (id) => {
    set((state) => ({
      notifications: state.notifications.map(n =>
        n.id === id ? { ...n, read: true } : n
      ),
      unreadCount: state.notifications.filter(n => n.id === id && !n.read).length
        ? state.unreadCount - 1
        : state.unreadCount
    }))
  },

  dismissAll: () => {
    set({ notifications: [], unreadCount: 0 })
  },

  isLoading: false,
  setLoading: (loading) => set({ isLoading: loading })
}))
```

### 3.5 API Client Architecture

```typescript
// shared/api/client.ts
import axios, { AxiosInstance, AxiosError } from 'axios'
import { useNavigate } from 'react-router-dom'

class ApiClient {
  private axios: AxiosInstance
  private isRefreshing = false
  private refreshSubscribers: ((token: string) => void)[] = []

  constructor() {
    this.axios = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL,
      timeout: 30000,
      withCredentials: true,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // Request interceptor
    this.axios.interceptors.request.use(
      (config) => {
        // Add correlation ID
        config.headers['X-Correlation-ID'] = this.generateCorrelationId()
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor
    this.axios.interceptors.response.use(
      (response) => response.data,
      async (error: AxiosError) => {
        const originalRequest = error.config

        // Handle 401 Unauthorized
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true
          return this.handleTokenRefresh(originalRequest)
        }

        // Handle other errors
        return Promise.reject(this.normalizeError(error))
      }
    )
  }

  private async handleTokenRefresh(originalRequest: any) {
    try {
      if (!this.isRefreshing) {
        this.isRefreshing = true
        await axios.post(
          `${import.meta.env.VITE_API_BASE_URL}/auth/refresh/`,
          {},
          { withCredentials: true }
        )
        this.isRefreshing = false
        this.refreshSubscribers.forEach(cb => cb('token'))
        this.refreshSubscribers = []
      }

      return new Promise((resolve) => {
        this.refreshSubscribers.push(() => {
          resolve(this.axios(originalRequest))
        })
      })
    } catch (error) {
      this.isRefreshing = false
      this.refreshSubscribers = []
      // Redirect to login
      window.location.href = '/login'
      return Promise.reject(error)
    }
  }

  private normalizeError(error: AxiosError): ApiError {
    if (error.response?.data) {
      return error.response.data as ApiError
    }
    return {
      errors: [{
        code: 'NETWORK_ERROR',
        message: error.message || 'Network error occurred'
      }]
    }
  }

  private generateCorrelationId(): string {
    return crypto.randomUUID()
  }

  // API methods
  public auth = {
    login: (data: LoginData) => this.axios.post('/auth/login/', data),
    logout: () => this.axios.post('/auth/logout/'),
    refresh: () => this.axios.post('/auth/refresh/'),
    me: () => this.axios.get('/auth/me/')
  }

  public materials = {
    list: (params?: MaterialFilters) =>
      this.axios.get('/materials/', { params }),
    create: (data: CreateMaterialData) =>
      this.axios.post('/materials/', data),
    get: (id: string) =>
      this.axios.get(`/materials/${id}/`),
    update: (id: string, data: UpdateMaterialData) =>
      this.axios.patch(`/materials/${id}/`, data),
    requestSampling: (id: string) =>
      this.axios.post(`/materials/${id}/request-sampling/`),
    getLabel: (id: string) =>
      this.axios.get(`/materials/${id}/label/`)
  }

  // ... other API methods
}

export const api = new ApiClient()
```

### 3.6 Routing Architecture

```typescript
// apps/storekeeper/src/routes/index.ts
import { createBrowserRouter } from 'react-router-dom'
import { ProtectedRoute } from './ProtectedRoute'
import Layout from './Layout'
import Materials from './Materials'
import Packaging from './Packaging'
import Notifications from './Notifications'

export const storekeeperRoutes = {
  path: '/',
  element: <ProtectedRoute role="storekeeper" />,
  children: [
    {
      element: <Layout />,
      children: [
        { index: true, element: <Materials /> },
        { path: 'materials', element: <Materials /> },
        { path: 'packaging', element: <Packaging /> },
        { path: 'notifications', element: <Notifications /> }
      ]
    }
  ]
}

// ProtectedRoute component
const ProtectedRoute: React.FC<{ role: string }> = ({ role, children }) => {
  const { user, isLoading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoading && !user) {
      navigate('/login')
    }
    if (!isLoading && user && user.job_role !== role) {
      // Redirect to the correct app for their role
      navigate(`/${user.job_role}`)
    }
  }, [user, isLoading, navigate])

  if (isLoading) return <LoadingSpinner />
  if (!user) return null
  if (user.job_role !== role) return null

  return children
}
```

---

## 4. Cross-Cutting Concerns

### 4.1 Security Implementation

```mermaid
flowchart TD
    subgraph Security["SECURITY LAYERS"]
        subgraph Transport["Transport Layer"]
            TLS["TLS 1.2+"]
            HSTS["HSTS Headers"]
        end

        subgraph Authentication["Authentication"]
            JWT["JWT Tokens"]
            Cookies["HTTP-only Cookies"]
            Session["Session Management"]
            MFA["MFA (TBS)"]
        end

        subgraph Authorisation["Authorisation"]
            RBAC["RBAC"]
            Permissions["Permission Checks"]
            API["API-level Enforcement"]
            UI["UI-level Enforcement"]
        end

        subgraph DataProtection["Data Protection"]
            Encryption["Encryption at Rest"]
            Validation["Input Validation"]
            Sanitisation["Output Sanitisation"]
            CSP["CSP Headers"]
        end
    end
```

### 4.2 Audit Trail Implementation

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Service
    participant DB
    participant Celery
    participant AuditDB

    User->>API: Perform action
    API->>Service: Process request
    Service->>DB: Execute change
    DB-->>Service: Confirm
    Service-->>API: Return response

    Note over Service,Celery: Async audit (non-blocking)
    Service->>Celery: Queue audit task
    Celery->>AuditDB: Write audit record
    AuditDB-->>Celery: Confirm
```

### 4.3 Error Handling Strategy

```mermaid
flowchart TD
    subgraph Backend["BACKEND ERROR HANDLING"]
        BE1["Custom Exception Classes"]
        BE2["DRF Exception Handler"]
        BE3["Standardised Error Response"]
        BE4["Error Logging"]
    end

    subgraph Frontend["FRONTEND ERROR HANDLING"]
        FE1["API Error Interceptor"]
        FE2["React Error Boundary"]
        FE3["Global Error Boundary"]
        FE4["Toast Notifications"]
        FE5["Error Logging"]
    end

    subgraph Common["COMMON PATTERNS"]
        C1["User-Friendly Messages"]
        C2["Recovery Options"]
        C3["Audit Logging"]
        C4["Monitoring"]
    end
```

### 4.4 Logging Strategy

| Log Type | Tool | Format | Retention | Purpose |
|----------|------|--------|-----------|---------|
| Application | Python logging | JSON | 30 days | Debugging, monitoring |
| Access | Nginx | JSON | 30 days | Request tracking |
| Audit | Django model | JSON | 10 years | Compliance |
| Security | Python logging | JSON | 90 days | Security monitoring |
| Performance | Django + Prometheus | Metrics | 30 days | Performance analysis |

---

## 5. Communication Patterns

### 5.1 Request Flow

```mermaid
sequenceDiagram
    participant UI as React App
    participant API as Nginx
    participant Auth as Auth Service
    participant View as API View
    participant Service as Service Layer
    participant DB as Database
    participant Celery as Celery

    UI->>API: HTTP Request + Cookie
    API->>Auth: Validate JWT
    Auth-->>API: User + Permissions
    API->>View: Forward Request
    View->>View: Check Permissions
    View->>Service: Business Logic
    Service->>DB: Query/Update
    DB-->>Service: Result
    Service->>Celery: Queue Async Task (audit)
    Service-->>View: Response
    View-->>API: JSON Response
    API-->>UI: HTTP Response
    Celery->>DB: Write Audit Record
```

### 5.2 WebSocket/Real-time (Future)

| Use Case | Priority | Technology |
|----------|----------|------------|
| Notifications | Future | WebSocket / Django Channels |
| Real-time updates | Future | WebSocket / Django Channels |
| Live dashboards | Future | WebSocket / Django Channels |

---

## 6. Implementation Roadmap

### 6.1 Phase 1: Foundation (Weeks 1-3)

```mermaid
gantt
    title Phase 1: Foundation
    dateFormat  YYYY-MM-DD

    section Backend
    Project Setup                     :b1, 2026-01-15, 3d
    Common Module                     :b2, 2026-01-18, 3d
    Users Module (Auth + RBAC)        :b3, 2026-01-21, 5d
    Audit Module                      :b4, 2026-01-26, 3d
    E-Signature Module                :b5, 2026-01-29, 2d
    API Foundation                    :b6, 2026-01-31, 2d

    section Frontend
    Monorepo Setup                    :f1, 2026-01-15, 3d
    Shared Components                 :f2, 2026-01-18, 5d
    API Client                        :f3, 2026-01-23, 3d
    Auth Integration                  :f4, 2026-01-26, 3d
    Core Hooks                        :f5, 2026-01-29, 2d
```

### 6.2 Phase 2: Storekeeper + Sampler (Weeks 4-6)

```mermaid
gantt
    title Phase 2: Storekeeper + Sampler
    dateFormat  YYYY-MM-DD

    section Backend
    Materials Module                  :b1, 2026-02-05, 5d
    Packaging Module                  :b2, 2026-02-10, 4d
    Sampling Module                   :b3, 2026-02-14, 5d
    Notifications Module              :b4, 2026-02-19, 3d

    section Frontend
    Storekeeper App                   :f1, 2026-02-05, 7d
    Sampler App                       :f2, 2026-02-12, 7d
    Shared Components Update          :f3, 2026-02-19, 3d
```

### 6.3 Phase 3: Analyst + QC Manager (Weeks 7-9)

```mermaid
gantt
    title Phase 3: Analyst + QC Manager
    dateFormat  YYYY-MM-DD

    section Backend
    Product Samples Module            :b1, 2026-02-26, 4d
    COA Module                        :b2, 2026-03-02, 6d
    Release Workflow                  :b3, 2026-03-08, 4d

    section Frontend
    Analyst App                       :f1, 2026-02-26, 7d
    QC Manager App                    :f2, 2026-03-05, 7d
    Admin Console                     :f3, 2026-03-12, 5d
```

### 6.4 Phase 4: Integration + Testing (Weeks 10-12)

```mermaid
gantt
    title Phase 4: Integration + Testing
    dateFormat  YYYY-MM-DD

    section Integration
    API Integration                   :i1, 2026-03-19, 5d
    End-to-End Workflows              :i2, 2026-03-24, 5d
    Performance Testing               :i3, 2026-03-29, 3d

    section Testing
    Unit Tests Complete               :t1, 2026-03-19, 7d
    Integration Tests                 :t2, 2026-03-26, 5d
    Security Testing                  :t3, 2026-03-31, 3d
    UAT                               :t4, 2026-04-03, 5d
    Validation                        :t5, 2026-04-08, 5d

    section Deployment
    Staging Deployment                :d1, 2026-04-03, 2d
    Production Deployment             :d2, 2026-04-13, 2d
    Go-Live                           :milestone, m1, 2026-04-15, 0d
```

---

## 7. Appendices

### A. Environment Variables

```bash
# Backend
DEBUG=false
SECRET_KEY=<secret>
ALLOWED_HOSTS=localhost,api.rm-rrs.example.com

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/rm_rrs

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
JWT_SECRET_KEY=<secret>
JWT_ACCESS_TOKEN_LIFETIME=900  # 15 minutes
JWT_REFRESH_TOKEN_LIFETIME=604800  # 7 days

# Email
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=user@example.com
EMAIL_HOST_PASSWORD=<password>

# Celery
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# Frontend
VITE_API_BASE_URL=https://api.rm-rrs.example.com/api/v1
VITE_APP_NAME=RM Receiving System
VITE_ENVIRONMENT=production
```

### B. Docker Compose Configuration

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
      - ./backups:/backups
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
    volumes:
      - redis_data:/data
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
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
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

  celery:
    build:
      context: ./rm-rrs-backend
      dockerfile: docker/celery.Dockerfile
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://rm_rrs_user:${DB_PASSWORD}@postgres:5432/rm_rrs
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
    volumes:
      - ./rm-rrs-backend:/app
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: celery -A rm_rrs worker --loglevel=info

  celery-beat:
    build:
      context: ./rm-rrs-backend
      dockerfile: docker/celery.Dockerfile
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://rm_rrs_user:${DB_PASSWORD}@postgres:5432/rm_rrs
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
    volumes:
      - ./rm-rrs-backend:/app
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: celery -A rm_rrs beat --loglevel=info

  frontend:
    build:
      context: ./rm-rrs-frontend
      dockerfile: docker/frontend.Dockerfile
    environment:
      - VITE_API_BASE_URL=https://api.rm-rrs.example.com/api/v1
    ports:
      - "5173:5173"
    volumes:
      - ./rm-rrs-frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    command: pnpm dev --host

  nginx:
    build:
      context: ./rm-rrs-backend
      dockerfile: docker/nginx.Dockerfile
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./staticfiles:/static
      - ./media:/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  redis_data:
```

### C. Build and Deployment Commands

```bash
# Backend
python manage.py migrate
python manage.py collectstatic
gunicorn config.wsgi:application --workers 4 --threads 2

# Frontend - Development
pnpm install
pnpm dev

# Frontend - Production
pnpm build
pnpm serve --port 5173

# Docker - Development
docker-compose up -d

# Docker - Production
docker-compose -f docker-compose.prod.yml up -d
```

---

**Document Approval**

| Role | Name | Date |
|------|------|------|
| Author | [Name] | [Date] |
| Reviewer (Backend) | [Name] | [Date] |
| Reviewer (Frontend) | [Name] | [Date] |
| Reviewer (Architecture) | [Name] | [Date] |
| Approver | [Name] | [Date] |

---

**Change History**

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | [Date] | [Author] | Initial baseline backend and frontend architecture |
