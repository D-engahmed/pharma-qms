# Mini-LIMS User Management Module — Overview

## Purpose

The User Management module manages the people who are authorized to use the Mini-LIMS application. Employee and application-account information are represented by a single `User` entity.

The module provides:

- Employee/user creation and maintenance
- Email-based authentication identity
- Department assignment
- Job title and employment status
- Role-profile assignment
- Multiple roles per user
- Database-driven permissions
- Authentication and session control
- Password management
- Account activation/deactivation
- User lifecycle management
- Security audit trail
- Separation of duties

## Design Decision: Employee and User Are Merged

There is no separate Employee table in Version 1.

A user record represents both:

1. The employee/person
2. The application login account

Every user has exactly one application account.

## Core Relationship

```text
User
 ├── Department
 ├── Job Title
 ├── Employment Status
 └── Roles (many-to-many)
       └── Permissions (many-to-many through Role)
```

## Authentication Identity

The user's email address is the login identifier.

Email must be unique and normalized.

## Employment Status

Version 1 supports:

- ACTIVE
- INACTIVE

Deactivating a user prevents authentication while preserving historical records.

## Roles

Initial roles:

- Administrator
- Store Keeper
- Sampler
- QC Analyst
- QC Supervisor
- Manager
- System Administrator

A user may have multiple roles.

## Authorization

Authorization is permission-based. Roles are collections of permissions.

The backend is the final authorization authority. Frontend permission checks only control presentation and usability.

## Audit

All security-sensitive User Management actions are audited.
