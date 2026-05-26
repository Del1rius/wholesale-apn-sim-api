from rest_framework import serializers
from django.db.models import Sum
from usage.models import BillingCycle, DataUsageRecord
from inventory.models import SIMCard

# Full serializer for BillingCycle with organization details.
class BillingCycleSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    total_usage_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = BillingCycle
        fields = [
            'cycle_id',
            'organization',
            'organization_name',
            'start_date',
            'end_date',
            'is_active',
            'total_usage_mb',
            'date_created',
            'date_modified'
        ]
        read_only_fields = ['cycle_id', 'date_created', 'date_modified']
    
    def get_total_usage_mb(self, obj):
        # Calculate total usage for this billing cycle
        total = obj.usage_records.aggregate(
            total=Sum('data_consumed_mb')
        )['total']
        return float(total) if total else 0.0

# Lightweight serializer for listing billing cycles.
class BillingCycleListSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = BillingCycle
        fields = [
            'cycle_id',
            'organization_name',
            'start_date',
            'end_date',
            'is_active'
        ]

# Full serializer for DataUsageRecord with SIM card details.
class DataUsageRecordSerializer(serializers.ModelSerializer):
    sim_iccid = serializers.CharField(source='sim_card.iccid', read_only=True)
    sim_phone_number = serializers.CharField(source='sim_card.phone_number', read_only=True)
    billing_cycle_info = serializers.SerializerMethodField()
    
    class Meta:
        model = DataUsageRecord
        fields = [
            'record_id',
            'sim_card',
            'sim_iccid',
            'sim_phone_number',
            'billing_cycle',
            'billing_cycle_info',
            'data_consumed_mb',
            'timestamp',
            'recorded_at',
            'source',
            'notes'
        ]
        read_only_fields = ['record_id', 'timestamp']
    
    def get_billing_cycle_info(self, obj):
        # Return billing cycle date range if exists
        if obj.billing_cycle:
            return f"{obj.billing_cycle.start_date} to {obj.billing_cycle.end_date}"
        return None
    
    def validate_data_consumed_mb(self, value):
        # Ensure data consumed is positive
        if value <= 0:
            raise serializers.ValidationError("Data consumed must be greater than 0")
        return value

# Lightweight serializer for listing usage records.
# Used in dashboard and list views.
class DataUsageRecordListSerializer(serializers.ModelSerializer):
    sim_iccid = serializers.CharField(source='sim_card.iccid', read_only=True)
    
    class Meta:
        model = DataUsageRecord
        fields = [
            'record_id',
            'sim_iccid',
            'data_consumed_mb',
            'recorded_at',
            'source'
        ]

# Serializer for creating usage records (used by Celery tasks).
# Simplified for bulk creation.
class DataUsageRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataUsageRecord
        fields = [
            'sim_card',
            'billing_cycle',
            'data_consumed_mb',
            'recorded_at',
            'source',
            'notes'
        ]
    
    def validate_data_consumed_mb(self, value):
        # Ensure data consumed is positive
        if value <= 0:
            raise serializers.ValidationError("Data consumed must be greater than 0")
        return value

# Custom serializer for SIM usage summary statistics.
# Used in dashboard and reporting endpoints.
class SIMUsageSummarySerializer(serializers.Serializer):
    sim_card = serializers.UUIDField()
    iccid = serializers.CharField()
    phone_number = serializers.CharField()
    total_usage_mb = serializers.DecimalField(max_digits=10, decimal_places=2)
    data_limit_mb = serializers.IntegerField()
    usage_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    status = serializers.CharField()
    last_recorded = serializers.DateTimeField()