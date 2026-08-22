from django.db import models
from django_fsm import FSMField, transition
from apps.common.models import BaseModel
from django.utils import timezone
from datetime import timedelta

class Material(BaseModel):
    class Status(models.TextChoices):
        RECEIVED = 'RECEIVED', 'Received'
        QUARANTINE = 'QUARANTINE', 'Quarantine'
        SAMPLING_REQUESTED = 'SAMPLING_REQUESTED', 'Sampling Requested'
        SAMPLED = 'SAMPLED', 'Sampled'
        UNDER_ANALYSIS = 'UNDER_ANALYSIS', 'Under Analysis'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        CERTIFICATE_DRAFT = 'CERTIFICATE_DRAFT', 'Certificate Draft'
        CERTIFICATE_UNDER_REVIEW = 'CERTIFICATE_UNDER_REVIEW', 'Certificate Under Review'
        CERTIFICATE_APPROVED = 'CERTIFICATE_APPROVED', 'Certificate Approved'
        CERTIFICATE_LOCKED = 'CERTIFICATE_LOCKED', 'Certificate Locked'
        RELEASED = 'RELEASED', 'Released'
    
    receipt_id = models.CharField(max_length=20, unique=True, db_index=True)
    material_name = models.CharField(max_length=100, db_index=True)
    supplier = models.CharField(max_length=100)
    supplier_batch = models.CharField(max_length=50)
    exp_date = models.DateField()
    receipt_date = models.DateField()
    received_by = models.CharField(max_length=100)
    status = FSMField(default=Status.QUARANTINE, choices=Status.choices, protected=True)
    qc_number = models.CharField(max_length=20, blank=True)
    qc_sign = models.CharField(max_length=100, blank=True)
    retest_date = models.DateField(null=True, blank=True)
    released_date = models.DateField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, default='')
    rejected_by = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='rejected_materials')
    rejected_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, related_name='materials_created')
    updated_by = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, related_name='materials_updated')
    
    @transition(field=status, source=Status.QUARANTINE, target=Status.SAMPLING_REQUESTED)
    def request_sampling(self, by_user):
        self.updated_by = by_user
    
    @transition(field=status, source=Status.SAMPLING_REQUESTED, target=Status.SAMPLED)
    def mark_sampled(self, by_user):
        self.updated_by = by_user
    
    @transition(field=status, source=Status.SAMPLED, target=Status.UNDER_ANALYSIS)
    def start_analysis(self, by_user):
        self.updated_by = by_user
    
    @transition(field=status, source=Status.UNDER_ANALYSIS, target=Status.UNDER_REVIEW)
    def submit_for_review(self, by_user):
        self.updated_by = by_user
    
    @transition(field=status, source=Status.UNDER_REVIEW, target=Status.APPROVED)
    def approve(self, by_user):
        self.updated_by = by_user
    
    @transition(field=status, source=Status.UNDER_REVIEW, target=Status.REJECTED)
    def reject(self, by_user, reason):
        self.updated_by = by_user
        self.rejection_reason = reason
        self.rejected_by = by_user
        self.rejected_at = timezone.now()
    
    @transition(field=status, source=Status.CERTIFICATE_APPROVED, target=Status.CERTIFICATE_LOCKED)
    def lock_certificate(self, by_user):
        self.updated_by = by_user
    
    @transition(field=status, source=Status.CERTIFICATE_LOCKED, target=Status.RELEASED)
    def release(self, by_user, qc_number, qc_sign):
        self.updated_by = by_user
        self.qc_number = qc_number
        self.qc_sign = qc_sign
        self.released_date = timezone.now().date()
        self.retest_date = self.released_date + timedelta(days=365)