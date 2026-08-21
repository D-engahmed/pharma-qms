from django.db import models
import uuid

class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('USER_CREATED', 'User Created'),
        ('USER_UPDATED', 'User Updated'),
        ('USER_ACTIVATED', 'User Activated'),
        ('USER_DEACTIVATED', 'User Deactivated'),
        ('USER_EMAIL_CHANGED', 'User Email Changed'),
        ('USER_ROLE_CHANGED', 'User Role Changed'),
        ('USER_PASSWORD_RESET', 'User Password Reset'),
        ('USER_PASSWORD_CHANGED', 'User Password Changed'),
        ('USER_UNLOCKED', 'User Unlocked'),
        ('USER_SESSION_REVOKED', 'User Session Revoked'),
        ('LOGIN_SUCCESS', 'Login Success'),
        ('LOGIN_FAILURE', 'Login Failure'),
        ('LOGIN_REJECTED_INACTIVE', 'Login Rejected Inactive'),
        ('LOGIN_REJECTED_LOCKED', 'Login Rejected Locked'),
        ('LOGIN_REJECTED_CONCURRENT', 'Login Rejected Concurrent Session'),
        ('SESSION_EXPIRED', 'Session Expired'),
        ('SESSION_UPDATED', 'Session Expired'),
        ('LOGOUT', 'Logout'),
        ('ROLE_CREATED', 'Role Created'),
        ('ROLE_UPDATED', 'Role Updated'),
        ('ROLE_ACTIVATED', 'Role Activated'),
        ('ROLE_DEACTIVATED', 'Role Deactivated'),
        ('ROLE_PERMISSIONS_CHANGED', 'Role Permissions Changed'),
        ('DEPARTMENT_CREATED', 'Department Created'),
        ('DEPARTMENT_UPDATED', 'Department Updated'),
        ('DEPARTMENT_ACTIVATED', 'Department Activated'),
        ('DEPARTMENT_DEACTIVATED', 'Department Deactivated'),
        ('RECEIVING_SAMPLING_REQUESTED', 'Sampling Requested'),
        ('MATERIAL_RELEASED', 'Material Released'),
        ('CERTIFICATE_APPROVED', 'Certificate Approved'),
        ('CERTIFICATE_REJECTED', 'Certificate Rejected'),
        ('SAMPLE_CREATED', 'Sample Created'),
        ('SAMPLE_UPDATED', 'Sample Updated'),
        ('SAMPLE_DELETED', 'Sample Deleted'),
        ('PACKAGING_CREATED', 'Packaging Created'),
        ('PACKAGING_UPDATED', 'Packaging Updated'),
        ('PACKAGING_DELETED', 'Packaging Deleted'),
        ('PRODUCTSAMPLE_CREATED', 'Product Sample Created'),
        ('PRODUCTSAMPLE_UPDATED', 'Product Sample Updated'),
        ('PRODUCTSAMPLE_DELETED', 'Product Sample Deleted'),
        ('COA_CREATED', 'COA Created'),
        ('COA_UPDATED', 'COA Updated'),
        ('COA_DELETED', 'COA Deleted'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    # SET_NULL, not CASCADE: an audit trail must survive deletion of the
    # actor it records. `username` is kept as a point-in-time snapshot
    # specifically so the row still reads sensibly once `user` is null.
    user = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, blank=True)
    username = models.CharField(max_length=100)  # snapshot
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    module = models.CharField(max_length=50)
    entity_type = models.CharField(max_length=50, blank=True)
    entity_id = models.CharField(max_length=50, blank=True)
    before_values = models.JSONField(null=True, blank=True)
    after_values = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_id = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.timestamp} {self.action_type} by {self.username}"