# apps/products/models.py
from django.db import models
from apps.common.models import BaseModel

class ProductSample(BaseModel):
    PRODUCT_TYPE_CHOICES = (
        ('Finished Product', 'Finished Product'),
        ('Semi-Finished Product', 'Semi-Finished Product'),
        ('Bulk', 'Bulk'),
    )
    TESTING_STATUS_CHOICES = (
        ('Not Tested', 'Not Tested'),
        ('In Testing', 'In Testing'),
        ('Completed', 'Completed'),
    )

    sample_id = models.CharField(max_length=20, unique=True)
    product_name = models.CharField(max_length=100)
    product_type = models.CharField(max_length=50, choices=PRODUCT_TYPE_CHOICES)  # increased from 20 to 50
    batch_no = models.CharField(max_length=50)
    batch_size = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, blank=True)
    mfg_date = models.DateField(null=True, blank=True)
    exp_date = models.DateField(null=True, blank=True)
    sample_size = models.DecimalField(max_digits=10, decimal_places=2)
    time_of_sampling = models.TimeField()
    sampling_date = models.DateField()
    stages = models.JSONField(default=list)
    testing_status = models.CharField(max_length=20, choices=TESTING_STATUS_CHOICES, default='Not Tested')

    created_by = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, related_name='productsamples_created')
    updated_by = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, related_name='productsamples_updated')

    def __str__(self):
        return f"{self.sample_id} - {self.product_name}"