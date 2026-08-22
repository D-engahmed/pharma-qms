from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/', include('apps.materials.urls')),
    path('api/v1/', include('apps.sampling.urls')),
    path('api/v1/', include('apps.analysis.urls')),
    path('api/v1/', include('apps.coa.urls')),
    path('api/v1/', include('apps.notifications.urls')),
    path('api/v1/audit/', include('apps.audit.urls')),
]