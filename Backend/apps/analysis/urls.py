from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalysisViewSet, TestResultViewSet, OOSReportViewSet

router = DefaultRouter()
router.register(r'analyses', AnalysisViewSet)
router.register(r'test-results', TestResultViewSet)
router.register(r'oos-reports', OOSReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]