# RM Receiving System — Professional React Structure

This project refactors the original RM Receiving System prototype into a feature-based React + TypeScript + Vite architecture.

## Architecture

- `components/` — globally reusable UI and layout primitives.
- `features/` — business capabilities. Receiving is the core domain; auth is isolated.
- `services/` — persistence/API boundary; localStorage is currently an adapter, not business logic.
- `store/` — feature state and persistence orchestration.
- `routes/` — application routing/protection boundary.
- `types/` — domain contracts.
- `utils/` — pure deterministic helpers.
- `lib/` — environment and third-party configuration.

## Run

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Important

The current application still uses the prototype's browser-local persistence. That is acceptable for a frontend prototype, but it is **not** a GMP production architecture. For production, replace the storage adapter with authenticated API services and add audit trails, RBAC enforcement, electronic signatures, immutable event history, validation, and backend persistence.
