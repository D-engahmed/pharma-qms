from django.db import models
import uuid
from django.utils import timezone


class AuditLog(models.Model):
    """Immutable audit log for all controlled actions"""
    
    ACTION_CHOICES = [
        # Authentication events
        ('LOGIN_SUCCESS', 'Login Success'),
        ('LOGIN_FAILURE', 'Login Failure'),
        ('LOGIN_REJECTED_INACTIVE', 'Login Rejected - Inactive'),
        ('LOGIN_REJECTED_LOCKED', 'Login Rejected - Locked'),
        ('LOGIN_REJECTED_CONCURRENT', 'Login Rejected - Concurrent Session'),
        ('LOGOUT', 'Logout'),
        ('SESSION_EXPIRED', 'Session Expired'),
        
        # User management events
        ('USER_CREATED', 'User Created'),
        ('USER_UPDATED', 'User Updated'),
        ('USER_ACTIVATED', 'User Activated'),
        ('USER_DEACTIVATED', 'User Deactivated'),
        ('USER_EMAIL_CHANGED', 'User Email Changed'),
        ('USER_ROLE_CHANGED', 'User Role Changed'),
        ('USER_PASSWORD_CHANGED', 'User Password Changed'),
        ('USER_PASSWORD_RESET', 'User Password Reset'),
        ('USER_UNLOCKED', 'User Unlocked'),
        
        # Department/Role events
        ('DEPARTMENT_CREATED', 'Department Created'),
        ('DEPARTMENT_UPDATED', 'Department Updated'),
        ('DEPARTMENT_ACTIVATED', 'Department Activated'),
        ('DEPARTMENT_DEACTIVATED', 'Department Deactivated'),
        ('ROLE_CREATED', 'Role Created'),
        ('ROLE_UPDATED', 'Role Updated'),
        ('ROLE_ACTIVATED', 'Role Activated'),
        ('ROLE_DEACTIVATED', 'Role Deactivated'),
        ('ROLE_PERMISSIONS_CHANGED', 'Role Permissions Changed'),
        
        # Material workflow events
        ('MATERIAL_CREATED', 'Material Created'),
        ('MATERIAL_UPDATED', 'Material Updated'),
        ('MATERIAL_SAMPLING_REQUESTED', 'Material Sampling Requested'),
        ('MATERIAL_SAMPLED', 'Material Sampled'),
        ('MATERIAL_UNDER_ANALYSIS', 'Material Under Analysis'),
        ('MATERIAL_UNDER_REVIEW', 'Material Under Review'),
        ('MATERIAL_APPROVED', 'Material Approved'),
        ('MATERIAL_REJECTED', 'Material Rejected'),
        ('MATERIAL_RELEASED', 'Material Released'),
        
        # Certificate events
        ('COA_CREATED', 'COA Created'),
        ('COA_UPDATED', 'COA Updated'),
        ('COA_SUBMITTED', 'COA Submitted'),
        ('COA_COMPLETED', 'COA Completed'),
        ('COA_APPROVED', 'COA Approved'),
        ('COA_REJECTED', 'COA Rejected'),
        ('COA_LOCKED', 'COA Locked'),
        ('COA_DOWNLOADED', 'COA Downloaded'),
        
        # E-signature events
        ('ESIGNATURE_VERIFIED', 'E-Signature Verified'),
        ('ESIGNATURE_FAILED', 'E-Signature Failed'),
        
        # Generic CRUD events
        ('RECORD_CREATED', 'Record Created'),
        ('RECORD_UPDATED', 'Record Updated'),
        ('RECORD_DELETED', 'Record Deleted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    
    # Actor information
    user = models.ForeignKey(
        'users.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    username = models.CharField(max_length=100)  # Snapshot for historical reference
    
    # Action information
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    module = models.CharField(max_length=50)
    
    # Entity information
    entity_type = models.CharField(max_length=50, blank=True)
    entity_id = models.CharField(max_length=50, blank=True)
    
    # Change tracking
    before_values = models.JSONField(null=True, blank=True)
    after_values = models.JSONField(null=True, blank=True)
    
    # Request context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_id = models.CharField(max_length=50, blank=True, default='')
    user_agent = models.CharField(max_length=255, blank=True, default='')
    
    # Additional information
    description = models.TextField(blank=True, default='')
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
    
    def __str__(self):
        return f"{self.timestamp} {self.action_type} by {self.username}"
    
    def save(self, *args, **kwargs):
        """Override save to prevent updates to existing records"""
        if self.pk and AuditLog.objects.filter(pk=self.pk).exists():
            raise ValueError("Audit log records cannot be modified")
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Override delete to prevent deletion"""
        raise ValueError("Audit log records cannot be deleted")