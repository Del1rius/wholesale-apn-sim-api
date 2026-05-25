from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from inventory.models import APN, SIMCard
from inventory.api.serializers import (
    APNSerializer,
    APNListSerializer,
    SIMCardSerializer,
    SIMCardListSerializer
)

class APNViewSet(viewsets.ModelViewSet):
    #
    #
    #
    #
    #
    #
    #
    queryset = APN.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'authentication_type', 'organization']
    search_fields = ['name', 'apn_string']
    ordering_fields = ['name', 'date_created']
    ordering = ['-date_created']

    # Use leightweight serializer for list view, full serializer for detail
    def get_serializer_class(self):
        if self.action == 'list':
            return APNListSerializer
        return APNSerializer

    # Filter APNs based on user's organization (if not superuser)
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Superusers can see all APNs
        if user.is_superuser:
            return queryset
        
        # Network admins can see all APNs
        if user.role == 'network_admin':
            return queryset
        
        # Client managers can only see their organization's APNs and public APNs
        if user.organization:
            return queryset.filter(
                models.Q(organization=user.organization) | models.Q(organization__isnull=true)
            )

        # Users without organization can only see public APNs
        return queryset.filter(organization__isnull=true)