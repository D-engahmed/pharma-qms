from rest_framework import serializers
from .models import ProductSample

class ProductSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSample
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']