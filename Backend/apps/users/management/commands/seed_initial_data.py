from django.core.management.base import BaseCommand
from apps.users.models import Permission, Role, RolePermission


class Command(BaseCommand):
    help = 'Seed initial permissions and roles'

    def handle(self, *args, **options):
        permissions_data = [
            ('users.view', 'View Users', 'users'),
            ('users.create', 'Create Users', 'users'),
            ('users.edit', 'Edit Users', 'users'),
            ('users.activate', 'Activate Users', 'users'),
            ('users.deactivate', 'Deactivate Users', 'users'),
            ('users.reset_password', 'Reset User Passwords', 'users'),
            ('users.unlock', 'Unlock Users', 'users'),
            ('departments.view', 'View Departments', 'departments'),
            ('departments.create', 'Create Departments', 'departments'),
            ('departments.edit', 'Edit Departments', 'departments'),
            ('departments.activate', 'Activate Departments', 'departments'),
            ('departments.deactivate', 'Deactivate Departments', 'departments'),
            ('roles.view', 'View Roles', 'roles'),
            ('roles.create', 'Create Roles', 'roles'),
            ('roles.edit', 'Edit Roles', 'roles'),
            ('roles.activate', 'Activate Roles', 'roles'),
            ('roles.deactivate', 'Deactivate Roles', 'roles'),
            ('roles.assign_permissions', 'Assign Permissions to Roles', 'roles'),
            ('permissions.view', 'View Permissions', 'permissions'),
            ('receiving.view', 'View Receiving', 'receiving'),
            ('receiving.create', 'Create Receiving', 'receiving'),
            ('receiving.edit', 'Edit Receiving', 'receiving'),
            ('receiving.request_sampling', 'Request Sampling', 'receiving'),
            ('sampling.view', 'View Sampling', 'sampling'),
            ('sampling.create', 'Create Sampling', 'sampling'),
            ('sampling.complete', 'Complete Sampling', 'sampling'),
            ('sampling.print', 'Print Sampling Labels', 'sampling'),
            ('analysis.view', 'View Analysis', 'analysis'),
            ('analysis.create', 'Create Analysis', 'analysis'),
            ('analysis.enter_result', 'Enter Result', 'analysis'),
            ('analysis.submit_for_review', 'Submit for Review', 'analysis'),
            ('analysis.review', 'Review Analysis', 'analysis'),
            ('analysis.approve', 'Approve Analysis', 'analysis'),
            ('certificate.view', 'View Certificates', 'certificate'),
            ('certificate.create', 'Create Certificate', 'certificate'),
            ('certificate.submit_for_review', 'Submit Certificate for Review', 'certificate'),
            ('certificate.review', 'Review Certificate', 'certificate'),
            ('certificate.approve', 'Approve Certificate', 'certificate'),
            ('certificate.lock', 'Lock Certificate', 'certificate'),
            ('material.view', 'View Material', 'material'),
            ('material.move', 'Move Material', 'material'),
            ('material.release', 'Release Material', 'material'),
            ('audit.view', 'View Audit Log', 'audit'),
        ]

        perms = {}
        for code, name, module in permissions_data:
            p, created = Permission.objects.get_or_create(
                code=code, defaults={'name': name, 'module': module}
            )
            perms[code] = p
            if created:
                self.stdout.write(f"Created permission: {code}")

        # 07-roles.md's 7-role taxonomy, confirmed authoritative. Codes for
        # storekeeper/sampler are unchanged from the old seed data; admin,
        # analyst, and qcmanager were renamed — see the one-time Role.objects
        # rename snippet if you already have seeded data, or you'll orphan
        # existing role assignments.
        roles_data = {
            'admin': {
                'name': 'Administrator',
                # UNDEFINED IN SPEC: 07-roles.md lists "Administrator" and
                # "System Administrator" as separate roles and never
                # explains the difference. Seeded with zero permissions
                # rather than guessing it inherits sysadmin's scope.
                'permissions': [],
            },
            'sysadmin': {
                'name': 'System Administrator',
                'permissions': [
                    'users.view', 'users.create', 'users.edit', 'users.activate', 'users.deactivate',
                    'users.reset_password', 'users.unlock',
                    'departments.view', 'departments.create', 'departments.edit',
                    'departments.activate', 'departments.deactivate',
                    'roles.view', 'roles.create', 'roles.edit', 'roles.activate',
                    'roles.deactivate', 'roles.assign_permissions',
                    'permissions.view', 'audit.view',
                ],
            },
            'storekeeper': {
                'name': 'Store Keeper',
                'permissions': [
                    'receiving.view', 'receiving.create', 'receiving.edit', 'receiving.request_sampling',
                    'sampling.view', 'sampling.print',
                    'material.view', 'material.move',
                ],
            },
            'sampler': {
                'name': 'Sampler',
                'permissions': [
                    'sampling.view', 'sampling.create', 'sampling.complete', 'sampling.print',
                    'receiving.view', 'material.view',
                ],
            },
            'qc_analyst': {
                'name': 'QC Analyst',
                'permissions': [
                    'analysis.view', 'analysis.create', 'analysis.enter_result',
                    'analysis.submit_for_review',
                    'certificate.view', 'certificate.create',
                    'sampling.view', 'material.view',
                ],
            },
            'qc_supervisor': {
                # Absorbs the old 'qcmanager' permission set as a starting
                # point. My call, not the spec's — 16-separation-of-duties.md
                # is itself inconsistent about whether "supervisor" only
                # reviews or also approves/releases. Revisit if wrong.
                'name': 'QC Supervisor',
                'permissions': [
                    'analysis.review', 'analysis.approve',
                    'certificate.review', 'certificate.approve', 'certificate.lock',
                    'material.release', 'receiving.view', 'material.view',
                ],
            },
            'manager': {
                'name': 'Manager',
                # UNDEFINED IN SPEC — 07-roles.md names it, never scopes it.
                'permissions': [],
            },
        }

        for role_code, role_info in roles_data.items():
            role, created = Role.objects.get_or_create(
                code=role_code, defaults={'name': role_info['name'], 'is_active': True}
            )
            if created:
                self.stdout.write(f"Created role: {role_code} ({role_info['name']})")
            for code in role_info['permissions']:
                if code in perms:
                    RolePermission.objects.get_or_create(role=role, permission=perms[code])
                else:
                    self.stdout.write(f"Warning: Permission {code} not found for role {role_code}")
            if not role_info['permissions']:
                self.stdout.write(self.style.WARNING(
                    f"Role '{role_code}' ({role_info['name']}) seeded with NO permissions — "
                    f"spec doesn't define this role's scope. Needs a decision before go-live."
                ))

        self.stdout.write(self.style.SUCCESS('Initial data seeded successfully.'))
