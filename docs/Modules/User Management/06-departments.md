# Department Management

## Hierarchy

Departments support parent-child relationships.

Example:

```text
Quality
├── Quality Control
│   ├── Chemical Laboratory
│   └── Microbiology Laboratory
└── Quality Assurance

Warehouse
├── Raw Material Warehouse
└── Packaging Material Warehouse
└── Cold Warehouse
```

## User Assignment

Each user has exactly one primary department.

## Department Operations

System Administrators can:

- Create department
- Edit department
- Activate department
- Deactivate department
- View hierarchy
- Search departments

## Rules

- A department cannot be deactivated if active users depend on it unless those users are reassigned or the operation explicitly handles the dependency.
- A department cannot be deleted if referenced by historical records.
- A department cannot be its own parent.
- Circular department hierarchies are prohibited.
- Department changes are audited.

## Suggested UI

Use a tree view for hierarchy and a table/detail view for administration.
