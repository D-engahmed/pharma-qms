from django.conf import settings

class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        request.audit_ip = request.META.get('REMOTE_ADDR')
        request.audit_session = request.session.session_key or ''
        return self.get_response(request)