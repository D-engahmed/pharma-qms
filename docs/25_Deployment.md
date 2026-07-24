# 25 — Deployment Specification

**Document Identifier:** RM-RRS-DEP-001
**Version:** 1.0
**Status:** Baseline
**Traces to:** Project Charter, SRS, NFR, SAS, Design Specification, Security Specification, Compliance Specification, Implementation Roadmap, Coding Roadmap
**Compliance Reference:** GAMP 5 (Deployment Phase), 21 CFR Part 11 (Electronic Records), EU GMP Annex 11 (Computerised Systems), ITIL 4 (Service Management)

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Deployment Strategy](#2-deployment-strategy)
3. [Environment Architecture](#3-environment-architecture)
4. [Infrastructure Requirements](#4-infrastructure-requirements)
5. [Deployment Artifacts](#5-deployment-artifacts)
6. [Deployment Procedure](#6-deployment-procedure)
7. [Validation and Testing](#7-validation-and-testing)
8. [Monitoring and Operations](#8-monitoring-and-operations)
9. [Disaster Recovery](#9-disaster-recovery)
10. [Security Hardening](#10-security-hardening)
11. [Performance Tuning](#11-performance-tuning)
12. [Appendices](#12-appendices)

---

## 1. Introduction

### 1.1 Purpose
This document defines the **Deployment Specification** for the **Raw Material Receiving & Release System (RM-RRS)** . It provides comprehensive deployment procedures, environment configurations, infrastructure requirements, security hardening measures, and operational runbooks. This document serves as the authoritative guide for deploying the system to production and maintaining it in a GMP-compliant operational state.

### 1.2 Scope
This deployment specification covers:
- **Deployment Strategy**: Blue-green deployment, canary releases, rollback procedures
- **Environment Architecture**: Production, staging, testing, and development environments
- **Infrastructure Requirements**: Hardware, software, networking, and storage
- **Deployment Artifacts**: Docker images, configuration files, database migrations
- **Deployment Procedure**: Step-by-step deployment instructions
- **Validation and Testing**: Smoke tests, validation, and verification
- **Monitoring and Operations**: Metrics, alerts, logging, and incident response
- **Disaster Recovery**: Backup, restoration, and business continuity
- **Security Hardening**: Infrastructure and application security controls
- **Performance Tuning**: Optimisation for production workloads

### 1.3 Deployment Principles

```mermaid
flowchart TD
    subgraph Principles["DEPLOYMENT PRINCIPLES"]
        P1["Automation<br/>All deployments automated via CI/CD"]
        P2["Repeatability<br/>Identical deployments every time"]
        P3["Auditability<br/>All deployment actions logged"]
        P4["Rollback<br/>Ability to revert to previous version"]
        P5["Zero Downtime<br/>No user impact during deployment"]
        P6["Validation<br/>Deployment verified before go-live"]
        P7["Security<br/>Secure by default configuration"]
    end
```

### 1.4 References

| Document | Reference |
|----------|-----------|
| 00_Project_Charter.md | Charter |
| 06_SRS.md | Software Requirements Specification |
| 07_NFR.md | Non-Functional Requirements |
| 08_SAS.md | Software Architecture Specification |
| 09_Design.md | Design Specification |
| 12_Security.md | Security Specification |
| 13_Compliance.md | Compliance Specification |
| 17_Backend_Architecture.md | Backend Architecture |
| 18_Frontend_Architecture.md | Frontend Architecture |
| 20_Implementation_Roadmap.md | Implementation Roadmap |
| RM-RRS-TEST-003 | Test Automation and CI/CD |
| GAMP 5 | Good Automated Manufacturing Practice |

---

## 2. Deployment Strategy

### 2.1 Deployment Approach

```mermaid
flowchart LR
    subgraph Strategy["DEPLOYMENT STRATEGY"]
        B["Build<br/>Docker Images<br/>Artifacts"]
        T["Test<br/>Unit + Integration<br/>Security + Performance"]
        V["Validate<br/>Smoke Tests<br/>Compliance Checks"]
        D["Deploy<br/>Blue-Green<br/>Zero Downtime"]
        M["Monitor<br/>Metrics<br/>Alerts"]
        R["Rollback<br/>If Validation Fails"]
    end

    B --> T --> V --> D --> M
    D --> R
    R --> B
```

### 2.2 Blue-Green Deployment

```mermaid
flowchart TD
    subgraph BlueGreen["BLUE-GREEN DEPLOYMENT"]
        subgraph Blue["BLUE (Current Production)"]
            LB1["Load Balancer"]
            BlueApp["Application (v1)"]
            BlueDB["Database (v1)"]
            LB1 --> BlueApp
            BlueApp --> BlueDB
        end

        subgraph Green["GREEN (New Version)"]
            GreenApp["Application (v2)"]
            GreenDB["Database (v2)"]
            GreenApp --> GreenDB
        end

        subgraph Routing["ROUTING"]
            Router["Router/Switch"]
            User["User Traffic"]
        end

        User --> Router
        Router -->|Active| LB1
        Router -.->|Standby| GreenApp
    end
```

### 2.3 Deployment Flow

```mermaid
sequenceDiagram
    participant Dev as Development
    participant CI as CI/CD Pipeline
    participant Staging as Staging Environment
    participant Blue as Blue Environment (Prod)
    participant Green as Green Environment
    participant Router as Router
    participant Monitor as Monitoring

    Dev->>CI: Push code to main
    CI->>CI: Build artifacts
    CI->>CI: Run tests
    CI->>Staging: Deploy to staging
    Staging->>Staging: Run smoke tests
    CI->>Green: Deploy to green
    Green->>Green: Run smoke tests
    Green->>Monitor: Send health checks
    Router->>Monitor: Check health
    Router->>Green: Route 10% traffic (canary)
    Router->>Green: Route 100% traffic (switch)
    Blue->>Blue: Drain connections
    Monitor->>Monitor: Verify metrics
    Blue->>Blue: Decommission
```

### 2.4 Rollback Strategy

| Scenario | Trigger | Action | RTO |
|----------|---------|--------|-----|
| **Deployment Failure** | Smoke tests fail | Automated rollback to previous version | < 5 min |
| **Performance Degradation** | Metrics threshold breached | Manual rollback | < 15 min |
| **Security Vulnerability** | Critical vulnerability detected | Emergency rollback | < 5 min |
| **Data Integrity Issue** | Validation failure | Manual rollback with data restoration | < 1 hour |

**Rollback Commands:**
```bash
# Automated rollback via CI/CD
./scripts/rollback.sh --environment production --target-version v1.0.0

# Manual rollback
docker-compose down
docker-compose --version v1.0.0 up -d
```

---

## 3. Environment Architecture

### 3.1 Environment Overview

```mermaid
flowchart TD
    subgraph Environments["DEPLOYMENT ENVIRONMENTS"]
        DEV["Development<br/>Local Docker Compose<br/>Developers"]
        CI["CI/CD Pipeline<br/>Ephemeral<br/>Automated Tests"]
        TEST["Test Environment<br/>Full Stack<br/>QA Team"]
        STAGING["Staging Environment<br/>Production-like<br/>UAT + Validation"]
        PROD["Production Environment<br/>Live System<br/>End Users"]
    end

    DEV --> CI --> TEST --> STAGING --> PROD
```

### 3.2 Environment Specifications

| Environment | Purpose | Configuration | Data | Access |
|-------------|---------|---------------|------|--------|
| **Development** | Developer testing | Docker Compose, debug | Synthetic | Dev Team |
| **CI/CD** | Automated tests | Ephemeral containers | Synthetic | CI Pipeline |
| **Test** | QA system testing | Full stack, debug | Synthetic | QA Team |
| **Staging** | UAT, Validation | Production-like | Anonymised prod | QA + Business |
| **Production** | Live operation | Production config | Real data | End Users |

### 3.3 Production Architecture

```mermaid
flowchart TD
    subgraph External["EXTERNAL"]
        DNS["DNS: rm-rrs.example.com"]
        CDN["CDN / DDoS Protection"]
        WAF["Web Application Firewall"]
    end

    subgraph DMZ["DMZ"]
        LB["Load Balancer (x2)"]
        NGINX["Nginx Reverse Proxy"]
    end

    subgraph App["APPLICATION LAYER"]
        subgraph Backend["Backend Servers (x3)"]
            B1["Django App Server 1"]
            B2["Django App Server 2"]
            B3["Django App Server 3"]
        end

        subgraph Workers["Background Workers"]
            CW1["Celery Worker 1"]
            CW2["Celery Worker 2"]
            CB["Celery Beat"]
        end

        subgraph Frontend["Frontend Servers (x2)"]
            F1["React App Server 1"]
            F2["React App Server 2"]
        end
    end

    subgraph Data["DATA LAYER"]
        PG["PostgreSQL (Primary)"]
        PGReplica["PostgreSQL (Replica)"]
        Redis["Redis Cluster"]
        S3["S3/Cloud Storage"]
    end

    subgraph Monitoring["MONITORING"]
        Prom["Prometheus"]
        Graf["Grafana"]
        ELK["ELK Stack"]
        Pager["PagerDuty"]
    end

    DNS --> CDN --> WAF --> LB
    LB --> NGINX
    NGINX --> F1
    NGINX --> F2
    NGINX --> B1
    NGINX --> B2
    NGINX --> B3

    B1 --> PG
    B2 --> PG
    B3 --> PG
    B1 --> PGReplica
    B2 --> PGReplica
    B3 --> PGReplica
    B1 --> Redis
    B2 --> Redis
    B3 --> Redis
    B1 --> S3
    B2 --> S3
    B3 --> S3

    CW1 --> PG
    CW2 --> PG
    CW1 --> Redis
    CW2 --> Redis
    CB --> Redis

    Prom --> B1
    Prom --> B2
    Prom --> B3
    Prom --> PG
    Prom --> Redis
    Graf --> Prom
    ELK --> B1
    ELK --> B2
    ELK --> B3
    ELK --> PG

    Pager --> Graf
    Pager --> ELK
```

### 3.4 Network Architecture

| Component | Port | Protocol | Access |
|-----------|------|----------|--------|
| **Nginx** | 443 | HTTPS | Internet |
| **Nginx** | 80 | HTTP | Redirect to 443 |
| **Backend** | 8000 | HTTP | Internal only |
| **PostgreSQL** | 5432 | TCP | Internal only |
| **Redis** | 6379 | TCP | Internal only |
| **Monitoring** | 9090 | HTTP | Internal + VPN |

**Firewall Rules:**
```
# Allow HTTPS from internet
Allow 0.0.0.0/0:443

# Allow SSH from bastion
Allow 10.0.0.0/24:22

# Allow internal communication
Allow 10.0.0.0/24:*

# Deny everything else
Deny *:*
```

---

## 4. Infrastructure Requirements

### 4.1 Hardware Requirements (Production)

| Component | CPU | RAM | Storage | Count |
|-----------|-----|-----|---------|-------|
| **Backend Server** | 4 vCPU | 8 GB | 50 GB | 3 |
| **Frontend Server** | 2 vCPU | 4 GB | 20 GB | 2 |
| **PostgreSQL** | 8 vCPU | 16 GB | 200 GB SSD | 1 |
| **PostgreSQL Replica** | 8 vCPU | 16 GB | 200 GB SSD | 1 |
| **Redis** | 4 vCPU | 8 GB | 20 GB | 3 (cluster) |
| **Celery Worker** | 2 vCPU | 4 GB | 20 GB | 2 |
| **Nginx/Load Balancer** | 2 vCPU | 4 GB | 20 GB | 2 |

### 4.2 Software Requirements

| Component | Version | Requirement |
|-----------|---------|-------------|
| **Operating System** | Ubuntu 22.04 LTS | Server OS |
| **Docker** | 24.0+ | Container runtime |
| **Docker Compose** | 2.20+ | Container orchestration |
| **Nginx** | 1.24+ | Reverse proxy |
| **PostgreSQL** | 15+ | Database |
| **Redis** | 7+ | Cache and broker |
| **Python** | 3.11+ | Backend runtime |
| **Node.js** | 18+ | Frontend runtime |

### 4.3 Network Requirements

| Requirement | Specification |
|-------------|---------------|
| **Bandwidth** | Minimum 100 Mbps (1 Gbps recommended) |
| **Latency** | < 50 ms between services |
| **SSL/TLS** | TLS 1.2+ with valid certificate |
| **DNS** | A record for `rm-rrs.example.com` |
| **Static IP** | At least one public static IP |
| **Subnet** | /24 private subnet for internal services |

### 4.4 Storage Requirements

| Volume | Size | Type | Purpose |
|--------|------|------|---------|
| **PostgreSQL Data** | 200 GB | SSD | Database storage |
| **PostgreSQL WAL** | 50 GB | SSD | Write-ahead logging |
| **Backup Volume** | 500 GB | HDD | Backup storage |
| **Application Logs** | 50 GB | SSD | Log storage |
| **Static Files** | 20 GB | SSD | Static assets |
| **Media Files** | 50 GB | SSD | Uploaded content |

---

## 5. Deployment Artifacts

### 5.1 Docker Images

```yaml
# rm-rrs-backend/docker/backend.Dockerfile
FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt requirements/prod.txt ./
RUN pip install --no-cache-dir -r prod.txt

COPY . .

# Production image
FROM python:3.11-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--workers", "4", "--threads", "2", "--bind", "0.0.0.0:8000", "--timeout", "120"]
```

```dockerfile
# rm-rrs-frontend/docker/frontend.Dockerfile
FROM node:18-alpine AS builder

WORKDIR /build

RUN npm install -g pnpm

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/storekeeper/package.json apps/storekeeper/
COPY apps/sampler/package.json apps/sampler/
COPY apps/analyst/package.json apps/analyst/
COPY apps/qcmanager/package.json apps/qcmanager/
COPY apps/admin/package.json apps/admin/
COPY shared/ ./shared/

RUN pnpm install --frozen-lockfile

COPY . .

RUN pnpm build --filter=storekeeper --filter=sampler --filter=analyst --filter=qcmanager --filter=admin

# Production image
FROM nginx:alpine

COPY --from=builder /build/apps/storekeeper/dist /usr/share/nginx/html/storekeeper
COPY --from=builder /build/apps/sampler/dist /usr/share/nginx/html/sampler
COPY --from=builder /build/apps/analyst/dist /usr/share/nginx/html/analyst
COPY --from=builder /build/apps/qcmanager/dist /usr/share/nginx/html/qcmanager
COPY --from=builder /build/apps/admin/dist /usr/share/nginx/html/admin

COPY docker/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
```

### 5.2 Docker Compose Configuration

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: rm-rrs-postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
      - ./config/postgresql.conf:/etc/postgresql/postgresql.conf
    ports:
      - "5432:5432"
    networks:
      - rm-rrs-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    image: redis:7-alpine
    container_name: rm-rrs-redis
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - rm-rrs-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  backend:
    build:
      context: ./rm-rrs-backend
      dockerfile: docker/backend.Dockerfile
    image: ${DOCKER_REGISTRY}/rm-rrs-backend:${VERSION}
    container_name: rm-rrs-backend
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
      - EMAIL_HOST=${EMAIL_HOST}
      - EMAIL_PORT=${EMAIL_PORT}
      - EMAIL_HOST_USER=${EMAIL_HOST_USER}
      - EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD}
      - STORAGE_BACKEND=s3
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_STORAGE_BUCKET_NAME=${AWS_STORAGE_BUCKET_NAME}
      - AWS_S3_REGION_NAME=${AWS_S3_REGION_NAME}
    volumes:
      - ./staticfiles:/static
      - ./media:/media
    ports:
      - "8000:8000"
    networks:
      - rm-rrs-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G

  celery:
    build:
      context: ./rm-rrs-backend
      dockerfile: docker/celery.Dockerfile
    image: ${DOCKER_REGISTRY}/rm-rrs-celery:${VERSION}
    container_name: rm-rrs-celery
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    networks:
      - rm-rrs-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    command: celery -A rm_rrs worker --loglevel=info --concurrency=4
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

  celery-beat:
    build:
      context: ./rm-rrs-backend
      dockerfile: docker/celery.Dockerfile
    image: ${DOCKER_REGISTRY}/rm-rrs-celery-beat:${VERSION}
    container_name: rm-rrs-celery-beat
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    networks:
      - rm-rrs-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    command: celery -A rm_rrs beat --loglevel=info
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    build:
      context: ./rm-rrs-frontend
      dockerfile: docker/frontend.Dockerfile
    image: ${DOCKER_REGISTRY}/rm-rrs-frontend:${VERSION}
    container_name: rm-rrs-frontend
    ports:
      - "80:80"
    networks:
      - rm-rrs-network
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  nginx:
    image: nginx:alpine
    container_name: rm-rrs-nginx
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./staticfiles:/static:ro
      - ./media:/media:ro
    ports:
      - "443:443"
      - "80:80"
    networks:
      - rm-rrs-network
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M

  prometheus:
    image: prom/prometheus:latest
    container_name: rm-rrs-prometheus
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - rm-rrs-network
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  grafana:
    image: grafana/grafana:latest
    container_name: rm-rrs-grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    ports:
      - "3000:3000"
    networks:
      - rm-rrs-network
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  rm-rrs-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

### 5.3 Nginx Configuration

```nginx
# nginx/nginx.conf
user nginx;
worker_processes auto;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    multi_accept on;
    use epoll;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format json escape=json '{"timestamp":"$time_iso8601",'
        '"client_ip":"$remote_addr",'
        '"request":"$request",'
        '"status":"$status",'
        '"body_bytes":"$body_bytes_sent",'
        '"referer":"$http_referer",'
        '"user_agent":"$http_user_agent",'
        '"request_time":"$request_time",'
        '"upstream_response_time":"$upstream_response_time",'
        '"x_forwarded_for":"$http_x_forwarded_for"}';

    access_log /var/log/nginx/access.log json;
    error_log /var/log/nginx/error.log warn;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json application/xml+rss application/rss+xml image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;

    # Upstreams
    upstream backend {
        server backend:8000 max_fails=3 fail_timeout=30s;
    }

    # Server configuration
    server {
        listen 80;
        server_name rm-rrs.example.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name rm-rrs.example.com;

        ssl_certificate /etc/nginx/ssl/rm-rrs.example.com.crt;
        ssl_certificate_key /etc/nginx/ssl/rm-rrs.example.com.key;

        # Root redirect
        location / {
            return 301 /storekeeper;
        }

        # Storekeeper App
        location /storekeeper {
            alias /usr/share/nginx/html/storekeeper;
            try_files $uri $uri/ /storekeeper/index.html;
        }

        # Sampler App
        location /sampler {
            alias /usr/share/nginx/html/sampler;
            try_files $uri $uri/ /sampler/index.html;
        }

        # Analyst App
        location /analyst {
            alias /usr/share/nginx/html/analyst;
            try_files $uri $uri/ /analyst/index.html;
        }

        # QC Manager App
        location /qcmanager {
            alias /usr/share/nginx/html/qcmanager;
            try_files $uri $uri/ /qcmanager/index.html;
        }

        # Admin Console
        location /admin {
            alias /usr/share/nginx/html/admin;
            try_files $uri $uri/ /admin/index.html;
        }

        # Login Page
        location /login {
            alias /usr/share/nginx/html/login;
            try_files $uri $uri/ /login/index.html;
        }

        # API
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_cache_bypass $http_upgrade;
            proxy_read_timeout 120s;
            proxy_connect_timeout 120s;
        }

        # Admin interface
        location /admin/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files
        location /static/ {
            alias /static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Media files
        location /media/ {
            alias /media/;
            expires 1d;
            add_header Cache-Control "public, immutable";
        }

        # Health check
        location /health {
            proxy_pass http://backend;
            access_log off;
        }

        # Metrics (internal)
        location /metrics {
            proxy_pass http://backend;
            allow 10.0.0.0/24;
            deny all;
        }
    }
}
```

### 5.4 Environment Variables

```bash
# .env.prod
# Application
DEBUG=false
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=rm-rrs.example.com,api.rm-rrs.example.com
VERSION=1.0.0

# Database
POSTGRES_DB=rm_rrs
POSTGRES_USER=rm_rrs_user
POSTGRES_PASSWORD=secure_db_password

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret-key

# Celery
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# Email
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=notifications@rm-rrs.example.com
EMAIL_HOST_PASSWORD=email_password

# AWS S3 (for file storage)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=rm-rrs-storage
AWS_S3_REGION_NAME=us-east-1

# Monitoring
GRAFANA_PASSWORD=secure_grafana_password

# Docker Registry
DOCKER_REGISTRY=registry.rm-rrs.example.com
```

---

## 6. Deployment Procedure

### 6.1 Pre-Deployment Checklist

| Check | Description | Status |
|-------|-------------|--------|
| ☐ | All tests passing (unit, integration, E2E) | |
| ☐ | Security scans passed | |
| ☐ | Performance tests passed | |
| ☐ | Code review approved | |
| ☐ | Validation documentation complete | |
| ☐ | Database backups taken | |
| ☐ | Rollback plan in place | |
| ☐ | Monitoring configured | |
| ☐ | Notification channels configured | |
| ☐ | Change request approved | |

### 6.2 Deployment Steps

```mermaid
flowchart TD
    subgraph Steps["DEPLOYMENT STEPS"]
        S1["1. Pre-Deployment<br/>Backup database<br/>Notify stakeholders"]
        S2["2. Build<br/>Build Docker images<br/>Tag with version"]
        S3["3. Staging<br/>Deploy to staging<br/>Run smoke tests"]
        S4["4. Blue-Green<br/>Deploy to Green environment<br/>Run validation"]
        S5["5. Canary<br/>Route 10% traffic to Green<br/>Monitor metrics"]
        S6["6. Full Switch<br/>Route 100% traffic to Green<br/>Run final smoke tests"]
        S7["7. Decommission<br/>Drain Blue environment<br/>Prepare for rollback"]
        S8["8. Post-Deployment<br/>Update documentation<br/>Notify stakeholders"]
    end

    S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7 --> S8
```

### 6.3 Deployment Commands

```bash
# 1. Pre-Deployment
./scripts/backup.sh
./scripts/notify.sh "Starting deployment of version ${VERSION}"

# 2. Build Docker images
docker build -t rm-rrs-backend:${VERSION} -f rm-rrs-backend/docker/backend.Dockerfile ./rm-rrs-backend
docker build -t rm-rrs-frontend:${VERSION} -f rm-rrs-frontend/docker/frontend.Dockerfile ./rm-rrs-frontend
docker build -t rm-rrs-celery:${VERSION} -f rm-rrs-backend/docker/celery.Dockerfile ./rm-rrs-backend

# 3. Push to registry
docker tag rm-rrs-backend:${VERSION} ${DOCKER_REGISTRY}/rm-rrs-backend:${VERSION}
docker tag rm-rrs-frontend:${VERSION} ${DOCKER_REGISTRY}/rm-rrs-frontend:${VERSION}
docker tag rm-rrs-celery:${VERSION} ${DOCKER_REGISTRY}/rm-rrs-celery:${VERSION}

docker push ${DOCKER_REGISTRY}/rm-rrs-backend:${VERSION}
docker push ${DOCKER_REGISTRY}/rm-rrs-frontend:${VERSION}
docker push ${DOCKER_REGISTRY}/rm-rrs-celery:${VERSION}

# 4. Deploy to staging
ssh staging-server "cd /opt/rm-rrs && docker-compose -f docker-compose.staging.yml pull && docker-compose -f docker-compose.staging.yml up -d"

# 5. Run smoke tests on staging
./scripts/smoke-tests.sh --environment staging

# 6. Deploy to Green (production)
ssh prod-server "cd /opt/rm-rrs && docker-compose -f docker-compose.green.yml pull && docker-compose -f docker-compose.green.yml up -d"

# 7. Run validation on Green
./scripts/validation-tests.sh --environment green

# 8. Canary - Route 10% traffic
./scripts/route-traffic.sh --green-percentage 10

# 9. Monitor canary
./scripts/monitor-canary.sh --duration 300

# 10. Full switch - Route 100% traffic to Green
./scripts/route-traffic.sh --green-percentage 100

# 11. Run final smoke tests
./scripts/smoke-tests.sh --environment production

# 12. Decommission Blue
ssh prod-server "cd /opt/rm-rrs && docker-compose -f docker-compose.blue.yml down"

# 13. Post-deployment
./scripts/backup.sh
./scripts/notify.sh "Deployment of version ${VERSION} complete"
```

### 6.4 Migration Handling

```python
# scripts/run_migrations.py
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def run_migrations():
    """Run database migrations with proper error handling."""
    print(f"[{datetime.now()}] Starting database migrations...")
    
    # Create backup before migrations
    backup_file = f"/backups/pre_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    subprocess.run([
        "pg_dump",
        "-U", os.environ['POSTGRES_USER'],
        "-d", os.environ['POSTGRES_DB'],
        "-f", backup_file
    ], check=True)
    print(f"[{datetime.now()}] Backup created: {backup_file}")
    
    # Run migrations
    try:
        result = subprocess.run([
            "python", "manage.py", "migrate",
            "--settings=config.settings.production"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"[{datetime.now()}] Migration failed: {result.stderr}")
            # Restore backup
            print(f"[{datetime.now()}] Restoring backup...")
            subprocess.run([
                "psql",
                "-U", os.environ['POSTGRES_USER'],
                "-d", os.environ['POSTGRES_DB'],
                "-f", backup_file
            ], check=True)
            sys.exit(1)
        
        print(f"[{datetime.now()}] Migrations completed successfully")
        print(result.stdout)
        
    except Exception as e:
        print(f"[{datetime.now()}] Migration error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()
```

---

## 7. Validation and Testing

### 7.1 Smoke Tests

```python
# scripts/smoke_tests.py
import requests
import json
import sys
from datetime import datetime

def run_smoke_tests(environment):
    """Run smoke tests for deployment validation."""
    base_url = {
        'staging': 'https://staging.rm-rrs.example.com',
        'production': 'https://rm-rrs.example.com',
        'green': 'https://green.rm-rrs.example.com',
    }.get(environment)
    
    if not base_url:
        print(f"Unknown environment: {environment}")
        sys.exit(1)
    
    tests = [
        {
            'name': 'Health Check',
            'url': f'{base_url}/health',
            'expected_status': 200,
        },
        {
            'name': 'API Access',
            'url': f'{base_url}/api/v1/auth/me/',
            'expected_status': 401,  # Unauthorized without token
        },
        {
            'name': 'Login',
            'url': f'{base_url}/api/v1/auth/login/',
            'method': 'POST',
            'payload': {'username': 'test_user', 'password': 'test_password'},
            'expected_status': 200,
        },
        {
            'name': 'Static Files',
            'url': f'{base_url}/static/admin/css/base.css',
            'expected_status': 200,
        },
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print(f"[{datetime.now()}] Running: {test['name']}")
        
        try:
            if test.get('method') == 'POST':
                response = requests.post(
                    test['url'],
                    json=test.get('payload', {}),
                    timeout=30
                )
            else:
                response = requests.get(test['url'], timeout=30)
            
            if response.status_code == test['expected_status']:
                print(f"✅ {test['name']}: Passed")
                passed += 1
            else:
                print(f"❌ {test['name']}: Failed (Expected {test['expected_status']}, Got {response.status_code})")
                failed += 1
                
        except Exception as e:
            print(f"❌ {test['name']}: Failed - {str(e)}")
            failed += 1
    
    print(f"\nSmoke Tests Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    import sys
    environment = sys.argv[1] if len(sys.argv) > 1 else 'staging'
    run_smoke_tests(environment)
```

### 7.2 Validation Test Suite

```python
# scripts/validation_tests.py
import requests
import json
import time
from datetime import datetime

class ValidationTestSuite:
    """Comprehensive validation test suite for deployment."""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.results = []
    
    def run_all_tests(self):
        """Run all validation tests."""
        self.test_login()
        self.test_material_workflow()
        self.test_sampling_workflow()
        self.test_coa_workflow()
        self.test_audit_trail()
        self.test_e_signature()
        self.print_report()
    
    def test_login(self):
        """Test authentication flow."""
        print(f"[{datetime.now()}] Testing Login...")
        
        # Test valid login
        response = requests.post(
            f'{self.base_url}/api/v1/auth/login/',
            json={'username': 'storekeeper1', 'password': 'TestPass123!'}
        )
        
        if response.status_code == 200:
            self.results.append(('Login - Valid', True))
            self.session = response.cookies
        else:
            self.results.append(('Login - Valid', False))
        
        # Test invalid login
        response = requests.post(
            f'{self.base_url}/api/v1/auth/login/',
            json={'username': 'invalid', 'password': 'invalid'}
        )
        
        self.results.append(('Login - Invalid', response.status_code == 401))
    
    def test_material_workflow(self):
        """Test material registration and sampling request."""
        print(f"[{datetime.now()}] Testing Material Workflow...")
        
        # Create material
        response = requests.post(
            f'{self.base_url}/api/v1/materials/',
            json={
                'material_name': 'Validation Test Material',
                'supplier': 'Test Supplier',
                'supplier_batch': 'VALIDATION-001',
                'exp_date': '2027-01-15',
                'receipt_date': '2026-01-15',
                'received_by': 'Test User'
            },
            cookies=self.session
        )
        
        if response.status_code != 201:
            self.results.append(('Material Creation', False))
            return
        
        material_id = response.json()['data']['id']
        self.results.append(('Material Creation', True))
        
        # Request sampling
        response = requests.post(
            f'{self.base_url}/api/v1/materials/{material_id}/request-sampling/',
            cookies=self.session
        )
        
        self.results.append(('Sampling Request', response.status_code == 200))
    
    def test_coa_workflow(self):
        """Test COA creation and approval workflow."""
        print(f"[{datetime.now()}] Testing COA Workflow...")
        # Implementation...
        pass
    
    def test_audit_trail(self):
        """Test audit trail logging."""
        print(f"[{datetime.now()}] Testing Audit Trail...")
        # Implementation...
        pass
    
    def test_e_signature(self):
        """Test electronic signature verification."""
        print(f"[{datetime.now()}] Testing E-Signature...")
        # Implementation...
        pass
    
    def print_report(self):
        """Print validation test results."""
        print("\n" + "="*50)
        print("VALIDATION TEST REPORT")
        print("="*50)
        
        passed = sum(1 for r in self.results if r[1])
        failed = len(self.results) - passed
        
        for test_name, result in self.results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print("-"*50)
        print(f"Total: {len(self.results)} | Passed: {passed} | Failed: {failed}")
        print("="*50)
        
        if failed > 0:
            sys.exit(1)

if __name__ == "__main__":
    import sys
    suite = ValidationTestSuite(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8000')
    suite.run_all_tests()
```

---

## 8. Monitoring and Operations

### 8.1 Metrics Collection

```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:9187']
    metrics_path: '/metrics'

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:9121']
    metrics_path: '/metrics'

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:9113']
    metrics_path: '/metrics'

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
    metrics_path: '/metrics'
```

### 8.2 Alert Rules

```yaml
# prometheus/alerts.yml
groups:
  - name: application_alerts
    rules:
      - alert: HighErrorRate
        expr: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}% over the last 5 minutes"

      - alert: SlowAPIResponse
        expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow API responses detected"
          description: "95th percentile response time is {{ $value }}s"

      - alert: DatabaseHighConnections
        expr: pg_stat_database_numbackends > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database connections"
          description: "Database connections are at {{ $value }}"

      - alert: CeleryQueueBacklog
        expr: celery_queue_length > 100
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Celery queue backlog"
          description: "Celery queue has {{ $value }} tasks pending"

      - alert: LowDiskSpace
        expr: node_filesystem_avail_bytes / node_filesystem_size_bytes * 100 < 15
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space"
          description: "Disk is {{ $value }}% full"

      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service down"
          description: "{{ $labels.instance }} is down"
```

### 8.3 Logging Configuration

```python
# config/settings/production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '{"timestamp":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","message":"%(message)s","module":"%(module)s","filename":"%(filename)s"}'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/rm-rrs/app.log',
            'maxBytes': 104857600,  # 100MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'audit': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/rm-rrs/audit.log',
            'maxBytes': 104857600,
            'backupCount': 20,
            'formatter': 'json',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file'],
    },
    'loggers': {
        'django': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
        },
        'apps.audit': {
            'level': 'INFO',
            'handlers': ['audit'],
            'propagate': False,
        },
        'apps.esignature': {
            'level': 'INFO',
            'handlers': ['audit'],
            'propagate': False,
        },
    },
}
```

### 8.4 Incident Response Plan

```mermaid
flowchart TD
    subgraph IR["INCIDENT RESPONSE PROCESS"]
        D["1. Detection<br/>Monitoring alerts<br/>User reports"]
        A["2. Assessment<br/>Severity classification<br/>Impact analysis"]
        C["3. Containment<br/>Isolate affected systems<br/>Prevent further damage"]
        E["4. Eradication<br/>Remove root cause<br/>Apply fixes"]
        R["5. Recovery<br/>Restore services<br/>Verify operation"]
        L["6. Lessons Learned<br/>Post-mortem<br/>Prevent recurrence"]
    end

    D --> A --> C --> E --> R --> L
    L --> D
```

**Incident Severity Levels:**

| Level | Description | Response Time | Escalation |
|-------|-------------|---------------|------------|
| **P1 - Critical** | System down, data loss, security breach | Immediate (15 min) | Tech Lead, Management |
| **P2 - High** | Major feature broken, performance issue | 1 hour | Tech Lead |
| **P3 - Medium** | Minor feature broken, cosmetic issues | 4 hours | Dev Team |
| **P4 - Low** | Non-urgent issues | 24 hours | Dev Team |

---

## 9. Disaster Recovery

### 9.1 Backup Strategy

```mermaid
flowchart TD
    subgraph Backup["BACKUP STRATEGY"]
        B1["Full Database Backup<br/>Daily at 02:00 UTC"]
        B2["WAL Archiving<br/>Continuous"]
        B3["Application Code<br/>Version Control (Git)"]
        B4["Configuration<br/>Infrastructure as Code"]
        B5["Media Files<br/>S3/Cloud Storage"]
    end

    subgraph Retention["RETENTION POLICY"]
        R1["Daily Backups<br/>30 days"]
        R2["Weekly Backups<br/>12 months"]
        R3["Monthly Backups<br/>7 years"]
        R4["Yearly Backups<br/>Permanent archive"]
    end

    Backup --> Retention
```

### 9.2 Backup Commands

```bash
# scripts/backup.sh
#!/bin/bash
set -e

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Database backup
echo "Creating database backup..."
pg_dump -U ${POSTGRES_USER} -d ${POSTGRES_DB} -Fc -f ${BACKUP_DIR}/db_${DATE}.dump

# WAL archiving (continuous)
echo "WAL archiving enabled..."

# Media files backup
echo "Backing up media files..."
tar -czf ${BACKUP_DIR}/media_${DATE}.tar.gz /media/

# Application code backup (from Git)
echo "Backing up application code..."
git archive --format=tar.gz --output=${BACKUP_DIR}/code_${DATE}.tar.gz HEAD

# Encrypt backups
echo "Encrypting backups..."
gpg --encrypt --recipient backup@rm-rrs.example.com ${BACKUP_DIR}/db_${DATE}.dump
gpg --encrypt --recipient backup@rm-rrs.example.com ${BACKUP_DIR}/media_${DATE}.tar.gz
gpg --encrypt --recipient backup@rm-rrs.example.com ${BACKUP_DIR}/code_${DATE}.tar.gz

# Upload to off-site storage
echo "Uploading to off-site storage..."
aws s3 sync ${BACKUP_DIR}/ s3://${BACKUP_BUCKET}/backups/${DATE}/ --exclude "*.gpg"

# Clean old backups
echo "Cleaning old backups..."
find ${BACKUP_DIR} -type f -mtime +${RETENTION_DAYS} -delete

echo "Backup completed: ${DATE}"
```

### 9.3 Recovery Procedures

```mermaid
flowchart TD
    subgraph Recovery["RECOVERY PROCEDURES"]
        R1["1. Assess Damage<br/>Determine extent of data loss"]
        R2["2. Choose Recovery Point<br/>Select appropriate backup"]
        R3["3. Restore Database<br/>Restore from backup + WAL"]
        R4["4. Restore Media<br/>Restore from S3 backup"]
        R5["5. Deploy Application<br/>Deploy from Git/registry"]
        R6["6. Verify Recovery<br/>Run validation tests"]
        R7["7. Resume Operations<br/>Switch back to production"]
    end

    R1 --> R2 --> R3 --> R4 --> R5 --> R6 --> R7
```

**Recovery Commands:**

```bash
# scripts/restore.sh
#!/bin/bash
set -e

BACKUP_FILE=$1
if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./restore.sh <backup_file>"
    exit 1
fi

echo "Restoring from backup: ${BACKUP_FILE}"

# Stop services
echo "Stopping services..."
docker-compose down

# Restore database
echo "Restoring database..."
pg_restore -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c -v ${BACKUP_FILE}

# Restore media files
echo "Restoring media files..."
tar -xzf ${BACKUP_FILE}.media.tar.gz -C /

# Restore code
echo "Restoring application code..."
git checkout ${BACKUP_FILE}.commit

# Start services
echo "Starting services..."
docker-compose up -d

# Run migrations
echo "Running migrations..."
docker-compose exec backend python manage.py migrate --settings=config.settings.production

# Run smoke tests
echo "Running smoke tests..."
./scripts/smoke-tests.sh --environment production

echo "Restore completed."
```

### 9.4 Recovery Time Objectives (RTO/RPO)

| Scenario | RTO | RPO | Action |
|----------|-----|-----|--------|
| **Database Failure** | < 1 hour | < 15 min | Restore from backup + WAL |
| **Application Failure** | < 30 min | < 5 min | Restart services |
| **Server Failure** | < 2 hours | < 15 min | Provision new server |
| **Data Corruption** | < 4 hours | < 1 hour | Restore from clean backup |
| **Full Disaster** | < 8 hours | < 1 hour | Off-site restoration |

---

## 10. Security Hardening

### 10.1 Infrastructure Hardening

| Area | Control | Implementation |
|------|---------|----------------|
| **Operating System** | Minimal packages | Only essential packages installed |
| **Operating System** | Regular updates | Automated security updates |
| **Operating System** | Firewall | UFW/iptables with restricted rules |
| **Operating System** | SSH | Key-based auth, fail2ban, port change |
| **Container Security** | Non-root user | Containers run as non-root |
| **Container Security** | Read-only FS | Critical containers read-only |
| **Network Security** | TLS 1.2+ | SSL/TLS with strong ciphers |
| **Network Security** | WAF | Web Application Firewall |
| **Network Security** | Rate Limiting | Nginx rate limiting |
| **Network Security** | IP Whitelist | Internal network restrictions |

### 10.2 Application Security

| Control | Implementation |
|---------|----------------|
| **Authentication** | JWT with HTTP-only cookies |
| **Authorisation** | RBAC with Django permissions |
| **Input Validation** | DRF serializers + Zod schemas |
| **XSS Protection** | React auto-escaping + CSP headers |
| **SQL Injection** | Django ORM parameterised queries |
| **CSRF Protection** | CSRF tokens + SameSite cookies |
| **Session Security** | Secure, HttpOnly, SameSite cookies |
| **Password Storage** | bcrypt hashing |
| **Secrets Management** | Environment variables |
| **Audit Logging** | Immutable audit trail |

### 10.3 Security Headers Configuration

```nginx
# Security headers in Nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "
    default-src 'self';
    script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://fonts.googleapis.com;
    style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
    font-src 'self' https://fonts.gstatic.com;
    img-src 'self' data: https:;
    connect-src 'self' https://api.rm-rrs.example.com;
" always;
```

### 10.4 Database Security

```sql
-- Database hardening
-- Use strong passwords
ALTER USER rm_rrs_user WITH PASSWORD 'strong_password';

-- Restrict connections
REVOKE CONNECT ON DATABASE rm_rrs FROM PUBLIC;
GRANT CONNECT ON DATABASE rm_rrs TO rm_rrs_user;

-- Restrict schema access
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO rm_rrs_user;

-- Restrict table access
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO rm_rrs_user;

-- Enable SSL
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/etc/ssl/certs/server.crt';
ALTER SYSTEM SET ssl_key_file = '/etc/ssl/private/server.key';

-- Restrict admin access
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM PUBLIC;
```

---

## 11. Performance Tuning

### 11.1 Database Optimisation

```sql
-- PostgreSQL performance tuning
-- Memory settings (for 16GB RAM system)
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET work_mem = '64MB';
ALTER SYSTEM SET maintenance_work_mem = '1GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET wal_buffers = '16MB';

-- Connection settings
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET max_parallel_workers = 8;

-- Checkpoint settings
ALTER SYSTEM SET checkpoint_timeout = '15min';
ALTER SYSTEM SET max_wal_size = '10GB';
ALTER SYSTEM SET min_wal_size = '2GB';

-- Query planning
ALTER SYSTEM SET enable_seqscan = off;  -- For specific high-query tables
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Reload configuration
SELECT pg_reload_conf();
```

### 11.2 Redis Optimisation

```conf
# redis.conf
# Memory management
maxmemory 512mb
maxmemory-policy allkeys-lru

# Persistence
appendonly yes
appendfsync everysec
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Performance
tcp-keepalive 60
timeout 300
tcp-backlog 511

# Security
requirepass your-redis-password
rename-command FLUSHALL ""
rename-command FLUSHDB ""
```

### 11.3 Django Performance

```python
# config/settings/production.py
# Database connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'CONN_MAX_AGE': 60,
            'OPTIONS': {
                'keepalives': 1,
                'keepalives_idle': 30,
                'keepalives_interval': 10,
                'keepalives_count': 3,
            }
        }
    }
}

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'SOCKET_TIMEOUT': 3,
        }
    }
}

# Session
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Static files
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
```

---

## 12. Appendices

### A. Deployment Checklist

| Phase | Task | Status |
|-------|------|--------|
| **Pre-Deployment** | Database backup taken | ☐ |
| **Pre-Deployment** | Configuration verified | ☐ |
| **Pre-Deployment** | Stakeholder notified | ☐ |
| **Pre-Deployment** | Change request approved | ☐ |
| **Build** | Docker images built | ☐ |
| **Build** | Images pushed to registry | ☐ |
| **Staging** | Deployed to staging | ☐ |
| **Staging** | Smoke tests passed | ☐ |
| **Green** | Deployed to green environment | ☐ |
| **Green** | Validation tests passed | ☐ |
| **Canary** | 10% traffic routed | ☐ |
| **Canary** | Metrics verified | ☐ |
| **Full Switch** | 100% traffic routed | ☐ |
| **Full Switch** | Smoke tests passed | ☐ |
| **Decommission** | Blue environment drained | ☐ |
| **Post-Deployment** | Documentation updated | ☐ |
| **Post-Deployment** | Stakeholder notified | ☐ |

### B. Troubleshooting Guide

| Issue | Possible Causes | Resolution |
|-------|-----------------|------------|
| **Service won't start** | Port conflict, misconfiguration | Check logs, verify config |
| **Database connection failed** | Credentials, network | Verify DATABASE_URL, check connectivity |
| **Redis connection failed** | Redis down, network | Check redis-service, connectivity |
| **Static files missing** | Build failed, collectstatic | Rebuild, run collectstatic |
| **API returns 500** | Code error, dependency | Check logs, debug |
| **Performance issues** | High load, inefficient queries | Monitor, optimise queries |
| **Security alert** | Vulnerability detected | Investigate, patch |

### C. Maintenance Schedule

| Activity | Frequency | Responsible |
|----------|-----------|-------------|
| **Security Updates** | Monthly | DevOps |
| **Database Backups** | Daily | DevOps |
| **Backup Verification** | Weekly | DevOps |
| **Log Rotation** | Daily | DevOps |
| **Performance Review** | Monthly | Tech Lead |
| **Security Audit** | Quarterly | Security |
| **User Access Review** | Quarterly | Compliance |
| **Compliance Review** | Annual | Compliance |

### D. Contact Information

| Role | Name | Email | Phone |
|------|------|-------|-------|
| **System Administrator** | [Name] | [Email] | [Phone] |
| **Application Administrator** | [Name] | [Email] | [Phone] |
| **Security Officer** | [Name] | [Email] | [Phone] |
| **Compliance Officer** | [Name] | [Email] | [Phone] |
| **Incident Response Lead** | [Name] | [Email] | [Phone] |

---

**Document Approval**

| Role | Name | Date |
|------|------|------|
| Author | [Name] | [Date] |
| Reviewer (DevOps) | [Name] | [Date] |
| Reviewer (Architecture) | [Name] | [Date] |
| Reviewer (Security) | [Name] | [Date] |
| Reviewer (Compliance) | [Name] | [Date] |
| Approver | [Name] | [Date] |

---

**Change History**

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | [Date] | [Author] | Initial baseline deployment specification |
