from django.core.management.base import BaseCommand
from apps.users.models import (
    Employee, Department, Role, Permission, RolePermission, UserRole
)
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Seed initial data for the pharmaceutical QMS'
    
    def handle(self, *args, **options):
        self.stdout.write('Seeding initial data...')
        
        # Create departments
        departments = [
            {'code': 'QC', 'name': 'Quality Control'},
            {'code': 'QA', 'name': 'Quality Assurance'},
            {'code': 'WH', 'name': 'Warehouse'},
            {'code': 'PROD', 'name': 'Production'},
            {'code': 'ADMIN', 'name': 'Administration'},
        ]
        
        for dept_data in departments:
            dept, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults={'name': dept_data['name']}
            )
            if created:
                self.stdout.write(f'Created department: {dept.name}')
        
        # Create permissions
        permissions = [
            # User management
            {'code': 'users.view', 'name': 'View Users', 'module': 'users'},
            {'code': 'users.create', 'name': 'Create Users', 'module': 'users'},
            {'code': 'users.edit', 'name': 'Edit Users', 'module': 'users'},
            {'code': 'users.deactivate', 'name': 'Deactivate Users', 'module': 'users'},
            {'code': 'users.activate', 'name': 'Activate Users', 'module': 'users'},
            {'code': 'users.reset_password', 'name': 'Reset User Password', 'module': 'users'},
            {'code': 'users.unlock', 'name': 'Unlock User Account', 'module': 'users'},
            
            # Department management
            {'code': 'departments.view', 'name': 'View Departments', 'module': 'departments'},
            {'code': 'departments.create', 'name': 'Create Departments', 'module': 'departments'},
            {'code': 'departments.edit', 'name': 'Edit Departments', 'module': 'departments'},
            {'code': 'departments.activate', 'name': 'Activate Departments', 'module': 'departments'},
            {'code': 'departments.deactivate', 'name': 'Deactivate Departments', 'module': 'departments'},
            
            # Role management
            {'code': 'roles.view', 'name': 'View Roles', 'module': 'roles'},
            {'code': 'roles.create', 'name': 'Create Roles', 'module': 'roles'},
            {'code': 'roles.edit', 'name': 'Edit Roles', 'module': 'roles'},
            {'code': 'roles.activate', 'name': 'Activate Roles', 'module': 'roles'},
            {'code': 'roles.deactivate', 'name': 'Deactivate Roles', 'module': 'roles'},
            
            # Permissions
            {'code': 'permissions.view', 'name': 'View Permissions', 'module': 'permissions'},
            
            # Receiving/Materials
            {'code': 'receiving.view', 'name': 'View Materials', 'module': 'receiving'},
            {'code': 'receiving.create', 'name': 'Create Materials', 'module': 'receiving'},
            {'code': 'receiving.edit', 'name': 'Edit Materials', 'module': 'receiving'},
            {'code': 'receiving.delete', 'name': 'Delete Materials', 'module': 'receiving'},
            {'code': 'receiving.request_sampling', 'name': 'Request Sampling', 'module': 'receiving'},
            
            # Sampling
            {'code': 'sampling.view', 'name': 'View Samples', 'module': 'sampling'},
            {'code': 'sampling.create', 'name': 'Create Samples', 'module': 'sampling'},
            {'code': 'sampling.complete', 'name': 'Complete Sampling', 'module': 'sampling'},
            
            # Analysis
            {'code': 'analysis.view', 'name': 'View Analysis', 'module': 'analysis'},
            {'code': 'analysis.start', 'name': 'Start Analysis', 'module': 'analysis'},
            {'code': 'analysis.submit_results', 'name': 'Submit Results', 'module': 'analysis'},
            
            # Review/Approval
            {'code': 'review.approve', 'name': 'Approve Review', 'module': 'review'},
            {'code': 'review.reject', 'name': 'Reject Review', 'module': 'review'},
            
            # Certificate
            {'code': 'certificate.view', 'name': 'View Certificates', 'module': 'certificate'},
            {'code': 'certificate.create', 'name': 'Create Certificates', 'module': 'certificate'},
            {'code': 'certificate.submit_for_review', 'name': 'Submit Certificate for Review', 'module': 'certificate'},
            {'code': 'certificate.review', 'name': 'Review Certificate', 'module': 'certificate'},
            {'code': 'certificate.approve', 'name': 'Approve Certificate', 'module': 'certificate'},
            {'code': 'certificate.reject', 'name': 'Reject Certificate', 'module': 'certificate'},
            {'code': 'certificate.lock', 'name': 'Lock Certificate', 'module': 'certificate'},
            {'code': 'certificate.download', 'name': 'Download Certificate', 'module': 'certificate'},
            
            # Material release
            {'code': 'material.release', 'name': 'Release Material', 'module': 'material'},
            
            # Audit
            {'code': 'audit.view', 'name': 'View Audit Logs', 'module': 'audit'},
        ]
        
        for perm_data in permissions:
            perm, created = Permission.objects.get_or_create(
                code=perm_data['code'],
                defaults={
                    'name': perm_data['name'],
                    'module': perm_data['module']
                }
            )
            if created:
                self.stdout.write(f'Created permission: {perm.code}')
        
        # Create roles
        roles = [
            {'code': 'admin', 'name': 'Administrator', 'description': 'System Administrator'},
            {'code': 'sysadmin', 'name': 'System Admin', 'description': 'System Administrator with full access'},
            {'code': 'storekeeper', 'name': 'Storekeeper', 'description': 'Warehouse storekeeper'},
            {'code': 'sampler', 'name': 'Sampler', 'description': 'QC Sampler'},
            {'code': 'qc_analyst', 'name': 'QC Analyst', 'description': 'QC Analyst'},
            {'code': 'qc_supervisor', 'name': 'QC Supervisor', 'description': 'QC Supervisor'},
            {'code': 'manager', 'name': 'Manager', 'description': 'Department Manager'},
        ]
        
        for role_data in roles:
            role, created = Role.objects.get_or_create(
                code=role_data['code'],
                defaults={
                    'name': role_data['name'],
                    'description': role_data['description']
                }
            )
            if created:
                self.stdout.write(f'Created role: {role.name}')
        
        # Assign permissions to roles
        # Admin/Sysadmin - all permissions
        admin_role = Role.objects.get(code='admin')
        sysadmin_role = Role.objects.get(code='sysadmin')
        all_permissions = Permission.objects.all()
        for perm in all_permissions:
            RolePermission.objects.get_or_create(role=admin_role, permission=perm)
            RolePermission.objects.get_or_create(role=sysadmin_role, permission=perm)
        
        # Storekeeper - receiving permissions
        storekeeper_role = Role.objects.get(code='storekeeper')
        storekeeper_permissions = [
            'receiving.view', 'receiving.create', 'receiving.edit',
            'receiving.request_sampling', 'sampling.view',
            'certificate.view', 'audit.view'
        ]
        for perm_code in storekeeper_permissions:
            perm = Permission.objects.get(code=perm_code)
            RolePermission.objects.get_or_create(role=storekeeper_role, permission=perm)
        
        # Sampler - sampling permissions
        sampler_role = Role.objects.get(code='sampler')
        sampler_permissions = [
            'sampling.view', 'sampling.create', 'sampling.complete',
            'receiving.view', 'audit.view'
        ]
        for perm_code in sampler_permissions:
            perm = Permission.objects.get(code=perm_code)
            RolePermission.objects.get_or_create(role=sampler_role, permission=perm)
        
        # QC Analyst - analysis permissions
        analyst_role = Role.objects.get(code='qc_analyst')
        analyst_permissions = [
            'analysis.view', 'analysis.start', 'analysis.submit_results',
            'sampling.view', 'certificate.view', 'certificate.create',
            'certificate.submit_for_review', 'audit.view'
        ]
        for perm_code in analyst_permissions:
            perm = Permission.objects.get(code=perm_code)
            RolePermission.objects.get_or_create(role=analyst_role, permission=perm)
        
        # QC Supervisor - review and approval permissions
        supervisor_role = Role.objects.get(code='qc_supervisor')
        supervisor_permissions = [
            'review.approve', 'review.reject', 'certificate.view',
            'certificate.review', 'certificate.approve', 'certificate.reject',
            'certificate.lock', 'material.release', 'analysis.view',
            'sampling.view', 'receiving.view', 'audit.view'
        ]
        for perm_code in supervisor_permissions:
            perm = Permission.objects.get(code=perm_code)
            RolePermission.objects.get_or_create(role=supervisor_role, permission=perm)
        
        # Create default admin user
        admin_dept = Department.objects.get(code='ADMIN')
        if not Employee.objects.filter(email='admin@pharma.com').exists():
            admin = Employee.objects.create_user(
                email='admin@pharma.com',
                password='Admin@123456',
                employee_number='EMP001',
                first_name='System',
                last_name='Administrator',
                job_title='System Administrator',
                department=admin_dept
            )
            admin.roles.add(sysadmin_role)
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            self.stdout.write('Created admin user: admin@pharma.com / Admin@123456')
        
        # Create test users for each role
        test_users = [
            {
                'email': 'storekeeper@pharma.com',
                'password': 'Store@123456',
                'employee_number': 'EMP002',
                'first_name': 'John',
                'last_name': 'Storekeeper',
                'job_title': 'Storekeeper',
                'department': 'WH',
                'role': 'storekeeper'
            },
            {
                'email': 'sampler@pharma.com',
                'password': 'Sample@123456',
                'employee_number': 'EMP003',
                'first_name': 'Sarah',
                'last_name': 'Sampler',
                'job_title': 'QC Sampler',
                'department': 'QC',
                'role': 'sampler'
            },
            {
                'email': 'analyst@pharma.com',
                'password': 'Analyst@123456',
                'employee_number': 'EMP004',
                'first_name': 'Alex',
                'last_name': 'Analyst',
                'job_title': 'QC Analyst',
                'department': 'QC',
                'role': 'qc_analyst'
            },
            {
                'email': 'supervisor@pharma.com',
                'password': 'Super@123456',
                'employee_number': 'EMP005',
                'first_name': 'Sam',
                'last_name': 'Supervisor',
                'job_title': 'QC Supervisor',
                'department': 'QC',
                'role': 'qc_supervisor'
            },
        ]
        
        for user_data in test_users:
            if not Employee.objects.filter(email=user_data['email']).exists():
                dept = Department.objects.get(code=user_data['department'])
                role = Role.objects.get(code=user_data['role'])
                user = Employee.objects.create_user(
                    email=user_data['email'],
                    password=user_data['password'],
                    employee_number=user_data['employee_number'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    job_title=user_data['job_title'],
                    department=dept
                )
                user.roles.add(role)
                self.stdout.write(f'Created user: {user_data["email"]} / {user_data["password"]}')
        
        self.stdout.write(self.style.SUCCESS('Initial data seeded successfully!'))