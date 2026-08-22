from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CertificateViewSet, CertificateTestResultViewSet

router = DefaultRouter()
router.register(r'certificates', CertificateViewSet)
router.register(r'certificate-tests', CertificateTestResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
]