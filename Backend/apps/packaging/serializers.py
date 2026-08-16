from rest_framework import serializers
from .models import Packaging

class PackagingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Packaging
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'receipt_id']