from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import User, Organization


class AuthenticationTestCase(APITestCase):
    """Test authentication endpoints"""

    def setUp(self):
        """Set up test data"""
        # Create organization
        self.org = Organization.objects.create(
            name="Test Organization",
            contact_email="test@example.com"
        )

        # Create test users
        self.admin_user = User.objects.create_user(
            username="test_admin",
            email="admin@test.com",
            password="TestPass123!",
            role="network_admin",
            organization=self.org
        )

        self.regular_user = User.objects.create_user(
            username="test_user",
            email="user@test.com",
            password="TestPass123!",
            role="client_manager",
            organization=self.org
        )

    def test_user_login(self):
        """Test user can login and receive JWT tokens"""
        url = reverse('user-login')
        data = {
            'username': 'test_user',
            'password': 'TestPass123!'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_invalid_login(self):
        """Test login with invalid credentials fails"""
        url = reverse('user-login')
        data = {
            'username': 'test_user',
            'password': 'WrongPassword'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Test JWT token refresh"""
        # First login to get tokens
        login_url = reverse('user-login')
        login_data = {
            'username': 'test_user',
            'password': 'TestPass123!'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        refresh_token = login_response.data['tokens']['refresh']

        # Test token refresh
        refresh_url = reverse('token-refresh')
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(refresh_url, refresh_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_get_current_user(self):
        """Test getting current authenticated user info"""
        # Login first
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('current-user')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'test_user')
        self.assertEqual(response.data['role'], 'client_manager')


class RateLimitingTestCase(APITestCase):
    """Test rate limiting and throttling"""

    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(
            name="Test Organization",
            contact_email="test@example.com"
        )

        self.admin_user = User.objects.create_user(
            username="test_admin",
            email="admin@test.com",
            password="TestPass123!",
            role="network_admin",
            organization=self.org
        )

        self.regular_user = User.objects.create_user(
            username="test_user",
            email="user@test.com",
            password="TestPass123!",
            role="client_manager",
            organization=self.org
        )

    def test_burst_rate_limit_enforced(self):
        """Test that burst rate limit is enforced for regular users"""
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('simcard-list')

        # Make requests up to the limit
        success_count = 0
        throttled_count = 0

        for i in range(65):
            response = self.client.get(url)
            if response.status_code == status.HTTP_200_OK:
                success_count += 1
            elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                throttled_count += 1

        # Should have some successful requests and some throttled
        self.assertGreater(success_count, 50)
        self.assertGreater(throttled_count, 0)

    def test_admin_rate_limit_bypass(self):
        """Test that admins bypass rate limits"""
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('simcard-list')

        # Make many requests - admin should not be throttled
        for i in range(70):
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserModelTestCase(TestCase):
    """Test User model"""

    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(
            name="Test Organization",
            contact_email="test@example.com"
        )

    def test_create_user(self):
        """Test creating a user"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="client_manager",
            organization=self.org
        )

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.role, "client_manager")
        self.assertEqual(user.organization, self.org)
        self.assertTrue(user.check_password("testpass123"))

    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        self.assertIn("testuser", str(user))


class OrganizationModelTestCase(TestCase):
    """Test Organization model"""

    def test_create_organization(self):
        """Test creating an organization"""
        org = Organization.objects.create(
            name="Test Company",
            contact_email="contact@testcompany.com"
        )

        self.assertEqual(org.name, "Test Company")
        self.assertEqual(org.contact_email, "contact@testcompany.com")

    def test_organization_str_representation(self):
        """Test organization string representation"""
        org = Organization.objects.create(
            name="Test Company",
            contact_email="contact@testcompany.com"
        )

        self.assertEqual(str(org), "Test Company")
