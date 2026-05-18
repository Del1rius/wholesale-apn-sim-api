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
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'role_display', 'organization', 'date_joined']
        read_only_fields = ['id', 'date_joined']

# Serializer for User Registration
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input': 'password'})