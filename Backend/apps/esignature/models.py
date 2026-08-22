from django.db import models
import uuid
from django.utils import timezone


class ElectronicSignature(models.Model):
    """Immutable record of an electronic signature"""
    
    MEANING_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('reviewed', 'Reviewed'),
        ('completed', 'Completed'),
        ('released', 'Released'),
        ('verified', 'Verified'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    
    # Signer information
    signer = models.ForeignKey(
        'users.Employee',
        on_delete=models.PROTECT,
        related_name='esignatures'
    )
    signer_printed_name = models.CharField(max_length=100)  # Snapshot
    signer_email = models.EmailField()  # Snapshot
    
    # Signature details
    meaning = models.CharField(max_length=20, choices=MEANING_CHOICES)
    record_type = models.CharField(max_length=50)
    record_id = models.CharField(max_length=50)
    comment = models.TextField(blank=True, default='')
    
    # Integrity checks
    record_hash = models.CharField(max_length=64, blank=True, default='')
    signature_hash = models.CharField(max_length=64, blank=True, default='')
    
    # Verification status
    is_verified = models.BooleanField(default=True)
    verification_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Electronic Signature'
        verbose_name_plural = 'Electronic Signatures'
    
    def __str__(self):
        return f"{self.timestamp} {self.signer_printed_name} {self.meaning} {self.record_id}"
    
    def save(self, *args, **kwargs):
        """Override save to prevent updates to existing records"""
        if self.pk and ElectronicSignature.objects.filter(pk=self.pk).exists():
            raise ValueError("Electronic signature records cannot be modified")
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Override delete to prevent deletion"""
        raise ValueError("Electronic signature records cannot be deleted")