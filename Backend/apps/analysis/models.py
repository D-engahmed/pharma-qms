from django.db import models
from apps.common.models import BaseModel

class Analysis(BaseModel):
    material = models.ForeignKey('materials.Material', on_delete=models.CASCADE, related_name='analyses')
    sample = models.ForeignKey('sampling.Sample', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING')
    assigned_to = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, related_name='assigned_analyses')
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')