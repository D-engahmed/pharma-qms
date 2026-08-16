# User / Employee Specification

## User Form

The System Administrator creates a user with:

- Employee Number
- First Name
- Last Name
- Email
- Phone
- Department
- Job Title
- Employment Status (Checkbox)
- Role Profile(s)

## Employee Number

Employee Number is globally unique.

## Email

Email is the login identifier and must be unique.

Changing an email changes the authentication identifier. Such changes must be audited.

## Status

### ACTIVE

The employee may authenticate if all other authentication conditions are satisfied.

### INACTIVE

The employee cannot authenticate.

## User Search

System Administrators should be able to search/filter by:

- Employee Number
- Name
- Email
- Department
- Job Title
- Status
- Role

## Profile View

The user profile should show:

- Identity information
- Department
- Job title
- Status
- Assigned roles
- Effective permissions
- Last successful login
- Account lock state
- Password-change-required state

The password itself must never be displayed.
