1. Do not bypass business workflows.

2. All authorization decisions must be enforced by the backend.

3. Every controlled business action must generate an audit event.

4. Locked records cannot be modified.

5. Database migrations must be committed.

6. Never modify an existing migration that has already
   been applied/shared.

7. Never store secrets in Git.

8. Never directly modify production database data to
   fix an application problem without documenting it.

9. Business rules belong in the backend.

10. React must not implement security decisions.

11. All API endpoints must be versioned.

12. All important business operations require tests.

13. Do not introduce new dependencies without justification.

14. Do not change the architecture without an ADR.

15. Do not implement functionality that is not specified
    in the requirements.

16. Pull requests require review before merging.

17. Never delete audit records through normal application UI.

18. Approved/locked records must preserve their historical state.