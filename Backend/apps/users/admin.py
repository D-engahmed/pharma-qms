from django.contrib import admin
from .models import Employee, UserRole, Department, Role, Permission, RolePermission


class UserRoleInline(admin.TabularInline):
    # roles is a ManyToManyField with a custom `through` model (UserRole),
    # so Django admin can't edit it via a plain fieldsets entry
    # (admin.E013). An inline on the through model is the supported way
    # to manage it from the Employee change page.
    model = UserRole
    fk_name = 'user'
    extra = 1
    autocomplete_fields = ('role',)
    readonly_fields = ('assigned_at',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    # Original list_display/search_fields referenced 'full_name'/'role'
    # (unpopulated legacy fields) and search_fields referenced 'username',
    # which doesn't exist anywhere on this model — that would throw a
    # FieldError the moment anyone used the admin search box. Fixed to use
    # real fields.
    list_display = ('email', 'full_name_prop', 'department', 'employment_status', 'is_active', 'last_login')
    list_filter = ('department', 'employment_status', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'employee_number')
    readonly_fields = ('id', 'created_at', 'updated_at', 'last_login')
    inlines = (UserRoleInline,)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('employee_number', 'first_name', 'last_name', 'phone', 'job_title')}),
        ('Assignment', {'fields': ('department',)}),  # roles managed via UserRoleInline below
        ('Status', {'fields': ('employment_status', 'is_active', 'is_staff', 'is_superuser')}),
        ('Security', {'fields': ('failed_login_count', 'locked_until', 'force_password_change')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    # NOTE — not fixed here, flagging only: this ModelAdmin has no custom
    # form. The original file's add_fieldsets referenced 'password1'/
    # 'password2', fields that don't exist on Employee or on the default
    # ModelForm without a UserCreationForm-style subclass. That would error
    # on rendering the add page. Removed rather than ship a form I can't
    # verify works. Create users through the API until someone writes a
    # proper EmployeeCreationForm.


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'parent', 'is_active')
    search_fields = ('code', 'name')
    list_filter = ('is_active',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_active')
    search_fields = ('code', 'name')
    list_filter = ('is_active',)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'module', 'is_active')
    search_fields = ('code', 'name', 'module')
    list_filter = ('module', 'is_active')
