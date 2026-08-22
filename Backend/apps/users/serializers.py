from rest_framework import serializers
from .models import Employee, Department, Role, Permission

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    class Meta:
        model = Role
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    roles = RoleSerializer(many=True, read_only=True)
    effective_permissions = serializers.SerializerMethodField()
    full_name = serializers.CharField(source='full_name', read_only=True)
    
    class Meta:
        model = Employee
        fields = ['id', 'employee_number', 'first_name', 'last_name', 'full_name', 'email', 'phone', 'job_title', 'employment_status', 'department', 'roles', 'effective_permissions', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'force_password_change', 'created_at', 'updated_at']
        read_only_fields = ['id', 'last_login', 'created_at', 'updated_at']
    
    def get_effective_permissions(self, obj):
        return list(obj.get_effective_permissions())

class EmployeeCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    department_id = serializers.IntegerField(required=False)
    role_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    
    class Meta:
        model = Employee
        fields = ['employee_number', 'first_name', 'last_name', 'email', 'phone', 'job_title', 'employment_status', 'department_id', 'role_ids', 'password', 'force_password_change']
    
    def create(self, validated_data):
        role_ids = validated_data.pop('role_ids', [])
        password = validated_data.pop('password')
        dept_id = validated_data.pop('department_id', None)
        
        user = Employee.objects.create_user(password=password, **validated_data)
        if dept_id:
            user.department_id = dept_id
        if role_ids:
            user.roles.set(role_ids)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})