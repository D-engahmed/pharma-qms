# Functional and Non-Functional Requirements

## Functional Requirements

### User Creation

- An authorized System Administrator can create a user.
- Required fields are First Name, Last Name, Email, Job Title, Department, Employment Status, and at least one Role.
- Employee Number is unique.
- Email is unique.
- New accounts may be created with an administrator-assigned temporary password or another approved initial-password mechanism.
- New users can be flagged to force password change on first login.

### User Maintenance

System Administrators can:

- View users
- Search users
- Filter by status, department, and role
- Edit permitted profile information
- Change role assignments
- Activate/deactivate accounts
- Reset passwords
- Force password change

### User Deactivation

When a user becomes INACTIVE:

- Login must be rejected.
- Existing active sessions must be invalidated/terminated where technically supported.
- Historical records must continue to identify the user.
- The user must not be deleted.

### Role Management

System Administrators can:

- Create roles
- Edit roles
- Deactivate roles
- Assign permissions to roles
- View permissions assigned to roles

### Authorization

Every protected backend operation must check permissions.

### Authentication

- Login uses email and password.
- Passwords are stored only as secure password hashes.
- Minimum password length is 8 characters.
- Passwords must contain at least one number.
- Password complexity must not be unnecessarily excessive.
- Failed-login protection uses temporary lockout/rate limiting.
- Concurrent login is not permitted.
- If a user already has an active session, a new login is rejected with a clear message.
- Idle session timeout is required.

## Non-Functional Requirements

- PostgreSQL
- Django/DRF backend
- React/Vite/TypeScript frontend
- Docker-based development
- Transaction-safe security operations
- Auditability
- Server-side authorization
- No hard deletion of users
- Automated tests for security-critical behavior
