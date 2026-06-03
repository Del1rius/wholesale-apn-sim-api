from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import timedelta
from decimal import Decimal
from usage.models import BillingCycle, DataUsageRecord
from inventory.models import SIMCard
from users.models import User, Organization


class BillingCycleModelTestCase(TestCase):
    """Test BillingCycle model"""
    
    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(
            name="Test Organization",
            contact_email="test@example.com"
        )
    
    def test_create_billing_cycle(self):
        """Test creating a billing cycle"""
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)
        
        cycle = BillingCycle.objects.create(
            organization=self.org,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
        
        self.assertEqual(cycle.organization, self.org)
        self.assertEqual(cycle.start_date, start_date)
        self.assertEqual(cycle.end_date, end_date)
        self.assertTrue(cycle.is_active)
    
    def test_billing_cycle_str_representation(self):
        """Test billing cycle string representation"""
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)
        
        cycle = BillingCycle.objects.create(
            organization=self.org,
            start_date=start_date,
            end_date=end_date
        )
        
        self.assertIn(str(start_date), str(cycle))
        self.assertIn(str(end_date), str(cycle))


class DataUsageRecordModelTestCase(TestCase):
    """Test DataUsageRecord model"""
    
    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(
            name="Test Organization",
            contact_email="test@example.com"
        )
        
        self.sim = SIMCard.objects.create(
            iccid="8927000000000000001",
            phone_number="+27123456789",
            carrier="Vodacom",
            status="assigned",
            data_limit_mb=5000,
            organization=self.org
        )
        
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)
        
        self.cycle = BillingCycle.objects.create(
            organization=self.org,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
    
    def test_create_usage_record(self):
        """Test creating a data usage record"""
        usage = DataUsageRecord.objects.create(
            sim_card=self.sim,
            billing_cycle=self.cycle,
            data_consumed_mb=Decimal('100.50'),
            recorded_at=timezone.now(),
            source='api_test'
        )
        
        self.assertEqual(usage.sim_card, self.sim)
        self.assertEqual(usage.billing_cycle, self.cycle)
        self.assertEqual(usage.data_consumed_mb, Decimal('100.50'))
        self.assertEqual(usage.source, 'api_test')


class BillingCycleAPITestCase(APITestCase):
    """Test Billing Cycle API endpoints"""
    
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
        
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)
        
        self.cycle = BillingCycle.objects.create(
            organization=self.org,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
    
    def test_list_billing_cycles(self):
        """Test listing billing cycles"""
        self.client.force_authenticate(user=self.regular_user)
        
        url = reverse('billingcycle-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_retrieve_billing_cycle(self):
        """Test retrieving a specific billing cycle"""
        self.client.force_authenticate(user=self.regular_user)
        
        url = reverse('billingcycle-detail', args=[self.cycle.cycle_id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cycle_id'], str(self.cycle.cycle_id))
    
    def test_get_active_billing_cycles(self):
        """Test getting active billing cycles"""
        self.client.force_authenticate(user=self.regular_user)
        
        url = reverse('billingcycle-active')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for cycle in response.data:
            self.assertTrue(cycle['is_active'])
    
    def test_get_usage_summary(self):
        """Test getting usage summary for a billing cycle"""
        # Create a SIM and usage record
        sim = SIMCard.objects.create(
            iccid="8927000000000000001",
            phone_number="+27123456789",
            carrier="Vodacom",
            status="assigned",
            data_limit_mb=5000,
            organization=self.org
        )
        
        DataUsageRecord.objects.create(
            sim_card=sim,
            billing_cycle=self.cycle,
            data_consumed_mb=Decimal('250.00'),
            recorded_at=timezone.now(),
            source='api_test'
        )
        
        self.client.force_authenticate(user=self.regular_user)
        
        url = reverse('billingcycle-usage-summary', args=[self.cycle.cycle_id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_usage_mb', response.data)


class DataUsageRecordAPITestCase(APITestCase):
    """Test Data Usage Record API endpoints"""
    
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
            status="assigned",
            data_limit_mb=5000,
            organization=self.org
        )
        
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)
        
        self.cycle = BillingCycle.objects.create(
            organization=self.org,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
        
        self.usage = DataUsageRecord.objects.create(
            sim_card=self.sim,
            billing_cycle=self.cycle,
            data_consumed_mb=Decimal('100.00'),
            recorded_at=timezone.now(),
            source='api_test'
        )
    
    def test_list_usage_records(self):
        """Test listing usage records"""
        self.client.force_authenticate(user=self.regular_user)
        
        url = reverse('usagerecord-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_retrieve_usage_record(self):
        """Test retrieving a specific usage record"""
        self.client.force_authenticate(user=self.regular_user)
        
        url = reverse('usagerecord-detail', args=[self.usage.record_id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['record_id'], str(self.usage.record_id))
    
    def test_create_usage_record(self):
        """Test creating a usage record"""
        self.client.force_authenticate(user=self.regular_user)
        
        url = reverse('usagerecord-list')
        data = {
            'sim_card': self.sim.sim_id,
            'billing_cycle': self.cycle.cycle_id,
            'data_consumed_mb': 50.00,
            'recorded_at': timezone.now().isoformat(),
            'source': 'api_test',
            'notes': 'Test usage record'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_get_recent_usage_records(self):
        """Test getting recent usage records"""
        self.client.force_authenticate(user=self.regular_user)
        
        url = reverse('usagerecord-recent')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_usage_summary(self):
        """Test getting usage summary"""
        self.client.force_authenticate(user=self.regular_user)
        
        url = reverse('usagerecord-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
    
    def test_filter_usage_by_sim(self):
        """Test filtering usage records by SIM card"""
        self.client.force_authenticate(user=self.regular_user)
        
        url = reverse('usagerecord-list') + f'?sim_card={self.sim.sim_id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_usage_by_date_range(self):
        """Test filtering usage records by date range"""
        self.client.force_authenticate(user=self.regular_user)
        
        start_date = (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        url = reverse('usagerecord-list') + f'?start_date={start_date}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_organization_data_isolation(self):
        """Test that users can only see their organization's usage records"""
        # Create another organization with SIM and usage
        other_org = Organization.objects.create(
            name="Other Organization",
            contact_email="other@example.com"
        )
        
        other_sim = SIMCard.objects.create(
            iccid="8927000000000000999",
            phone_number="+27999999999",
            carrier="Vodacom",
            status="assigned",
            data_limit_mb=5000,
            organization=other_org
        )
        
        other_cycle = BillingCycle.objects.create(
            organization=other_org,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
            is_active=True
        )
        
        other_usage = DataUsageRecord.objects.create(
            sim_card=other_sim,
            billing_cycle=other_cycle,
            data_consumed_mb=Decimal('200.00'),
            recorded_at=timezone.now(),
            source='api_test'
        )
        
        # Regular user should not see other org's usage
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('usagerecord-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle paginated response
        data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        record_ids = [record['record_id'] for record in data]
        self.assertNotIn(str(other_usage.record_id), record_ids)
