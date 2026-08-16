# Development Tasks

## Backend Developer

### Phase 1 — Foundation

- [ ] Create Django project structure
- [ ] Configure PostgreSQL
- [ ] Docker Compose
- [ ] Environment configuration
- [ ] Base API `/api/v1/`
- [ ] Authentication/session strategy
- [ ] Base audit service

### Phase 2 — User Domain

- [ ] User model
- [ ] Department model
- [ ] Role model
- [ ] Permission model
- [ ] UserRole
- [ ] RolePermission
- [ ] Database constraints
- [ ] Migrations
- [ ] Seed initial permissions
- [ ] Seed initial roles

### Phase 3 — Authentication

- [ ] Login
- [ ] Logout
- [ ] Password change
- [ ] Admin reset
- [ ] Forced password change
- [ ] Failed-login rate limiting
- [ ] Temporary lockout
- [ ] Concurrent session prevention
- [ ] Idle timeout

### Phase 4 — APIs

- [ ] User APIs
- [ ] Department APIs
- [ ] Role APIs
- [ ] Permission APIs
- [ ] Effective permissions endpoint
- [ ] Session endpoint

### Phase 5 — Security

- [ ] Backend permission enforcement
- [ ] Separation-of-duties service
- [ ] Audit events
- [ ] Administrator protection

### Phase 6 — Tests

- [ ] Unit tests
- [ ] API tests
- [ ] Authentication tests
- [ ] Authorization tests
- [ ] Audit tests

## Frontend Developer

### Phase 1

- [ ] React/Vite/TypeScript foundation
- [ ] Routing
- [ ] Authentication state
- [ ] API client
- [ ] Protected routes
- [ ] Permission-aware navigation

### Phase 2

- [ ] Login
- [ ] Forced password-change screen
- [ ] User list
- [ ] User create/edit
- [ ] User details
- [ ] Role assignment
- [ ] Security actions

### Phase 3

- [ ] Department tree/list
- [ ] Department create/edit
- [ ] Role list
- [ ] Role create/edit
- [ ] Permission matrix
- [ ] Effective permissions display

### Phase 4

- [ ] Loading/error/empty states
- [ ] Confirmation dialogs
- [ ] Validation
- [ ] Responsive layout
- [ ] Audit history view where permitted

## Joint

- [ ] API contract agreed
- [ ] Integration testing
- [ ] Docker integration
- [ ] Permission matrix verification
- [ ] UAT scenarios
- [ ] Documentation update
