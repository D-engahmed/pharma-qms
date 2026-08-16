# RM Receiving System — Frontend Architecture

## 1. Architectural style

The frontend uses **feature-based modular architecture**. Business capabilities live under `src/features`; shared presentation primitives live under `src/components`.

### Dependency direction

```text
App
 └── Routes
      ├── Auth feature
      └── Receiving feature
           ├── UI components
           ├── Feature store
           ├── Domain services
           └── Domain types

Shared components / utils / lib
        ↑
Features depend on shared code
```

A feature must not import another feature's private implementation. Cross-feature behavior should go through an explicit shared contract or application-level route/orchestrator.

## 2. Receiving bounded context

`src/features/receiving/` is the main business domain. It is divided by operational role:

- `storekeeper/` — raw-material and packaging registration, receiving status, sampling requests.
- `sampler/` — sampling requests, sample history, product/semi-finished/bulk samples and labels.
- `analyst/` — sample testing and COA lifecycle.
- `qc-manager/` — COA review, approval/rejection and material release.
- `shared/` — receiving-specific presentation pieces used by more than one role.

## 3. State management

The current prototype uses `ReceivingProvider` as a feature store. Persistence is isolated behind `receivingStorage.ts`.

This is intentional: the UI should not know whether data comes from `localStorage`, REST, GraphQL, or another backend.

## 4. Production migration path

The current storage adapter is a prototype boundary only. A production implementation should replace it with:

```text
UI component
   ↓
Feature hook / action
   ↓
Feature service
   ↓
Authenticated API client
   ↓
Backend domain/API
   ↓
Database + audit/event store
```

For a GMP/QMS deployment, frontend-only state is insufficient. Backend authorization, immutable audit history, electronic-signature controls, validation rules, concurrency handling, and server-side workflow transitions must be authoritative.

## 5. Why this structure

- Reduces the original monolithic `App.jsx` into maintainable modules.
- Makes role-specific workflows independently testable.
- Prevents business logic from being embedded in global UI primitives.
- Gives the backend integration a clear seam.
- Makes future modules such as inventory, warehouse, QC specifications, deviations, CAPA, and document control possible without turning `App.tsx` into a monolith.
