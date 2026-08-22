from django.db import models
from apps.common.models import BaseModel

class COA(BaseModel):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'), 
        ('IN_REVIEW', 'In Review'), 
        ('APPROVED', 'Approved'), 
        ('REJECTED', 'Rejected'), 
        ('LOCKED', 'Locked')
    ]
    
    # Removed primary_key=True, kept unique=True
    coa_id = models.CharField(max_length=20, unique=True) 
    material = models.ForeignKey('materials.Material', on_delete=models.PROTECT, related_name='coas')
    analysis = models.ForeignKey('analysis.Analysis', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    approved_by = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_coas')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, default='')