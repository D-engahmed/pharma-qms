from django.db import models
from django_fsm import FSMField, transition
from apps.common.models import BaseModel
from django.utils import timezone
from datetime import timedelta


class Material(BaseModel):
    """Material model with state machine for workflow management"""
    
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
    
    # Basic information
    receipt_id = models.CharField(max_length=20, unique=True, db_index=True)
    material_name = models.CharField(max_length=100, db_index=True)
    category = models.CharField(max_length=50, blank=True)
    
    # Supplier information
    supplier = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100, blank=True)
    country_origin = models.CharField(max_length=50, blank=True)
    
    # Batch information
    supplier_batch = models.CharField(max_length=50)
    mfg_date = models.DateField(null=True, blank=True)
    exp_date = models.DateField()
    
    # Quantity information
    batch_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=20, blank=True)
    package_type = models.CharField(max_length=50, blank=True)
    num_packages = models.IntegerField(null=True, blank=True)
    package_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_qty = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Location information
    warehouse = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=50, blank=True)
    
    # Receipt information
    po_no = models.CharField(max_length=50, blank=True)
    inv_no = models.CharField(max_length=50, blank=True)
    receipt_date = models.DateField()
    received_by = models.CharField(max_length=100)
    
    # State machine field
    status = FSMField(
        default=Status.QUARANTINE,
        choices=Status.choices,
        protected=True
    )
    
    # QC information (populated on release)
    qc_number = models.CharField(max_length=20, blank=True)
    qc_sign = models.CharField(max_length=100, blank=True)
    retest_date = models.DateField(null=True, blank=True)
    released_date = models.DateField(null=True, blank=True)
    storage_condition = models.CharField(max_length=50, blank=True)
    
    # Rejection information
    rejection_reason = models.TextField(blank=True, default='')
    rejected_by = models.ForeignKey(
        'users.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rejected_materials'
    )
    rejected_at = models.DateTimeField(null=True, blank=True)
    
    # Audit fields
    created_by = models.ForeignKey(
        'users.Employee',
        on_delete=models.SET_NULL,
        null=True,
        related_name='materials_created'
    )
    updated_by = models.ForeignKey(
        'users.Employee',
        on_delete=models.SET_NULL,
        null=True,
        related_name='materials_updated'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.receipt_id} - {self.material_name}"
    
    # State transitions
    @transition(
        field=status,
        source=Status.RECEIVED,
        target=Status.QUARANTINE
    )
    def quarantine(self, by_user):
        """Transition from received to quarantine"""
        self.updated_by = by_user
    
    @transition(
        field=status,
        source=Status.QUARANTINE,
        target=Status.SAMPLING_REQUESTED
    )
    def request_sampling(self, by_user):
        """Request sampling for material"""
        self.updated_by = by_user
    
    @transition(
        field=status,
        source=Status.SAMPLING_REQUESTED,
        target=Status.SAMPLED
    )
    def mark_sampled(self, by_user):
        """Mark material as sampled"""
        self.updated_by = by_user
    
    @transition(
        field=status,
        source=Status.SAMPLED,
        target=Status.UNDER_ANALYSIS
    )
    def start_analysis(self, by_user):
        """Start analysis of material"""
        self.updated_by = by_user
    
    @transition(
        field=status,
        source=Status.UNDER_ANALYSIS,
        target=Status.UNDER_REVIEW
    )
    def submit_for_review(self, by_user):
        """Submit material for review"""
        self.updated_by = by_user
    
    @transition(
        field=status,
        source=Status.UNDER_REVIEW,
        target=Status.APPROVED
    )
    def approve(self, by_user):
        """Approve material after review"""
        self.updated_by = by_user
    
    @transition(
        field=status,
        source=Status.UNDER_REVIEW,
        target=Status.REJECTED
    )
    def reject(self, by_user, reason):
        """Reject material"""
        self.updated_by = by_user
        self.rejection_reason = reason
        self.rejected_by = by_user
        self.rejected_at = timezone.now()
    
    @transition(
        field=status,
        source=Status.APPROVED,
        target=Status.CERTIFICATE_DRAFT
    )
    def create_certificate(self, by_user):
        """Create certificate draft"""
        self.updated_by = by_user
    
    @transition(
        field=status,
        source=Status.CERTIFICATE_DRAFT,
        target=Status.CERTIFICATE_UNDER_REVIEW
    )
    def submit_certificate(self, by_user):
        """Submit certificate for review"""
        self.updated_by = by_user
    
    @transition(
        field=status,
        source=Status.CERTIFICATE_UNDER_REVIEW,
        target=Status.CERTIFICATE_APPROVED
    )
    def approve_certificate(self, by_user):
        """Approve certificate"""
        self.updated_by = by_user
    
    @transition(
        field=status,
        source=Status.CERTIFICATE_UNDER_REVIEW,
        target=Status.REJECTED
    )
    def reject_certificate(self, by_user, reason):
        """Reject certificate"""
        self.updated_by = by_user
        self.rejection_reason = reason
        self.rejected_by = by_user
        self.rejected_at = timezone.now()
    
    @transition(
        field=status,
        source=Status.CERTIFICATE_APPROVED,
        target=Status.CERTIFICATE_LOCKED
    )
    def lock_certificate(self, by_user):
        """Lock certificate"""
        self.updated_by = by_user
    
    @transition(
        field=status,
        source=Status.CERTIFICATE_LOCKED,
        target=Status.RELEASED
    )
    def release(self, by_user, qc_number, qc_sign):
        """Release material"""
        self.updated_by = by_user
        self.qc_number = qc_number
        self.qc_sign = qc_sign
        self.released_date = timezone.now().date()
        self.retest_date = self.released_date + timedelta(days=365)
    
    @property
    def is_locked(self):
        """Check if material is in a locked state"""
        return self.status in [
            self.Status.CERTIFICATE_LOCKED,
            self.Status.RELEASED,
            self.Status.REJECTED
        ]
    
    @property
    def can_be_modified(self):
        """Check if material can be modified"""
        return not self.is_locked and self.status != self.Status.UNDER_REVIEW