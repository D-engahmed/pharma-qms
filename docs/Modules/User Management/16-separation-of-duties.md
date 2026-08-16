# Separation of Duties

## Purpose

The LIMS must prevent a user from approving or independently reviewing their own controlled work where the workflow requires independent review.

## Examples

### Analysis Result


Analyst A enters result
        ↓
Supervisor B reviews


Analyst A must not approve their own result.

### Certificate


User A prepares certificate
        ↓
User B reviews/approves


User A must not approve their own certificate if independent approval is required.

## Implementation

The backend must record the actor responsible for each controlled action.

Before approval/review:


if reviewer_id == performer_id:
    reject


The exact performer/reviewer relationships must be defined for each business module.

## Role Does Not Override Separation of Duties

Having a role with approval permission does not permit self-approval.

## Audit

Every prevented self-approval should be logged as a security/business event where appropriate.
