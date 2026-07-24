# 23 — Test Automation and CI/CD (RM-RRS-TEST-003)

**Document Identifier:** RM-RRS-TEST-003
**Version:** 1.0
**Status:** Baseline
**Traces to:** SRS, NFR, TDD, Testing Strategy (RM-RRS-TEST-001), Test Cases (RM-RRS-TEST-002)
**Compliance Reference:** IEEE Std 829-2008, ISO/IEC/IEEE 29119, GAMP 5, FDA General Principles of Software Validation

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Test Automation Framework](#2-test-automation-framework)
3. [CI/CD Integration](#3-cicd-integration)
4. [Test Automation Implementation](#4-test-automation-implementation)
5. [Test Reporting and Analytics](#5-test-reporting-and-analytics)
6. [Maintenance and Evolution](#6-maintenance-and-evolution)
7. [Appendices](#7-appendices)

---

## 1. Introduction

### 1.1 Purpose
This document defines the **Test Automation and CI/CD** strategy for the **Raw Material Receiving & Release System (RM-RRS)** . It provides comprehensive specifications for automated testing frameworks, CI/CD pipeline integration, test script implementation, reporting mechanisms, and ongoing maintenance. This document serves as the implementation guide for all test automation activities.

### 1.2 Scope
This document covers:
- **Test Automation Frameworks**: Tools, libraries, and configurations
- **CI/CD Integration**: Pipeline design, triggers, and execution
- **Test Implementation**: Script development, data management, and execution
- **Reporting and Analytics**: Metrics, dashboards, and notifications
- **Maintenance**: Version control, updates, and continuous improvement

### 1.3 Automation Objectives

```mermaid
flowchart TD
    subgraph Objectives["AUTOMATION OBJECTIVES"]
        O1["Speed<br/>Run tests in minutes, not days"]
        O2["Reliability<br/>Consistent, repeatable results"]
        O3["Coverage<br/>Maximize test coverage"]
        O4["Shift-Left<br/>Find defects early in development"]
        O5["Compliance<br/>Traceable, auditable test execution"]
        O6["Efficiency<br/>Reduce manual testing effort"]
    end
```

### 1.4 References

| Document | Reference |
|----------|-----------|
| 16_TDD.md | Test Design and Development |
| 17_Backend_Architecture.md | Backend Architecture |
| 18_Frontend_Architecture.md | Frontend Architecture |
| 19_Coding Standards.md | Coding Standards |
| 21_Coding Roadmap.md | Coding Roadmap |
| RM-RRS-TEST-001 | Testing Strategy and Plan |
| RM-RRS-TEST-002 | Test Cases and Execution |

---

## 2. Test Automation Framework

### 2.1 Framework Architecture

```mermaid
flowchart TD
    subgraph Automation["TEST AUTOMATION FRAMEWORK"]
        subgraph Backend["BACKEND TESTS"]
            B1["pytest<br/>Test Runner"]
            B2["pytest-django<br/>Django Integration"]
            B3["pytest-cov<br/>Coverage Reporting"]
            B4["pytest-xdist<br/>Parallel Execution"]
            B5["factory-boy<br/>Test Data Factory"]
        end

        subgraph Frontend["FRONTEND TESTS"]
            F1["Jest<br/>Test Runner"]
            F2["React Testing Library<br/>Component Testing"]
            F3["Cypress<br/>E2E Testing"]
            F4["Vitest<br/>Alternative Runner"]
            F5["Testing Library<br/>User Interaction"]
        end

        subgraph Performance["PERFORMANCE TESTS"]
            P1["k6<br/>Load Testing"]
            P2["Locust<br/>Alternative Load Testing"]
            P3["Grafana<br/>Metrics Visualisation"]
        end

        subgraph Security["SECURITY TESTS"]
            S1["OWASP ZAP<br/>DAST"]
            S2["Bandit<br/>SAST"]
            S3["SonarQube<br/>Code Quality"]
            S4["Trivy<br/>Container Scanning"]
            S5["Snyk<br/>Dependency Scanning"]
        end

        subgraph CI["CI/CD PIPELINE"]
            C1["GitHub Actions<br/>Orchestration"]
            C2["Docker Compose<br/>Test Environment"]
            C3["Test Reports<br/>JUnit/HTML"]
        end
    end
```

### 2.2 Tool Selection and Justification

| Tool Category | Tool | Version | Purpose | Justification |
|---------------|------|---------|---------|---------------|
| **Backend Test Runner** | pytest | 7.4+ | Unit/Integration testing | Python standard; rich ecosystem; Django integration |
| **Backend Coverage** | pytest-cov | 4.1+ | Code coverage | Comprehensive reporting; CI integration |
| **Backend Mocking** | pytest-mock | 3.11+ | Mocking services | Simplifies isolated testing |
| **Backend Factories** | factory-boy | 3.3+ | Test data generation | Creates consistent test data |
| **Frontend Test Runner** | Jest | 29.7+ | Unit/Component testing | React standard; fast; snapshot testing |
| **Frontend E2E** | Cypress | 13.0+ | End-to-end testing | Real browser; time-travel; excellent debugging |
| **Performance** | k6 | 0.46+ | Load testing | Open source; scriptable; Grafana integration |
| **Security (SAST)** | Bandit | 1.7+ | Static analysis | Python-specific; easy configuration |
| **Security (DAST)** | OWASP ZAP | 2.13+ | Dynamic analysis | Industry standard; comprehensive coverage |
| **Container Scanning** | Trivy | 0.45+ | Container vulnerabilities | Fast; comprehensive; CI-friendly |
| **Dependency Scanning** | Snyk | 1.0+ | Dependency vulnerabilities | Accurate; integrates with GitHub |
| **Code Quality** | SonarQube | 10.0+ | Code analysis | Comprehensive; quality gate enforcement |

### 2.3 Framework Configuration

#### 2.3.1 Backend Configuration (pytest)

```python
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.testing
python_files = test_*.py
testpaths = tests apps
addopts = 
    -v
    --tb=short
    --maxfail=5
    --strict-markers
    --showlocals
    -p no:cacheprovider
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (API, database)
    slow: Slow tests (performance, complex)
    regression: Regression tests
    smoke: Smoke tests (critical paths)
```

```python
# conftest.py
import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests."""
    pass

@pytest.fixture
def api_client():
    """Return DRF API client."""
    return APIClient()

@pytest.fixture
def authenticated_client():
    """Return authenticated API client."""
    client = APIClient()
    user = User.objects.create_user(
        username='testuser',
        password='testpass123',
        job_role='storekeeper'
    )
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def test_user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        job_role='storekeeper'
    )

@pytest.fixture
def material_factory():
    """Factory for creating test materials."""
    from apps.materials.models import Material
    
    def _create_material(**kwargs):
        defaults = {
            'receipt_id': 'RCV-2026-0001',
            'material_name': 'Test Material',
            'supplier': 'Test Supplier',
            'supplier_batch': 'BATCH-001',
            'exp_date': '2027-01-15',
            'receipt_date': '2026-01-15',
            'received_by': 'Test Receiver',
        }
        defaults.update(kwargs)
        return Material.objects.create(**defaults)
    
    return _create_material
```

#### 2.3.2 Frontend Configuration (Jest)

```javascript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/src'],
  testMatch: [
    '**/__tests__/**/*.ts?(x)',
    '**/?(*.)+(spec|test).ts?(x)'
  ],
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/main.tsx',
    '!src/vite-env.d.ts'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@shared/(.*)$': '<rootDir>/../shared/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
  },
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts']
};
```

#### 2.3.3 Cypress Configuration

```javascript
// cypress.config.ts
import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:5173',
    supportFile: 'cypress/support/e2e.ts',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    env: {
      apiBaseUrl: 'http://localhost:8000/api/v1'
    }
  },
  component: {
    devServer: {
      framework: 'react',
      bundler: 'vite'
    }
  }
});
```

#### 2.3.4 k6 Configuration

```javascript
// k6-config.js
export const config = {
  // Test configuration
  stages: [
    { duration: '2m', target: 10 },   // Ramp up
    { duration: '5m', target: 10 },   // Steady
    { duration: '2m', target: 0 },    // Ramp down
  ],
  
  // Thresholds
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
  
  // Environment variables
  env: {
    API_BASE_URL: 'http://localhost:8000/api/v1',
  },
};
```

---

## 3. CI/CD Integration

### 3.1 CI/CD Pipeline Architecture

```mermaid
flowchart TD
    subgraph Pipeline["CI/CD PIPELINE"]
        subgraph Source["SOURCE"]
            Push["Code Push"]
            PR["Pull Request"]
            Schedule["Scheduled"]
        end

        subgraph Build["BUILD"]
            Lint["Linting"]
            Security["Security Scan"]
            Unit["Unit Tests"]
            Integration["Integration Tests"]
            BuildApp["Build Application"]
            BuildImage["Build Docker Image"]
        end

        subgraph Test["TEST"]
            E2E["E2E Tests"]
            Performance["Performance Tests"]
            SecurityDAST["Security DAST"]
            Compliance["Compliance Tests"]
        end

        subgraph Deploy["DEPLOY"]
            Staging["Deploy to Staging"]
            Smoke["Smoke Tests"]
            UAT["User Acceptance Tests"]
            Prod["Deploy to Production"]
        end

        subgraph Report["REPORT"]
            Metrics["Metrics Collection"]
            Dashboard["Dashboard Update"]
            Notify["Notifications"]
        end

        Push --> Lint
        PR --> Lint
        Schedule --> Performance
        Schedule --> SecurityDAST

        Lint --> Security --> Unit --> Integration --> BuildApp --> BuildImage
        BuildImage --> E2E --> Staging
        Staging --> Smoke --> UAT --> Prod
        Prod --> Metrics --> Dashboard --> Notify
    end
```

### 3.2 GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  schedule:
    - cron: '0 2 * * *'  # Daily security scan
  workflow_dispatch:

env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '18'
  POETRY_VERSION: '1.6.1'

jobs:
  # ============ BACKEND TESTS ============
  backend-lint:
    name: Backend Linting
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          cd rm-rrs-backend
          pip install -r requirements/dev.txt
      
      - name: Run flake8
        run: |
          cd rm-rrs-backend
          flake8 apps/ --count --max-complexity=10 --statistics
      
      - name: Run black (check)
        run: |
          cd rm-rrs-backend
          black --check apps/
      
      - name: Run isort (check)
        run: |
          cd rm-rrs-backend
          isort --check-only apps/

  backend-unit:
    name: Backend Unit Tests
    runs-on: ubuntu-latest
    needs: backend-lint
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          cd rm-rrs-backend
          pip install -r requirements/dev.txt
          pip install -r requirements/test.txt
      
      - name: Run migrations
        run: |
          cd rm-rrs-backend
          python manage.py migrate --settings=config.settings.testing
      
      - name: Run pytest unit tests
        run: |
          cd rm-rrs-backend
          pytest --cov=apps --cov-report=xml --cov-report=html -m "unit"
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./rm-rrs-backend/coverage.xml
          flags: backend
          fail_ci_if_error: false

  backend-integration:
    name: Backend Integration Tests
    runs-on: ubuntu-latest
    needs: backend-unit
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          cd rm-rrs-backend
          pip install -r requirements/dev.txt
          pip install -r requirements/test.txt
      
      - name: Run migrations
        run: |
          cd rm-rrs-backend
          python manage.py migrate --settings=config.settings.testing
      
      - name: Load test data
        run: |
          cd rm-rrs-backend
          python manage.py loaddata test_data.json --settings=config.settings.testing
      
      - name: Run pytest integration tests
        run: |
          cd rm-rrs-backend
          pytest --cov=apps --cov-report=xml --cov-report=html -m "integration"
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./rm-rrs-backend/coverage.xml
          flags: backend-integration
          fail_ci_if_error: false

  # ============ FRONTEND TESTS ============
  frontend-lint:
    name: Frontend Linting
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'pnpm'
          cache-dependency-path: rm-rrs-frontend/pnpm-lock.yaml
      
      - name: Install pnpm
        run: npm install -g pnpm@8
      
      - name: Install dependencies
        run: |
          cd rm-rrs-frontend
          pnpm install
      
      - name: Run ESLint
        run: |
          cd rm-rrs-frontend
          pnpm lint
      
      - name: Run Prettier check
        run: |
          cd rm-rrs-frontend
          pnpm format:check

  frontend-unit:
    name: Frontend Unit Tests
    runs-on: ubuntu-latest
    needs: frontend-lint
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'pnpm'
          cache-dependency-path: rm-rrs-frontend/pnpm-lock.yaml
      
      - name: Install pnpm
        run: npm install -g pnpm@8
      
      - name: Install dependencies
        run: |
          cd rm-rrs-frontend
          pnpm install
      
      - name: Run Jest tests
        run: |
          cd rm-rrs-frontend
          pnpm test --coverage
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          directory: ./rm-rrs-frontend/coverage
          flags: frontend
          fail_ci_if_error: false

  # ============ E2E TESTS ============
  e2e-tests:
    name: E2E Tests
    runs-on: ubuntu-latest
    needs: [backend-integration, frontend-unit]
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'pnpm'
          cache-dependency-path: rm-rrs-frontend/pnpm-lock.yaml
      
      - name: Install pnpm
        run: npm install -g pnpm@8
      
      - name: Install dependencies
        run: |
          cd rm-rrs-frontend
          pnpm install
      
      - name: Start services with Docker Compose
        run: |
          docker-compose -f docker-compose.test.yml up -d
          docker-compose -f docker-compose.test.yml ps
      
      - name: Wait for services
        run: |
          sleep 30
          curl --retry 5 --retry-delay 5 --retry-connrefused http://localhost:8000/health
      
      - name: Run Cypress E2E tests
        run: |
          cd rm-rrs-frontend
          pnpm cypress:run
      
      - name: Upload Cypress artifacts
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: cypress-artifacts
          path: |
            rm-rrs-frontend/cypress/videos
            rm-rrs-frontend/cypress/screenshots
      
      - name: Stop services
        if: always()
        run: docker-compose -f docker-compose.test.yml down

  # ============ SECURITY SCANS ============
  security-scan:
    name: Security Scans
    runs-on: ubuntu-latest
    needs: backend-integration
    steps:
      - uses: actions/checkout@v4
      
      # SAST - Bandit
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install Bandit
        run: pip install bandit
      
      - name: Run Bandit (SAST)
        run: |
          cd rm-rrs-backend
          bandit -r apps/ -f json -o bandit-report.json
      
      - name: Upload Bandit report
        uses: actions/upload-artifact@v3
        with:
          name: bandit-report
          path: rm-rrs-backend/bandit-report.json
      
      # Container Scanning - Trivy
      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
      
      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
      
      # Dependency Scanning - Snyk
      - name: Run Snyk
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

  # ============ PERFORMANCE TESTS ============
  performance-tests:
    name: Performance Tests
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup k6
        uses: grafana/setup-k6-action@v1
      
      - name: Start services
        run: |
          docker-compose -f docker-compose.test.yml up -d
          sleep 30
      
      - name: Run k6 load tests
        run: |
          cd rm-rrs-backend/tests/performance
          k6 run -e API_BASE_URL=http://localhost:8000/api/v1 load-test.js
      
      - name: Stop services
        if: always()
        run: docker-compose -f docker-compose.test.yml down

  # ============ DEPLOYMENT ============
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [e2e-tests, security-scan]
    if: github.ref == 'refs/heads/develop'
    environment: staging
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker images
        run: |
          docker build -t rm-rrs-backend:latest -f rm-rrs-backend/docker/backend.Dockerfile .
          docker build -t rm-rrs-frontend:latest -f rm-rrs-frontend/docker/frontend.Dockerfile .
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker tag rm-rrs-backend:latest ${{ secrets.DOCKER_REGISTRY }}/rm-rrs-backend:staging
          docker tag rm-rrs-frontend:latest ${{ secrets.DOCKER_REGISTRY }}/rm-rrs-frontend:staging
          docker push ${{ secrets.DOCKER_REGISTRY }}/rm-rrs-backend:staging
          docker push ${{ secrets.DOCKER_REGISTRY }}/rm-rrs-frontend:staging
      
      - name: Deploy to staging
        run: |
          ssh ${{ secrets.STAGING_HOST }} "cd /opt/rm-rrs && docker-compose pull && docker-compose up -d"

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v4
      
      - name: Build production images
        run: |
          docker build -t rm-rrs-backend:latest -f rm-rrs-backend/docker/backend.Dockerfile .
          docker build -t rm-rrs-frontend:latest -f rm-rrs-frontend/docker/frontend.Dockerfile .
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker tag rm-rrs-backend:latest ${{ secrets.DOCKER_REGISTRY }}/rm-rrs-backend:production
          docker tag rm-rrs-frontend:latest ${{ secrets.DOCKER_REGISTRY }}/rm-rrs-frontend:production
          docker push ${{ secrets.DOCKER_REGISTRY }}/rm-rrs-backend:production
          docker push ${{ secrets.DOCKER_REGISTRY }}/rm-rrs-frontend:production
      
      - name: Deploy to production
        run: |
          ssh ${{ secrets.PROD_HOST }} "cd /opt/rm-rrs && docker-compose pull && docker-compose up -d"
      
      - name: Run smoke tests
        run: |
          sleep 30
          curl --retry 5 --retry-delay 10 --retry-connrefused https://api.rm-rrs.example.com/health
```

### 3.3 Quality Gates

```mermaid
flowchart LR
    subgraph Gates["QUALITY GATES"]
        G1["Gate 1: Linting<br/>No linting errors"]
        G2["Gate 2: Unit Tests<br/>≥80% coverage<br/>All passing"]
        G3["Gate 3: Integration<br/>All workflows passing"]
        G4["Gate 4: Security<br/>No critical vulnerabilities"]
        G5["Gate 5: Performance<br/>Thresholds met"]
        G6["Gate 6: UAT<br/>Sign-off received"]
    end

    G1 --> G2 --> G3 --> G4 --> G5 --> G6
```

### 3.4 Pipeline Triggers

| Trigger | Pipeline | Executed Tests | Environment |
|---------|----------|----------------|-------------|
| **Pull Request** | Full CI | Lint, Unit, Integration, Security | Test |
| **Push to develop** | Full CI + Staging | All tests + E2E | Test + Staging |
| **Push to main** | Full CI + Prod | All tests + UAT | Test + Prod |
| **Schedule (daily)** | Security + Performance | Security DAST, Performance | Test |
| **Manual** | Full validation | All tests | Staging |

---

## 4. Test Automation Implementation

### 4.1 Backend Test Implementation

#### 4.1.1 Unit Test Example

```python
# apps/materials/tests/test_services.py
import pytest
from decimal import Decimal
from datetime import date, timedelta

from apps.materials.models import Material
from apps.materials.services import MaterialService
from apps.common.exceptions import ConflictError


@pytest.mark.unit
class TestMaterialService:
    """Unit tests for MaterialService."""

    @pytest.fixture
    def service(self, test_user):
        """Create MaterialService instance."""
        return MaterialService(test_user)

    @pytest.fixture
    def material_data(self):
        """Sample material data."""
        return {
            'material_name': 'Paracetamol',
            'supplier': 'PharmaChem Ltd',
            'supplier_batch': 'BATCH-2024-001',
            'exp_date': date.today() + timedelta(days=365),
            'receipt_date': date.today(),
            'received_by': 'Test Receiver'
        }

    def test_create_material_success(self, service, material_data):
        """Test successful material creation."""
        material = service.create_material(material_data)
        
        assert material is not None
        assert material.receipt_id.startswith('RCV-')
        assert material.material_name == 'Paracetamol'
        assert material.status == Material.Status.QUARANTINE
        assert material.sampling_status == Material.SamplingStatus.NOT_SAMPLED
        assert material.created_by == service.user

    def test_create_material_receipt_id_format(self, service, material_data):
        """Test receipt ID format generation."""
        material = service.create_material(material_data)
        
        assert material.receipt_id.startswith('RCV-2026-')
        assert len(material.receipt_id) == 14  # RCV-YYYY-####

    def test_create_material_invalid_data(self, service):
        """Test material creation with invalid data."""
        invalid_data = {
            'material_name': '',  # Required field empty
            'supplier': 'PharmaChem Ltd',
        }
        
        with pytest.raises(Exception):  # ValidationError
            service.create_material(invalid_data)

    def test_request_sampling_success(self, service, material_data):
        """Test successful sampling request."""
        material = service.create_material(material_data)
        
        updated = service.request_sampling(material.id)
        
        assert updated.sampling_status == Material.SamplingStatus.SAMPLING_REQUESTED

    def test_request_sampling_already_requested(self, service, material_data):
        """Test conflict when sampling already requested."""
        material = service.create_material(material_data)
        service.request_sampling(material.id)
        
        with pytest.raises(ConflictError):
            service.request_sampling(material.id)

    def test_request_sampling_already_sampled(self, service, material_data):
        """Test conflict when material already sampled."""
        material = service.create_material(material_data)
        material.sampling_status = Material.SamplingStatus.SAMPLED
        material.save()
        
        with pytest.raises(ConflictError):
            service.request_sampling(material.id)

    def test_get_material_success(self, service, material_data):
        """Test retrieving a material by ID."""
        material = service.create_material(material_data)
        
        retrieved = service.get_material(material.id)
        
        assert retrieved.id == material.id
        assert retrieved.material_name == material.material_name

    def test_get_material_not_found(self, service):
        """Test retrieving a non-existent material."""
        with pytest.raises(Exception):  # NotFoundError
            service.get_material('non-existent-id')
```

#### 4.1.2 Integration Test Example

```python
# apps/materials/tests/test_api.py
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.integration
class TestMaterialAPI:
    """Integration tests for Material API endpoints."""

    @pytest.fixture
    def material_payload(self):
        """Sample material payload."""
        return {
            'material_name': 'Paracetamol',
            'supplier': 'PharmaChem Ltd',
            'supplier_batch': 'BATCH-2024-001',
            'exp_date': '2027-01-15',
            'receipt_date': '2026-01-15',
            'received_by': 'John Storekeeper'
        }

    def test_list_materials_unauthorized(self, api_client):
        """Test listing materials without authentication."""
        url = reverse('material-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_materials_authorized(self, authenticated_client):
        """Test listing materials with authentication."""
        url = reverse('material-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'data' in response.data
        assert 'meta' in response.data

    def test_create_material_success(self, authenticated_client, material_payload):
        """Test creating a material successfully."""
        url = reverse('material-list')
        response = authenticated_client.post(url, material_payload)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['data']['material_name'] == 'Paracetamol'
        assert response.data['data']['status'] == 'Quarantine'
        assert response.data['data']['sampling_status'] == 'Not Sampled'

    def test_create_material_missing_fields(self, authenticated_client):
        """Test creating a material with missing required fields."""
        url = reverse('material-list')
        payload = {
            'supplier': 'PharmaChem Ltd',
        }
        response = authenticated_client.post(url, payload)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'material_name' in str(response.data)

    def test_get_material_detail(self, authenticated_client, material_payload):
        """Test retrieving material details."""
        # Create material first
        url = reverse('material-list')
        create_response = authenticated_client.post(url, material_payload)
        material_id = create_response.data['data']['id']
        
        # Retrieve material
        detail_url = reverse('material-detail', args=[material_id])
        response = authenticated_client.get(detail_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['material_name'] == 'Paracetamol'

    def test_request_sampling(self, authenticated_client, material_payload):
        """Test requesting sampling."""
        # Create material
        url = reverse('material-list')
        create_response = authenticated_client.post(url, material_payload)
        material_id = create_response.data['data']['id']
        
        # Request sampling
        sampling_url = reverse('material-request-sampling', args=[material_id])
        response = authenticated_client.post(sampling_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['sampling_status'] == 'Sampling Requested'

    def test_request_sampling_already_requested(self, authenticated_client, material_payload):
        """Test requesting sampling on already requested material."""
        # Create material
        url = reverse('material-list')
        create_response = authenticated_client.post(url, material_payload)
        material_id = create_response.data['data']['id']
        
        # Request sampling twice
        sampling_url = reverse('material-request-sampling', args=[material_id])
        authenticated_client.post(sampling_url)
        response = authenticated_client.post(sampling_url)
        
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_search_materials(self, authenticated_client, material_payload):
        """Test searching materials."""
        url = reverse('material-list')
        authenticated_client.post(url, material_payload)
        authenticated_client.post(url, {
            **material_payload,
            'material_name': 'Ibuprofen',
            'supplier_batch': 'BATCH-2024-002'
        })
        
        # Search for Paracetamol
        response = authenticated_client.get(url, {'search': 'Paracetamol'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) >= 1
        assert response.data['data'][0]['material_name'] == 'Paracetamol'

    def test_filter_materials_by_status(self, authenticated_client, material_payload):
        """Test filtering materials by status."""
        url = reverse('material-list')
        authenticated_client.post(url, material_payload)
        
        # Filter by Quarantine
        response = authenticated_client.get(url, {'status': 'Quarantine'})
        
        assert response.status_code == status.HTTP_200_OK
        for material in response.data['data']:
            assert material['status'] == 'Quarantine'
```

### 4.2 Frontend Test Implementation

#### 4.2.1 Component Test Example

```tsx
// apps/storekeeper/src/components/MaterialForm/MaterialForm.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MaterialForm } from './MaterialForm';
import { useCreateMaterial } from '../../hooks/useMaterials';

// Mock the custom hook
jest.mock('../../hooks/useMaterials');

// Mock toast
jest.mock('@shared/hooks/useToast', () => ({
  useToast: () => ({
    showToast: jest.fn(),
  }),
}));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('MaterialForm', () => {
  const mockMutateAsync = jest.fn().mockResolvedValue({ id: 'mat-123' });

  beforeEach(() => {
    (useCreateMaterial as jest.Mock).mockReturnValue({
      mutateAsync: mockMutateAsync,
      isLoading: false,
    });
    jest.clearAllMocks();
  });

  test('renders all required fields', () => {
    renderWithProviders(<MaterialForm />);

    expect(screen.getByLabelText(/Material Name \*/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Supplier \*/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Supplier Batch \*/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Expiry Date \*/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Receipt Date \*/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Received By \*/i)).toBeInTheDocument();
  });

  test('shows validation errors for empty required fields', async () => {
    renderWithProviders(<MaterialForm />);
    
    const submitButton = screen.getByRole('button', { name: /Register Material/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Material name is required/i)).toBeInTheDocument();
    });
  });

  test('submits form with valid data', async () => {
    renderWithProviders(<MaterialForm />);

    // Fill in required fields
    fireEvent.change(screen.getByLabelText(/Material Name \*/i), {
      target: { value: 'Paracetamol' },
    });
    fireEvent.change(screen.getByLabelText(/Supplier \*/i), {
      target: { value: 'PharmaChem Ltd' },
    });
    fireEvent.change(screen.getByLabelText(/Supplier Batch \*/i), {
      target: { value: 'BATCH-2024-001' },
    });
    fireEvent.change(screen.getByLabelText(/Expiry Date \*/i), {
      target: { value: '2027-01-15' },
    });
    fireEvent.change(screen.getByLabelText(/Receipt Date \*/i), {
      target: { value: '2026-01-15' },
    });
    fireEvent.change(screen.getByLabelText(/Received By \*/i), {
      target: { value: 'John Storekeeper' },
    });

    const submitButton = screen.getByRole('button', { name: /Register Material/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalledWith({
        material_name: 'Paracetamol',
        supplier: 'PharmaChem Ltd',
        supplier_batch: 'BATCH-2024-001',
        exp_date: '2027-01-15',
        receipt_date: '2026-01-15',
        received_by: 'John Storekeeper',
      });
    });
  });

  test('calculates total quantity automatically', async () => {
    renderWithProviders(<MaterialForm />);

    const numPackagesInput = screen.getByLabelText(/No. of Packages/i);
    const packageSizeInput = screen.getByLabelText(/Package Size/i);
    const totalQtyInput = screen.getByLabelText(/Total Quantity \(auto\)/i);

    fireEvent.change(numPackagesInput, { target: { value: '10' } });
    fireEvent.change(packageSizeInput, { target: { value: '25' } });

    expect(totalQtyInput).toHaveValue('250');
  });

  test('disables submit button while submitting', async () => {
    (useCreateMaterial as jest.Mock).mockReturnValue({
      mutateAsync: new Promise(() => {}), // Never resolves
      isLoading: true,
    });

    renderWithProviders(<MaterialForm />);

    const submitButton = screen.getByRole('button', { name: /Register Material/i });
    expect(submitButton).toBeDisabled();
  });
});
```

#### 4.2.2 E2E Test Example (Cypress)

```typescript
// cypress/e2e/materials-workflow.cy.ts
describe('Materials Workflow', () => {
  beforeEach(() => {
    cy.login('storekeeper1', 'TestPass123!');
    cy.visit('/materials');
  });

  it('should register a new material successfully', () => {
    cy.contains('Register Material').click();
    
    // Fill the form
    cy.get('[data-testid="material-name"]').click();
    cy.get('[data-testid="material-name"] input').type('Paracetamol');
    
    cy.get('[data-testid="supplier"]').click();
    cy.get('[data-testid="supplier"] input').type('PharmaChem Ltd');
    
    cy.get('[data-testid="supplier-batch"]').type('BATCH-2024-001');
    cy.get('[data-testid="exp-date"]').type('2027-01-15');
    cy.get('[data-testid="receipt-date"]').type('2026-01-15');
    cy.get('[data-testid="received-by"]').type('John Storekeeper');
    
    // Submit
    cy.contains('Register Material').click();
    
    // Verify success
    cy.contains('Material registered successfully!').should('be.visible');
    cy.get('[data-testid="materials-table"]').should('contain', 'Paracetamol');
  });

  it('should show validation errors for empty fields', () => {
    cy.contains('Register Material').click();
    cy.contains('Register Material').click();
    
    cy.contains('Material name is required').should('be.visible');
    cy.contains('Supplier is required').should('be.visible');
  });

  it('should request sampling and verify status update', () => {
    // Create material first
    cy.createMaterial({
      materialName: 'Ibuprofen',
      supplier: 'BioSource Inc',
      supplierBatch: 'BATCH-2024-002',
      expDate: '2027-01-15',
      receiptDate: '2026-01-15',
      receivedBy: 'John Storekeeper'
    });

    // Find the material and request sampling
    cy.get('[data-testid="materials-table"]').contains('Ibuprofen');
    cy.get('[data-testid="row-actions"]').first().contains('View').click();
    cy.contains('Request Sampling').click();
    cy.contains('Submit Request').click();
    
    // Verify status update
    cy.contains('Sampling request submitted!').should('be.visible');
    cy.get('[data-testid="sampling-status"]').should('contain', 'Sampling Requested');
  });

  it('should complete end-to-end workflow: Material → Sampling → COA → Release', () => {
    // Step 1: Create material
    cy.createMaterial({
      materialName: 'Amoxicillin',
      supplier: 'EuroChem GmbH',
      supplierBatch: 'BATCH-2024-003',
      expDate: '2027-01-15',
      receiptDate: '2026-01-15',
      receivedBy: 'John Storekeeper'
    });

    // Step 2: Request sampling (Storekeeper)
    cy.get('[data-testid="materials-table"]').contains('Amoxicillin');
    cy.get('[data-testid="row-actions"]').first().contains('View').click();
    cy.contains('Request Sampling').click();
    cy.contains('Submit Request').click();

    // Step 3: Record sample (Sampler)
    cy.logout();
    cy.login('sampler1', 'TestPass123!');
    cy.visit('/sampling-requests');
    
    cy.contains('Amoxicillin').should('be.visible');
    cy.contains('Sample').click();
    
    cy.get('[data-testid="sample-size"]').type('200');
    cy.get('[data-testid="containers"]').type('3');
    cy.get('[data-testid="sampler-name"]').type('John Sampler');
    cy.get('[data-testid="storage"]').select('Ambient (15–25°C)');
    cy.get('[data-testid="sampling-date"]').type('2026-01-15');
    cy.contains('Save & Preview Labels').click();

    // Step 4: Create COA (Analyst)
    cy.logout();
    cy.login('analyst1', 'TestPass123!');
    cy.visit('/samples');
    
    cy.contains('Amoxicillin').should('be.visible');
    cy.contains('Start Testing').click();
    
    cy.get('[data-testid="specs-code"]').type('SPC-2024-001');
    cy.get('[data-testid="reference"]').select('BP 2025');
    cy.get('[data-testid="analyst-name"]').type('Jane Analyst');
    cy.contains('Create & Open COA').click();

    // Step 5: Submit and complete COA (Analyst)
    cy.contains('Submit for Review').click();
    cy.contains('Mark Completed').click();

    // Step 6: Approve and release (QC Manager)
    cy.logout();
    cy.login('qcmanager1', 'TestPass123!');
    cy.visit('/coa-review');
    
    cy.contains('Amoxicillin').should('be.visible');
    cy.contains('View').click();
    cy.contains('Approve COA').click();
    cy.contains('Confirm Approval').click();

    // Step 7: Release material
    cy.get('[data-testid="qc-number"]').type('QC-2026-0001');
    cy.get('[data-testid="qc-signature"]').type('Jane QC Manager');
    cy.contains('Release Material').click();

    // Step 8: Verify release label (Storekeeper)
    cy.logout();
    cy.login('storekeeper1', 'TestPass123!');
    cy.visit('/materials');
    
    cy.contains('Amoxicillin').should('be.visible');
    cy.get('[data-testid="status"]').should('contain', 'Released');
    cy.contains('Label').click();
    cy.contains('Print Release Label').should('be.visible');
  });
});
```

### 4.3 Performance Test Implementation

```javascript
// tests/performance/load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '2m', target: 10 },   // Ramp up to 10 users
    { duration: '5m', target: 10 },   // Stay at 10 users
    { duration: '2m', target: 0 },    // Ramp down to 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests < 500ms
    http_req_failed: ['rate<0.01'],     // < 1% failure rate
    errors: ['rate<0.1'],               // < 10% error rate
  },
};

const API_BASE_URL = __ENV.API_BASE_URL || 'http://localhost:8000/api/v1';

// Test data
const testUser = {
  username: 'storekeeper1',
  password: 'TestPass123!',
};

export function setup() {
  // Login once to get session
  const loginRes = http.post(`${API_BASE_URL}/auth/login/`, testUser);
  
  check(loginRes, {
    'login successful': (r) => r.status === 200,
  });

  return {
    cookies: loginRes.cookies,
  };
}

export default function (data) {
  const cookies = data.cookies;

  // === Test: List Materials ===
  const listRes = http.get(`${API_BASE_URL}/materials/`, {
    headers: { Cookie: cookies },
    tags: { name: 'list-materials' },
  });

  check(listRes, {
    'list materials status 200': (r) => r.status === 200,
  });
  errorRate.add(listRes.status !== 200);

  // === Test: Create Material ===
  const materialData = {
    material_name: `Test Material ${Date.now()}`,
    supplier: 'Test Supplier',
    supplier_batch: `BATCH-${Date.now()}`,
    exp_date: '2027-01-15',
    receipt_date: '2026-01-15',
    received_by: 'Test User',
  };

  const createRes = http.post(`${API_BASE_URL}/materials/`, JSON.stringify(materialData), {
    headers: {
      'Content-Type': 'application/json',
      Cookie: cookies,
    },
    tags: { name: 'create-material' },
  });

  check(createRes, {
    'create material status 201': (r) => r.status === 201,
  });
  errorRate.add(createRes.status !== 201);

  // === Test: Get Material Detail ===
  if (createRes.status === 201) {
    const materialId = JSON.parse(createRes.body).data.id;
    const detailRes = http.get(`${API_BASE_URL}/materials/${materialId}/`, {
      headers: { Cookie: cookies },
      tags: { name: 'material-detail' },
    });

    check(detailRes, {
      'material detail status 200': (r) => r.status === 200,
    });
    errorRate.add(detailRes.status !== 200);
  }

  sleep(1);
}

export function teardown(data) {
  // Cleanup: Logout
  http.post(`${API_BASE_URL}/auth/logout/`, {}, {
    headers: { Cookie: data.cookies },
  });
}
```

### 4.4 Security Test Implementation

#### 4.4.1 SAST with Bandit

```bash
# Run Bandit security scan
bandit -r apps/ -f json -o bandit-report.json -ll

# Generate HTML report
bandit -r apps/ -f html -o bandit-report.html
```

```yaml
# .bandit.yml
exclude_dirs:
  - tests
  - migrations
  - .venv
  - node_modules

skips:
  - B101  # assert used (allow in tests)
  - B311  # random module

severity:
  - HIGH
  - MEDIUM

confidence:
  - HIGH
  - MEDIUM
```

#### 4.4.2 DAST with OWASP ZAP

```python
# tests/security/zap_test.py
import requests
from zapv2 import ZAPv2

class ZAPTest:
    def __init__(self, target_url, api_key=None):
        self.target_url = target_url
        self.zap = ZAPv2(api_key=api_key)
        self.base_url = 'http://localhost:8080'  # ZAP proxy
    
    def run_scan(self):
        """Run full security scan."""
        # Access target URL
        self.zap.urlopen(self.target_url)
        
        # Spider the site
        print('Spidering...')
        self.zap.spider.scan(self.target_url)
        while int(self.zap.spider.status()) < 100:
            print(f'Spider progress: {self.zap.spider.status()}%')
            time.sleep(2)
        
        # Active scan
        print('Active scanning...')
        self.zap.ascan.scan(self.target_url)
        while int(self.zap.ascan.status()) < 100:
            print(f'Scan progress: {self.zap.ascan.status()}%')
            time.sleep(5)
        
        # Get alerts
        alerts = self.zap.core.alerts()
        return alerts
    
    def get_report(self):
        """Generate security report."""
        report = self.zap.core.htmlreport()
        return report

def test_owasp_zap_security():
    """Run OWASP ZAP security scan."""
    zap = ZAPTest('http://localhost:8000')
    alerts = zap.run_scan()
    
    # Check for critical/high vulnerabilities
    critical_alerts = [
        a for a in alerts 
        if a['risk'] in ['High', 'Critical']
    ]
    
    assert len(critical_alerts) == 0, f"Found {len(critical_alerts)} critical/high vulnerabilities"
```

---

## 5. Test Reporting and Analytics

### 5.1 Test Report Structure

```mermaid
flowchart TD
    subgraph Reports["TEST REPORTS"]
        R1["Execution Summary<br/>Pass/Fail/Error counts"]
        R2["Coverage Report<br/>Line/function/statement coverage"]
        R3["Defect Report<br/>Open/Closed by severity"]
        R4["Performance Report<br/>Response times, throughput"]
        R5["Security Report<br/>Vulnerabilities by severity"]
        R6["Trend Report<br/>Metrics over time"]
    end
```

### 5.2 Dashboard Configuration (Grafana)

```json
{
  "title": "RM-RRS Test Dashboard",
  "panels": [
    {
      "title": "Test Execution Status",
      "type": "stat",
      "targets": [
        {
          "query": "sum(test_execution_total{status='passed'})",
          "legendFormat": "Passed"
        },
        {
          "query": "sum(test_execution_total{status='failed'})",
          "legendFormat": "Failed"
        }
      ]
    },
    {
      "title": "Test Coverage",
      "type": "gauge",
      "targets": [
        {
          "query": "coverage_percentage{module='backend'}",
          "legendFormat": "Backend"
        },
        {
          "query": "coverage_percentage{module='frontend'}",
          "legendFormat": "Frontend"
        }
      ],
      "fieldConfig": {
        "defaults": {
          "unit": "percent",
          "thresholds": {
            "mode": "absolute",
            "steps": [
              { "color": "red", "value": 0 },
              { "color": "yellow", "value": 70 },
              { "color": "green", "value": 80 }
            ]
          }
        }
      }
    },
    {
      "title": "API Response Time (95th)",
      "type": "graph",
      "targets": [
        {
          "query": "quantile(0.95, http_request_duration_seconds)",
          "legendFormat": "95th Percentile"
        }
      ]
    },
    {
      "title": "Security Vulnerabilities",
      "type": "table",
      "targets": [
        {
          "query": "security_vulnerabilities_total{severity='critical'}"
        }
      ]
    }
  ]
}
```

### 5.3 Notification Configuration

```yaml
# Notification configuration
notifications:
  - type: slack
    channel: '#test-alerts'
    triggers:
      - event: build_failure
      - event: coverage_below_threshold
      - event: security_vulnerability_found
    template: |
      🚨 **Test Alert**
      Event: {{ .Event }}
      Branch: {{ .Branch }}
      Details: {{ .Details }}
      Link: {{ .Link }}

  - type: email
    recipients:
      - qa-team@example.com
      - dev-team@example.com
    triggers:
      - event: test_suite_complete
    template: |
      Subject: RM-RRS Test Report - {{ .Date }}
      
      Summary:
      - Total Tests: {{ .Total }}
      - Passed: {{ .Passed }}
      - Failed: {{ .Failed }}
      - Coverage: {{ .Coverage }}%
      - Defects: {{ .Defects }}
```

---

## 6. Maintenance and Evolution

### 6.1 Test Maintenance Process

```mermaid
flowchart TD
    subgraph Maintenance["TEST MAINTENANCE CYCLE"]
        M1["Monitor<br/>Track test health"]
        M2["Analyze<br/>Identify flaky tests"]
        M3["Prioritize<br/>High-impact fixes"]
        M4["Fix<br/>Update test code"]
        M5["Validate<br/>Run test suite"]
        M6["Deploy<br/>Merge to main"]
    end

    M1 --> M2 --> M3 --> M4 --> M5 --> M6
    M6 --> M1
```

### 6.2 Flaky Test Management

| Strategy | Description | Implementation |
|----------|-------------|----------------|
| **Retries** | Re-run failed tests | `pytest --reruns 2` |
| **Quarantine** | Isolate flaky tests | `@pytest.mark.flaky` |
| **Investigation** | Root cause analysis | Dedicated team time |
| **Stabilisation** | Fix underlying issues | Code review + fix |

```python
# Flaky test handling
@pytest.mark.flaky(reruns=2)
def test_potentially_flaky_operation():
    # Test with retries
    pass
```

### 6.3 Continuous Improvement

```mermaid
flowchart LR
    subgraph Improvement["CONTINUOUS IMPROVEMENT"]
        I1["Review<br/>Test results"]
        I2["Identify<br/>Gaps"]
        I3["Add<br/>New tests"]
        I4["Optimize<br/>Existing tests"]
        I5["Update<br/>Frameworks"]
    end

    I1 --> I2 --> I3 --> I4 --> I5
    I5 --> I1
```

### 6.4 Test Debt Management

| Debt Type | Identification | Action |
|-----------|----------------|--------|
| **Old Tests** | Outdated/ignored | Review and update |
| **Slow Tests** | > 5 seconds | Optimize or split |
| **Redundant Tests** | Overlapping coverage | Merge or remove |
| **Broken Tests** | Always failing | Fix or rewrite |

---

## 7. Appendices

### A. Test Execution Commands

```bash
# Backend tests
pytest                                           # Run all tests
pytest -m unit                                   # Run unit tests only
pytest -m integration                            # Run integration tests
pytest apps/materials/tests/                     # Run specific module
pytest --cov=apps --cov-report=html              # Generate coverage report

# Frontend tests
pnpm test                                        # Run all tests
pnpm test --coverage                             # Run with coverage
pnpm test --watch                                # Watch mode
pnpm cypress run                                 # Run E2E tests
pnpm cypress open                                # Open Cypress UI

# Performance tests
k6 run load-test.js                              # Run load test
k6 run -e API_BASE_URL=https://prod-api.example.com load-test.js

# Security tests
bandit -r apps/ -f html -o bandit-report.html   # Run Bandit
zap-cli quick-scan -t http://localhost:8000     # Quick ZAP scan
```

### B. Docker Test Setup

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: test_db
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_pass
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  backend:
    build:
      context: ./rm-rrs-backend
      dockerfile: docker/backend.Dockerfile
    environment:
      DEBUG: "true"
      SECRET_KEY: "test_secret_key"
      DATABASE_URL: "postgresql://test_user:test_pass@postgres:5432/test_db"
      REDIS_URL: "redis://redis:6379/0"
    volumes:
      - ./rm-rrs-backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    command: python manage.py runserver 0.0.0.0:8000
  
  frontend:
    build:
      context: ./rm-rrs-frontend
      dockerfile: docker/frontend.Dockerfile
    volumes:
      - ./rm-rrs-frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    depends_on:
      - backend
    command: pnpm dev --host
```

### C. CI/CD Pipeline Variables

```yaml
# Required GitHub Secrets
secrets:
  # Docker Registry
  DOCKER_USERNAME: string
  DOCKER_PASSWORD: string
  DOCKER_REGISTRY: string
  
  # Deployment
  STAGING_HOST: string
  PROD_HOST: string
  STAGING_SSH_KEY: string
  PROD_SSH_KEY: string
  
  # Security
  SNYK_TOKEN: string
  SONARQUBE_TOKEN: string
  
  # Notifications
  SLACK_WEBHOOK_URL: string
```

### D. Test Metrics Collection

```python
# tests/metrics_collector.py
import json
import time
from datetime import datetime
from typing import Dict, Any

class TestMetricsCollector:
    """Collect and report test metrics."""
    
    def __init__(self):
        self.metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'duration': 0,
            'coverage': {},
            'performance': {},
            'security': {},
        }
    
    def record_test_result(self, test_name: str, status: str, duration: float):
        """Record individual test result."""
        self.metrics['total_tests'] += 1
        if status == 'passed':
            self.metrics['passed'] += 1
        elif status == 'failed':
            self.metrics['failed'] += 1
        else:
            self.metrics['skipped'] += 1
        self.metrics['duration'] += duration
    
    def record_coverage(self, coverage: Dict[str, float]):
        """Record code coverage."""
        self.metrics['coverage'] = coverage
    
    def record_performance(self, metrics: Dict[str, Any]):
        """Record performance metrics."""
        self.metrics['performance'] = metrics
    
    def record_security(self, vulnerabilities: list):
        """Record security findings."""
        self.metrics['security'] = {
            'critical': len([v for v in vulnerabilities if v['severity'] == 'critical']),
            'high': len([v for v in vulnerabilities if v['severity'] == 'high']),
            'medium': len([v for v in vulnerabilities if v['severity'] == 'medium']),
            'low': len([v for v in vulnerabilities if v['severity'] == 'low']),
        }
    
    def report(self) -> Dict[str, Any]:
        """Generate final report."""
        return self.metrics
    
    def send_to_dashboard(self):
        """Send metrics to monitoring dashboard."""
        # Implementation depends on monitoring system
        pass
```

---

**Document Approval**

| Role | Name | Date |
|------|------|------|
| Author | [Name] | [Date] |
| Reviewer (QA Lead) | [Name] | [Date] |
| Reviewer (Tech Lead) | [Name] | [Date] |
| Reviewer (DevOps) | [Name] | [Date] |
| Approver | [Name] | [Date] |

---

**Change History**

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | [Date] | [Author] | Initial baseline test automation and CI/CD specification |
