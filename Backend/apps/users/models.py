from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid


# ---------- Manager ----------
class EmployeeManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        # 04-database-design.md: "Normalize email consistently before uniqueness
        # checks and authentication." normalize_email() alone only lowercases
        # the domain half — we lowercase the whole address so login identity
        # is consistent end to end.
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        # Makes authenticate() case-insensitive on login, matching the
        # normalization applied at create_user time. Without this,
        # "Ahmed@x.com" and "ahmed@x.com" behave as different identities
        # even though only one could ever be created.
        return self.get(email__iexact=self.normalize_email(email).lower())


# ---------- Department ----------
class Department(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# ---------- Permission ----------
class Permission(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    module = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


# ---------- Role ----------
class Role(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    permissions = models.ManyToManyField('Permission', through='RolePermission', related_name='roles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# ---------- RolePermission (junction) ----------
class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('role', 'permission')


# ---------- UserRole (junction) ----------
class UserRole(models.Model):
    user = models.ForeignKey('Employee', on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, related_name='assigned_roles')

    class Meta:
        unique_together = ('user', 'role')


# ---------- Employee (User) ----------
class Employee(AbstractBaseUser, PermissionsMixin):
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
    # 04-database-design.md: department_id NOT NULL — was nullable, confirmed
    # this should match the spec. Requires backfilling any existing NULL
    # rows before this migration will apply.
    department = models.ForeignKey(Department, on_delete=models.PROTECT)

    roles = models.ManyToManyField(Role, through=UserRole, related_name='users')

    # Legacy fields — kept for compatibility. apps/audit's AuditLogSerializer
    # still reads `user.full_name` directly (never populated by anything, so
    # that read is already effectively broken independent of this change).
    # Not touching that cross-app dependency here — flagging it, not fixing
    # it blind.
    full_name = models.CharField(max_length=100, blank=True)  # deprecated; use first_name + last_name
    role = models.CharField(max_length=20, blank=True)        # deprecated; kept temporarily

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    failed_login_count = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    force_password_change = models.BooleanField(default=False)  # renamed from must_change_password
    last_login = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = EmployeeManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['employee_number', 'first_name', 'last_name', 'job_title']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name_prop(self):
        return f"{self.first_name} {self.last_name}"

    def get_effective_permissions(self):
        """Return set of permission codes from all active roles."""
        perms = set()
        for role in self.roles.filter(is_active=True):
            perms.update(role.permissions.filter(is_active=True).values_list('code', flat=True))
        return perms

    def has_perm(self, perm_code):
        if self.is_superuser:
            return True
        return perm_code in self.get_effective_permissions()

    def is_last_active_sysadmin(self):
        """
        15-security-rules.md / 07-roles.md: the backend must not allow the
        last active System Administrator to be demoted, deactivated, or
        stripped of the role in a way that locks the system out.
        """
        if not self.roles.filter(code='sysadmin').exists():
            return False
        others = Employee.objects.filter(
            roles__code='sysadmin', is_active=True
        ).exclude(id=self.id).distinct()
        return not others.exists()
