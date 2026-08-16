from django.db import models
from apps.common.models import BaseModel

class Material(BaseModel):
    class Status(models.TextChoices):
        QUARANTINE = 'Quarantine', 'Quarantine'
        RELEASED = 'Released', 'Released'
        REJECTED = 'Rejected', 'Rejected'

    class SamplingStatus(models.TextChoices):
        NOT_SAMPLED = 'Not Sampled', 'Not Sampled'
        SAMPLING_REQUESTED = 'Sampling Requested', 'Sampling Requested'
        SAMPLED = 'Sampled', 'Sampled'

    receipt_id = models.CharField(max_length=20, unique=True, db_index=True)
    material_name = models.CharField(max_length=100, db_index=True)
    category = models.CharField(max_length=50, blank=True)
    supplier = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100, blank=True)
    country_origin = models.CharField(max_length=50, blank=True)
    supplier_batch = models.CharField(max_length=50)
    mfg_date = models.DateField(null=True, blank=True)
    exp_date = models.DateField()
    batch_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=20, blank=True)
    package_type = models.CharField(max_length=50, blank=True)
    num_packages = models.IntegerField(null=True, blank=True)
    package_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_qty = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    warehouse = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=50, blank=True)
    po_no = models.CharField(max_length=50, blank=True)
    inv_no = models.CharField(max_length=50, blank=True)
    receipt_date = models.DateField()
    received_by = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUARANTINE)
    sampling_status = models.CharField(max_length=20, choices=SamplingStatus.choices, default=SamplingStatus.NOT_SAMPLED)
    qc_number = models.CharField(max_length=20, blank=True)
    qc_sign = models.CharField(max_length=100, blank=True)
    retest_date = models.DateField(null=True, blank=True)
    released_date = models.DateField(null=True, blank=True)
    storage_condition = models.CharField(max_length=50, blank=True)

    created_by = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, related_name='materials_created')
    updated_by = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, related_name='materials_updated')