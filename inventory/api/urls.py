from django.urls import path, include
from rest_framework.routers import DefaultRouter
from inventory.api.views import APNViewSet, SIMCardViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'apns', APNViewSet, basename='apn')
router.register(r'sim', SIMCardViewSet, basename='simcard')

 # API URLS are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
 ]