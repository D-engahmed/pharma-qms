from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Employee, Department, Role, Permission, UserRole


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'
        read_only_fields = ['id']


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoleCreateUpdateSerializer(serializers.ModelSerializer):
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Role
        fields = ['id', 'code', 'name', 'description', 'is_active', 'permission_ids']
    
    def create(self, validated_data):
        perm_ids = validated_data.pop('permission_ids', [])
        role = Role.objects.create(**validated_data)
        if perm_ids:
            role.permissions.set(perm_ids)
        return role
    
    def update(self, instance, validated_data):
        perm_ids = validated_data.pop('permission_ids', None)
        if perm_ids is not None:
            instance.permissions.set(perm_ids)
        return super().update(instance, validated_data)


class EmployeeSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    roles = RoleSerializer(many=True, read_only=True)
    effective_permissions = serializers.SerializerMethodField()
    full_name = serializers.CharField(source='full_name', read_only=True)
    department_id = serializers.IntegerField(write_only=True, required=False)
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_number', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'job_title', 'employment_status', 'department',
            'department_id', 'roles', 'role_ids', 'effective_permissions',
            'is_active', 'is_staff', 'is_superuser', 'last_login',
            'force_password_change', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_login', 'created_at', 'updated_at']
    
    def get_effective_permissions(self, obj):
        return list(obj.get_effective_permissions())
    
    def validate_email(self, value):
        if self.instance:
            qs = Employee.objects.filter(email__iexact=value).exclude(id=self.instance.id)
        else:
            qs = Employee.objects.filter(email__iexact=value)
        if qs.exists():
            raise serializers.ValidationError("Email already exists.")
        return value.lower()
    
    def validate_employee_number(self, value):
        if self.instance:
            qs = Employee.objects.filter(employee_number=value).exclude(id=self.instance.id)
        else:
            qs = Employee.objects.filter(employee_number=value)
        if qs.exists():
            raise serializers.ValidationError("Employee number already exists.")
        return value
    
    def validate_department_id(self, value):
        if not Department.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Department must reference an active department.")
        return value
    
    def validate_role_ids(self, value):
        if value:
            if Role.objects.filter(id__in=value, is_active=True).count() != len(set(value)):
                raise serializers.ValidationError("One or more roles are invalid or inactive.")
        return value
    
    def create(self, validated_data):
        role_ids = validated_data.pop('role_ids', [])
        department_id = validated_data.pop('department_id', None)
        
        user = Employee.objects.create_user(**validated_data)
        
        if department_id:
            user.department_id = department_id
        if role_ids:
            user.roles.set(role_ids)
        user.save()
        
        return user
    
    def update(self, instance, validated_data):
        role_ids = validated_data.pop('role_ids', None)
        department_id = validated_data.pop('department_id', None)
        
        if department_id is not None:
            instance.department_id = department_id
        if role_ids is not None:
            instance.roles.set(role_ids)
        
        return super().update(instance, validated_data)


class EmployeeCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    department_id = serializers.IntegerField(required=True)
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True
    )
    
    class Meta:
        model = Employee
        fields = [
            'employee_number', 'first_name', 'last_name', 'email', 'phone',
            'job_title', 'employment_status', 'department_id', 'role_ids',
            'password', 'force_password_change'
        ]
    
    def validate_email(self, value):
        if Employee.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value.lower()
    
    def validate_employee_number(self, value):
        if Employee.objects.filter(employee_number=value).exists():
            raise serializers.ValidationError("Employee number already exists.")
        return value
    
    def validate_department_id(self, value):
        if not Department.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Department must reference an active department.")
        return value
    
    def validate_role_ids(self, value):
        if Role.objects.filter(id__in=value, is_active=True).count() != len(set(value)):
            raise serializers.ValidationError("One or more roles are invalid or inactive.")
        return value
    
    def create(self, validated_data):
        role_ids = validated_data.pop('role_ids')
        password = validated_data.pop('password')
        department_id = validated_data.pop('department_id')
        
        user = Employee.objects.create_user(
            password=password,
            department_id=department_id,
            **validated_data
        )
        user.roles.set(role_ids)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])


class ESignatureSerializer(serializers.Serializer):
    """Serializer for e-signature verification"""
    password = serializers.CharField(style={'input_type': 'password'})
    meaning = serializers.CharField(max_length=20)
    comment = serializers.CharField(required=False, allow_blank=True)