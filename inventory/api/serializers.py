from rest_framework import serializers
from inventory.models import APN, SIMCard
from users.api.serializers import OrganizationSerializer
from django.utils.html import strip_tags


# Serializer for APN Model
class APNSerializer(serializers.ModelSerializer):
    organization_detail = OrganizationSerializer(
        source='organization', read_only=True)

    class Meta:
        model = APN
        fields = [
            'apn_id',
            'name',
            'apn_string',
            'username',
            'password',
            'authentication_type',
            'organization',
            'organization_detail',
            'is_active',
            'date_created',
            'date_modified'
        ]
        read_only_fields = ['apn_id', 'date_created', 'date_modified']
        extra_kwargs = {
            # Makes it not expose password in response
            'password': {'write_only': True}
        }

# Lightweight Serializer for APN lists (doesn't have sensitive data)


class APNListSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source='organization.name', read_only=True)

    class Meta:
        model = APN
        fields = [
            'apn_id',
            'name',
            'authentication_type',
            'organization',
            'organization_name',
            'is_active',
            'date_created'
        ]
        read_only_fields = ['apn_id', 'date_created']

# Serializer for SIMCard Model


class SIMCardSerializer(serializers.ModelSerializer):
    organization_detail = OrganizationSerializer(
        source='organization', read_only=True)
    apn_detail = APNListSerializer(source='apn', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)
    network_type_display = serializers.CharField(
        source='get_network_type_display', read_only=True)

    class Meta:
        model = SIMCard
        fields = [
            'sim_id',
            'iccid',
            'phone_number',
            'status',
            'status_display',
            'carrier',
            'network_type',
            'network_type_display',
            'organization',
            'organization_detail',
            'apn',
            'apn_detail',
            'data_limit_mb',
            'activation_date',
            'expiry_date',
            'date_created',
            'date_modified',
            'notes'
        ]
        read_only_fields = ['sim_id', 'date_created', 'date_modified']

    # Validate ICCID format (19-22 digits)
    def validate_iccid(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(
                "ICCID must contain only digits.")
        if len(value) < 19 or len(value) > 22:
            raise serializers.ValidationError(
                "ICCID must be between 19 and 22 digits.")
        return value

    # Validate phone number format
    def validate_phone_number(self, value):
        if value and not value.startswith('+'):
            raise serializers.ValidationError(
                "Phone number must start with '+' (e.g., +27821234567)")
        return value

    # Validate data limit (maximum 100,000 MB)
    def validate_data_limit_mb(self, value):
        if value is not None:
            if value < 1:
                raise serializers.ValidationError(
                    "Data limit must be at least 1 MB.")
            if value > 100000:
                raise serializers.ValidationError(
                    "Data limit cannot exceed 100,000 MB.")
        return value

    # Validate and sanitize notes field
    def validate_notes(self, value):
        if value:
            # Limit length to prevent database bloat
            if len(value) > 2000:
                raise serializers.ValidationError(
                    "Notes cannot exceed 2000 characters")
            # Strip HTML tags for XSS prevention
            value = strip_tags(value)
        return value

# Lightweight serializer for SIM card lists


class SIMCardListSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source='organization.name', read_only=True)
    apn_name = serializers.CharField(source='apn.name', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)

    class Meta:
        model = SIMCard
        fields = [
            'sim_id',
            'iccid',
            'phone_number',
            'status',
            'status_display',
            'carrier',
            'network_type',
            'organization',
            'organization_name',
            'apn',
            'apn_name',
            'date_created'
        ]
        read_only_fields = ['sim_id', 'date_created']
