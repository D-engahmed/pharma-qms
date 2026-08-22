from rest_framework.routers import DefaultRouter
from .views import AnalysisViewSet
router = DefaultRouter()
router.register(r'analyses', AnalysisViewSet, basename='analysis')
urlpatterns = router.urls