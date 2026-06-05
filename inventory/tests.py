from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from inventory.models import APN, SIMCard
from users.models import User, Organization


class APNModelTestCase(TestCase):
    """Test APN model"""

    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(
            name="Test Organization",
            contact_email="test@example.com"
        )

    def test_create_apn(self):
        """Test creating an APN"""
        apn = APN.objects.create(
            name="Test APN",
            apn_string="test.apn.com",
            organization=self.org,
            is_active=True
        )

        self.assertEqual(apn.name, "Test APN")
        self.assertEqual(apn.apn_string, "test.apn.com")
        self.assertTrue(apn.is_active)
        self.assertEqual(apn.organization, self.org)

    def test_apn_str_representation(self):
        """Test APN string representation"""
        apn = APN.objects.create(
            name="Test APN",
            apn_string="test.apn.com"
        )

        self.assertIn("Test APN", str(apn))


class SIMCardModelTestCase(TestCase):
    """Test SIMCard model"""

    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(
            name="Test Organization",
            contact_email="test@example.com"
        )

    def test_create_sim_card(self):
        """Test creating a SIM card"""
        sim = SIMCard.objects.create(
            iccid="8927000000000000001",
            phone_number="+27123456789",
            carrier="Vodacom",
            status="available",
            data_limit_mb=5000,
            organization=self.org
        )

        self.assertEqual(sim.iccid, "8927000000000000001")
        self.assertEqual(sim.carrier, "Vodacom")
        self.assertEqual(sim.status, "available")
        self.assertEqual(sim.data_limit_mb, 5000)

    def test_sim_card_str_representation(self):
        """Test SIM card string representation"""
        sim = SIMCard.objects.create(
            iccid="8927000000000000001",
            phone_number="+27123456789",
            carrier="Vodacom",
            status="available",
            data_limit_mb=5000
        )

        self.assertIn("8927000000000000001", str(sim))


class APNAPITestCase(APITestCase):
    """Test APN API endpoints"""

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

        self.apn = APN.objects.create(
            name="Test APN",
            apn_string="test.apn.com",
            organization=self.org,
            is_active=True
        )

    def test_list_apns(self):
        """Test listing APNs"""
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('apn-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_retrieve_apn(self):
        """Test retrieving a specific APN"""
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('apn-detail', args=[self.apn.apn_id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test APN")

    def test_create_apn_as_admin(self):
        """Test creating an APN as admin"""
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('apn-list')
        data = {
            'name': 'New Test APN',
            'apn_string': 'new.test.apn',
            'is_active': True,
            'organization': self.org.org_id
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Test APN')

    def test_create_apn_as_regular_user_forbidden(self):
        """Test that regular users cannot create APNs"""
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('apn-list')
        data = {
            'name': 'New Test APN',
            'apn_string': 'new.test.apn',
            'is_active': True
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_apn_as_admin(self):
        """Test updating an APN as admin"""
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('apn-detail', args=[self.apn.apn_id])
        data = {'is_active': False}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_active'], False)

    def test_delete_apn_as_admin(self):
        """Test deleting an APN as admin"""
        self.client.force_authenticate(user=self.admin_user)

        apn_to_delete = APN.objects.create(
            name="To Delete",
            apn_string="delete.apn.com",
            organization=self.org
        )

        url = reverse('apn-detail', args=[apn_to_delete.apn_id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(APN.objects.filter(apn_id=apn_to_delete.apn_id).exists())

    def test_search_apns(self):
        """Test searching APNs"""
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('apn-list') + '?search=Test'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class SIMCardAPITestCase(APITestCase):
    """Test SIM Card API endpoints"""

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

        self.sim = SIMCard.objects.create(
            iccid="8927000000000000001",
            phone_number="+27123456789",
            carrier="Vodacom",
            status="available",
            data_limit_mb=5000,
            organization=self.org
        )

    def test_list_sims(self):
        """Test listing SIM cards"""
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('simcard-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_retrieve_sim(self):
        """Test retrieving a specific SIM card"""
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('simcard-detail', args=[self.sim.sim_id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['iccid'], "8927000000000000001")

    def test_create_sim_as_admin(self):
        """Test creating a SIM card as admin"""
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('simcard-list')
        data = {
            'iccid': '8927000000000000002',
            'phone_number': '+27987654321',
            'carrier': 'MTN',
            'status': 'available',
            'data_limit_mb': 10000,
            'organization': self.org.org_id
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['iccid'], '8927000000000000002')

    def test_create_sim_as_regular_user_forbidden(self):
        """Test that regular users cannot create SIM cards"""
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('simcard-list')
        data = {
            'iccid': '8927000000000000003',
            'phone_number': '+27111111111',
            'carrier': 'MTN',
            'status': 'available',
            'data_limit_mb': 5000
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_sim_as_admin(self):
        """Test updating a SIM card as admin"""
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('simcard-detail', args=[self.sim.sim_id])
        data = {'status': 'assigned', 'data_limit_mb': 10000}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'assigned')
        self.assertEqual(response.data['data_limit_mb'], 10000)

    def test_filter_sims_by_status(self):
        """Test filtering SIM cards by status"""
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('simcard-list') + '?status=available'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle paginated response
        data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        for sim in data:
            self.assertEqual(sim['status'], 'available')

    def test_get_available_sims(self):
        """Test getting available SIM cards via custom action"""
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('simcard-available')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_organization_data_isolation(self):
        """Test that users can only see their organization's SIM cards"""
        # Create another organization
        other_org = Organization.objects.create(
            name="Other Organization",
            contact_email="other@example.com"
        )

        # Create SIM in other organization
        other_sim = SIMCard.objects.create(
            iccid="8927000000000000999",
            phone_number="+27999999999",
            carrier="Vodacom",
            status="available",
            data_limit_mb=5000,
            organization=other_org
        )

        # Regular user should not see other org's SIM
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('simcard-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle paginated response
        data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        iccids = [sim['iccid'] for sim in data]
        self.assertNotIn(other_sim.iccid, iccids)
