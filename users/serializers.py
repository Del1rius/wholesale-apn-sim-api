from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import Organization

User = get_user_model()

# Serliazer for Organisation Data
class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['org_id', 'name', 'industry', 'contact_email', 'date_created']
        read_only_fields = ['org_id', 'date_created']

# Serializer for User Data (responses)
class UserSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = user
        fields = ['id', 'username', ]