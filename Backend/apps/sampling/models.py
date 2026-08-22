from django.db import models
from apps.common.models import BaseModel

class Sample(BaseModel):
    material = models.ForeignKey('materials.Material', on_delete=models.CASCADE, related_name='samples')
    sample_id = models.CharField(max_length=20, unique=True)
    sampler = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, related_name='samples_taken')
    sampling_date = models.DateField()
    testing_status = models.CharField(max_length=20, choices=[('NOT_TESTED', 'Not Tested'), ('IN_TESTING', 'In Testing'), ('COMPLETED', 'Completed')], default='NOT_TESTED')