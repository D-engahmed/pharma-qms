# Validation Rules

## Employee Number

- Required
- Globally unique
- Trim whitespace
- Follow company-defined format

## Name

- First name required
- Last name required
- Trim leading/trailing whitespace

## Email

- Required
- Valid email syntax
- Normalize consistently
- Unique
- Used as login identifier

## Phone

Optional in Version 1.

## Department

- Required
- Must reference an active department for normal user creation
- Department changes audited

## Job Title

Required.

## Status

Only:

- ACTIVE
- INACTIVE

## Roles

- At least one active role required for an active user
- Inactive roles cannot be assigned
- Role changes audited

## Password

- Minimum 8 characters
- At least one numeric character
- Never returned by API
- Never logged

## Department Hierarchy

Reject:

- Self-parent
- Circular parent chain

## Deactivation

Before deactivation, the system should warn if the user is the only active holder of a critical role or permission. Business policy may determine whether this is a warning or a hard block.
