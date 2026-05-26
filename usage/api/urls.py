from django.urls import path, include
from rest_framework.routers import DefaultRouter
from usage.api.views import BillingCycleViewSet, DataUsageRecordViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'billing-cycles', BillingCycleViewSet, basename='billingcycle')
router.register(r'usage-records', DataUsageRecordViewSet, basename='usagerecord')

urlpatterns = [
    path('', include(router.urls)),
]
