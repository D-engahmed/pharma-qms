from apps.common.models import BaseModel
from django.db import models

class Packaging(BaseModel):
    receipt_id = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=[('Primary','Primary'),('Secondary','Secondary'),('Tertiary','Tertiary'),('Labeling','Labeling'),('Other','Other')])
    description = models.TextField(blank=True)
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, blank=True)
    supplier = models.CharField(max_length=100)
    po = models.CharField(max_length=50, blank=True)
    receipt_date = models.DateField()
    warehouse = models.CharField(max_length=50, blank=True)
    recipient = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    sampling_status = models.CharField(max_length=20, choices=[('Not Sampled','Not Sampled'),('Sampling Requested','Sampling Requested'),('Sampled','Sampled')], default='Not Sampled')
    created_by = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, related_name='packagings_created')
    updated_by = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, related_name='packagings_updated')