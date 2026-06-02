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
from config.throttling import BurstRateThrottle, SustainedRateThrottle, AdminRateThrottle

class APNViewSet(viewsets.ModelViewSet):
    # ViewSet for SIM Card CRUD operations
    # list: GET /api/inventory/sims/ - List all SIM cards
    # retrieve: GET /api/inventory/sim/{id}/ - Get single SIM Card
    # create: POST /api/inventory/apns/ - Create new APN
    # update: PUT /api/inventory/apns/{id}/ - Update APN
    # partial_update: PATCH /api/inventory/apns/{id}/ - Partial update
    # destroy: DELETE /api/inventory/apns/{id}/ - Delete APN
    queryset = APN.objects.all()
    permission_classes = [IsAuthenticated]
    throttle_classes = [AdminRateThrottle, BurstRateThrottle, SustainedRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'authentication_type', 'organization']
    search_fields = ['name', 'apn_string']
    ordering_fields = ['name', 'date_created']
    ordering = ['-date_created']

    # Use lightweight serializer for list view, full serializer for detail
    def get_serializer_class(self):
        if self.action == 'list':
            return APNListSerializer
        return APNSerializer
    
    def get_permissions(self):
        """
        Only network admins and superusers can create, update, or delete APNs
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def check_write_permission(self):
        """Check if user has permission for write operations"""
        user = self.request.user
        if not (user.is_superuser or user.role == 'network_admin'):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only network administrators can modify APNs.")
    
    def create(self, request, *args, **kwargs):
        self.check_write_permission()
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        self.check_write_permission()
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        self.check_write_permission()
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        self.check_write_permission()
        return super().destroy(request, *args, **kwargs)

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
                models.Q(organization=user.organization) | models.Q(organization__isnull=True)
            )

        # Users without organization can only see public APNs
        return queryset.filter(organization__isnull=True)

    @action(detail=False, methods=['get'])
    def active(self, request):
        # Get only active APNs
        active_apns = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(active_apns, many=True)
        return Response(serializer.data)


class SIMCardViewSet(viewsets.ModelViewSet):
   
    # ViewSet for SIM Card CRUD operations
    
    # list: GET /api/inventory/sims/ - List all SIM cards
    # retrieve: GET /api/inventory/sims/{id}/ - Get single SIM card
    # create: POST /api/inventory/sims/ - Create new SIM card
    # update: PUT /api/inventory/sims/{id}/ - Update SIM card
    # partial_update: PATCH /api/inventory/sims/{id}/ - Partial update
    # destroy: DELETE /api/inventory/sims/{id}/ - Delete SIM card

    queryset = SIMCard.objects.select_related('organization', 'apn').all()
    permission_classes = [IsAuthenticated]
    throttle_classes = [AdminRateThrottle, BurstRateThrottle, SustainedRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'carrier', 'network_type', 'organization']
    search_fields = ['iccid', 'phone_number', 'carrier']
    ordering_fields = ['iccid', 'phone_number', 'date_created', 'status']
    ordering = ['-date_created']

    def get_serializer_class(self):
        # Use lightweight serializer for list view, full serializer for detail
        if self.action == 'list':
            return SIMCardListSerializer
        return SIMCardSerializer
    
    def check_write_permission(self):
        """Check if user has permission for write operations"""
        user = self.request.user
        if not (user.is_superuser or user.role == 'network_admin'):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only network administrators can modify SIM cards.")
    
    def create(self, request, *args, **kwargs):
        self.check_write_permission()
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        self.check_write_permission()
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        self.check_write_permission()
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        self.check_write_permission()
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        # Filter SIM cards based on user's organization
        queryset = super().get_queryset()
        user = self.request.user
        
        # Superusers can see all SIM cards
        if user.is_superuser:
            return queryset
        
        # Network admins can see all SIM cards
        if user.role == 'network_admin':
            return queryset
        
        # Client managers can only see their organization's SIM cards
        if user.organization:
            return queryset.filter(organization=user.organization)
        
        # Users without organization see nothing
        return queryset.none()

    @action(detail=False, methods=['get'])
    def available(self, request):
        # Get only available SIM cards 
        available_sims = self.get_queryset().filter(status='available')
        serializer = self.get_serializer(available_sims, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def suspended(self, request):
        # Get only suspended SIM cards 
        suspended_sims = self.get_queryset().filter(status='suspended')
        serializer = self.get_serializer(suspended_sims, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        # Assign SIM card to an organization 
        sim_card = self.get_object()
        organization_id = request.data.get('organization_id')
        
        if not organization_id:
            return Response(
                {'error': 'organization_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from users.models import Organization
            organization = Organization.objects.get(org_id=organization_id)
            sim_card.organization = organization
            sim_card.status = 'assigned'
            sim_card.save()
            
            serializer = self.get_serializer(sim_card)
            return Response(serializer.data)
        except Organization.DoesNotExist:
            return Response(
                {'error': 'Organization not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        # Suspend a SIM card
        sim_card = self.get_object()
        sim_card.status = 'suspended'
        sim_card.save()
        
        serializer = self.get_serializer(sim_card)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        # Activate a suspended SIM card
        sim_card = self.get_object()
        
        if sim_card.status == 'suspended':
            sim_card.status = 'assigned' if sim_card.organization else 'available'
        else:
            sim_card.status = 'assigned' if sim_card.organization else 'available'
        
        sim_card.save()
        
        serializer = self.get_serializer(sim_card)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        # Get SIM card statistics
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'available': queryset.filter(status='available').count(),
            'assigned': queryset.filter(status='assigned').count(),
            'suspended': queryset.filter(status='suspended').count(),
            'deactivated': queryset.filter(status='deactivated').count(),
            'lost': queryset.filter(status='lost').count(),
            'by_carrier': {},
            'by_network_type': {}
        }
        
        # Count by carrier
        for carrier in queryset.values_list('carrier', flat=True).distinct():
            stats['by_carrier'][carrier] = queryset.filter(carrier=carrier).count()
        
        # Count by network type
        for network_type in queryset.values_list('network_type', flat=True).distinct():
            stats['by_network_type'][network_type] = queryset.filter(network_type=network_type).count()
        
        return Response(stats)