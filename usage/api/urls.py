from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="APN & SIM Management API",
        default_version='v1',
        description="API for managing APNs, SIM cards, and data usage",
        contact=openapi.Contact(email="support@backspace.tech"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.api.urls')),
    path('api/inventory/', include('inventory.api.urls')),
    path('api/usage/', include('usage.api.urls')), 
    path('', include('users.dashboard_urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
