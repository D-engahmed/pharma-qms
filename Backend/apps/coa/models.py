from django.db import models
from apps.common.models import BaseModel

class COA(models.Model):
    id = models.CharField(max_length=20, primary_key=True)  # COA-YYYY-####
    sample = models.ForeignKey('sampling.Sample', on_delete=models.SET_NULL, null=True, blank=True)
    product_sample = models.ForeignKey('products.ProductSample', on_delete=models.SET_NULL, null=True, blank=True)
    sample_src = models.CharField(max_length=10, choices=[('rm','Raw Material'), ('fp','Product'), ('pkg','Packaging')])
    material = models.ForeignKey('materials.Material', on_delete=models.SET_NULL, null=True, blank=True)
    receipt_id = models.CharField(max_length=20)
    sample_name = models.CharField(max_length=200)
    batch_no = models.CharField(max_length=50)
    batch_size = models.CharField(max_length=50)
    supplier = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100, blank=True)
    mfg_date = models.CharField(max_length=50, blank=True)
    exp_date = models.CharField(max_length=50, blank=True)
    received_date = models.CharField(max_length=50, blank=True)
    specs_code = models.CharField(max_length=50)
    reference = models.CharField(max_length=20, choices=[('BP 2025','BP 2025'), ('USP','USP'), ('EP','EP'), ('JP','JP'), ('In-House','In-House')])
    analyst = models.CharField(max_length=100)
    analysis_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[('Draft','Draft'),('In Progress','In Progress'),('Completed','Completed'),('Approved','Approved'),('Rejected','Rejected')], default='Draft')
    created_date = models.DateField(auto_now_add=True)
    qc_comment = models.TextField(blank=True)
    created_by = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, related_name='coas_created')
    updated_by = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, related_name='coas_updated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} - {self.sample_name}"