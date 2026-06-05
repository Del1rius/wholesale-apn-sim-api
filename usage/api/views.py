from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from usage.models import BillingCycle, DataUsageRecord
from usage.api.serializers import (
    BillingCycleSerializer,
    BillingCycleListSerializer,
    DataUsageRecordSerializer,
    DataUsageRecordListSerializer,
    DataUsageRecordCreateSerializer,
    SIMUsageSummarySerializer
)
from inventory.models import SIMCard
from config.throttling import BurstRateThrottle, SustainedRateThrottle, UsageLoggingThrottle, AdminRateThrottle


# ViewSet for managing billing cycles.
# Supports CRUD operations and filtering by organization.
class BillingCycleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AdminRateThrottle, BurstRateThrottle, SustainedRateThrottle]

    def get_queryset(self):
        # Filter billing cycles based on user role
        user = self.request.user

        if user.is_superuser or user.role == 'network_admin':
            # Superusers and network admins see all billing cycles
            return BillingCycle.objects.all()
        else:
            # Client managers see only their organization's billing cycles
            return BillingCycle.objects.filter(organization=user.organization)

    def get_serializer_class(self):
        # Use lightweight serializer for list view
        if self.action == 'list':
            return BillingCycleListSerializer
        return BillingCycleSerializer

    @action(detail=False, methods=['get'])
    def active(self, request):
        # Get all active billing cycles
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def usage_summary(self, request, pk=None):
        # Get usage summary for a specific billing cycle
        billing_cycle = self.get_object()

        # Get all usage records for this billing cycle
        usage_records = billing_cycle.usage_records.values('sim_card').annotate(
            total_usage=Sum('data_consumed_mb')
        )

        summary = {
            'cycle_id': billing_cycle.cycle_id,
            'start_date': billing_cycle.start_date,
            'end_date': billing_cycle.end_date,
            'total_usage_mb': sum(record['total_usage'] for record in usage_records),
            'sim_count': usage_records.count(),
            'usage_by_sim': list(usage_records)
        }

        return Response(summary)

# ViewSet for managing data usage records.
# Supports CRUD operations, filtering, and usage analytics.


class DataUsageRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AdminRateThrottle, UsageLoggingThrottle, SustainedRateThrottle]

    def get_queryset(self):
        # Filter usage records based on user role
        user = self.request.user

        if user.is_superuser or user.role == 'network_admin':
            # Superusers and network admins see all usage records
            queryset = DataUsageRecord.objects.all()
        else:
            # Client managers see only their organization's usage records
            queryset = DataUsageRecord.objects.filter(
                sim_card__organization=user.organization
            )

        # Filter by SIM card if provided
        sim_card_id = self.request.query_params.get('sim_card', None)
        if sim_card_id:
            queryset = queryset.filter(sim_card__sim_id=sim_card_id)

        # Filter by billing cycle if provided
        billing_cycle_id = self.request.query_params.get('billing_cycle', None)
        if billing_cycle_id:
            queryset = queryset.filter(billing_cycle__cycle_id=billing_cycle_id)

        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if start_date:
            queryset = queryset.filter(recorded_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(recorded_at__lte=end_date)

        return queryset.select_related('sim_card', 'billing_cycle')

    def get_serializer_class(self):
        """Use appropriate serializer based on action"""
        if self.action == 'list':
            return DataUsageRecordListSerializer
        elif self.action == 'create':
            return DataUsageRecordCreateSerializer
        return DataUsageRecordSerializer

    def perform_create(self, serializer):
        """
        Override create to trigger Celery task immediately after saving usage record.
        This ensures real-time data limit checking and auto-suspension.
        """
        # Save the usage record
        instance = serializer.save()

        # Trigger Celery task immediately to check data limit
        from usage.tasks import process_usage_and_check_limit
        process_usage_and_check_limit.delay(instance.sim_card.iccid)

        return instance

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent usage records (last 50)"""
        queryset = self.get_queryset().order_by('-recorded_at')[:50]
        serializer = DataUsageRecordListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_sim(self, request):
        """Get usage records grouped by SIM card"""
        sim_card_id = request.query_params.get('sim_card_id', None)

        if not sim_card_id:
            return Response(
                {'error': 'sim_card_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            sim_card = SIMCard.objects.get(sim_id=sim_card_id)
        except SIMCard.DoesNotExist:
            return Response(
                {'error': 'SIM card not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check permission
        user = request.user
        if not (user.is_superuser or user.role == 'network_admin'):
            if sim_card.organization != user.organization:
                return Response(
                    {'error': 'You do not have permission to view this SIM card'},
                    status=status.HTTP_403_FORBIDDEN
                )

        # Get usage records for this SIM
        usage_records = DataUsageRecord.objects.filter(
            sim_card=sim_card
        ).order_by('-recorded_at')

        # Calculate total usage
        total_usage = usage_records.aggregate(
            total=Sum('data_consumed_mb')
        )['total'] or 0

        serializer = DataUsageRecordListSerializer(usage_records, many=True)

        return Response({
            'sim_card': {
                'sim_id': sim_card.sim_id,
                'iccid': sim_card.iccid,
                'phone_number': sim_card.phone_number,
                'data_limit_mb': sim_card.data_limit_mb,
                'status': sim_card.status
            },
            'total_usage_mb': float(total_usage),
            'usage_percentage': (float(total_usage) / sim_card.data_limit_mb * 100) if sim_card.data_limit_mb else 0,
            'records': serializer.data
        })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get usage summary statistics for the current user's organization"""
        user = request.user

        # Get organization's SIM cards
        if user.is_superuser or user.role == 'network_admin':
            sim_cards = SIMCard.objects.all()
        else:
            sim_cards = SIMCard.objects.filter(organization=user.organization)

        # Get current billing cycle (if exists)
        current_date = timezone.now().date()
        current_cycle = BillingCycle.objects.filter(
            start_date__lte=current_date,
            end_date__gte=current_date,
            is_active=True
        ).first()

        # Calculate usage for each SIM
        usage_data = []
        for sim in sim_cards:
            if current_cycle:
                usage_records = DataUsageRecord.objects.filter(
                    sim_card=sim,
                    billing_cycle=current_cycle
                )
            else:
                # If no current cycle, get usage from last 30 days
                thirty_days_ago = timezone.now() - timedelta(days=30)
                usage_records = DataUsageRecord.objects.filter(
                    sim_card=sim,
                    recorded_at__gte=thirty_days_ago
                )

            total_usage = usage_records.aggregate(
                total=Sum('data_consumed_mb')
            )['total'] or 0

            usage_percentage = (float(total_usage) / sim.data_limit_mb * 100) if sim.data_limit_mb else 0

            last_record = usage_records.order_by('-recorded_at').first()

            usage_data.append({
                'sim_card': sim.sim_id,
                'iccid': sim.iccid,
                'phone_number': sim.phone_number,
                'total_usage_mb': float(total_usage),
                'data_limit_mb': sim.data_limit_mb,
                'usage_percentage': round(usage_percentage, 2),
                'status': sim.status,
                'last_recorded': last_record.recorded_at if last_record else None
            })

        serializer = SIMUsageSummarySerializer(usage_data, many=True)

        return Response({
            'billing_cycle': {
                'cycle_id': current_cycle.cycle_id if current_cycle else None,
                'start_date': current_cycle.start_date if current_cycle else None,
                'end_date': current_cycle.end_date if current_cycle else None
            } if current_cycle else None,
            'summary': serializer.data
        })
