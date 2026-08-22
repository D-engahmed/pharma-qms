from django.db import models
import uuid

class ElectronicSignature(models.Model):
    MEANING_CHOICES = [('approved', 'Approved'), ('rejected', 'Rejected'), ('reviewed', 'Reviewed'), ('completed', 'Completed'), ('released', 'Released')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    signer = models.ForeignKey('users.Employee', on_delete=models.PROTECT, related_name='esignatures')
    signer_printed_name = models.CharField(max_length=100)
    meaning = models.CharField(max_length=20, choices=MEANING_CHOICES)
    record_type = models.CharField(max_length=50)
    record_id = models.CharField(max_length=50)
    comment = models.TextField(blank=True, default='')
    
    def save(self, *args, **kwargs):
        if self.pk and ElectronicSignature.objects.filter(pk=self.pk).exists():
            raise ValueError("E-signature records cannot be modified")
        super().save(*args, **kwargs)