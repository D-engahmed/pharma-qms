from django.test import TestCase

# Still a stub. New behavior in this app that has NO test coverage yet and
# needs it before this is production-safe:
#   - UserViewSet.get_permissions() action->permission map (the bug that
#     started this whole pass — write a regression test per action)
#   - last-active-sysadmin protection (destroy, roles action, Role deactivate)
#   - department_id now required on create/update
#   - force_password_change rename didn't break reset_password flow
#   - Department deactivate blocked while active users are assigned
#   - Role/Department activate/deactivate audit events actually get written
