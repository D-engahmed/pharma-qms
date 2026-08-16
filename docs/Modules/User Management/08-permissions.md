# Permission Model

## Principle

Permissions are not generic CRUD Only.

Preferred:

receiving.request_sampling
analysis.enter_result
analysis.submit_for_review
certificate.approve
material.release


Avoid relying only on:

receiving.update
analysis.update


## Naming Convention

`module.action`

Examples:

### Users

- users.view
- users.create
- users.edit
- users.activate
- users.deactivate
- users.reset_password
- users.unlock

### Departments

- departments.view
- departments.create
- departments.edit
- departments.activate
- departments.deactivate

### Roles

- roles.view
- roles.create
- roles.edit
- roles.activate
- roles.deactivate
- roles.assign_permissions

### Receiving

- receiving.view
- receiving.create
- receiving.edit
- receiving.request_sampling

### Sampling

- sampling.view
- sampling.create
- sampling.assign
- sampling.complete
- sampling.print

### Analysis

- analysis.view
- analysis.create
- analysis.enter_result
- analysis.submit_for_review
- analysis.review
- analysis.approve

### Certificates

- certificate.view
- certificate.create
- certificate.submit_for_review
- certificate.review
- certificate.approve
- certificate.lock

### Material

- material.view
- material.move
- material.release

### Audit

- audit.view

## Authorization Rule

The backend must verify permissions for every protected action.

The frontend  use permissions to:

- hide menu items
- disable buttons
- control routes
- improve UX

frontend checks never replace backend authorization.

## Effective Permissions


EffectivePermissions(User)
=
Union(Permissions(Role1), Permissions(Role2), ...)


A permission belonging to one active role is sufficient unless a future policy explicitly introduces deny rules. Version 1 should not implement deny permissions.
