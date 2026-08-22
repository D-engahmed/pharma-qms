from django.core.management.base import BaseCommand
from apps.users.models import Employee, Department, Role, Permission, RolePermission

class Command(BaseCommand):
    help = 'Seed initial data'
    
    def handle(self, *args, **options):
        # Departments
        qc_dept, _ = Department.objects.get_or_create(code='QC', defaults={'name': 'Quality Control'})
        wh_dept, _ = Department.objects.get_or_create(code='WH', defaults={'name': 'Warehouse'})
        admin_dept, _ = Department.objects.get_or_create(code='ADMIN', defaults={'name': 'Administration'})
        
        # Permissions (Added missing ones like certificate.review, users.activate, etc.)
        perms = [
            'users.view', 'users.create', 'users.edit', 'users.deactivate', 'users.activate',
            'departments.view', 'departments.create', 'departments.edit', 'departments.activate', 'departments.deactivate',
            'roles.view', 'roles.create', 'roles.edit', 'roles.activate', 'roles.deactivate',
            'permissions.view',
            'receiving.view', 'receiving.create', 'receiving.edit', 'receiving.delete', 'receiving.request_sampling',
            'sampling.view', 'sampling.create', 'sampling.complete',
            'analysis.view', 'analysis.start', 'analysis.submit_results',
            'review.approve', 'review.reject',
            'certificate.view', 'certificate.create', 'certificate.submit_for_review', 'certificate.review', 'certificate.approve', 'certificate.reject', 'certificate.lock',
            'material.release',
            'audit.view'
        ]
        for p in perms:
            Permission.objects.get_or_create(code=p, defaults={'name': p, 'module': p.split('.')[0]})
        
        # Roles
        admin_role, _ = Role.objects.get_or_create(code='admin', defaults={'name': 'Administrator'})
        storekeeper_role, _ = Role.objects.get_or_create(code='storekeeper', defaults={'name': 'Storekeeper'})
        sampler_role, _ = Role.objects.get_or_create(code='sampler', defaults={'name': 'Sampler'})
        analyst_role, _ = Role.objects.get_or_create(code='qc_analyst', defaults={'name': 'QC Analyst'})
        supervisor_role, _ = Role.objects.get_or_create(code='qc_supervisor', defaults={'name': 'QC Supervisor'})
        
        # Assign all permissions to admin
        all_perms = Permission.objects.all()
        for p in all_perms:
            RolePermission.objects.get_or_create(role=admin_role, permission=p)
        
        # Storekeeper perms
        storekeeper_perms = ['receiving.view', 'receiving.create', 'receiving.edit', 'receiving.request_sampling', 'sampling.view', 'certificate.view', 'audit.view']
        for p in storekeeper_perms:
            RolePermission.objects.get_or_create(role=storekeeper_role, permission=Permission.objects.get(code=p))
            
        # Sampler perms
        sampler_perms = ['sampling.view', 'sampling.create', 'sampling.complete', 'receiving.view', 'audit.view']
        for p in sampler_perms:
            RolePermission.objects.get_or_create(role=sampler_role, permission=Permission.objects.get(code=p))
            
        # Analyst perms
        analyst_perms = ['analysis.view', 'analysis.start', 'analysis.submit_results', 'sampling.view', 'certificate.view', 'certificate.create', 'certificate.submit_for_review', 'audit.view']
        for p in analyst_perms:
            RolePermission.objects.get_or_create(role=analyst_role, permission=Permission.objects.get(code=p))
            
        # Supervisor perms
        supervisor_perms = ['review.approve', 'review.reject', 'certificate.view', 'certificate.review', 'certificate.approve', 'certificate.reject', 'certificate.lock', 'material.release', 'analysis.view', 'sampling.view', 'receiving.view', 'audit.view']
        for p in supervisor_perms:
            RolePermission.objects.get_or_create(role=supervisor_role, permission=Permission.objects.get(code=p))
        
        # Users
        if not Employee.objects.filter(email='admin@pharma.com').exists():
            admin = Employee.objects.create_user(
                email='admin@pharma.com', password='Admin@123456',
                employee_number='EMP001', first_name='System', last_name='Admin',
                job_title='Administrator', department=admin_dept
            )
            admin.roles.add(admin_role)
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            
        if not Employee.objects.filter(email='storekeeper@pharma.com').exists():
            user = Employee.objects.create_user(
                email='storekeeper@pharma.com', password='Store@123456',
                employee_number='EMP002', first_name='John', last_name='Store',
                job_title='Storekeeper', department=wh_dept
            )
            user.roles.add(storekeeper_role)
            
        if not Employee.objects.filter(email='sampler@pharma.com').exists():
            user = Employee.objects.create_user(
                email='sampler@pharma.com', password='Sample@123456',
                employee_number='EMP003', first_name='Sarah', last_name='Sampler',
                job_title='Sampler', department=qc_dept
            )
            user.roles.add(sampler_role)
            
        if not Employee.objects.filter(email='analyst@pharma.com').exists():
            user = Employee.objects.create_user(
                email='analyst@pharma.com', password='Analyst@123456',
                employee_number='EMP004', first_name='Alex', last_name='Analyst',
                job_title='Analyst', department=qc_dept
            )
            user.roles.add(analyst_role)
            
        if not Employee.objects.filter(email='supervisor@pharma.com').exists():
            user = Employee.objects.create_user(
                email='supervisor@pharma.com', password='Super@123456',
                employee_number='EMP005', first_name='Sam', last_name='Supervisor',
                job_title='Supervisor', department=qc_dept
            )
            user.roles.add(supervisor_role)
            
        self.stdout.write(self.style.SUCCESS('Data seeded successfully!'))