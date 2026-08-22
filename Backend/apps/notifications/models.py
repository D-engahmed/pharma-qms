from django.db import models
from apps.common.models import BaseModel

class Notification(BaseModel):
    target_role = models.CharField(max_length=20)
    title = models.CharField(max_length=100)
    message = models.TextField()
    read = models.BooleanField(default=False)