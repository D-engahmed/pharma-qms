from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SupplierViewSet, WarehouseViewSet, StorageLocationViewSet,
    MaterialSpecificationViewSet, TestSpecificationViewSet
)

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet)
router.register(r'warehouses', WarehouseViewSet)
router.register(r'locations', StorageLocationViewSet)
router.register(r'material-specs', MaterialSpecificationViewSet)
router.register(r'test-specs', TestSpecificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]