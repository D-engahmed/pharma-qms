# Testing Requirements

## Unit Tests

Test:

- Email normalization
- Password policy
- Permission calculation
- Department hierarchy validation
- Role assignment validation
- Status transitions
- Separation-of-duties checks

## Authentication Tests

- Successful login
- Invalid password
- Unknown email
- Inactive user
- Locked user
- Rate limiting
- Concurrent login rejection
- Idle timeout
- Logout
- Forced password change
- Password reset
- Password change

## Authorization Tests

For every protected permission:

- Authorized user succeeds
- Unauthorized user is rejected

Test both:

- API directly
- UI behavior where applicable

## User Management Tests

- Create
- Edit
- Activate
- Deactivate
- Role assignment
- Role removal
- Department assignment
- Email change
- Duplicate employee number
- Duplicate email

## Role Tests

- Create role
- Assign permission
- Remove permission
- Deactivate role
- Effective permission recalculation

## Audit Tests

Verify that security-sensitive operations generate audit events and that audit records do not contain passwords/tokens.

## Separation of Duties

Explicitly test:


performer == reviewer -> rejected
performer != reviewer -> allowed if permission and workflow conditions pass

