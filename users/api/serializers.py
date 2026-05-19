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
    organization_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone_number', 'role', 'organization_id']

        #Validate passwords match
        def validate(self, data):
            if data['password'] != data['passwprd_confirm']:
                raise serializers.ValidationError({"password": "Passwords must match."})
            return data

        #Validate Email is unique
        def validate_email(self, value):
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("A user with this email already exists.")
            return value
        
        #Create User with hashed password
        def create(self, validated_data):
            validated_data.pop('password_confirm')
            organization_id = validated_data.pop('organization_id', None)
            password = validated_data.pop('password')

            # Get organization if provided
            organization = None
            if organization_id:
                try:
                    organization = Organization.objects.get(org_id=organization_id)
                except Organization.DoesNotExist:
                    raise serializers.ValidationError({"organization_id": "Organization not found"})

            user = User.objects.create_user(
                password=password,
                organization=organization,
                **validated_data
            )

            return user

#Serializer for Login validation
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
