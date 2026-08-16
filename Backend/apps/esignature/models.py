from django.db import models
import uuid

class ElectronicSignature(models.Model):
    MEANING_CHOICES = (
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('reviewed', 'Reviewed'),
        ('completed', 'Completed'),
        ('released', 'Released'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    signer = models.ForeignKey('users.Employee', on_delete=models.CASCADE)
    signer_printed_name = models.CharField(max_length=100)
    meaning = models.CharField(max_length=20, choices=MEANING_CHOICES)
    record_type = models.CharField(max_length=50)
    record_id = models.CharField(max_length=50)
    comment = models.TextField(blank=True)
    record_hash = models.CharField(max_length=64, blank=True)
    signature_hash = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return f"{self.timestamp} {self.signer.username} {self.meaning} {self.record_id}"