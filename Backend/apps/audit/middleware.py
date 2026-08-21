from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class AuditMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.audit_ip = self.get_client_ip(request)
        request.audit_session = request.session.session_key

    def get_client_ip(self, request):
        remote_addr = request.META.get('REMOTE_ADDR')
        # X-Forwarded-For is attacker-controlled unless the request actually
        # came through a proxy we trust — otherwise anyone can inject an
        # arbitrary IP into the audit trail. settings.TRUSTED_PROXIES
        # defaults to empty, meaning REMOTE_ADDR is used as-is.
        trusted_proxies = getattr(settings, 'TRUSTED_PROXIES', [])
        if remote_addr in trusted_proxies:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                return x_forwarded_for.split(',')[0].strip()
        return remote_addr