# Role Management

## Initial Roles

1. Administrator
2. Store Keeper
3. Sampler
4. QC Analyst
5. QC Supervisor
6. Manager
7. System Administrator

## Multiple Roles

A user may have multiple roles.

Example:

User: Ahmed
Roles:
- QC Analyst
- QC Supervisor


Effective permissions are the union of permissions granted by the user's active roles.

## Role Operations

System Administrator only:

- Create role
- Edit role
- Activate role
- Deactivate role
- Assign permissions
- Remove permissions
- View users assigned to role

## System Administrator Protection

A System Administrator must not be able to remove their own final administrative authorization in a way that locks the account out unintentionally.

The backend must prevent unsafe self-demotion/self-removal of the final required administrative access.

## Role Deactivation

Deactivating a role does not delete it.

A deactivated role contributes no effective permissions.

The system should warn the administrator about affected users before deactivation.
