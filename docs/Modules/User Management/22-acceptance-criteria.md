# Acceptance Criteria

The User Management module is accepted when all of the following are true.

## User

- [ ] System Administrator can create users.
- [ ] Employee Number is unique.
- [ ] Email is unique.
- [ ] Email is used for login.
- [ ] User has one primary department.
- [ ] User can have multiple roles.
- [ ] User can be activated/deactivated.
- [ ] Historical records remain linked to inactive users.

## Departments

- [ ] Departments support hierarchy.
- [ ] Circular hierarchy is prevented.
- [ ] Users have one primary department.
- [ ] Department changes are audited.

## Roles

- [ ] Initial roles exist.
- [ ] System Administrator can create custom roles.
- [ ] Roles can be activated/deactivated.
- [ ] Users can have multiple roles.
- [ ] Role changes are audited.

## Permissions

- [ ] Permissions are database-driven.
- [ ] Permissions use business-action naming.
- [ ] Backend checks permissions.
- [ ] Effective permissions are calculated from active roles.
- [ ] Frontend does not act as the security boundary.

## Authentication

- [ ] Email/password login works.
- [ ] Password minimum policy is enforced.
- [ ] Failed login protection works.
- [ ] Inactive accounts cannot login.
- [ ] Concurrent login is rejected.
- [ ] Idle timeout works.
- [ ] Password reset works.
- [ ] Forced password change works.

## Audit

- [ ] All specified security events are audited.
- [ ] Audit records are immutable through normal UI/API.
- [ ] Passwords and secrets never appear in audit data.

## Security

- [ ] Self-approval is blocked where required.
- [ ] Last critical administrator cannot be accidentally removed.
- [ ] No normal user deletion is available.
- [ ] Automated tests cover security-critical behavior.
