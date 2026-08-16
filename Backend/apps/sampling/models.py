from django.db import models
from apps.common.models import BaseModel

class Sample(BaseModel):
    SAMPLE_TYPE_CHOICES = (
        ('RM', 'Raw Material'),
        ('Packaging', 'Packaging'),
    )
    TESTING_STATUS_CHOICES = (
        ('Not Tested', 'Not Tested'),
        ('In Testing', 'In Testing'),
        ('Completed', 'Completed'),
    )

    sample_id = models.CharField(max_length=20)
    material = models.ForeignKey('materials.Material', on_delete=models.SET_NULL, null=True, blank=True)
    packaging = models.ForeignKey('packaging.Packaging', on_delete=models.SET_NULL, null=True, blank=True)
    sample_type = models.CharField(max_length=20, choices=SAMPLE_TYPE_CHOICES)

    # Denormalized fields for quick display
    material_name = models.CharField(max_length=100)
    receipt_id = models.CharField(max_length=20)
    supplier_batch = models.CharField(max_length=50)
    supplier = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100, blank=True)
    receipt_date = models.DateField()
    batch_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mfg_date = models.DateField(null=True, blank=True)
    exp_date = models.DateField()
    unit = models.CharField(max_length=20, blank=True)

    # Sampling fields
    sample_size = models.DecimalField(max_digits=10, decimal_places=2)
    containers = models.IntegerField()
    sampler = models.CharField(max_length=100)
    storage = models.CharField(max_length=50)
    sampling_date = models.DateField()
    testing_status = models.CharField(max_length=20, choices=TESTING_STATUS_CHOICES, default='Not Tested')

    created_by = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, related_name='samples_created')
    updated_by = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, related_name='samples_updated')

    def __str__(self):
        return f"{self.sample_id} - {self.material_name}"