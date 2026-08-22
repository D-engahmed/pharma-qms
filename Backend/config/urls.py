from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Swagger UI
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-docs'),
    
    # Your APIs
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/', include('apps.materials.urls')),
    path('api/v1/', include('apps.sampling.urls')),
    path('api/v1/', include('apps.analysis.urls')),
    path('api/v1/', include('apps.coa.urls')),
    path('api/v1/', include('apps.notifications.urls')),
    path('api/v1/audit/', include('apps.audit.urls')),
]