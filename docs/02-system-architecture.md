# System Architecture

## 1. Architecture Style

modular monolithic architecture.

## 2. Components

### Frontend

React + Vite + TypeScript

Responsibilities:

* User interface
* Routing
* Forms
* Tables
* Dashboard
* API communication
* Client-side validation
* Permission-based UI visibility

The frontend must not be considered a security boundary.

### Backend

Django + Django REST Framework

Responsibilities:

* Authentication
* Authorization
* Business rules
* Workflow enforcement
* Database access
* Audit trail
* API
* Validation
* Transaction management

### Database

PostgreSQL

Responsibilities:

* Persistent data
* Relationships
* Constraints
* Transactions
* JSON audit data where required

## 3. Backend Modules

Recommended Django applications:

* users managment 
* audit trail


## 4. API

REST API.

All application APIs must use:

/api/v1/

## 5. Architectural Rules

1. Business rules belong in the backend.
2. React must not trusted for authorization.
3. Workflow transitions must be validated by the backend.
4. All business actions must generate audit events.
5. Locked records must be immutable.
6. Database migrations must be committed to Git.
7. Architecture changes require an ADR.

## 6. Environment

Development:

Docker 


