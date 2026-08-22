from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
from django.utils import timezone


class EmployeeManager(BaseUserManager):
    """Custom manager for Employee model"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('employment_status', 'ACTIVE')
        return self.create_user(email, password, **extra_fields)
    
    def get_by_natural_key(self, email):
        return self.get(email__iexact=self.normalize_email(email).lower())


class Department(models.Model):
    """Department model for organizational structure"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class Permission(models.Model):
    """Permission model for granular access control"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    module = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.code


class Role(models.Model):
    """Role model for grouping permissions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    permissions = models.ManyToManyField(
        'Permission',
        through='RolePermission',
        related_name='roles'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class RolePermission(models.Model):
    """Through model for Role-Permission relationship"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('role', 'permission')


class UserRole(models.Model):
    """Through model for Employee-Role relationship"""
    user = models.ForeignKey('Employee', on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_roles'
    )
    
    class Meta:
        unique_together = ('user', 'role')


class Employee(AbstractBaseUser, PermissionsMixin):
    """Custom user model representing an employee in the pharmaceutical facility"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    job_title = models.CharField(max_length=100)
    employment_status = models.CharField(
        max_length=20,
        choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')],
        default='ACTIVE'
    )
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    roles = models.ManyToManyField(
        Role,
        through=UserRole,
        through_fields=('user', 'role'),
        related_name='users'
    )
    
    # Security fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    failed_login_count = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    force_password_change = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Audit fields
    created_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = EmployeeManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['employee_number', 'first_name', 'last_name', 'job_title']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_effective_permissions(self):
        """Return set of permission codes from all active roles"""
        perms = set()
        for role in self.roles.filter(is_active=True):
            perms.update(
                role.permissions.filter(is_active=True).values_list('code', flat=True)
            )
        return perms
    
    def has_perm(self, perm_code):
        """Check if user has specific permission"""
        if self.is_superuser:
            return True
        return perm_code in self.get_effective_permissions()
    
    def has_role(self, role_code):
        """Check if user has specific role"""
        return self.roles.filter(code=role_code, is_active=True).exists()
    
    def is_last_active_sysadmin(self):
        """Check if this is the last active system administrator"""
        if not self.roles.filter(code='sysadmin').exists():
            return False
        others = Employee.objects.filter(
            roles__code='sysadmin',
            is_active=True
        ).exclude(id=self.id).distinct()
        return not others.exists()
    
    def is_locked(self):
        """Check if account is currently locked"""
        return self.locked_until is not None and self.locked_until > timezone.now()
    
    def increment_failed_login(self):
        """Increment failed login count and lock if threshold exceeded"""
        self.failed_login_count += 1
        if self.failed_login_count >= 5:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=30)
        self.save(update_fields=['failed_login_count', 'locked_until'])
    
    def reset_failed_login(self):
        """Reset failed login count after successful login"""
        self.failed_login_count = 0
        self.locked_until = None
        self.save(update_fields=['failed_login_count', 'locked_until'])