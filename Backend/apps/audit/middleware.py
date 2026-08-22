from django.conf import settings


class AuditMiddleware:
    """Middleware to capture audit-related information from requests"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Store audit information on request object
        request.audit_ip = self.get_client_ip(request)
        request.audit_session = request.session.session_key or ''
        request.audit_user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Get client IP address, respecting trusted proxies"""
        remote_addr = request.META.get('REMOTE_ADDR')
        trusted_proxies = getattr(settings, 'TRUSTED_PROXIES', [])
        
        if remote_addr in trusted_proxies:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                return x_forwarded_for.split(',')[0].strip()
        
        return remote_addr
    
    def process_request(self, request):
        """Legacy method for older Django middleware"""
        request.audit_ip = self.get_client_ip(request)
        request.audit_session = request.session.session_key or ''
        request.audit_user_agent = request.META.get('HTTP_USER_AGENT', '')