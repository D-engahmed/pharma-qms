from rest_framework import serializers
from .models import COA

class COASerializer(serializers.ModelSerializer):
    class Meta:
        model = COA
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'coa_id', 'approved_by', 'approved_at']